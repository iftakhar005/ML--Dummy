import requests
import pandas as pd
import praw
from datetime import datetime, timedelta
import time
import json

print("=" * 100)
print("COLLECTING POSTS FROM USERS LOCATED IN DHAKA")
print("=" * 100)
print()

# Reddit API credentials (using praw for user location info)
# Note: You may need to provide your own credentials for better results
# For now, we'll try to extract user location from their profile comments

def get_user_location(username):
    """Try to extract location from user profile"""
    try:
        url = f"https://www.reddit.com/user/{username}/about/.json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {})
    except:
        pass
    return None

def search_reddit_by_location(location_keywords, subreddits, max_posts=500):
    """Search posts and filter by user location"""
    
    all_posts = []
    
    for subreddit in subreddits:
        print(f"\n🔍 Searching r/{subreddit}...")
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new/.json"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            params = {
                'limit': 100,
                'sort': 'new'
            }
            
            after = None
            collected = 0
            
            while collected < max_posts:
                if after:
                    params['after'] = after
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    print(f"   Error: Status {response.status_code}")
                    break
                
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                if not posts:
                    print(f"   No more posts found")
                    break
                
                for post in posts:
                    post_data = post.get('data', {})
                    author = post_data.get('author')
                    
                    if author and author != '[deleted]':
                        # Try to get user location
                        # Note: Reddit API doesn't expose location directly in posts
                        # We would need to use PRAW with OAuth for full profile access
                        
                        # Alternative: Look for location mentions in post title/content
                        title = str(post_data.get('title', '')).lower()
                        selftext = str(post_data.get('selftext', '')).lower()
                        
                        full_text = title + " " + selftext
                        
                        # Check for Dhaka location keywords
                        dhaka_keywords = [
                            'dhaka', 'gulshan', 'banani', 'dhanmondi', 'mirpur',
                            'baridhara', 'uttara', 'motijheel', 'kawran bazar',
                            'badda', 'bashundhara', 'pallabi', 'mohakhali',
                            'i am in dhaka', 'live in dhaka', 'based in dhaka',
                            'located in dhaka', 'from dhaka'
                        ]
                        
                        has_location = any(keyword in full_text for keyword in dhaka_keywords)
                        
                        if has_location:
                            all_posts.append({
                                'title': post_data.get('title', ''),
                                'author': author,
                                'subreddit': subreddit,
                                'upvotes': post_data.get('score', 0),
                                'comments': post_data.get('num_comments', 0),
                                'created': datetime.fromtimestamp(post_data.get('created_utc', 0)),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'content_preview': (post_data.get('selftext', '')[:200] or post_data.get('title', '')[:200]),
                                'location_indicator': 'Location mentioned in post'
                            })
                            
                            print(f"   ✓ Found: {post_data.get('title', '')[:60]}...")
                            collected += 1
                    
                    if collected >= max_posts:
                        break
                
                after = data.get('data', {}).get('after')
                if not after:
                    break
                
                time.sleep(1)  # Rate limiting
        
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    return all_posts

print("Note: This will search for posts that MENTION location as 'Dhaka'")
print("to find users located in Dhaka.")
print()
print("Better alternative: Using Reddit API with OAuth would give us:")
print("  • Direct access to user profile location data")
print("  • More accurate user filtering")
print("  • Historical post data")
print()

# Search for posts
subreddits = ['dhaka', 'bangladesh']
posts = search_reddit_by_location(['dhaka', 'gulshan'], subreddits, max_posts=300)

print(f"\n\n✓ Found {len(posts)} posts from users mentioning Dhaka location")

if posts:
    # Create DataFrame
    df = pd.DataFrame(posts)
    
    # Save to CSV
    filename = f"location_based_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"\n✓ Saved to: {filename}")
    print()
    print("Sample posts:")
    print(df[['title', 'author', 'subreddit', 'created']].head(10).to_string())
else:
    print("\nNo posts found with explicit location mentions.")
    print()
    print("=" * 100)
    print("🔴 LIMITATION ENCOUNTERED")
    print("=" * 100)
    print("""
Reddit API Limitations:
1. Public API doesn't expose user "location" field directly
2. To get user locations, we need:
   • PRAW with OAuth (requires Reddit app registration)
   • User must have location set in profile (many don't)
   
Alternative Solutions:
✓ Option 1: Use PRAW with OAuth credentials
  - Register Reddit app at: https://www.reddit.com/prefs/apps
  - Get client_id, client_secret, user_agent
  - Can then access user profiles and their locations
  
✓ Option 2: Manual keyword-based approach (what we just tried)
  - Search for posts mentioning "I'm in Dhaka", "based in Dhaka", etc.
  - Less accurate but doesn't need API credentials
  
✓ Option 3: Filter by user comments/posts that mention location
  - Parse comments for location mentions
  - Build a database of Dhaka-located users
  - Collect their recent posts

🎯 RECOMMENDATION:
Would you like to:
1. Set up PRAW OAuth credentials for direct location access? (Requires Reddit app setup)
2. Use advanced keyword-based filtering to find location-related posts? 
3. Go back to content-based analysis (posts about Dhaka topics)?
""")

print()
