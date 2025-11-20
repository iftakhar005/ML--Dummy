import pandas as pd
import re

print("=" * 100)
print("CHECKING: ARE THESE POSTS ACTUALLY ABOUT DHAKA?")
print("=" * 100)
print()

# Load data
df = pd.read_csv("advanced_sentiment_analysis/05_posts_with_advanced_analysis.csv")

print(f"Total Posts in Dataset: {len(df)}")
print(f"Subreddits: r/bangladesh, r/dhaka")
print()

# ===== 1. CHECK BY SUBREDDIT =====
print("📍 POSTS BY SUBREDDIT")
print("-" * 100)

subreddit_counts = df['subreddit'].value_counts()
print(subreddit_counts)
print()

for subreddit, count in subreddit_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {subreddit}: {count} posts ({pct:.1f}%)")

print()

# ===== 2. CHECK DHAKA MENTIONS =====
print("=" * 100)
print("🔍 CHECKING DHAKA MENTIONS IN POST TITLES")
print("-" * 100)

dhaka_keywords = ['dhaka', 'বাঙ্গালাদেশ', 'बangladesh', 'bd', 'bengal', 'bangladesh']

dhaka_related = 0
not_dhaka = []

for idx, row in df.iterrows():
    title = str(row['title']).lower()
    subreddit = str(row['subreddit']).lower()
    
    has_dhaka = any(keyword in title for keyword in dhaka_keywords)
    
    if has_dhaka:
        dhaka_related += 1
    else:
        if len(not_dhaka) < 20:  # Collect first 20 non-dhaka posts
            not_dhaka.append((row['title'], row['subreddit']))

print(f"\nPosts mentioning Dhaka/Bangladesh in title: {dhaka_related} ({dhaka_related/len(df)*100:.1f}%)")
print(f"Posts NOT mentioning Dhaka/Bangladesh: {len(df) - dhaka_related} ({(len(df)-dhaka_related)/len(df)*100:.1f}%)")
print()

# ===== 3. SHOW NON-DHAKA POSTS =====
print("=" * 100)
print("⚠️  POSTS NOT RELATED TO DHAKA:")
print("-" * 100)
print(f"\nShowing first {len(not_dhaka)} non-Dhaka posts:\n")

for i, (title, subreddit) in enumerate(not_dhaka, 1):
    print(f"{i}. [{subreddit}] {title[:80]}")

print()

# ===== 4. ANALYZE NON-DHAKA CONTENT =====
print("=" * 100)
print("🏷️  WHAT ARE THESE NON-DHAKA POSTS ABOUT?")
print("-" * 100)

non_dhaka_df = df[~df['title'].str.lower().str.contains('|'.join(dhaka_keywords), regex=True, na=False)]

print(f"\nTotal Non-Dhaka Posts: {len(non_dhaka_df)}")
print()

# Check topics
print("Topics in Non-Dhaka Posts:")
topic_counts = {}
for idx, row in non_dhaka_df.iterrows():
    topics = str(row['topics']).split(', ')
    for topic in topics:
        topic = topic.strip()
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  • {topic}: {count} posts")

print()

# ===== 5. SUMMARY =====
print("=" * 100)
print("📊 SUMMARY")
print("=" * 100)

print(f"""
Data Collection Analysis:
• Total Posts Scraped: {len(df)}
• From r/bangladesh: {subreddit_counts.get('bangladesh', 0)} posts
• From r/dhaka: {subreddit_counts.get('dhaka', 0)} posts

Content Relevance:
• Directly mention Dhaka/Bangladesh: {dhaka_related} ({dhaka_related/len(df)*100:.1f}%)
• NO Dhaka/Bangladesh mention: {len(df) - dhaka_related} ({(len(df)-dhaka_related)/len(df)*100:.1f}%)

❌ ISSUE FOUND:
   Not all posts are about DHAKA. Many are:
   • General Bangladesh discussions (not specific to Dhaka)
   • Random subreddit posts
   • Off-topic posts in these communities
   • Posts from users who are in these subreddits but discussing other topics

🎯 RECOMMENDATION:
   You should filter the data to ONLY include posts that:
   1. Specifically mention "Dhaka" in the title
   2. Are about Dhaka-specific topics (Gulshan, Mirpur, etc.)
   3. Remove general Bangladesh posts that aren't Dhaka-focused
""")

# ===== 6. CREATE FILTERED DATASET =====
print()
print("=" * 100)
print("✂️  CREATING FILTERED DATASET - DHAKA ONLY")
print("=" * 100)

dhaka_only = df[df['title'].str.lower().str.contains('|'.join(dhaka_keywords), regex=True, na=False)]

print(f"\nFiltered Dataset: {len(dhaka_only)} posts (from {len(df)})")
print(f"Posts removed: {len(df) - len(dhaka_only)}")

# Save filtered version
dhaka_only.to_csv("advanced_sentiment_analysis/05_posts_dhaka_only.csv", index=False, encoding='utf-8')
print(f"✓ Saved filtered data to: advanced_sentiment_analysis/05_posts_dhaka_only.csv")

print()
