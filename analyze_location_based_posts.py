import pandas as pd
from textblob import TextBlob
from collections import Counter
import re
import os

print("=" * 100)
print("SENTIMENT ANALYSIS - POSTS FROM DHAKA USERS (LOCATION-BASED)")
print("=" * 100)
print()

# Load location-based posts
df = pd.read_csv("location_based_posts_20251119_232939.csv")

print(f"📊 Dataset: {len(df)} posts from Dhaka-located users")
print(f"Date Range: Last 3 months")
print()

# ===== SENTIMENT ANALYSIS =====
def advanced_sentiment(text):
    """Calculate sentiment with polarity and subjectivity"""
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

# ===== EMOTION DETECTION =====
emotion_keywords = {
    'joy': ['good', 'great', 'love', 'happy', 'excellent', 'amazing', 'awesome', 'wonderful', 
            'best', 'beautiful', 'perfect', 'nice', 'fantastic', 'brilliant', 'lovely', 'enjoyed'],
    'anger': ['angry', 'furious', 'hate', 'bad', 'terrible', 'awful', 'horrible', 'disgusting',
              'frustrated', 'annoyed', 'upset', 'irritated', 'outrageous', 'worst', 'stupid', 'dumb'],
    'sadness': ['sad', 'depressed', 'unhappy', 'down', 'miserable', 'sorrowful', 'hurt', 
                'broken', 'heartbroken', 'cry', 'suffering', 'struggle', 'difficult', 'hard'],
    'fear': ['afraid', 'scared', 'worried', 'anxious', 'nervous', 'panic', 'fear', 'terrified',
             'concerned', 'uncertain', 'risky', 'danger', 'dangerous', 'threat'],
    'trust': ['trust', 'reliable', 'recommend', 'believe', 'confident', 'honest', 'faithful',
              'loyal', 'sincere', 'genuine', 'authentic', 'credible', 'reputable'],
    'surprise': ['surprise', 'amazing', 'shocking', 'unexpected', 'wow', 'astonished', 'stunned',
                 'amazed', 'surprising', 'interesting', 'curious', 'intrigued']
}

def detect_emotion(text):
    """Detect emotions in text"""
    text_lower = str(text).lower()
    emotions_found = {}
    
    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        if count > 0:
            emotions_found[emotion] = count
    
    if emotions_found:
        return max(emotions_found, key=emotions_found.get)
    return 'neutral'

# ===== TOPIC CATEGORIZATION =====
topic_keywords = {
    'Food/Dining': ['food', 'restaurant', 'eat', 'cafe', 'breakfast', 'lunch', 'dinner', 'soup', 'biryani', 'pizza', 'burger', 'tea'],
    'Healthcare/Medical': ['doctor', 'hospital', 'dermatologist', 'surgery', 'medicine', 'health', 'patient', 'disease', 'treatment', 'psychiatrist', 'dental'],
    'Housing/Real Estate': ['flat', 'apartment', 'rent', 'house', 'property', 'building', 'landlord', 'tenant', 'lease', 'neighborhood'],
    'Technology/Gadgets': ['phone', 'laptop', 'computer', 'gadget', 'software', 'app', 'tech', 'keyboard', 'repair', 'gaming'],
    'Shopping/Commerce': ['buy', 'shop', 'sell', 'store', 'price', 'cost', 'product', 'clothes', 'shoes', 'online', 'market'],
    'Education/Career': ['job', 'internship', 'university', 'college', 'school', 'exam', 'study', 'course', 'learning', 'work', 'career'],
    'Travel/Transportation': ['flight', 'travel', 'trip', 'tour', 'hotel', 'transport', 'road', 'traffic', 'taxi', 'bus', 'metro'],
    'Sports/Recreation': ['sports', 'gym', 'fitness', 'football', 'cricket', 'badminton', 'swimming', 'climbing', 'game', 'exercise'],
    'Entertainment': ['movie', 'concert', 'music', 'entertainment', 'show', 'event', 'festival', 'comedy', 'film', 'anime'],
    'Relationships/Social': ['relationship', 'dating', 'marriage', 'wedding', 'love', 'couple', 'friend', 'family', 'social'],
    'Services/Professional': ['lawyer', 'accountant', 'tax', 'legal', 'repair', 'service', 'professional', 'consultant'],
    'General/Miscellaneous': ['question', 'help', 'advice', 'suggestion', 'recommend', 'need', 'looking', 'want']
}

def categorize_topics(text):
    """Categorize topics from text"""
    text_lower = str(text).lower()
    topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)
    
    if not topics:
        topics.append('General/Miscellaneous')
    
    return ', '.join(topics)

# Apply analysis
print("🔍 Analyzing sentiment...")
df['polarity'] = 0.0
df['subjectivity'] = 0.0
df['sentiment'] = ''
df['emotion'] = ''
df['topics'] = ''

for idx, row in df.iterrows():
    if idx % 50 == 0:
        print(f"   Processing... {idx}/{len(df)}")
    
    title = str(row['title'])
    polarity, subjectivity, sentiment = advanced_sentiment(title)
    emotion = detect_emotion(title)
    topics = categorize_topics(title)
    
    df.at[idx, 'polarity'] = polarity
    df.at[idx, 'subjectivity'] = subjectivity
    df.at[idx, 'sentiment'] = sentiment
    df.at[idx, 'emotion'] = emotion
    df.at[idx, 'topics'] = topics

print(f"✓ Analysis complete!")
print()

# ===== STATISTICS =====
print("=" * 100)
print("📊 SENTIMENT STATISTICS")
print("=" * 100)

sentiment_counts = df['sentiment'].value_counts()
print("\nSentiment Distribution:")
for sentiment, count in sentiment_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {sentiment.capitalize()}: {count} ({pct:.1f}%)")

print(f"\nAverage Polarity: {df['polarity'].mean():.3f}")
print(f"Average Subjectivity: {df['subjectivity'].mean():.3f}")

print()

# ===== EMOTION DISTRIBUTION =====
emotion_counts = df['emotion'].value_counts()
print("=" * 100)
print("😊 EMOTION DISTRIBUTION")
print("=" * 100)

for emotion, count in emotion_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {emotion.capitalize()}: {count} ({pct:.1f}%)")

print()

# ===== TOPIC ANALYSIS =====
print("=" * 100)
print("🏷️  TOP TOPICS DISCUSSED")
print("=" * 100)

all_topics = []
for topics_str in df['topics']:
    topics = [t.strip() for t in str(topics_str).split(',')]
    all_topics.extend(topics)

topic_counter = Counter(all_topics)
print()
for idx, (topic, count) in enumerate(topic_counter.most_common(15), 1):
    pct = (count / len(df)) * 100
    print(f"{idx}. {topic}: {count} posts ({pct:.1f}%)")

print()

# ===== TOPIC SENTIMENT ANALYSIS =====
print("=" * 100)
print("💬 SENTIMENT BY TOPIC")
print("=" * 100)

topic_sentiment = []
for topic in list(dict(topic_counter.most_common(10)).keys()):
    topic_df = df[df['topics'].str.contains(topic, na=False)]
    if len(topic_df) > 0:
        pos = (topic_df['sentiment'] == 'positive').sum()
        neg = (topic_df['sentiment'] == 'negative').sum()
        neu = (topic_df['sentiment'] == 'neutral').sum()
        avg_pol = topic_df['polarity'].mean()
        
        print(f"\n{topic}")
        print(f"  Posts: {len(topic_df)}")
        print(f"  Positive: {pos} ({pos/len(topic_df)*100:.0f}%)")
        print(f"  Negative: {neg} ({neg/len(topic_df)*100:.0f}%)")
        print(f"  Neutral: {neu} ({neu/len(topic_df)*100:.0f}%)")
        print(f"  Avg Polarity: {avg_pol:.3f}")
        print(f"  Vibe: {'😊 Happy' if avg_pol > 0.1 else '😐 Neutral' if avg_pol > -0.1 else '😞 Critical'}")

print()

# ===== TOP POSITIVE POSTS =====
print("=" * 100)
print("✨ TOP 10 MOST POSITIVE POSTS FROM DHAKA USERS")
print("=" * 100)

top_positive = df.nlargest(10, 'polarity')[['title', 'subreddit', 'polarity', 'emotion', 'upvotes']]
print()
for idx, (_, row) in enumerate(top_positive.iterrows(), 1):
    print(f"{idx}. [{row['subreddit']}] {row['title'][:70]}")
    print(f"   Polarity: {row['polarity']:.3f} | Emotion: {row['emotion']} | Upvotes: {row['upvotes']}")

print()

# ===== TOP NEGATIVE POSTS =====
print("=" * 100)
print("⚠️  TOP 10 MOST NEGATIVE POSTS FROM DHAKA USERS")
print("=" * 100)

top_negative = df.nsmallest(10, 'polarity')[['title', 'subreddit', 'polarity', 'emotion', 'upvotes']]
print()
for idx, (_, row) in enumerate(top_negative.iterrows(), 1):
    print(f"{idx}. [{row['subreddit']}] {row['title'][:70]}")
    print(f"   Polarity: {row['polarity']:.3f} | Emotion: {row['emotion']} | Upvotes: {row['upvotes']}")

print()

# ===== ENGAGEMENT BY SENTIMENT =====
print("=" * 100)
print("📈 ENGAGEMENT BY SENTIMENT")
print("=" * 100)

for sentiment in ['positive', 'negative', 'neutral']:
    sent_df = df[df['sentiment'] == sentiment]
    avg_upvotes = sent_df['upvotes'].mean()
    avg_comments = sent_df['comments'].mean()
    
    print(f"\n{sentiment.capitalize()}:")
    print(f"  Average Upvotes: {avg_upvotes:.1f}")
    print(f"  Average Comments: {avg_comments:.1f}")
    print(f"  Total Engagement: {sent_df['upvotes'].sum() + sent_df['comments'].sum()}")

print()

# ===== SAVE RESULTS =====
output_dir = "location_sentiment_analysis"
os.makedirs(output_dir, exist_ok=True)

# Full analysis
df.to_csv(f"{output_dir}/01_full_analysis.csv", index=False, encoding='utf-8')

# Most positive
df.nlargest(15, 'polarity')[['title', 'subreddit', 'polarity', 'emotion', 'topics', 'upvotes', 'comments']].to_csv(
    f"{output_dir}/02_most_positive_posts.csv", index=False, encoding='utf-8'
)

# Most negative
df.nsmallest(15, 'polarity')[['title', 'subreddit', 'polarity', 'emotion', 'topics', 'upvotes', 'comments']].to_csv(
    f"{output_dir}/03_most_negative_posts.csv", index=False, encoding='utf-8'
)

# Topic analysis
topic_analysis = []
for topic in list(dict(topic_counter.most_common(12)).keys()):
    topic_df = df[df['topics'].str.contains(topic, na=False)]
    if len(topic_df) > 0:
        topic_analysis.append({
            'topic': topic,
            'posts': len(topic_df),
            'positive': (topic_df['sentiment'] == 'positive').sum(),
            'negative': (topic_df['sentiment'] == 'negative').sum(),
            'neutral': (topic_df['sentiment'] == 'neutral').sum(),
            'avg_polarity': topic_df['polarity'].mean(),
            'avg_upvotes': topic_df['upvotes'].mean(),
            'total_upvotes': topic_df['upvotes'].sum()
        })

pd.DataFrame(topic_analysis).to_csv(f"{output_dir}/04_topic_sentiment_analysis.csv", index=False, encoding='utf-8')

# Subreddit comparison
subreddit_analysis = []
for subreddit in df['subreddit'].unique():
    sub_df = df[df['subreddit'] == subreddit]
    subreddit_analysis.append({
        'subreddit': subreddit,
        'posts': len(sub_df),
        'positive': (sub_df['sentiment'] == 'positive').sum(),
        'negative': (sub_df['sentiment'] == 'negative').sum(),
        'neutral': (sub_df['sentiment'] == 'neutral').sum(),
        'avg_polarity': sub_df['polarity'].mean(),
        'avg_upvotes': sub_df['upvotes'].mean()
    })

pd.DataFrame(subreddit_analysis).to_csv(f"{output_dir}/05_subreddit_comparison.csv", index=False, encoding='utf-8')

print("=" * 100)
print("✓ FILES SAVED")
print("=" * 100)
print(f"📁 Output Directory: {output_dir}/")
print(f"  • 01_full_analysis.csv - Complete data with all metrics")
print(f"  • 02_most_positive_posts.csv - Top 15 positive posts")
print(f"  • 03_most_negative_posts.csv - Top 15 negative posts")
print(f"  • 04_topic_sentiment_analysis.csv - Sentiment by topic")
print(f"  • 05_subreddit_comparison.csv - r/dhaka vs r/bangladesh")
print()

# Summary report
emotion_lines = "\n  ".join([f"• {emotion.capitalize()}: {count} ({count/len(df)*100:.1f}%)" for emotion, count in emotion_counts.items()])
topic_lines = "\n  ".join([f"• {topic}: {count} posts ({count/len(df)*100:.1f}%)" for topic, count in topic_counter.most_common(8)])

summary = f"""
SENTIMENT ANALYSIS SUMMARY - DHAKA LOCATION-BASED POSTS
{'=' * 80}

Dataset: {len(df)} posts from Dhaka-located Reddit users
Date: November 2025

OVERALL SENTIMENT:
  • Positive: {sentiment_counts.get('positive', 0)} ({sentiment_counts.get('positive', 0)/len(df)*100:.1f}%)
  • Neutral: {sentiment_counts.get('neutral', 0)} ({sentiment_counts.get('neutral', 0)/len(df)*100:.1f}%)
  • Negative: {sentiment_counts.get('negative', 0)} ({sentiment_counts.get('negative', 0)/len(df)*100:.1f}%)
  • Average Polarity: {df['polarity'].mean():.3f}
  • Average Subjectivity: {df['subjectivity'].mean():.3f}

TOP EMOTIONS:
  {emotion_lines}

TOP TOPICS:
  {topic_lines}

KEY INSIGHTS:
  • Most discussed: {topic_counter.most_common(1)[0][0]}
  • Most positive topic: {max([t for t in topic_analysis], key=lambda x: x['avg_polarity'])['topic']}
  • Most critical topic: {min([t for t in topic_analysis], key=lambda x: x['avg_polarity'])['topic']}
"""

with open(f"{output_dir}/00_summary.txt", "w", encoding='utf-8') as f:
    f.write(summary)

print(summary)
