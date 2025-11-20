import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# ------------------------------
# Configuration
# ------------------------------
query = "Dhaka"                                    # Keyword to search
subreddits = ["bangladesh", "dhaka"]               # Multiple subreddits
max_posts_total = 2000                             # Total posts to collect
max_posts_per_subreddit = 500                      # Posts per subreddit
date_range_days = 365                              # Search last N days (None for all time)

# Set up headers for Reddit API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ------------------------------
# Collect Posts
# ------------------------------
all_posts = []
posts_collected = 0

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days=date_range_days) if date_range_days else datetime(2005, 1, 1)

print(f"Searching for '{query}' in subreddits: {', '.join(subreddits)}")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Target: {max_posts_total} posts total\n")

for subreddit in subreddits:
    if posts_collected >= max_posts_total:
        break
    
    print(f"Scraping r/{subreddit}...")
    after = None
    subreddit_posts = 0
    
    while subreddit_posts < max_posts_per_subreddit and posts_collected < max_posts_total:
        # Construct URL for Reddit search
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'new',
            'limit': '100'
        }
        
        if after:
            params['after'] = after
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            children = data.get('data', {}).get('children', [])
            
            if not children:
                print(f"  No more posts found in r/{subreddit}")
                break
            
            for post_data in children:
                if subreddit_posts >= max_posts_per_subreddit or posts_collected >= max_posts_total:
                    break
                
                post = post_data.get('data', {})
                post_timestamp = post.get('created_utc', 0)
                post_date = datetime.fromtimestamp(post_timestamp)
                
                # Filter by date range
                if post_date < start_date or post_date > end_date:
                    continue
                
                all_posts.append([
                    post.get('title', ''),
                    post.get('selftext', ''),
                    post.get('url', ''),
                    post.get('author', '[deleted]'),
                    post.get('score', 0),
                    post.get('num_comments', 0),
                    post_date,
                    subreddit  # Track which subreddit the post came from
                ])
                subreddit_posts += 1
                posts_collected += 1
            
            # Get the 'after' token for pagination
            after = data.get('data', {}).get('after')
            if not after:
                print(f"  Reached end of r/{subreddit} (collected {subreddit_posts} posts)")
                break
            
            # Add delay to avoid rate limiting
            time.sleep(1)
                
        except Exception as e:
            print(f"  Error fetching posts from r/{subreddit}: {e}")
            break
    
    print(f"  Collected {subreddit_posts} posts from r/{subreddit} (total: {posts_collected})\n")

# ------------------------------
# Save to CSV
# ------------------------------
df = pd.DataFrame(all_posts, columns=[
    "title", "body", "url", "author", "upvotes", "comments", "date", "subreddit"
])

# Optional: convert date to readable format
df["date"] = df["date"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))

filename = f"dhaka_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"Saved {len(df)} posts to {filename}")
