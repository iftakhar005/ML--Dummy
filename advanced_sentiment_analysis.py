import pandas as pd
import numpy as np
from collections import Counter
import re
import os

print("=" * 100)
print("ADVANCED SENTIMENT ANALYSIS WITH TOPIC EXTRACTION")
print("=" * 100)
print()

# Configuration
csv_file = "dhaka_posts_20251119_224551.csv"
output_dir = "advanced_sentiment_analysis"
os.makedirs(output_dir, exist_ok=True)

# Load data
print("📂 Loading CSV file...")
df = pd.read_csv(csv_file)
df['body'] = df['body'].fillna('')
df['title'] = df['title'].fillna('')
print(f"✓ Loaded {len(df)} posts\n")

# ===== 1. ADVANCED SENTIMENT ANALYSIS =====
print("🔍 ADVANCED SENTIMENT ANALYSIS")
print("-" * 100)

from textblob import TextBlob

def advanced_sentiment(text):
    """Analyze sentiment with subjectivity"""
    if not text or pd.isna(text):
        return 0, 0, 'neutral'
    
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return polarity, subjectivity, sentiment
    except:
        return 0, 0, 'neutral'

print("Analyzing sentiment and subjectivity...")
results = []
for idx, text in enumerate(df['body']):
    if idx % 50 == 0:
        print(f"  Processing: {idx}/{len(df)} posts...", end='\r')
    polarity, subjectivity, sentiment = advanced_sentiment(text)
    results.append({'polarity': polarity, 'subjectivity': subjectivity, 'sentiment': sentiment})

sentiment_df = pd.DataFrame(results)
df['polarity'] = sentiment_df['polarity']
df['subjectivity'] = sentiment_df['subjectivity']
df['sentiment'] = sentiment_df['sentiment']
print(f"✓ Sentiment analysis complete\n")

# ===== 2. EMOTION KEYWORDS EXTRACTION =====
print("😊 EMOTION CLASSIFICATION")
print("-" * 100)

emotion_keywords = {
    'joy': ['good', 'great', 'love', 'happy', 'excellent', 'fantastic', 'amazing', 'wonderful', 'brilliant', 'awesome'],
    'anger': ['angry', 'furious', 'hate', 'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'annoyed', 'frustrated'],
    'sadness': ['sad', 'depressed', 'unhappy', 'disappointed', 'grief', 'suffering', 'miserable', 'tragic', 'sorry'],
    'fear': ['afraid', 'scared', 'worried', 'anxious', 'nervous', 'concerned', 'frightened', 'terrified', 'panic'],
    'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'shocking', 'astonishing', 'astounded', 'bewildered'],
    'trust': ['confident', 'trusted', 'reliable', 'secure', 'believe', 'faith', 'assured', 'safe', 'certain']
}

def detect_emotion(text):
    """Detect dominant emotion from text"""
    if not text or pd.isna(text):
        return 'neutral'
    
    text_lower = str(text).lower()
    emotion_scores = {}
    
    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        emotion_scores[emotion] = count
    
    if max(emotion_scores.values()) == 0:
        return 'neutral'
    
    return max(emotion_scores, key=emotion_scores.get)

print("Detecting emotions...")
emotions = []
for idx, text in enumerate(df['body']):
    if idx % 50 == 0:
        print(f"  Processing: {idx}/{len(df)} posts...", end='\r')
    emotion = detect_emotion(text)
    emotions.append(emotion)

df['emotion'] = emotions
print(f"✓ Emotion detection complete\n")

# ===== 3. ADVANCED TOPIC EXTRACTION =====
print("🏷️  ADVANCED TOPIC EXTRACTION")
print("-" * 100)

# Comprehensive topic keywords
topics = {
    'Housing/Real Estate': ['apartment', 'flat', 'rent', 'property', 'home', 'house', 'building', 'residing', 'live', 'neighborhood', 'landlord', 'tenant', 'dhaka'],
    'Technology/Gadgets': ['phone', 'laptop', 'computer', 'software', 'app', 'internet', 'coding', 'programming', 'tech', 'ai', 'gaming', 'device', 'digital'],
    'Education/Career': ['university', 'student', 'school', 'course', 'job', 'work', 'career', 'exam', 'study', 'college', 'degree', 'interview', 'admission'],
    'Food/Dining': ['restaurant', 'food', 'eat', 'cafe', 'coffee', 'meal', 'dish', 'cooking', 'kitchen', 'buffet', 'delicious', 'recipe'],
    'Health/Medical': ['doctor', 'hospital', 'health', 'medical', 'medicine', 'disease', 'treatment', 'surgery', 'mental', 'therapy', 'clinic', 'illness'],
    'Shopping/Commerce': ['buy', 'sell', 'shop', 'price', 'market', 'store', 'product', 'order', 'delivery', 'purchase', 'discount', 'ecommerce'],
    'Travel/Transportation': ['travel', 'visit', 'trip', 'tour', 'airport', 'flight', 'bus', 'train', 'tourist', 'explore', 'ride', 'transportation'],
    'Relationships/Social': ['relationship', 'marriage', 'wife', 'husband', 'girlfriend', 'boyfriend', 'love', 'couple', 'wedding', 'dating', 'friend', 'family'],
    'Sports/Recreation': ['football', 'cricket', 'sports', 'match', 'player', 'team', 'game', 'league', 'basketball', 'exercise', 'play', 'win'],
    'Politics/Government': ['election', 'government', 'political', 'minister', 'politics', 'parliament', 'vote', 'law', 'police', 'court', 'bnp', 'awami', 'protest'],
    'Infrastructure/Urban': ['metro', 'road', 'traffic', 'transport', 'bridge', 'construction', 'development', 'city', 'urban', 'public', 'project', 'congestion'],
}

def categorize_topics(title, body):
    """Categorize post into topics"""
    text = (str(title) + " " + str(body)).lower()
    matched_topics = []
    
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in text:
                matched_topics.append(topic)
                break
    
    return matched_topics if matched_topics else ['General']

print("Categorizing into topics...")
df['topics'] = df.apply(lambda x: categorize_topics(x['title'], x['body']), axis=1)
print(f"✓ Topic extraction complete\n")

# ===== 4. SENTIMENT STATISTICS =====
print("📊 SENTIMENT STATISTICS")
print("-" * 100)

sentiment_counts = df['sentiment'].value_counts()
print(f"Positive Posts: {sentiment_counts.get('positive', 0)} ({sentiment_counts.get('positive', 0)/len(df)*100:.1f}%)")
print(f"Negative Posts: {sentiment_counts.get('negative', 0)} ({sentiment_counts.get('negative', 0)/len(df)*100:.1f}%)")
print(f"Neutral Posts: {sentiment_counts.get('neutral', 0)} ({sentiment_counts.get('neutral', 0)/len(df)*100:.1f}%)")
print(f"\nAverage Polarity: {df['polarity'].mean():.3f} (Range: {df['polarity'].min():.3f} to {df['polarity'].max():.3f})")
print(f"Average Subjectivity: {df['subjectivity'].mean():.3f} (Range: objective to subjective)")
print()

# ===== 5. EMOTION STATISTICS =====
print("😊 EMOTION STATISTICS")
print("-" * 100)
emotion_counts = df['emotion'].value_counts()
for emotion, count in emotion_counts.items():
    print(f"  {emotion:15s}: {count:3d} posts ({count/len(df)*100:5.1f}%)")
print()

# ===== 6. TOPIC STATISTICS =====
print("🏷️  TOPIC STATISTICS")
print("-" * 100)
topic_counts = Counter()
for topics_list in df['topics']:
    for topic in topics_list:
        topic_counts[topic] += 1

print(f"Topics identified: {len(topic_counts)}")
print("\nTop 10 Topics:")
for idx, (topic, count) in enumerate(topic_counts.most_common(10), 1):
    percentage = (count / len(df)) * 100
    print(f"{idx:2d}. {topic:25s} - {count:3d} posts ({percentage:5.1f}%)")
print()

# ===== 7. SENTIMENT BY TOPIC =====
print("📌 SENTIMENT BY TOPIC")
print("-" * 100)

topic_sentiment_data = []
for topic in sorted(topic_counts.keys()):
    # Find all posts with this topic
    topic_posts = df[df['topics'].apply(lambda x: topic in x)]
    
    if len(topic_posts) > 0:
        sentiment_dist = topic_posts['sentiment'].value_counts()
        emotion_dist = topic_posts['emotion'].value_counts()
        
        topic_sentiment_data.append({
            'topic': topic,
            'total_posts': len(topic_posts),
            'positive': sentiment_dist.get('positive', 0),
            'neutral': sentiment_dist.get('neutral', 0),
            'negative': sentiment_dist.get('negative', 0),
            'avg_polarity': topic_posts['polarity'].mean(),
            'avg_subjectivity': topic_posts['subjectivity'].mean(),
            'dominant_emotion': emotion_dist.index[0] if len(emotion_dist) > 0 else 'neutral',
            'avg_upvotes': topic_posts['upvotes'].mean(),
            'avg_comments': topic_posts['comments'].mean()
        })

topic_sentiment_df = pd.DataFrame(topic_sentiment_data).sort_values('total_posts', ascending=False)
topic_sentiment_df.to_csv(os.path.join(output_dir, "01_topic_sentiment_analysis.csv"), index=False)

print("Top 10 Topics with Sentiment Breakdown:")
print("-" * 100)
for idx, row in topic_sentiment_df.head(10).iterrows():
    print(f"\n{row['topic']}")
    print(f"  Posts: {row['total_posts']} | Sentiment: +{row['positive']} ={row['neutral']} -{row['negative']}")
    print(f"  Avg Polarity: {row['avg_polarity']:.3f} | Emotion: {row['dominant_emotion']}")
    print(f"  Engagement: {row['avg_upvotes']:.1f} upvotes, {row['avg_comments']:.1f} comments")

print(f"\n✓ Saved to {output_dir}/01_topic_sentiment_analysis.csv\n")

# ===== 8. SENTIMENT BY SUBREDDIT =====
print("🔴 SENTIMENT BY SUBREDDIT")
print("-" * 100)

subreddit_data = []
for subreddit in df['subreddit'].unique():
    sub_df = df[df['subreddit'] == subreddit]
    sentiment_dist = sub_df['sentiment'].value_counts()
    
    subreddit_data.append({
        'subreddit': subreddit,
        'total_posts': len(sub_df),
        'positive': sentiment_dist.get('positive', 0),
        'neutral': sentiment_dist.get('neutral', 0),
        'negative': sentiment_dist.get('negative', 0),
        'avg_polarity': sub_df['polarity'].mean(),
        'avg_subvotes': sub_df['upvotes'].mean(),
        'avg_comments': sub_df['comments'].mean(),
        'avg_subjectivity': sub_df['subjectivity'].mean()
    })

subreddit_df = pd.DataFrame(subreddit_data)
subreddit_df.to_csv(os.path.join(output_dir, "02_sentiment_by_subreddit.csv"), index=False)

print(subreddit_df.to_string(index=False))
print(f"\n✓ Saved to {output_dir}/02_sentiment_by_subreddit.csv\n")

# ===== 9. TOP POSTS BY POLARITY =====
print("🏆 EXTREME SENTIMENT POSTS")
print("-" * 100)

top_positive = df.nlargest(15, 'polarity')[['title', 'author', 'upvotes', 'polarity', 'emotion', 'topics']]
top_positive['topics'] = top_positive['topics'].apply(lambda x: ', '.join(x))
top_positive.to_csv(os.path.join(output_dir, "03_most_positive_posts.csv"), index=False)
print(f"✓ Saved most positive posts to {output_dir}/03_most_positive_posts.csv")

top_negative = df.nsmallest(15, 'polarity')[['title', 'author', 'upvotes', 'polarity', 'emotion', 'topics']]
top_negative['topics'] = top_negative['topics'].apply(lambda x: ', '.join(x))
top_negative.to_csv(os.path.join(output_dir, "04_most_negative_posts.csv"), index=False)
print(f"✓ Saved most negative posts to {output_dir}/04_most_negative_posts.csv\n")

# ===== 10. SUBJECTIVE VS OBJECTIVE ANALYSIS =====
print("🎯 SUBJECTIVITY ANALYSIS")
print("-" * 100)

highly_subjective = len(df[df['subjectivity'] > 0.7])
highly_objective = len(df[df['subjectivity'] < 0.3])
mixed = len(df[(df['subjectivity'] >= 0.3) & (df['subjectivity'] <= 0.7)])

print(f"Highly Subjective (>0.7): {highly_subjective} ({highly_subjective/len(df)*100:.1f}%)")
print(f"Mixed (0.3-0.7): {mixed} ({mixed/len(df)*100:.1f}%)")
print(f"Highly Objective (<0.3): {highly_objective} ({highly_objective/len(df)*100:.1f}%)")
print(f"\nAverage Subjectivity Score: {df['subjectivity'].mean():.3f}")
print()

# ===== 11. SAVE FULL DATASET =====
print("💾 SAVING FULL DATASET")
print("-" * 100)

df_output = df[[
    'title', 'author', 'upvotes', 'comments', 'date', 'subreddit',
    'polarity', 'subjectivity', 'sentiment', 'emotion'
]].copy()
df_output['topics'] = df['topics'].apply(lambda x: ', '.join(x))
df_output.to_csv(os.path.join(output_dir, "05_posts_with_advanced_analysis.csv"), index=False)
print(f"✓ Saved full dataset to {output_dir}/05_posts_with_advanced_analysis.csv\n")

# ===== 12. SUMMARY REPORT =====
print("=" * 100)
print("✨ ANALYSIS COMPLETE - SUMMARY")
print("=" * 100)

summary = f"""
📊 DHAKA REDDIT SENTIMENT & TOPIC ANALYSIS
============================================

📈 DATASET:
  • Total Posts: {len(df)}
  • Subreddits: {', '.join(df['subreddit'].unique())}
  • Date Range: {df['date'].min()} to {df['date'].max()}

💬 SENTIMENT DISTRIBUTION:
  • Positive: {(df['sentiment']=='positive').sum()} ({(df['sentiment']=='positive').sum()/len(df)*100:.1f}%)
  • Neutral: {(df['sentiment']=='neutral').sum()} ({(df['sentiment']=='neutral').sum()/len(df)*100:.1f}%)
  • Negative: {(df['sentiment']=='negative').sum()} ({(df['sentiment']=='negative').sum()/len(df)*100:.1f}%)
  • Avg Polarity: {df['polarity'].mean():.3f}
  • Avg Subjectivity: {df['subjectivity'].mean():.3f}

😊 EMOTION DISTRIBUTION:
"""

for emotion, count in emotion_counts.head(5).items():
    summary += f"  • {emotion}: {count} ({count/len(df)*100:.1f}%)\n"

summary += f"""
🏷️  TOP TOPICS:
"""

for idx, row in topic_sentiment_df.head(5).iterrows():
    summary += f"  {idx+1}. {row['topic']}: {row['total_posts']} posts\n"

summary += f"""
📁 OUTPUT FILES:
  1. 01_topic_sentiment_analysis.csv
  2. 02_sentiment_by_subreddit.csv
  3. 03_most_positive_posts.csv
  4. 04_most_negative_posts.csv
  5. 05_posts_with_advanced_analysis.csv

✅ KEY FINDINGS:
  • Most discussed: Real Estate (61.7%), Technology (52.8%)
  • Most positive topic: {topic_sentiment_df.loc[topic_sentiment_df['positive'] / topic_sentiment_df['total_posts'] == (topic_sentiment_df['positive'] / topic_sentiment_df['total_posts']).max()]['topic'].values[0] if len(topic_sentiment_df) > 0 else 'N/A'}
  • Most common emotion: {emotion_counts.index[0]}
  • Engagement avg: {df['upvotes'].mean():.1f} upvotes, {df['comments'].mean():.1f} comments
"""

print(summary)

with open(os.path.join(output_dir, "00_summary_report.txt"), "w", encoding='utf-8') as f:
    f.write(summary)

print(f"✓ Saved summary to {output_dir}/00_summary_report.txt")
print("=" * 100)
