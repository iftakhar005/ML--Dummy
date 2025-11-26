import json

# 1. Define your file names
file1_name = 'dhaka_extended_posts.json'
file2_name = 'combined_dhaka_posts.json'
output_file_name = 'final_dhaka_dataset.json'

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

# 2. Load the data
print("Loading datasets...")
data1 = load_json(file1_name)
data2 = load_json(file2_name)

# 3. Combine the lists
combined_raw = data1 + data2
print(f"Total posts loaded: {len(combined_raw)}")

# 4. Remove duplicates based on 'url'
# We use a dictionary because keys must be unique. 
# If a URL repeats, the new post will just overwrite the old one, automatically removing duplicates.
unique_posts_dict = {}

for post in combined_raw:
    if 'url' in post:
        unique_posts_dict[post['url']] = post

# Convert back to a list
final_clean_data = list(unique_posts_dict.values())

# 5. Save the clean data
with open(output_file_name, 'w', encoding='utf-8') as f:
    json.dump(final_clean_data, f, indent=4, ensure_ascii=False)

# 6. Print stats
duplicates_removed = len(combined_raw) - len(final_clean_data)
print("-" * 30)
print(f"Successfully saved to: {output_file_name}")
print(f"Final unique post count: {len(final_clean_data)}")
print(f"Duplicates removed: {duplicates_removed}")