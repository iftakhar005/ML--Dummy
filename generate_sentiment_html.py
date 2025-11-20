import os
import pandas as pd
from collections import Counter
from datetime import datetime, timezone
import re

# Candidate sources in priority order
CANDIDATES = [
    'advanced_sentiment_analysis/05_posts_with_advanced_analysis.csv',
    'location_sentiment_analysis/01_full_analysis.csv',
    'general_bangladesh_analysis/01_full_analysis.csv'
]

OUT_PATH = 'sentiment_overview.html'

# Find the first existing source
SRC = None
for p in CANDIDATES:
    if os.path.exists(p):
        SRC = p
        break

if SRC is None:
    raise FileNotFoundError('No sentiment CSV found. Expected one of: ' + ', '.join(CANDIDATES))

print(f'Loading sentiment data from: {SRC}')
df = pd.read_csv(SRC)
rows = len(df)

# Normalize expected columns
has_cols = set(df.columns)

# Sentiment distribution
if 'sentiment' in has_cols:
    sent_counts = df['sentiment'].value_counts()
else:
    # Try to infer from polarity
    if 'polarity' in has_cols:
        def lbl(p):
            if p > 0.1: return 'positive'
            if p < -0.1: return 'negative'
            return 'neutral'
        sent_counts = df['polarity'].apply(lbl).value_counts()
        df['sentiment'] = df['polarity'].apply(lbl)
    else:
        sent_counts = pd.Series()

# Emotion distribution (optional)
emo_counts = df['emotion'].value_counts() if 'emotion' in has_cols else pd.Series()

# Topics
def split_topics(x):
    parts = [t.strip() for t in str(x).split(',') if str(x) != 'nan']
    return [p for p in parts if p]

all_topics = []
if 'topics' in has_cols:
    for t in df['topics']:
        all_topics.extend(split_topics(t))
    topic_counter = Counter(all_topics)
else:
    topic_counter = Counter()

# Topic sentiment breakdown
topic_sentiment = []
if 'topics' in has_cols and 'sentiment' in has_cols:
    top_topics = [t for t, _ in topic_counter.most_common(12)]
    for topic in top_topics:
        tdf = df[df['topics'].astype(str).str.contains(re.escape(topic), regex=True, na=False)]
        if not len(tdf):
            continue
        pos = (tdf['sentiment'] == 'positive').sum()
        neg = (tdf['sentiment'] == 'negative').sum()
        neu = (tdf['sentiment'] == 'neutral').sum()
        avg_pol = tdf['polarity'].mean() if 'polarity' in has_cols else float('nan')
        topic_sentiment.append({
            'topic': topic,
            'posts': len(tdf),
            'positive': pos,
            'negative': neg,
            'neutral': neu,
            'avg_polarity': avg_pol
        })

# Subreddit comparison (optional)
subreddit_summary = []
if 'subreddit' in has_cols:
    for sub, sdf in df.groupby('subreddit'):
        subreddit_summary.append({
            'subreddit': sub,
            'posts': len(sdf),
            'positive': int((sdf.get('sentiment','') == 'positive').sum()) if 'sentiment' in has_cols else None,
            'negative': int((sdf.get('sentiment','') == 'negative').sum()) if 'sentiment' in has_cols else None,
            'neutral': int((sdf.get('sentiment','') == 'neutral').sum()) if 'sentiment' in has_cols else None,
            'avg_polarity': float(sdf['polarity'].mean()) if 'polarity' in has_cols else None
        })

# Top +/- posts
def safe_slice(cols):
    existing = [c for c in cols if c in has_cols]
    return existing

top_pos = df.nlargest(15, 'polarity')[safe_slice(['title','subreddit','polarity','emotion','topics','upvotes','comments'])] if 'polarity' in has_cols else pd.DataFrame()
low_neg = df.nsmallest(15, 'polarity')[safe_slice(['title','subreddit','polarity','emotion','topics','upvotes','comments'])] if 'polarity' in has_cols else pd.DataFrame()

# Helper
def esc(s):
    return (str(s)
            .replace('&','&amp;')
            .replace('<','&lt;')
            .replace('>','&gt;'))

html=[]
html.append('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" />')
html.append('<title>Sentiment Analysis Overview</title>')
html.append('<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#fafafa;color:#222}h1,h2{margin-top:36px}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}th,td{border:1px solid #ddd;padding:6px;vertical-align:top}th{background:#222;color:#fff;position:sticky;top:0}tr:nth-child(even){background:#f4f4f4}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:12px;box-shadow:0 1px 2px rgba(0,0,0,.06)}.pill{background:#4A90E2;color:#fff;padding:2px 8px;border-radius:20px;font-size:12px;margin-right:6px}.bar{height:14px;background:#4A90E2;border-radius:3px}.row{display:flex;gap:12px;align-items:center;margin:4px 0}.label{width:140px;font-size:12px}.small{font-size:12px;color:#555}.mono{font-family:Consolas,monospace;font-size:12px}</style>')
html.append('</head><body>')
html.append('<h1>Sentiment Analysis Overview</h1>')
html.append(f'<p class="small">Source: {esc(SRC)} • Generated: {datetime.now(timezone.utc).isoformat()}</p>')

# Summary cards
html.append('<div class="grid">')
html.append(f'<div class="card"><h3>Total Posts</h3><div class="pill">{rows}</div></div>')
if 'polarity' in has_cols:
    html.append(f'<div class="card"><h3>Avg Polarity</h3><div class="pill">{df["polarity"].mean():.3f}</div></div>')
if 'subjectivity' in has_cols:
    html.append(f'<div class="card"><h3>Avg Subjectivity</h3><div class="pill">{df["subjectivity"].mean():.3f}</div></div>')
html.append('</div>')

# Sentiment distribution
if not sent_counts.empty:
    html.append('<h2>1) Sentiment Distribution</h2>')
    max_cnt = sent_counts.max()
    for s, cnt in sent_counts.items():
        w = 220 * (cnt / max_cnt)
        html.append(f'<div class="row"><div class="label">{esc(str(s).title())}</div><div class="bar" style="width:{w}px"></div><div class="small">{cnt} ({cnt/rows*100:.1f}%)</div></div>')

# Emotions
if not emo_counts.empty:
    html.append('<h2>2) Emotion Distribution</h2>')
    max_e = emo_counts.max()
    for e, cnt in emo_counts.items():
        w = 220 * (cnt / max_e)
        html.append(f'<div class="row"><div class="label">{esc(str(e).title())}</div><div class="bar" style="width:{w}px"></div><div class="small">{cnt} ({cnt/rows*100:.1f}%)</div></div>')

# Topics
if topic_counter:
    html.append('<h2>3) Top Topics</h2>')
    max_t = max(topic_counter.values())
    html.append('<div>')
    for t, cnt in topic_counter.most_common(20):
        w = 220 * (cnt / max_t)
        html.append(f'<div class="row"><div class="label">{esc(t)}</div><div class="bar" style="width:{w}px"></div><div class="small">{cnt} ({cnt/rows*100:.1f}%)</div></div>')
    html.append('</div>')

# Topic sentiment table
if topic_sentiment:
    html.append('<h2>4) Sentiment by Topic</h2>')
    html.append('<table><thead><tr><th>Topic</th><th>Posts</th><th>Positive</th><th>Negative</th><th>Neutral</th><th>Avg Polarity</th></tr></thead><tbody>')
    for t in topic_sentiment:
        html.append(f'<tr><td>{esc(t["topic"])}</td><td>{t["posts"]}</td><td>{t["positive"]}</td><td>{t["negative"]}</td><td>{t["neutral"]}</td><td>{t["avg_polarity"]:.3f}</td></tr>')
    html.append('</tbody></table>')

# Subreddit comparison
if subreddit_summary:
    html.append('<h2>5) Subreddit Comparison</h2>')
    html.append('<table><thead><tr><th>Subreddit</th><th>Posts</th><th>Positive</th><th>Negative</th><th>Neutral</th><th>Avg Polarity</th></tr></thead><tbody>')
    for s in subreddit_summary:
        pos = '' if s['positive'] is None else s['positive']
        neg = '' if s['negative'] is None else s['negative']
        neu = '' if s['neutral'] is None else s['neutral']
        avg = '' if s['avg_polarity'] is None else f"{s['avg_polarity']:.3f}"
        html.append(f'<tr><td>{esc(s["subreddit"])}</td><td>{s["posts"]}</td><td>{pos}</td><td>{neg}</td><td>{neu}</td><td>{avg}</td></tr>')
    html.append('</tbody></table>')

# Top positive and negative
if not top_pos.empty:
    html.append('<h2>6) Top Positive Posts</h2>')
    html.append('<table><thead><tr><th>Polarity</th><th>Subreddit</th><th>Title</th><th>Emotion</th><th>Topics</th><th>Upvotes</th><th>Comments</th></tr></thead><tbody>')
    for _, r in top_pos.iterrows():
        html.append(f'<tr><td>{r.get("polarity",""):.3f}</td><td>{esc(r.get("subreddit",""))}</td><td>{esc(str(r.get("title",""))[:140])}</td><td>{esc(r.get("emotion",""))}</td><td>{esc(r.get("topics",""))}</td><td>{esc(r.get("upvotes",""))}</td><td>{esc(r.get("comments",""))}</td></tr>')
    html.append('</tbody></table>')

if not low_neg.empty:
    html.append('<h2>7) Top Negative Posts</h2>')
    html.append('<table><thead><tr><th>Polarity</th><th>Subreddit</th><th>Title</th><th>Emotion</th><th>Topics</th><th>Upvotes</th><th>Comments</th></tr></thead><tbody>')
    for _, r in low_neg.iterrows():
        html.append(f'<tr><td>{r.get("polarity",""):.3f}</td><td>{esc(r.get("subreddit",""))}</td><td>{esc(str(r.get("title",""))[:140])}</td><td>{esc(r.get("emotion",""))}</td><td>{esc(r.get("topics",""))}</td><td>{esc(r.get("upvotes",""))}</td><td>{esc(r.get("comments",""))}</td></tr>')
    html.append('</tbody></table>')

html.append('<p class="small">Tip: Press Ctrl+F in your browser to search within this page.</p>')
html.append('</body></html>')

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(''.join(html))

print(f'Wrote sentiment dashboard to {OUT_PATH}')
