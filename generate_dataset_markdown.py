import pandas as pd, os, re, math
from collections import Counter
from datetime import datetime

CSV_PATH = 'dhaka_posts_20251119_224551.csv'
OUT_PATH = 'dataset_overview.md'

print('Loading CSV...')
df = pd.read_csv(CSV_PATH)
rows, cols = df.shape

# Basic column info
col_info = []
for col in df.columns:
    non_null = df[col].notna().sum()
    missing = rows - non_null
    dtype = df[col].dtype
    sample = ''
    try:
        sample = str(df[col].dropna().iloc[0])[:120]
    except Exception:
        sample = ''
    col_info.append((col, dtype, non_null, missing, sample))

# Date range
try:
    df['date_parsed'] = pd.to_datetime(df['date'])
    date_min = df['date_parsed'].min()
    date_max = df['date_parsed'].max()
    span_days = (date_max - date_min).days + 1
except Exception:
    date_min = date_max = span_days = None
date_col = None
for candidate in ['date','created','created_utc','timestamp']:
    if candidate in df.columns:
        date_col = candidate
        break

if date_col:
    try:
        df['date_parsed'] = pd.to_datetime(df[date_col])
        date_min = df['date_parsed'].min()
        date_max = df['date_parsed'].max()
        span_days = (date_max - date_min).days + 1
    except Exception:
        date_min = date_max = span_days = None
else:
    date_min = date_max = span_days = None

# Subreddit distribution
sub_counts = df['subreddit'].value_counts()

# Engagement stats
upvotes_stats = df['upvotes'].describe()
comments_stats = df['comments'].describe()

# Top posts by upvotes / comments
top_upvotes = df.sort_values('upvotes', ascending=False).head(15)
top_comments = df.sort_values('comments', ascending=False).head(15)

# Engagement score (simple composite)
df['engagement_score'] = df['upvotes'] + df['comments']
engaged = df.sort_values('engagement_score', ascending=False).head(15)

# Word frequency in titles
stopwords = set(['the','a','an','to','of','and','in','for','on','is','it','i','you','me','my','we','be','are','was','were','at','or','from','this','that','with','as','by','about','any','can','do','how','what','why','where'])
words = []
for t in df['title'].astype(str):
    t_clean = re.sub(r'[^A-Za-z0-9অ-হ]+',' ', t.lower())
    for w in t_clean.split():
        if len(w) > 2 and w not in stopwords:
            words.append(w)
word_counts = Counter(words)
common_words = word_counts.most_common(30)

# Temporal distribution (posts per day)
if 'date_parsed' in df.columns:
    per_day = df.groupby(df['date_parsed'].dt.date).size().reset_index(name='count')
else:
    per_day = pd.DataFrame(columns=['date', 'count'])

# Hour-of-day distribution
if 'date_parsed' in df.columns:
    df['hour'] = df['date_parsed'].dt.hour
    hour_counts = df['hour'].value_counts().sort_index()
else:
    hour_counts = pd.Series(dtype=int)

# Author activity
author_counts = df['author'].value_counts().head(20)

# Potential data quality issues
issues = []
if df['title'].isna().any():
    issues.append('Missing titles detected.')
if df['author'].eq('[deleted]').any():
    issues.append('Deleted authors present.')
if (df['upvotes'] < 0).any():
    issues.append('Negative upvotes found (unexpected).')
if (df['comments'] < 0).any():
    issues.append('Negative comments found (unexpected).')
if df['upvotes'].max() == 0:
    issues.append('All upvotes are zero – possible scrape issue.')
if date_min and date_max and span_days < 2:
    issues.append('Date range unusually narrow.')
if not issues:
    issues.append('No major data quality flags detected.')

# Sample slices
sample_head = df.head(5)
sample_tail = df.tail(5)

def md_table(headers, rows):
    out = '| ' + ' | '.join(headers) + ' |\n'
    out += '| ' + ' | '.join(['---']*len(headers)) + ' |\n'
    for r in rows:
        out += '| ' + ' | '.join(str(x) for x in r) + ' |\n'
    return out

md = []
md.append('# Dhaka Posts Dataset Overview\n')
md.append('> Auto-generated comprehensive summary of `dhaka_posts_20251119_224551.csv`.')
md.append('\n## 1. Dataset Snapshot\n')
md.append(f'- Total rows: **{rows}**')
md.append(f'- Total columns: **{cols}**')
if date_min:
    md.append(f'- Date range: **{date_min}** → **{date_max}** ({span_days} days)')
md.append(f'- Subreddits present: {', '.join(sub_counts.index.tolist())}')
md.append('\n### Columns\n')
col_rows = [(c, d, nn, m, s) for c,d,nn,m,s in col_info]
md.append(md_table(['Name','Type','Non-Null','Missing','Sample'], col_rows))

md.append('\n## 2. Subreddit Distribution\n')
sub_rows = [(sr, cnt, f"{cnt/rows*100:.1f}%") for sr, cnt in sub_counts.items()]
md.append(md_table(['Subreddit','Posts','Percent'], sub_rows))

md.append('\n## 3. Engagement Statistics\n')
md.append('### Upvotes\n')
for stat in upvotes_stats.index:
    md.append(f'- {stat}: {upvotes_stats[stat]}')
md.append('\n### Comments\n')
for stat in comments_stats.index:
    md.append(f'- {stat}: {comments_stats[stat]}')

md.append('\n### Top 15 by Upvotes\n')
up_rows = [(r['upvotes'], r['comments'], r['subreddit'], r['title'][:80]) for _, r in top_upvotes.iterrows()]
md.append(md_table(['Upvotes','Comments','Subreddit','Title'], up_rows))

md.append('\n### Top 15 by Comments\n')
com_rows = [(r['comments'], r['upvotes'], r['subreddit'], r['title'][:80]) for _, r in top_comments.iterrows()]
md.append(md_table(['Comments','Upvotes','Subreddit','Title'], com_rows))

md.append('\n### Top 15 by Engagement Score (Upvotes + Comments)\n')
eng_rows = [(r['engagement_score'], r['upvotes'], r['comments'], r['subreddit'], r['title'][:70]) for _, r in engaged.iterrows()]
md.append(md_table(['Eng.Score','Upvotes','Comments','Subreddit','Title'], eng_rows))

md.append('\n## 4. Title Vocabulary (Top 30 Tokens)\n')
word_rows = [(w, c) for w,c in common_words]
md.append(md_table(['Word','Frequency'], word_rows))

md.append('\n## 5. Temporal Distribution\n')
if not per_day.empty:
    md.append('### Posts per Day (first 20 days shown)\n')
    day_rows = [(str(r[per_day.columns[0]]), r['count']) for _, r in per_day.head(20).iterrows()]
    md.append(md_table(['Date','Posts'], day_rows))
else:
    md.append('_Date parsing failed; no temporal stats._')

md.append('\n### Hour of Day Posting Pattern\n')
if not hour_counts.empty:
    hour_rows = [(h, hour_counts[h]) for h in hour_counts.index]
    md.append(md_table(['Hour','Posts'], hour_rows))
else:
    md.append('_Hour extraction unavailable._')

md.append('\n## 6. Author Activity (Top 20)\n')
author_rows = [(a, c) for a,c in author_counts.items()]
md.append(md_table(['Author','Posts'], author_rows))

md.append('\n## 7. Data Quality Checks\n')
for issue in issues:
    md.append(f'- {issue}')

md.append('\n## 8. Sample Records\n')
md.append('### Head (first 5)\n')
head_rows = [(r['date'], r['subreddit'], r['upvotes'], r['comments'], r['title'][:60]) for _, r in sample_head.iterrows()]
md.append(md_table(['Date','Subreddit','Upvotes','Comments','Title'], head_rows))
md.append('### Tail (last 5)\n')
tail_rows = [(r['date'], r['subreddit'], r['upvotes'], r['comments'], r['title'][:60]) for _, r in sample_tail.iterrows()]
md.append(md_table(['Date','Subreddit','Upvotes','Comments','Title'], tail_rows))

md.append('\n## 9. Suggested Next Analyses\n')
md.append('- Sentiment enrichment (already performed in advanced scripts).')
md.append('- Topic modeling using transformer embeddings for semantic clusters.')
md.append('- User cohort analysis (repeat posters vs one-off).')
md.append('- Trend detection: rolling 7-day moving average of posts.')
md.append('- Entity extraction: place names beyond Dhaka (e.g., Sylhet, Chittagong).')

content = '\n'.join(md)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Written markdown summary to {OUT_PATH}')
