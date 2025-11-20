import pandas as pd
import os
from datetime import datetime

# Read the CSV file
csv_file = "dhaka_posts_20251119_224551.csv"
df = pd.read_csv(csv_file)

print("=" * 100)
print("REDDIT POSTS DATA - FORMATTED SUMMARY")
print("=" * 100)
print()

# 1. BASIC STATISTICS
print("📊 BASIC STATISTICS")
print("-" * 100)
print(f"Total Posts: {len(df)}")
print(f"Subreddits: {', '.join(df['subreddit'].unique())}")
print(f"Posts per Subreddit:")
for sub in df['subreddit'].unique():
    count = len(df[df['subreddit'] == sub])
    print(f"  • r/{sub}: {count} posts")
print(f"\nDate Range: {df['date'].min()} to {df['date'].max()}")
print()

# 2. ENGAGEMENT METRICS
print("📈 ENGAGEMENT METRICS")
print("-" * 100)
print(f"Average Upvotes: {df['upvotes'].mean():.2f}")
print(f"Average Comments: {df['comments'].mean():.2f}")
print(f"Total Upvotes: {df['upvotes'].sum():,}")
print(f"Total Comments: {df['comments'].sum():,}")
print()

# 3. TOP POSTS BY UPVOTES
print("🏆 TOP 10 POSTS BY UPVOTES")
print("-" * 100)
top_posts = df.nlargest(10, 'upvotes')[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date']]
for idx, (i, row) in enumerate(top_posts.iterrows(), 1):
    print(f"\n{idx}. {row['title'][:80]}...")
    print(f"   Author: {row['author']} | Upvotes: {row['upvotes']} | Comments: {row['comments']} | r/{row['subreddit']}")
    print(f"   Date: {row['date']}")

print()

# 4. TOP POSTS BY COMMENTS
print("💬 TOP 10 POSTS BY COMMENTS")
print("-" * 100)
top_comments = df.nlargest(10, 'comments')[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date']]
for idx, (i, row) in enumerate(top_comments.iterrows(), 1):
    print(f"\n{idx}. {row['title'][:80]}...")
    print(f"   Author: {row['author']} | Upvotes: {row['upvotes']} | Comments: {row['comments']} | r/{row['subreddit']}")
    print(f"   Date: {row['date']}")

print()

# 5. DETAILED TABLE FORMAT
print("📋 DETAILED POST LIST")
print("-" * 100)
display_df = df[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date']].copy()
display_df['title'] = display_df['title'].str[:60]  # Truncate long titles

print(display_df.to_string(index=False))

print()
print("=" * 100)

# 6. CREATE FORMATTED CSV FILES
print("\n✅ CREATING FORMATTED OUTPUT FILES...")
print("-" * 100)

# Create a summary sheet
output_dir = "formatted_output"
os.makedirs(output_dir, exist_ok=True)

# File 1: Summary statistics
summary_df = pd.DataFrame({
    'Metric': ['Total Posts', 'Total Upvotes', 'Total Comments', 'Avg Upvotes', 'Avg Comments', 'Date Range'],
    'Value': [
        len(df),
        df['upvotes'].sum(),
        df['comments'].sum(),
        f"{df['upvotes'].mean():.2f}",
        f"{df['comments'].mean():.2f}",
        f"{df['date'].min()} to {df['date'].max()}"
    ]
})
summary_df.to_csv(f"{output_dir}/01_summary.csv", index=False)
print(f"✓ Created: {output_dir}/01_summary.csv")

# File 2: Top posts by upvotes
df.nlargest(50, 'upvotes')[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date', 'url']].to_csv(
    f"{output_dir}/02_top_by_upvotes.csv", index=False
)
print(f"✓ Created: {output_dir}/02_top_by_upvotes.csv")

# File 3: Top posts by comments
df.nlargest(50, 'comments')[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date', 'url']].to_csv(
    f"{output_dir}/03_top_by_comments.csv", index=False
)
print(f"✓ Created: {output_dir}/03_top_by_comments.csv")

# File 4: Posts organized by subreddit
for subreddit in df['subreddit'].unique():
    sub_df = df[df['subreddit'] == subreddit].sort_values('upvotes', ascending=False)
    sub_df[['title', 'author', 'upvotes', 'comments', 'date', 'url']].to_csv(
        f"{output_dir}/04_posts_{subreddit}.csv", index=False
    )
    print(f"✓ Created: {output_dir}/04_posts_{subreddit}.csv")

# File 5: Sorted by date (newest first)
df.sort_values('date', ascending=False)[['title', 'author', 'upvotes', 'comments', 'subreddit', 'date', 'url']].to_csv(
    f"{output_dir}/05_posts_by_date.csv", index=False
)
print(f"✓ Created: {output_dir}/05_posts_by_date.csv")

# File 6: Full detailed data
df.to_csv(f"{output_dir}/06_full_data.csv", index=False)
print(f"✓ Created: {output_dir}/06_full_data.csv")

print("\n" + "=" * 100)
print(f"✨ All formatted files saved to: {output_dir}/")
print("=" * 100)
