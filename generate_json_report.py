import json
import pandas as pd
from collections import Counter
from datetime import datetime
import re
import os

INPUT_FILE = 'e:/Reddit/final_dhaka_dataset.json'
OUTPUT_FILE = 'e:/Reddit/combined_dhaka_overview.html'

def generate_report():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    # Convert date
    df['date'] = pd.to_datetime(df['date'])
    
    # Basic Stats
    total_posts = len(df)
    unique_authors = df['author'].nunique()
    total_upvotes = df['upvotes'].sum()
    total_comments = df['comments'].sum()
    subreddits = df['subreddit'].unique()
    start_date = df['date'].min()
    end_date = df['date'].max()

    # Aggregations
    
    # 1. Posts per Subreddit
    sub_counts = df['subreddit'].value_counts()
    
    # 2. Posts per Day
    daily_counts = df['date'].dt.date.value_counts().sort_index()
    
    # 3. Top Authors
    author_counts = df['author'].value_counts().head(10)
    
    # 4. Top Posts by Upvotes
    top_upvoted = df.nlargest(10, 'upvotes')
    
    # 5. Top Posts by Comments
    top_commented = df.nlargest(10, 'comments')
    
    # 6. Word Frequency (Title)
    # Simple tokenizer
    def get_tokens(text):
        if not isinstance(text, str): return []
        # Remove punctuation and lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        return [w for w in text.split() if len(w) > 3]

    all_words = []
    for t in df['title']:
        all_words.extend(get_tokens(t))
    
    # Basic stopwords (English)
    stopwords = {'this', 'that', 'with', 'from', 'have', 'what', 'about', 'there', 'just', 'your', 'some', 'like', 'will', 'would', 'should', 'could', 'dhaka', 'bangladesh', 'people', 'know', 'want', 'need', 'help', 'please', 'anyone', 'does', 'going', 'where', 'when', 'which', 'best', 'good', 'looking', 'find', 'guys', 'time', 'been', 'much', 'many', 'more', 'most', 'only', 'also', 'into', 'over', 'after', 'before', 'then', 'than', 'here', 'they', 'them', 'their', 'very', 'even', 'back', 'down', 'made', 'make', 'think', 'take', 'come', 'being', 'because', 'those', 'these', 'while', 'still', 'never', 'really', 'always', 'last', 'first', 'next', 'other', 'another', 'thing', 'things'}
    
    filtered_words = [w for w in all_words if w not in stopwords]
    word_counts = Counter(filtered_words).most_common(20)

    # 7. Missing Data Analysis
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0]
    
    # 8. Language Detection (Heuristic: Bengali vs English/Other)
    def detect_language(text):
        if not isinstance(text, str): return 'Unknown'
        # Check for Bengali Unicode range (U+0980 to U+09FF)
        if re.search(r'[\u0980-\u09FF]', text):
            return 'Bengali'
        return 'English/Other'

    df['language'] = df['title'].apply(detect_language)
    language_counts = df['language'].value_counts()

    # 9. Content Stats
    df['title_length'] = df['title'].str.len()
    df['body_length'] = df['body'].str.len().fillna(0)
    avg_title_len = df['title_length'].mean()
    avg_body_len = df['body_length'].mean()
    
    # 10. Media Distribution
    def get_media_type(url):
        if not isinstance(url, str): return 'Text'
        url_lower = url.lower()
        if 'i.redd.it' in url_lower or 'imgur' in url_lower: return 'Image'
        if 'v.redd.it' in url_lower or 'youtube' in url_lower or 'youtu.be' in url_lower: return 'Video'
        if 'reddit.com/gallery' in url_lower: return 'Gallery'
        if 'reddit.com' in url_lower: return 'Text/Link'
        return 'External Link'

    df['media_type'] = df['url'].apply(get_media_type)
    media_counts = df['media_type'].value_counts()

    # HTML Generation
    html = []
    html.append('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">')
    html.append('<title>Dhaka Reddit Dataset Overview</title>')
    html.append('<style>')
    html.append('body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; color: #333; }')
    html.append('.container { max-width: 1200px; margin: 0 auto; padding: 20px; }')
    html.append('header { background-color: #00796b; color: white; padding: 20px 0; text-align: center; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }')
    html.append('h1 { margin: 0; font-size: 2.5em; }')
    html.append('.subtitle { font-size: 1.1em; opacity: 0.9; margin-top: 10px; }')
    html.append('.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }')
    html.append('.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; }')
    html.append('.card h3 { margin-top: 0; color: #555; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }')
    html.append('.card .value { font-size: 2.5em; font-weight: bold; color: #00796b; margin: 10px 0; }')
    html.append('.section { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }')
    html.append('h2 { color: #00796b; border-bottom: 2px solid #e0f2f1; padding-bottom: 10px; margin-top: 0; }')
    html.append('.chart-container { margin-top: 20px; }')
    html.append('.bar-row { display: flex; align-items: center; margin-bottom: 8px; }')
    html.append('.bar-label { width: 150px; font-size: 0.9em; text-align: right; padding-right: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }')
    html.append('.bar-area { flex-grow: 1; background-color: #e0f2f1; height: 20px; border-radius: 10px; overflow: hidden; }')
    html.append('.bar-fill { height: 100%; background-color: #00796b; border-radius: 10px; transition: width 0.5s ease-in-out; }')
    html.append('.bar-value { width: 60px; padding-left: 10px; font-size: 0.9em; color: #666; }')
    html.append('table { width: 100%; border-collapse: collapse; margin-top: 15px; }')
    html.append('th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }')
    html.append('th { background-color: #f9f9f9; color: #555; font-weight: 600; }')
    html.append('tr:hover { background-color: #f5f5f5; }')
    html.append('.post-link { color: #00796b; text-decoration: none; font-weight: 500; }')
    html.append('.post-link:hover { text-decoration: underline; }')
    html.append('.tag { display: inline-block; background: #e0f2f1; color: #00796b; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px; }')
    html.append('.footer { text-align: center; color: #888; margin-top: 50px; padding-bottom: 20px; font-size: 0.9em; }')
    html.append('</style>')
    html.append('</head><body>')

    # Header
    html.append('<header>')
    html.append('<h1>Dhaka Reddit Dataset Analysis</h1>')
    html.append(f'<div class="subtitle">Comprehensive overview of {total_posts} posts from {start_date.strftime("%B %d, %Y")} to {end_date.strftime("%B %d, %Y")}</div>')
    html.append('</header>')

    html.append('<div class="container">')

    # KPI Cards
    html.append('<div class="card-grid">')
    html.append(f'<div class="card"><h3>Total Posts</h3><div class="value">{total_posts:,}</div></div>')
    html.append(f'<div class="card"><h3>Unique Authors</h3><div class="value">{unique_authors:,}</div></div>')
    html.append(f'<div class="card"><h3>Total Upvotes</h3><div class="value">{total_upvotes:,}</div></div>')
    html.append(f'<div class="card"><h3>Total Comments</h3><div class="value">{total_comments:,}</div></div>')
    html.append('</div>')

    # Data Quality & Details Section
    html.append('<div class="section">')
    html.append('<h2>Data Quality & Details</h2>')
    html.append('<div style="display: flex; flex-wrap: wrap; gap: 40px;">')

    # Missing Data
    html.append('<div style="flex: 1; min-width: 250px;">')
    html.append('<h3>Missing Data Points</h3>')
    if not missing_data.empty:
        html.append('<table><thead><tr><th>Column</th><th>Missing Count</th><th>% Missing</th></tr></thead><tbody>')
        for col, count in missing_data.items():
            pct = (count / total_posts) * 100
            html.append(f'<tr><td>{col}</td><td>{count}</td><td>{pct:.1f}%</td></tr>')
        html.append('</tbody></table>')
    else:
        html.append('<p>No missing data found in key columns.</p>')
    html.append('</div>')

    # Language Distribution
    html.append('<div style="flex: 1; min-width: 250px;">')
    html.append('<h3>Language Distribution (Titles)</h3>')
    html.append('<div class="chart-container">')
    max_lang = language_counts.max()
    for lang, count in language_counts.items():
        width = (count / max_lang) * 100
        html.append(f'<div class="bar-row"><div class="bar-label">{lang}</div><div class="bar-area"><div class="bar-fill" style="width: {width}%"></div></div><div class="bar-value">{count}</div></div>')
    html.append('</div></div>')

    # Content Stats
    html.append('<div style="flex: 1; min-width: 250px;">')
    html.append('<h3>Content Statistics</h3>')
    html.append('<table><tbody>')
    html.append(f'<tr><td><strong>Avg Title Length</strong></td><td>{avg_title_len:.1f} chars</td></tr>')
    html.append(f'<tr><td><strong>Avg Body Length</strong></td><td>{avg_body_len:.1f} chars</td></tr>')
    html.append(f'<tr><td><strong>Date Range</strong></td><td>{(end_date - start_date).days} days</td></tr>')
    html.append('</tbody></table>')
    
    html.append('<h3 style="margin-top: 20px;">Media Type Distribution</h3>')
    html.append('<div class="chart-container">')
    max_media = media_counts.max()
    for media, count in media_counts.items():
        width = (count / max_media) * 100
        html.append(f'<div class="bar-row"><div class="bar-label">{media}</div><div class="bar-area"><div class="bar-fill" style="width: {width}%"></div></div><div class="bar-value">{count}</div></div>')
    html.append('</div>')
    html.append('</div>')

    html.append('</div></div>')

    # Charts Section
    html.append('<div class="section">')
    html.append('<h2>Dataset Composition</h2>')
    html.append('<div style="display: flex; flex-wrap: wrap; gap: 40px;">')
    
    # Subreddit Chart
    html.append('<div style="flex: 1; min-width: 300px;">')
    html.append('<h3>Posts by Subreddit</h3>')
    html.append('<div class="chart-container">')
    max_sub = sub_counts.max()
    for sub, count in sub_counts.items():
        width = (count / max_sub) * 100
        html.append(f'<div class="bar-row"><div class="bar-label">r/{sub}</div><div class="bar-area"><div class="bar-fill" style="width: {width}%"></div></div><div class="bar-value">{count}</div></div>')
    html.append('</div></div>')

    # Top Authors Chart
    html.append('<div style="flex: 1; min-width: 300px;">')
    html.append('<h3>Top 10 Active Authors</h3>')
    html.append('<div class="chart-container">')
    max_auth = author_counts.max()
    for auth, count in author_counts.items():
        width = (count / max_auth) * 100
        html.append(f'<div class="bar-row"><div class="bar-label">{auth}</div><div class="bar-area"><div class="bar-fill" style="width: {width}%"></div></div><div class="bar-value">{count}</div></div>')
    html.append('</div></div>')
    
    html.append('</div></div>')

    # Timeline Section
    html.append('<div class="section">')
    html.append('<h2>Activity Timeline (Last 30 Days)</h2>')
    html.append('<div class="chart-container">')
    # Show last 30 entries if too many
    display_daily = daily_counts.tail(30)
    max_day = display_daily.max() if not display_daily.empty else 1
    for day, count in display_daily.items():
        width = (count / max_day) * 100
        html.append(f'<div class="bar-row"><div class="bar-label">{day}</div><div class="bar-area"><div class="bar-fill" style="width: {width}%"></div></div><div class="bar-value">{count}</div></div>')
    html.append('</div>')
    html.append('<p style="text-align: center; color: #666; font-size: 0.9em; margin-top: 10px;">*Showing activity for the most recent days in the dataset</p>')
    html.append('</div>')

    # Word Frequency
    html.append('<div class="section">')
    html.append('<h2>Common Topics (Title Keywords)</h2>')
    html.append('<div style="display: flex; flex-wrap: wrap; gap: 10px;">')
    max_word = word_counts[0][1] if word_counts else 1
    for word, count in word_counts:
        # Size relative to frequency
        size = 0.8 + (count / max_word) * 1.5
        html.append(f'<span style="background: #e0f2f1; color: #004d40; padding: 5px 15px; border-radius: 20px; font-size: {size}em;">{word} ({count})</span>')
    html.append('</div></div>')

    # Top Content Tables
    html.append('<div class="section">')
    html.append('<h2>Most Engaging Content</h2>')
    
    html.append('<h3>Top 10 Most Upvoted Posts</h3>')
    html.append('<table><thead><tr><th>Title</th><th>Subreddit</th><th>Author</th><th>Upvotes</th><th>Comments</th></tr></thead><tbody>')
    for _, row in top_upvoted.iterrows():
        title_short = (row['title'][:75] + '...') if len(row['title']) > 75 else row['title']
        html.append(f'<tr><td><a href="{row["url"]}" target="_blank" class="post-link">{title_short}</a></td><td><span class="tag">{row["subreddit"]}</span></td><td>{row["author"]}</td><td><strong>{row["upvotes"]}</strong></td><td>{row["comments"]}</td></tr>')
    html.append('</tbody></table>')

    html.append('<h3 style="margin-top: 30px;">Top 10 Most Discussed Posts</h3>')
    html.append('<table><thead><tr><th>Title</th><th>Subreddit</th><th>Author</th><th>Upvotes</th><th>Comments</th></tr></thead><tbody>')
    for _, row in top_commented.iterrows():
        title_short = (row['title'][:75] + '...') if len(row['title']) > 75 else row['title']
        html.append(f'<tr><td><a href="{row["url"]}" target="_blank" class="post-link">{title_short}</a></td><td><span class="tag">{row["subreddit"]}</span></td><td>{row["author"]}</td><td>{row["upvotes"]}</td><td><strong>{row["comments"]}</strong></td></tr>')
    html.append('</tbody></table>')
    
    html.append('</div>')

    # Footer
    html.append('<div class="footer">Generated by GitHub Copilot • ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</div>')
    html.append('</div></body></html>')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"Successfully generated report at: {OUTPUT_FILE}")

if __name__ == '__main__':
    generate_report()
