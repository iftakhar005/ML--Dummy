import pandas as pd, os, re, json, math
from collections import Counter
from datetime import datetime

CSV_PATH = 'dhaka_posts_20251119_224551.csv'
OUT_PATH = 'dataset_overview.html'

print('Loading CSV...')
df = pd.read_csv(CSV_PATH)
rows, cols = df.shape

# Detect date column
date_col = None
for c in ['date','created','created_utc','timestamp']:
    if c in df.columns:
        date_col = c
        break

if date_col:
    try:
        df['_date_parsed'] = pd.to_datetime(df[date_col])
    except Exception:
        df['_date_parsed'] = pd.NaT
else:
    df['_date_parsed'] = pd.NaT

# Basic stats
sub_counts = df['subreddit'].value_counts() if 'subreddit' in df.columns else pd.Series()
upvotes_stats = df['upvotes'].describe() if 'upvotes' in df.columns else pd.Series()
comments_stats = df['comments'].describe() if 'comments' in df.columns else pd.Series()

# Engagement score
if {'upvotes','comments'} <= set(df.columns):
    df['engagement_score'] = df['upvotes'] + df['comments']
else:
    df['engagement_score'] = 0

# Top lists
def safe_sort(col, ascending=False, n=15):
    if col in df.columns:
        return df.sort_values(col, ascending=ascending).head(n)
    return df.head(0)

top_upvotes = safe_sort('upvotes')
top_comments = safe_sort('comments')
top_engagement = df.sort_values('engagement_score', ascending=False).head(15)

# Column metadata
col_meta = []
for col in df.columns:
    non_null = df[col].notna().sum()
    missing = rows - non_null
    dtype = str(df[col].dtype)
    sample_val = ''
    if non_null:
        sample_val = str(df[col].dropna().iloc[0])[:100]
    col_meta.append({'name':col,'dtype':dtype,'non_null':non_null,'missing':missing,'sample':sample_val})

# Title vocabulary
stopwords = set(['the','a','an','to','of','and','in','for','on','is','it','i','you','me','my','we','be','are','was','were','at','or','from','this','that','with','as','by','about','any','can','do','how','what','why','where'])
words=[]
if 'title' in df.columns:
    for t in df['title'].astype(str):
        t_clean = re.sub(r'[^A-Za-z0-9অ-হ]+',' ', t.lower())
        for w in t_clean.split():
            if len(w)>2 and w not in stopwords:
                words.append(w)
word_counts = Counter(words)
common_words = word_counts.most_common(40)

# Temporal distribution
if df['_date_parsed'].notna().any():
    per_day = df.groupby(df['_date_parsed'].dt.date).size().reset_index(name='count')
    hour_counts = df['_date_parsed'].dt.hour.value_counts().sort_index()
else:
    per_day = pd.DataFrame(columns=['date','count'])
    hour_counts = pd.Series(dtype=int)

# Authors
author_counts = df['author'].value_counts().head(30) if 'author' in df.columns else pd.Series()

# Data quality checks
issues=[]
if 'title' in df.columns and df['title'].isna().any(): issues.append('Missing titles present.')
if 'author' in df.columns and df['author'].eq('[deleted]').any(): issues.append('Deleted authors found.')
if 'upvotes' in df.columns and (df['upvotes']<0).any(): issues.append('Negative upvote values detected.')
if 'comments' in df.columns and (df['comments']<0).any(): issues.append('Negative comment counts detected.')
if 'upvotes' in df.columns and df['upvotes'].max()==0: issues.append('All upvotes are zero (possible scrape issue).')
if date_col and per_day.empty: issues.append('Date parsing failed.')
if not issues: issues.append('No major data quality flags.')

# Samples
sample_head = df.head(10)
sample_tail = df.tail(10)

# Helper to escape HTML
def esc(s):
    return (str(s)
            .replace('&','&amp;')
            .replace('<','&lt;')
            .replace('>','&gt;'))

# Build HTML
html=[]
html.append('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" />')
html.append('<title>Dhaka Posts Dataset Overview</title>')
html.append('<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#fafafa;color:#222}h1,h2{margin-top:40px}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}th,td{border:1px solid #ddd;padding:6px;vertical-align:top}th{background:#222;color:#fff;position:sticky;top:0}tr:nth-child(even){background:#f4f4f4}.badge{display:inline-block;padding:2px 6px;border-radius:4px;background:#222;color:#fff;font-size:11px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:12px;box-shadow:0 1px 2px rgba(0,0,0,.06)}.bar{height:14px;background:#4A90E2;border-radius:3px}.small{font-size:12px;color:#555}.pill{background:#4A90E2;color:#fff;padding:2px 8px;border-radius:20px;font-size:12px;margin-right:6px}.flex{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.warn{color:#B00020;font-weight:600}.ok{color:#0A7F2E;font-weight:600}details{margin:8px 0}summary{cursor:pointer;font-weight:600}.chart-row{display:flex;align-items:center;margin:4px 0} .chart-label{width:110px;font-size:12px} .chart-bar{background:#4A90E2;height:14px;border-radius:3px} .mono{font-family:Consolas,monospace;font-size:12px;}</style>')
html.append("<script>function filterTable(tableId,val){const v=val.toLowerCase();document.querySelectorAll('#'+tableId+' tbody tr').forEach(r=>{r.style.display=r.textContent.toLowerCase().includes(v)?'':'none';});}</script>")
html.append('</head><body>')
html.append('<h1>Dhaka Posts Dataset Overview</h1>')
html.append(f'<p class="small">Generated: {datetime.utcnow().isoformat()}Z</p>')
html.append('<div class="grid">')
html.append(f'<div class="card"><h3>Rows</h3><div class="pill">{rows}</div></div>')
html.append(f'<div class="card"><h3>Columns</h3><div class="pill">{cols}</div></div>')
if date_col and df['_date_parsed'].notna().any():
    span_days=(df['_date_parsed'].max()-df['_date_parsed'].min()).days+1
    html.append(f'<div class="card"><h3>Date Span</h3><div class="pill">{span_days} days</div></div>')
if not sub_counts.empty:
    html.append(f'<div class="card"><h3>Subreddits</h3><div class="pill">{len(sub_counts)}</div></div>')
html.append('</div>')

# Column dictionary
html.append('<h2>1. Column Dictionary</h2>')
html.append('<input placeholder="Filter columns..." oninput="filterTable(\'col_table\',this.value)" id="col_filter" style="padding:6px;width:240px;border:1px solid #ccc;border-radius:4px" />')
html.append('<table id="col_table"><thead><tr><th>Name</th><th>Type</th><th>Non-Null</th><th>Missing</th><th>Sample</th></tr></thead><tbody>')
for m in col_meta:
    html.append(f'<tr><td>{esc(m["name"])}</td><td>{esc(m["dtype"])}</td><td>{m["non_null"]}</td><td>{m["missing"]}</td><td class="mono">{esc(m["sample"])}</td></tr>')
html.append('</tbody></table>')

# Subreddit distribution
if not sub_counts.empty:
    html.append('<h2>2. Subreddit Distribution</h2><div>')
    max_sub = sub_counts.max()
    for sr, cnt in sub_counts.items():
        width = (cnt / max_sub) * 220
        html.append(f'<div class="chart-row"><div class="chart-label">{esc(sr)}</div><div class="chart-bar" style="width:{width}px"></div><div class="small">{cnt} ({cnt/rows*100:.1f}%)</div></div>')
    html.append('</div>')

# Engagement stats
if not upvotes_stats.empty:
    html.append('<h2>3. Engagement Statistics</h2><div class="grid">')
    for stat in upvotes_stats.index:
        html.append(f'<div class="card"><h4>Upvotes {esc(stat)}</h4><div class="mono">{upvotes_stats[stat]:.2f}</div></div>')
    for stat in comments_stats.index:
        html.append(f'<div class="card"><h4>Comments {esc(stat)}</h4><div class="mono">{comments_stats[stat]:.2f}</div></div>')
    html.append('</div>')

# Top tables helper
def make_top_table(df_slice, headers, id_):
    html.append(f'<details open><summary>{esc(id_)}</summary>')
    html.append('<table><thead><tr>' + ''.join(f'<th>{esc(h)}</th>' for h in headers) + '</tr></thead><tbody>')
    for _, r in df_slice.iterrows():
        html.append('<tr>')
        for h in headers:
            val = r.get(h.lower(), r.get(h, ''))
            if h.lower()=='title':
                val = str(val)[:120]
            html.append(f'<td>{esc(val)}</td>')
        html.append('</tr>')
    html.append('</tbody></table></details>')

html.append('<h2>4. Top Posts</h2>')
make_top_table(top_upvotes[['upvotes','comments','subreddit','title']], ['Upvotes','Comments','Subreddit','Title'], 'Top 15 by Upvotes')
make_top_table(top_comments[['comments','upvotes','subreddit','title']], ['Comments','Upvotes','Subreddit','Title'], 'Top 15 by Comments')
make_top_table(top_engagement[['engagement_score','upvotes','comments','subreddit','title']], ['Engagement_Score','Upvotes','Comments','Subreddit','Title'], 'Top 15 by Engagement Score')

# Vocabulary
html.append('<h2>5. Title Vocabulary (Top 40)</h2>')
html.append('<table><thead><tr><th>Word</th><th>Freq</th><th>Bar</th></tr></thead><tbody>')
max_word = common_words[0][1] if common_words else 1
for w,c in common_words:
    width = (c / max_word) * 200
    html.append(f'<tr><td>{esc(w)}</td><td>{c}</td><td><div class="bar" style="width:{width}px"></div></td></tr>')
html.append('</tbody></table>')

# Temporal
html.append('<h2>6. Temporal Distribution</h2>')
if not per_day.empty:
    html.append('<h4>Posts per Day</h4><table><thead><tr><th>Date</th><th>Posts</th></tr></thead><tbody>')
    day_col_name = per_day.columns[0]
    for _, r in per_day.iterrows():
        html.append(f"<tr><td>{r[day_col_name]}</td><td>{r['count']}</td></tr>")
    html.append('</tbody></table>')
else:
    html.append('<p class="small">No parsed date data available.</p>')

if not hour_counts.empty:
    html.append('<h4>Posts by Hour (UTC parsed)</h4><div>')
    max_hour = hour_counts.max()
    for h, cnt in hour_counts.items():
        width = (cnt / max_hour) * 220
        html.append(f'<div class="chart-row"><div class="chart-label">Hour {h}</div><div class="chart-bar" style="width:{width}px"></div><div class="small">{cnt}</div></div>')
    html.append('</div>')

# Authors
if not author_counts.empty:
    html.append('<h2>7. Top Authors</h2><table><thead><tr><th>Author</th><th>Posts</th><th>Bar</th></tr></thead><tbody>')
    max_auth = author_counts.max()
    for a,cnt in author_counts.items():
        width = (cnt / max_auth) * 200
        html.append(f'<tr><td>{esc(a)}</td><td>{cnt}</td><td><div class="bar" style="width:{width}px"></div></td></tr>')
    html.append('</tbody></table>')

# Quality
html.append('<h2>8. Data Quality</h2><ul>')
for i in issues:
    cls = 'warn' if 'Missing' in i or 'Negative' in i or 'failed' in i else 'ok'
    html.append(f'<li class="{cls}">{esc(i)}</li>')
html.append('</ul>')

# Samples
html.append('<h2>9. Sample Records</h2><details open><summary>Head (first 10)</summary><table><thead><tr><th>Date</th><th>Subreddit</th><th>Upvotes</th><th>Comments</th><th>Title</th></tr></thead><tbody>')
for _, r in sample_head.iterrows():
    html.append(f"<tr><td>{esc(r.get(date_col, ''))}</td><td>{esc(r.get('subreddit',''))}</td><td>{esc(r.get('upvotes',''))}</td><td>{esc(r.get('comments',''))}</td><td>{esc(str(r.get('title',''))[:120])}</td></tr>")
html.append('</tbody></table></details>')
html.append('<details><summary>Tail (last 10)</summary><table><thead><tr><th>Date</th><th>Subreddit</th><th>Upvotes</th><th>Comments</th><th>Title</th></tr></thead><tbody>')
for _, r in sample_tail.iterrows():
    html.append(f"<tr><td>{esc(r.get(date_col, ''))}</td><td>{esc(r.get('subreddit',''))}</td><td>{esc(r.get('upvotes',''))}</td><td>{esc(r.get('comments',''))}</td><td>{esc(str(r.get('title',''))[:120])}</td></tr>")
html.append('</tbody></table></details>')

# Recommendations
html.append('<h2>10. Suggested Next Analyses</h2><ul>')
html.append('<li>Sentiment & emotion overlay for each top author.</li>')
html.append('<li>Interactive filtering by keyword / time range.</li>')
html.append('<li>Geographical tagging of neighborhood mentions.</li>')
html.append('<li>Entity extraction for places (Sylhet, Gulshan, Mirpur etc.).</li>')
html.append('<li>Cluster similar titles using embeddings.</li>')
html.append('</ul>')

html.append('<p class="small">Use browser Find (Ctrl+F) or column filter box to quickly locate fields.</p>')
html.append('</body></html>')

content=''.join(html)
with open(OUT_PATH,'w',encoding='utf-8') as f:
    f.write(content)
print(f'Wrote HTML visualization to {OUT_PATH}')
