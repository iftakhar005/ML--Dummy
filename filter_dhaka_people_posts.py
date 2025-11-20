import pandas as pd
import re
from datetime import datetime

SRC = 'dhaka_posts_20251119_224551.csv'
OUT_ALL = 'dhaka_people_posts_combined.csv'
OUT_BREAKDOWN = 'dhaka_people_posts_breakdown.csv'

print('='*100)
print('FILTER: POSTS FROM DHAKA PEOPLE (r/dhaka OR Dhaka-area mentions)')
print('='*100)

# Load
df = pd.read_csv(SRC)
print(f"Loaded {len(df)} rows from {SRC}")

# Normalize text helper
def norm(s):
    return str(s).lower()

# Dhaka area keywords (from your list)
areas = [
    # City corporations
    'dncc','dscc','dhaka north city corporation','dhaka south city corporation',
    # Major areas (DNCC)
    'uttara','mirpur','pallabi','airport','shahjalal','mohammadpur','dhanmondi','shyamoli','tejgaon',
    'turag','banani','gulshan','badda','khilgaon','shantinagar','kallyanpur','gabtoli','agargaon',
    # Major areas (DSCC)
    'old dhaka','puran dhaka','sadarghat','lalbagh','kotwali','kamrangirchar','motijheel','ramna',
    'baridhara','jatrabari','paltan','banasree','demra','wari',
    # Other notable
    'uttarkhan','bashundhara','mohakhali','rampura','khilkhet','niketon','kafrul'
]

# Build regex pattern (word-boundary match, allow hyphens/spaces)
# Escape special chars and join
kw_parts = []
for a in areas + ['dhaka']:
    a = a.strip().lower()
    a = re.sub(r"\s+", r"[\s-]", re.escape(a))  # spaces/hyphens interchangeable
    kw_parts.append(fr"\b{a}\b")
pattern = re.compile('|'.join(kw_parts))

# Classify posts
is_dhaka_sub = (df['subreddit'].str.lower() == 'dhaka')
text = (df['title'].astype(str).str.lower() + ' ' + df['body'].astype(str).str.lower())
has_area_mention = text.str.contains(pattern, regex=True, na=False)

mask = is_dhaka_sub | has_area_mention
filtered = df[mask].copy()

print(f"\nFound {len(filtered)} posts likely from Dhaka people")
print(f" - From r/dhaka: {(is_dhaka_sub & mask).sum()}")
print(f" - From r/bangladesh with Dhaka-area mentions: {(~is_dhaka_sub & mask).sum()}")

# Save combined
filtered.to_csv(OUT_ALL, index=False, encoding='utf-8')

# Breakdown by subreddit
bd = (
    filtered.assign(_is_dhaka=is_dhaka_sub)
    .groupby('subreddit')
    .size()
    .reset_index(name='posts')
    .sort_values('posts', ascending=False)
)
bd.to_csv(OUT_BREAKDOWN, index=False, encoding='utf-8')

print(f"\n✓ Saved combined to: {OUT_ALL}")
print(f"✓ Saved breakdown to: {OUT_BREAKDOWN}")

# Sample preview
print('\nSample (first 10):')
cols = ['subreddit','upvotes','comments','date','title']
cols = [c for c in cols if c in filtered.columns]
print(filtered[cols].head(10).to_string(index=False))
