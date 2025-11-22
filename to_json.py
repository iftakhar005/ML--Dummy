import json

def analyze_and_merge(file1_path, file2_path, output_path):
    print(f"--- Starting Process ---")
    
    # 1. Load the first file (Older data)
    try:
        with open(file1_path, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
            print(f"Loaded {file1_path}: {len(data1)} records")
    except Exception as e:
        print(f"Error loading {file1_path}: {e}")
        data1 = []

    # 2. Load the second file (Newer data)
    try:
        with open(file2_path, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
            print(f"Loaded {file2_path}: {len(data2)} records")
    except Exception as e:
        print(f"Error loading {file2_path}: {e}")
        data2 = []

    # 3. Merge and Deduplicate
    # We use a dictionary keyed by 'url' to ensure uniqueness.
    unique_posts = {}
    
    # Add entries from File 1
    for post in data1:
        if 'url' in post:
            unique_posts[post['url']] = post
            
    # Add entries from File 2
    # This will overwrite entries from File 1 if they share the same URL,
    # effectively updating them with the newer data.
    duplicates_count = 0
    new_count = 0
    for post in data2:
        if 'url' in post:
            if post['url'] in unique_posts:
                duplicates_count += 1
                unique_posts[post['url']] = post # Update with newer version
            else:
                new_count += 1
                unique_posts[post['url']] = post

    # Convert back to a list
    combined_list = list(unique_posts.values())

    # 4. Stats and Save
    print(f"\n--- Merge Analysis ---")
    print(f"Duplicates consolidated: {duplicates_count}")
    print(f"New unique posts added: {new_count}")
    print(f"Total combined posts: {len(combined_list)}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_list, f, indent=4, ensure_ascii=False)
    
    print(f"\nSuccessfully saved to: {output_path}")

if __name__ == "__main__":
    analyze_and_merge('reddit_data.json', 'reddit_data_dhaka.json', 'combined_dhaka_posts.json')