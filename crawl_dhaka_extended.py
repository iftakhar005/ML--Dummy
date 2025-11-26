import requests
import json
import time
from datetime import datetime

def generate_dhaka_query():
    # 1. Define your keyword groups
    # Note: We include "Dhaka" itself, plus all the specific locations
    neighborhoods = [
        "Dhaka", "Gulshan", "Banani", "Dhanmondi", "Mirpur", "Uttara", 
        "Motijheel", "Farmgate", "Mohammadpur", "Badda", "Rampura", 
        "Khilgaon", "Bashundhara", "Tejgaon", "Shahbag", "Lalmatia", 
        "Malibagh", "Moghbazar", "Jatrabari", "Puran Dhaka", "Old Dhaka",
        "Keraniganj", "Savar"
    ]
    
    universities = [
        "BUET", "DU", "Dhaka University", "NSU", "North South University", 
        "BRACU", "BRAC University", "AUST", "IUB", "AIUB", "EWU", "JNU"
    ]
    
    landmarks = [
        "Hatirjheel", "Jamuna Future Park", "Bashundhara City", 
        "New Market", "Sangsad Bhaban", "TSC", "Ahsan Manzil", "Lalbagh Fort"
    ]

    # Combine all lists
    all_keywords = neighborhoods + universities + landmarks
    
    # Split into chunks to avoid query length limits
    chunk_size = 10
    keyword_chunks = [all_keywords[i:i + chunk_size] for i in range(0, len(all_keywords), chunk_size)]
    
    queries = []
    for chunk in keyword_chunks:
        query_parts = [f'"{term}"' for term in chunk]
        full_query_string = " OR ".join(query_parts)
        queries.append(f"({full_query_string})")
        
    return queries

def crawl_reddit_extended(max_posts=2000):
    queries = generate_dhaka_query()
    print(f"Generated {len(queries)} sub-queries to cover all keywords.")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    subreddits = ["bangladesh", "dhaka"]
    all_posts = {} # Use dict for deduplication by URL
    
    for query_string in queries:
        print(f"\n--- Processing Query Chunk: {query_string[:50]}... ---")
        
        for sub in subreddits:
            print(f"  Searching r/{sub}...")
            url = f"https://www.reddit.com/r/{sub}/search.json"
            after = None
            chunk_posts_count = 0
            
            while chunk_posts_count < 200: # Limit per chunk per sub to avoid excessive requests
                params = {
                    'q': query_string,
                    'sort': 'new',
                    'limit': 100,
                    'restrict_sr': 'on',
                    't': 'all'
                }
                if after:
                    params['after'] = after
                    
                try:
                    response = requests.get(url, headers=headers, params=params)
                    
                    if response.status_code != 200:
                        print(f"    Error: {response.status_code}")
                        break
                        
                    data = response.json()
                    children = data.get('data', {}).get('children', [])
                    
                    if not children:
                        break
                        
                    for child in children:
                        post = child['data']
                        post_url = post.get('url')
                        
                        if post_url not in all_posts:
                            post_data = {
                                'title': post.get('title'),
                                'body': post.get('selftext', ''),
                                'url': post_url,
                                'author': post.get('author'),
                                'upvotes': post.get('ups'),
                                'comments': post.get('num_comments'),
                                'date': datetime.fromtimestamp(post.get('created_utc')).strftime('%Y-%m-%d %H:%M:%S'),
                                'subreddit': post.get('subreddit'),
                                'permalink': f"https://www.reddit.com{post.get('permalink')}"
                            }
                            all_posts[post_url] = post_data
                    
                    chunk_posts_count += len(children)
                    print(f"    Fetched {len(children)} posts. Total unique: {len(all_posts)}")
                    
                    after = data.get('data', {}).get('after')
                    if not after:
                        break
                        
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    Exception: {e}")
                    break
    
    # Convert back to list
    final_posts = list(all_posts.values())
    
    # Save to JSON
    output_file = 'e:/Reddit/dhaka_extended_posts.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_posts, f, indent=4, ensure_ascii=False)
        
    print(f"\nSaved {len(final_posts)} unique posts to {output_file}")

if __name__ == "__main__":
    crawl_reddit_extended()
