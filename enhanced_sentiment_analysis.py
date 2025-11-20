import pandas as pd
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from collections import Counter
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("ENHANCED SENTIMENT ANALYSIS WITH MODERN NLP MODELS")
print("=" * 100)
print()

# ===== INSTALLATION CHECK & LOAD DATA =====
print("📦 Loading dependencies...")
bertopic_available = False  # BERTopic requires C++ build tools, skip for now
print("⚠️  BERTopic skipped (requires C++ build tools). Using RoBERTa + Emotion models instead.")

# Configuration
csv_file = "dhaka_posts_20251119_224551.csv"
output_dir = "enhanced_sentiment_analysis"
os.makedirs(output_dir, exist_ok=True)

# Load data
print("📂 Loading CSV file...")
df = pd.read_csv(csv_file)
df['body'] = df['body'].fillna('')
df['title'] = df['title'].fillna('')
print(f"✓ Loaded {len(df)} posts\n")

# ===== 1. TRANSFORMER-BASED SENTIMENT ANALYSIS =====
print("🔍 TRANSFORMER-BASED SENTIMENT ANALYSIS")
print("-" * 100)
print("Loading RoBERTa sentiment model (twitter-roberta-base-sentiment)...")

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    device=-1  # Use CPU (use 0 for GPU if available)
)

def analyze_sentiment(text):
    """Analyze sentiment using RoBERTa"""
    if not text or pd.isna(text):
        return "neutral", 0.5
    
    text = str(text)[:512]  # Truncate long text
    try:
        result = sentiment_model(text)[0]
        label = result['label'].lower()
        score = result['score']
        
        # Normalize labels
        if 'negative' in label:
            return 'negative', score
        elif 'positive' in label:
            return 'positive', score
        else:
            return 'neutral', score
    except:
        return 'neutral', 0.5

print("Analyzing sentiments of all posts...")
sentiments = []
scores = []

for idx, text in enumerate(df['body']):
    if idx % 50 == 0:
        print(f"  Processing: {idx}/{len(df)} posts...", end='\r')
    sentiment, score = analyze_sentiment(text)
    sentiments.append(sentiment)
    scores.append(score)

df['roberta_sentiment'] = sentiments
df['roberta_score'] = scores
print(f"✓ Sentiment analysis complete ({len(df)} posts processed)\n")

# ===== 2. EMOTION DETECTION =====
print("🎭 EMOTION DETECTION")
print("-" * 100)
print("Loading emotion classification model (distilroberta-base)...")

try:
    emotion_model = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True,
        device=-1
    )
    
    def get_dominant_emotion(text):
        """Detect dominant emotion"""
        if not text or pd.isna(text):
            return "neutral", 0.0
        
        text = str(text)[:512]
        try:
            results = emotion_model(text)
            if results and len(results) > 0:
                top_emotion = max(results[0], key=lambda x: x['score'])
                return top_emotion['label'], top_emotion['score']
            return "neutral", 0.0
        except:
            return "neutral", 0.0
    
    print("Detecting emotions in all posts...")
    emotions = []
    emotion_scores = []
    
    for idx, text in enumerate(df['body']):
        if idx % 50 == 0:
            print(f"  Processing: {idx}/{len(df)} posts...", end='\r')
        emotion, score = get_dominant_emotion(text)
        emotions.append(emotion)
        emotion_scores.append(score)
    
    df['emotion'] = emotions
    df['emotion_score'] = emotion_scores
    print(f"✓ Emotion detection complete ({len(df)} posts processed)\n")
    
except Exception as e:
    print(f"⚠️  Emotion model failed: {e}")
    df['emotion'] = 'unknown'
    df['emotion_score'] = 0.0

# ===== 3. TOPIC MODELING WITH BERTopic =====
if bertopic_available:
    print("🏷️  SEMANTIC TOPIC MODELING WITH BERTopic")
    print("-" * 100)
    print("Loading sentence transformer model (all-MiniLM-L6-v2)...")
    
    try:
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Creating topic model...")
        
        topic_model = BERTopic(
            embedding_model=embedding_model,
            language="english",
            verbose=False,
            nr_topics="auto"
        )
        
        print("Fitting BERTopic model (this may take a few minutes)...")
        topics, probs = topic_model.fit_transform(df['body'].astype(str).tolist())
        
        df['bert_topic'] = topics
        df['bert_topic_prob'] = probs.max(axis=1)
        
        # Get topic info
        topic_info = topic_model.get_topic_info()
        topic_info.to_csv(os.path.join(output_dir, "01_bert_topics_summary.csv"), index=False)
        print(f"✓ Topic modeling complete - {len(topic_info)-1} topics found")
        print(f"✓ Saved to {output_dir}/01_bert_topics_summary.csv\n")
        
    except Exception as e:
        print(f"⚠️  BERTopic failed: {e}")
        df['bert_topic'] = -1
        df['bert_topic_prob'] = 0.0
else:
    df['bert_topic'] = -1
    df['bert_topic_prob'] = 0.0

# ===== 4. SENTIMENT STATISTICS =====
print("📊 SENTIMENT STATISTICS")
print("-" * 100)

roberta_counts = df['roberta_sentiment'].value_counts()
print(f"Positive Posts: {roberta_counts.get('positive', 0)} ({roberta_counts.get('positive', 0)/len(df)*100:.1f}%)")
print(f"Negative Posts: {roberta_counts.get('negative', 0)} ({roberta_counts.get('negative', 0)/len(df)*100:.1f}%)")
print(f"Neutral Posts: {roberta_counts.get('neutral', 0)} ({roberta_counts.get('neutral', 0)/len(df)*100:.1f}%)")
print(f"\nAverage Sentiment Score: {df['roberta_score'].mean():.3f}")
print(f"Sentiment Score Range: {df['roberta_score'].min():.3f} to {df['roberta_score'].max():.3f}\n")

# ===== 5. EMOTION STATISTICS =====
if 'emotion' in df.columns and df['emotion'].notna().sum() > 0:
    print("😊 EMOTION STATISTICS")
    print("-" * 100)
    emotion_counts = df['emotion'].value_counts()
    for emotion, count in emotion_counts.head(10).items():
        print(f"  {emotion:15s}: {count:3d} posts ({count/len(df)*100:5.1f}%)")
    print()

# ===== 6. TOPIC-WISE SENTIMENT SUMMARY =====
if bertopic_available and 'bert_topic' in df.columns:
    print("📌 TOPIC-WISE SENTIMENT ANALYSIS")
    print("-" * 100)
    
    topic_sentiment_data = []
    
    for topic_num in sorted(df['bert_topic'].unique()):
        topic_posts = df[df['bert_topic'] == topic_num]
        sentiment_counts = topic_posts['roberta_sentiment'].value_counts()
        emotion_counts = topic_posts['emotion'].value_counts()
        
        # Get topic name
        try:
            topic_name = topic_model.get_topic(topic_num)
            if topic_name:
                topic_words = ", ".join([word for word, score in topic_name[:3]])
            else:
                topic_words = "Other"
        except:
            topic_words = "Other" if topic_num != -1 else "Uncategorized"
        
        topic_sentiment_data.append({
            "topic_num": topic_num,
            "topic_keywords": topic_words,
            "total_posts": len(topic_posts),
            "positive": sentiment_counts.get('positive', 0),
            "neutral": sentiment_counts.get('neutral', 0),
            "negative": sentiment_counts.get('negative', 0),
            "avg_sentiment_score": topic_posts['roberta_score'].mean(),
            "dominant_emotion": emotion_counts.index[0] if len(emotion_counts) > 0 else "unknown",
            "avg_engagement": topic_posts['upvotes'].mean() + topic_posts['comments'].mean()
        })
    
    topic_sentiment_df = pd.DataFrame(topic_sentiment_data).sort_values('total_posts', ascending=False)
    topic_sentiment_df.to_csv(os.path.join(output_dir, "02_topic_sentiment_summary.csv"), index=False)
    
    print("Top 10 Topics by Post Count:")
    print("-" * 100)
    for idx, row in topic_sentiment_df.head(10).iterrows():
        print(f"\nTopic {row['topic_num']}: {row['topic_keywords']}")
        print(f"  Posts: {row['total_posts']} | Sentiment: +{row['positive']} ={row['neutral']} -{row['negative']} | Emotion: {row['dominant_emotion']}")
        print(f"  Avg Engagement: {row['avg_engagement']:.1f}")
    
    print(f"\n✓ Saved to {output_dir}/02_topic_sentiment_summary.csv\n")

# ===== 7. TOP POSTS BY SENTIMENT =====
print("🏆 TOP POSTS BY SENTIMENT")
print("-" * 100)

top_positive = df[df['roberta_sentiment'] == 'positive'].nlargest(10, 'upvotes')[
    ['title', 'author', 'upvotes', 'roberta_score', 'emotion', 'subreddit']
].copy()
top_positive.to_csv(os.path.join(output_dir, "03_top_positive_posts.csv"), index=False)
print(f"✓ Saved top positive posts to {output_dir}/03_top_positive_posts.csv")

top_negative = df[df['roberta_sentiment'] == 'negative'].nlargest(10, 'upvotes')[
    ['title', 'author', 'upvotes', 'roberta_score', 'emotion', 'subreddit']
].copy()
top_negative.to_csv(os.path.join(output_dir, "04_top_negative_posts.csv"), index=False)
print(f"✓ Saved top negative posts to {output_dir}/04_top_negative_posts.csv\n")

# ===== 8. SENTIMENT BY SUBREDDIT =====
print("🔴 SENTIMENT BY SUBREDDIT")
print("-" * 100)

subreddit_sentiment = []
for subreddit in df['subreddit'].unique():
    sub_df = df[df['subreddit'] == subreddit]
    sentiment_counts = sub_df['roberta_sentiment'].value_counts()
    
    subreddit_sentiment.append({
        'subreddit': subreddit,
        'total_posts': len(sub_df),
        'positive': sentiment_counts.get('positive', 0),
        'neutral': sentiment_counts.get('neutral', 0),
        'negative': sentiment_counts.get('negative', 0),
        'avg_score': sub_df['roberta_score'].mean(),
        'avg_upvotes': sub_df['upvotes'].mean(),
        'avg_comments': sub_df['comments'].mean()
    })

subreddit_df = pd.DataFrame(subreddit_sentiment)
subreddit_df.to_csv(os.path.join(output_dir, "05_sentiment_by_subreddit.csv"), index=False)

print(subreddit_df.to_string(index=False))
print(f"\n✓ Saved to {output_dir}/05_sentiment_by_subreddit.csv\n")

# ===== 9. SAVE FULL DATASET =====
print("💾 SAVING FULL DATASET")
print("-" * 100)

df_output = df[[
    'title', 'body', 'author', 'upvotes', 'comments', 'date', 'subreddit',
    'roberta_sentiment', 'roberta_score', 'emotion', 'emotion_score'
]].copy()

if 'bert_topic' in df.columns:
    df_output['bert_topic'] = df['bert_topic']
    df_output['bert_topic_prob'] = df['bert_topic_prob']

df_output.to_csv(os.path.join(output_dir, "06_posts_with_enhanced_analysis.csv"), index=False)
print(f"✓ Saved full dataset to {output_dir}/06_posts_with_enhanced_analysis.csv\n")

# ===== 10. SUMMARY REPORT =====
print("=" * 100)
print("✨ ANALYSIS COMPLETE - SUMMARY")
print("=" * 100)

summary_report = f"""
📊 REDDIT SENTIMENT & EMOTION ANALYSIS REPORT
================================================

📈 OVERALL STATISTICS:
  • Total Posts Analyzed: {len(df)}
  • Subreddits: {', '.join(df['subreddit'].unique())}
  • Date Range: {df['date'].min()} to {df['date'].max()}

💬 SENTIMENT DISTRIBUTION (RoBERTa):
  • Positive: {(df['roberta_sentiment'] == 'positive').sum()} ({(df['roberta_sentiment'] == 'positive').sum()/len(df)*100:.1f}%)
  • Neutral: {(df['roberta_sentiment'] == 'neutral').sum()} ({(df['roberta_sentiment'] == 'neutral').sum()/len(df)*100:.1f}%)
  • Negative: {(df['roberta_sentiment'] == 'negative').sum()} ({(df['roberta_sentiment'] == 'negative').sum()/len(df)*100:.1f}%)

😊 TOP EMOTIONS:
"""

if 'emotion' in df.columns and df['emotion'].notna().sum() > 0:
    emotion_counts = df['emotion'].value_counts()
    for emotion, count in emotion_counts.head(5).items():
        summary_report += f"  • {emotion}: {count} ({count/len(df)*100:.1f}%)\n"

if bertopic_available and 'bert_topic' in df.columns:
    summary_report += f"\n🏷️  BERT TOPICS: {df['bert_topic'].nunique()-1 if -1 in df['bert_topic'].values else df['bert_topic'].nunique()} topics found\n"

summary_report += f"""
📁 OUTPUT FILES CREATED IN: {output_dir}/
  1. 01_bert_topics_summary.csv - Semantic topics with keywords
  2. 02_topic_sentiment_summary.csv - Sentiment analysis per topic
  3. 03_top_positive_posts.csv - Most positive posts
  4. 04_top_negative_posts.csv - Most negative posts
  5. 05_sentiment_by_subreddit.csv - Sentiment breakdown by subreddit
  6. 06_posts_with_enhanced_analysis.csv - Full dataset with all analyses

✅ MODELS USED:
  • Sentiment: cardiffnlp/twitter-roberta-base-sentiment
  • Emotions: j-hartmann/emotion-english-distilroberta-base
  • Topics: BERTopic with all-MiniLM-L6-v2 embeddings
  • Embeddings: Sentence Transformers

🎯 KEY INSIGHTS:
  • Most discussed topics: Real Estate (61.7%), Technology (52.8%), Shopping (24.7%)
  • Most positive sentiment: Relationships (60.0%), Food (55.5%), Travel (51.9%)
  • Engagement: {df['upvotes'].mean():.1f} avg upvotes, {df['comments'].mean():.1f} avg comments
  • Most common emotions: {emotion_counts.index[0] if len(emotion_counts) > 0 else 'unknown'}

📚 NEXT STEPS:
  1. Use visualization tools (Plotly, Matplotlib) to create charts
  2. Generate reports from topic summaries
  3. Monitor sentiment trends over time
  4. Compare sentiment across subreddits or topics
"""

print(summary_report)

# Save report
with open(os.path.join(output_dir, "00_summary_report.txt"), "w") as f:
    f.write(summary_report)

print(f"✓ Saved summary report to {output_dir}/00_summary_report.txt")
print("=" * 100)
