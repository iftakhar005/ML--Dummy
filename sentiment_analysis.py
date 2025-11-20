import pandas as pd
import numpy as np
from textblob import TextBlob
from collections import Counter
import re
import os

# Read the CSV file
csv_file = "dhaka_posts_20251119_224551.csv"
df = pd.read_csv(csv_file)

print("=" * 100)
print("SENTIMENT ANALYSIS & TOPIC EXTRACTION")
print("=" * 100)
print()

# ===== SENTIMENT ANALYSIS =====
print("🔍 PERFORMING SENTIMENT ANALYSIS...")
print("-" * 100)

def get_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    if pd.isna(text) or text == "":
        return 0, "neutral"
    try:
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return polarity, "positive"
        elif polarity < -0.1:
            return polarity, "negative"
        else:
            return polarity, "neutral"
    except:
        return 0, "neutral"

# Apply sentiment analysis to title and body
print("Analyzing sentiments...")
df[['title_polarity', 'title_sentiment']] = df['title'].apply(lambda x: pd.Series(get_sentiment(x)))
df[['body_polarity', 'body_sentiment']] = df['body'].apply(lambda x: pd.Series(get_sentiment(x)))

# Combined sentiment (average of title and body)
df['combined_polarity'] = (df['title_polarity'] + df['body_polarity']) / 2
df['combined_sentiment'] = df[['title_sentiment', 'body_sentiment']].apply(
    lambda x: x[0] if abs(get_sentiment(df['title'].iloc[0])[0]) > abs(get_sentiment(df['body'].iloc[0])[0]) else x[1], 
    axis=1
)

# ===== SENTIMENT STATISTICS =====
print("\n✅ SENTIMENT ANALYSIS COMPLETE\n")
print("📊 OVERALL SENTIMENT DISTRIBUTION")
print("-" * 100)

sentiment_counts = df['combined_sentiment'].value_counts()
print(f"Positive Posts: {sentiment_counts.get('positive', 0)} ({sentiment_counts.get('positive', 0)/len(df)*100:.1f}%)")
print(f"Negative Posts: {sentiment_counts.get('negative', 0)} ({sentiment_counts.get('negative', 0)/len(df)*100:.1f}%)")
print(f"Neutral Posts: {sentiment_counts.get('neutral', 0)} ({sentiment_counts.get('neutral', 0)/len(df)*100:.1f}%)")

print(f"\nAverage Sentiment Polarity: {df['combined_polarity'].mean():.3f}")
print(f"Sentiment Polarity Range: {df['combined_polarity'].min():.3f} to {df['combined_polarity'].max():.3f}")

print()

# ===== TOPIC EXTRACTION =====
print("🏷️  TOPIC EXTRACTION (KEYWORDS)")
print("-" * 100)

# Common words to exclude
stopwords = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'was',
    'are', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'some', 'any', 'no',
    'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just', 'am', 'as', 'if',
    'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'him', 'his', 'himself', 'her', 'hers', 'herself', 'its',
    'itself', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'having', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'ought', 'i',
    'you', 'he', 'she', 'it', 'we', 'they', 'them', 'there', 'here', 'need', 'help',
    'please', 'thanks', 'thank', 'want', 'like', 'give', 'get', 'make', 'take', 'go',
    'come', 'know', 'see', 'find', 'use', 'think', 'say', 'tell', 'ask', 'give', 'work',
    'call', 'try', 'ask', 'need', 'feel', 'seem', 'look', 'watch', 'follow', 'play',
    'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch',
    'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow',
    'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy',
    'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach',
    'kill', 'remain', 'suggest', 'raise', 'pass', 'sell', 'require', 'report', 'decide',
    'pull', 'explain', 'develop', 'carry', 'break', 'receive', 'agree', 'support',
    'hit', 'produce', 'eat', 'cover', 'catch', 'draw', 'choose', 'cause', 'follow',
    'begin', 'drink', 'hold', 'write', 'provide', 'pay', 'meet', 'include', 'continue',
    'should', 'would', 'could', 'may', 'might', 'must', 'can', 'will', 'shall', 'want',
    'wish', 'trying', 'anyone', 'someone', 'everybody', 'nobody', 'everything', 'nothing',
    'know', 'going', 'trying', 'making', 'bd', 'bangladesh', 'dhaka', 'pm', 're'
}

# Extract keywords from titles and body
all_words = []

for title in df['title'].dropna():
    words = re.findall(r'\b[a-z]+\b', str(title).lower())
    all_words.extend([w for w in words if w not in stopwords and len(w) > 2])

for body in df['body'].dropna():
    words = re.findall(r'\b[a-z]+\b', str(body).lower())
    all_words.extend([w for w in words if w not in stopwords and len(w) > 2])

# Get top keywords
top_keywords = Counter(all_words).most_common(30)

print("\n🔤 TOP 30 KEYWORDS:")
print("-" * 100)
for idx, (keyword, count) in enumerate(top_keywords, 1):
    print(f"{idx:2d}. {keyword:15s} - {count:4d} mentions")

print()

# ===== TOPIC CATEGORIZATION =====
print("📌 TOPIC CATEGORIZATION")
print("-" * 100)

# Define topic keywords
topics = {
    'Education': ['study', 'university', 'student', 'school', 'course', 'exam', 'hsc', 'ssc', 'college', 'admission', 'engineering', 'degree'],
    'Career/Jobs': ['job', 'work', 'career', 'employment', 'hired', 'interview', 'company', 'business', 'freelance', 'hire', 'salary'],
    'Relationships': ['relationship', 'marriage', 'wife', 'husband', 'girlfriend', 'boyfriend', 'love', 'couple', 'wedding', 'dating'],
    'Health/Medical': ['doctor', 'hospital', 'health', 'medical', 'medicine', 'disease', 'treatment', 'surgery', 'mental', 'therapy', 'mental health'],
    'Travel/Tourism': ['travel', 'visit', 'trip', 'tour', 'airport', 'flight', 'tourist', 'explore', 'destination'],
    'Shopping/Commerce': ['buy', 'sell', 'shop', 'price', 'market', 'store', 'product', 'order', 'delivery', 'ecommerce'],
    'Food/Restaurants': ['restaurant', 'food', 'eat', 'cafe', 'coffee', 'meal', 'dish', 'cooking', 'kitchen', 'buffet'],
    'Politics/Government': ['election', 'government', 'political', 'minister', 'politics', 'parliament', 'vote', 'law', 'police', 'court', 'bnp', 'awami'],
    'Sports': ['football', 'cricket', 'sports', 'match', 'player', 'team', 'game', 'league', 'basketball'],
    'Technology': ['phone', 'laptop', 'computer', 'software', 'app', 'internet', 'coding', 'programming', 'tech', 'ai', 'gaming'],
    'Real Estate': ['apartment', 'flat', 'house', 'rent', 'property', 'home', 'building', 'land', 'dhaka'],
    'Infrastructure': ['metro', 'road', 'traffic', 'transport', 'bus', 'train', 'railway', 'bridge', 'construction'],
}

# Categorize posts
def categorize_post(title, body):
    text = (str(title) + " " + str(body)).lower()
    matched_topics = []
    
    for topic, keywords in topics.items():
        if any(keyword in text for keyword in keywords):
            matched_topics.append(topic)
    
    return matched_topics if matched_topics else ['Other']

df['topics'] = df.apply(lambda x: categorize_post(x['title'], x['body']), axis=1)

# Count topics
topic_counts = Counter()
for topics_list in df['topics']:
    for topic in topics_list:
        topic_counts[topic] += 1

print("\nPosts by Topic:")
print("-" * 100)
for idx, (topic, count) in enumerate(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True), 1):
    percentage = (count / len(df)) * 100
    print(f"{idx:2d}. {topic:20s} - {count:3d} posts ({percentage:5.1f}%)")

print()

# ===== SENTIMENT BY TOPIC =====
print("💭 SENTIMENT BY TOPIC")
print("-" * 100)

# Expand dataframe to have one row per topic
topic_sentiment_data = []
for idx, row in df.iterrows():
    for topic in row['topics']:
        topic_sentiment_data.append({
            'topic': topic,
            'sentiment': row['combined_sentiment'],
            'polarity': row['combined_polarity'],
            'upvotes': row['upvotes'],
            'comments': row['comments']
        })

topic_df = pd.DataFrame(topic_sentiment_data)

for topic in sorted(topic_counts.keys()):
    topic_data = topic_df[topic_df['topic'] == topic]
    if len(topic_data) > 0:
        positive_pct = (topic_data['sentiment'] == 'positive').sum() / len(topic_data) * 100
        negative_pct = (topic_data['sentiment'] == 'negative').sum() / len(topic_data) * 100
        neutral_pct = (topic_data['sentiment'] == 'neutral').sum() / len(topic_data) * 100
        avg_polarity = topic_data['polarity'].mean()
        avg_upvotes = topic_data['upvotes'].mean()
        
        print(f"\n{topic} ({len(topic_data)} posts)")
        print(f"  Sentiment: Positive {positive_pct:.1f}% | Negative {negative_pct:.1f}% | Neutral {neutral_pct:.1f}%")
        print(f"  Avg Polarity: {avg_polarity:.3f} | Avg Engagement: {avg_upvotes:.1f} upvotes")

print()
print("=" * 100)

# ===== SAVE RESULTS =====
print("\n✅ SAVING ANALYSIS RESULTS...")
print("-" * 100)

output_dir = "sentiment_analysis"
os.makedirs(output_dir, exist_ok=True)

# 1. Sentiment summary
sentiment_summary = pd.DataFrame({
    'Sentiment': ['Positive', 'Negative', 'Neutral', 'Total'],
    'Count': [
        (df['combined_sentiment'] == 'positive').sum(),
        (df['combined_sentiment'] == 'negative').sum(),
        (df['combined_sentiment'] == 'neutral').sum(),
        len(df)
    ],
    'Percentage': [
        f"{(df['combined_sentiment'] == 'positive').sum() / len(df) * 100:.1f}%",
        f"{(df['combined_sentiment'] == 'negative').sum() / len(df) * 100:.1f}%",
        f"{(df['combined_sentiment'] == 'neutral').sum() / len(df) * 100:.1f}%",
        "100%"
    ]
})
sentiment_summary.to_csv(f"{output_dir}/01_sentiment_summary.csv", index=False)
print(f"✓ Created: {output_dir}/01_sentiment_summary.csv")

# 2. Topic distribution
topic_dist = pd.DataFrame(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True), 
                           columns=['Topic', 'Count'])
topic_dist['Percentage'] = (topic_dist['Count'] / len(df) * 100).round(1)
topic_dist.to_csv(f"{output_dir}/02_topic_distribution.csv", index=False)
print(f"✓ Created: {output_dir}/02_topic_distribution.csv")

# 3. Detailed posts with sentiment
df_output = df[['title', 'author', 'upvotes', 'comments', 'combined_sentiment', 'combined_polarity', 'subreddit', 'date']]
df_output['topics'] = df['topics'].apply(lambda x: ', '.join(x))
df_output.to_csv(f"{output_dir}/03_posts_with_sentiment.csv", index=False)
print(f"✓ Created: {output_dir}/03_posts_with_sentiment.csv")

# 4. Top positive posts
top_positive = df[df['combined_sentiment'] == 'positive'].nlargest(20, 'upvotes')[
    ['title', 'author', 'upvotes', 'combined_polarity', 'topics']
].copy()
top_positive['topics'] = top_positive['topics'].apply(lambda x: ', '.join(x))
top_positive.to_csv(f"{output_dir}/04_top_positive_posts.csv", index=False)
print(f"✓ Created: {output_dir}/04_top_positive_posts.csv")

# 5. Top negative posts
top_negative = df[df['combined_sentiment'] == 'negative'].nlargest(20, 'upvotes')[
    ['title', 'author', 'upvotes', 'combined_polarity', 'topics']
].copy()
top_negative['topics'] = top_negative['topics'].apply(lambda x: ', '.join(x))
top_negative.to_csv(f"{output_dir}/05_top_negative_posts.csv", index=False)
print(f"✓ Created: {output_dir}/05_top_negative_posts.csv")

# 6. Keywords analysis
keywords_df = pd.DataFrame(top_keywords, columns=['Keyword', 'Frequency'])
keywords_df.to_csv(f"{output_dir}/06_top_keywords.csv", index=False)
print(f"✓ Created: {output_dir}/06_top_keywords.csv")

print("\n" + "=" * 100)
print(f"✨ All sentiment analysis results saved to: {output_dir}/")
print("=" * 100)
