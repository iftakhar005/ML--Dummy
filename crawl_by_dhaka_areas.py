import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

print("=" * 100)
print("ENHANCED DHAKA CRAWLER - ALL DIVISIONS, AREAS & COORDINATES")
print("=" * 100)
print()

# Define all Dhaka areas and keywords
dhaka_data = {
    'DNCC (Dhaka North City Corporation)': {
        'areas': ['Uttara', 'Mirpur', 'Pallabi', 'Shahjalal', 'Mohammadpur', 'Dhanmondi', 
                  'Shyamoli', 'Tejgaon', 'Turag', 'Banani', 'Gulshan', 'Badda', 'Khilgaon', 
                  'Shantinagar', 'Kallyanpur', 'Gabtoli', 'Agargaon'],
        'coordinates': [(23.8753, 90.3961), (23.8130, 90.3663), (23.8050, 90.3800)]  # Uttara, Mirpur, Pallabi
    },
    'DSCC (Dhaka South City Corporation)': {
        'areas': ['Old Dhaka', 'Puran Dhaka', 'Sadarghat', 'Lalbagh', 'Kotwali', 'Kamrangirchar',
                  'Motijheel', 'Ramna', 'Baridhara', 'Jatrabari', 'Paltan', 'Banasree', 
                  'Demra', 'Wari', 'Khilgaon'],
        'coordinates': [(23.7461, 90.3760), (23.7286, 90.4144), (23.8103, 90.4125)]  # Dhanmondi, Motijheel, Center
    },
    'Other Notable Areas': {
        'areas': ['Uttarkhan', 'Bashundhara', 'Mohakhali', 'Rampura', 'Khilkhet', 'Niketon',
                  'Kafrul', 'Shyamoli'],
        'coordinates': [(23.8103, 90.4125)]
    }
}

# All Dhaka location keywords for searching
all_dhaka_keywords = []
for division, data in dhaka_data.items():
    all_dhaka_keywords.extend(data['areas'])

print(f"📍 Dhaka Areas to Search: {len(all_dhaka_keywords)} locations")
print(f"   {', '.join(all_dhaka_keywords[:10])}...")
print()

def search_reddit_by_areas(subreddits, max_posts=1000):
    """Search Reddit for posts mentioning Dhaka areas"""
    
    all_posts = []
    posts_by_area = {}
    
    for subreddit in subreddits:
        print(f"🔍 Searching r/{subreddit}...")
        
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
                    title = str(post_data.get('title', '')).lower()
                    selftext = str(post_data.get('selftext', '')).lower()
                    full_text = title + " " + selftext
                    
                    # Find which areas are mentioned
                    mentioned_areas = []
                    for area in all_dhaka_keywords:
                        if area.lower() in full_text:
                            mentioned_areas.append(area)
                    
                    if mentioned_areas:
                        post_entry = {
                            'title': post_data.get('title', ''),
                            'author': author,
                            'subreddit': subreddit,
                            'upvotes': post_data.get('score', 0),
                            'comments': post_data.get('num_comments', 0),
                            'created': datetime.fromtimestamp(post_data.get('created_utc', 0)),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'areas_mentioned': ', '.join(mentioned_areas),
                            'area_count': len(mentioned_areas),
                            'content_preview': (post_data.get('selftext', '')[:150] or post_data.get('title', '')[:150])
                        }
                        
                        all_posts.append(post_entry)
                        
                        # Track by area
                        for area in mentioned_areas:
                            if area not in posts_by_area:
                                posts_by_area[area] = 0
                            posts_by_area[area] += 1
                        
                        collected += 1
                        
                        if len(mentioned_areas) > 1:
                            print(f"   ✓ [{', '.join(mentioned_areas)}] {post_data.get('title', '')[:60]}...")
                        else:
                            print(f"   ✓ [{mentioned_areas[0]}] {post_data.get('title', '')[:60]}...")
                    
                    if collected >= max_posts:
                        break
                
                after = data.get('data', {}).get('after')
                if not after:
                    break
                
                time.sleep(1)  # Rate limiting
        
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    return all_posts, posts_by_area

# Search for posts
subreddits = ['dhaka', 'bangladesh']
posts, area_stats = search_reddit_by_areas(subreddits, max_posts=500)

print()
print("=" * 100)
print("📊 RESULTS - POSTS BY DHAKA AREA")
print("=" * 100)

if posts:
    print(f"\n✓ Found {len(posts)} area-specific posts\n")
    
    # Show area distribution
    print("Posts mentioned by area:")
    for area, count in sorted(area_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {area}: {count} posts")
    
    # Create DataFrame
    df = pd.DataFrame(posts)
    
    # Save comprehensive data
    df.to_csv("dhaka_area_specific_posts.csv", index=False, encoding='utf-8')
    print(f"\n✓ Saved to: dhaka_area_specific_posts.csv")
    
    # Create area summary
    area_summary = []
    for area, count in sorted(area_stats.items(), key=lambda x: x[1], reverse=True):
        area_posts = df[df['areas_mentioned'].str.contains(area, na=False)]
        avg_upvotes = area_posts['upvotes'].mean()
        avg_comments = area_posts['comments'].mean()
        
        area_summary.append({
            'area': area,
            'posts': count,
            'avg_upvotes': avg_upvotes,
            'avg_comments': avg_comments,
            'total_engagement': area_posts['upvotes'].sum() + area_posts['comments'].sum()
        })
    
    area_summary_df = pd.DataFrame(area_summary)
    area_summary_df.to_csv("dhaka_areas_summary.csv", index=False, encoding='utf-8')
    print(f"✓ Saved to: dhaka_areas_summary.csv")
    
    print()
    print("=" * 100)
    print("🏘️  TOP AREAS DISCUSSED ON REDDIT (by engagement)")
    print("=" * 100)
    print()
    for idx, row in area_summary_df.head(15).iterrows():
        print(f"{idx+1}. {row['area']}")
        print(f"   Posts: {row['posts']} | Avg Upvotes: {row['avg_upvotes']:.1f} | Total Engagement: {row['total_engagement']:.0f}")
    
    # Show most discussed post from each top area
    print()
    print("=" * 100)
    print("🔝 TOP POST FROM EACH MAJOR AREA")
    print("=" * 100)
    print()
    
    for area in area_summary_df.head(8)['area'].values:
        area_posts = df[df['areas_mentioned'].str.contains(area, na=False)]
        top_post = area_posts.nlargest(1, 'upvotes').iloc[0]
        
        print(f"\n📍 {area}")
        print(f"   Post: {top_post['title'][:80]}")
        print(f"   Upvotes: {top_post['upvotes']} | Comments: {top_post['comments']}")
        print(f"   Author: {top_post['author']}")
    
    print()
    print("=" * 100)
    print("📈 STATISTICS")
    print("=" * 100)
    print(f"""
Total Posts Found: {len(df)}
Date Range: Last 3 months

Area Coverage:
  • Unique areas mentioned: {len(area_stats)}
  • Most discussed: {area_summary_df.iloc[0]['area']} ({area_summary_df.iloc[0]['posts']} posts)
  • Highest engagement: {area_summary_df.nlargest(1, 'total_engagement').iloc[0]['area']}

Overall Engagement:
  • Avg Upvotes per Post: {df['upvotes'].mean():.1f}
  • Avg Comments per Post: {df['comments'].mean():.1f}
  • Total Engagement: {(df['upvotes'].sum() + df['comments'].sum()):.0f}

City Corporation Distribution:
  • DNCC areas: {sum([count for area, count in area_stats.items() if area in dhaka_data['DNCC (Dhaka North City Corporation)']['areas']])} posts
  • DSCC areas: {sum([count for area, count in area_stats.items() if area in dhaka_data['DSCC (Dhaka South City Corporation)']['areas']])} posts
  • Other areas: {sum([count for area, count in area_stats.items() if area in dhaka_data['Other Notable Areas']['areas']])} posts
""")
    
else:
    print("\n⚠️  No area-specific posts found with direct mentions.")
    print("\nTrying alternative approach: searching with coordinate hints...")

print()
