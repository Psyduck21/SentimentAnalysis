import re
import os
import csv

def read_url(file_path):
    """
    Reads the product URL from a file and returns it.
    """
    with open(file_path, "r") as file:
        product_url = file.read().strip()
    return product_url

def product_details(url):
    title_pattern = r"amazon\.in/([^/]+)/dp/"
    product_id_pattern = r"/dp/([A-Z0-9]+)"

    title_match = re.search(title_pattern, url)
    product_id_match = re.search(product_id_pattern, url)

    product_title = title_match.group(1) if title_match else None
    product_id = product_id_match.group(1) if product_id_match else None

    if not product_title or not product_id:
        print("Unable to extract product details from the URL.")
        raise ValueError("Invalid product URL.")
    
    print(f"Extracted Product ID: {product_id}, Product Title: {product_title}")
    return product_id, product_title

# Ensure the folder and CSV file exist
def setup_amazon(product_id):
    folder = f"./webscrapping/{product_id}"
    csv_file = os.path.join(folder, f"reviews_{product_id}.csv")
    os.makedirs(folder, exist_ok=True)
    with open("./textfiles/id.txt", "w") as f:
        f.write(product_id)
    if not os.path.exists(csv_file):
        print(f"Creating new CSV file: {csv_file}")
        with open(csv_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["category", "review"])  # Write header
    else:
        print(f"CSV file already exists: {csv_file}")
    return folder, csv_file

def video_details(url):
    video_id_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:&|\/|$)"
    
    video_id_match = re.search(video_id_pattern, url)

    video_id = video_id_match.group(1) if video_id_match else None

    if not video_id:
        print("Unable to extract product details from the URL.")
        raise ValueError("Invalid product URL.")
    
    print(f"Extracted Video ID: {video_id}")
    return video_id

def setup_youtube(video_id):
    folder = f"./webscrapping/{video_id}"
    csv_file = os.path.join(folder, f"comment_{video_id}.csv")
    os.makedirs(folder, exist_ok=True)
    with open("./textfiles/id.txt", "w") as f:
        f.write(video_id)
    if not os.path.exists(csv_file):
        print(f"Creating new CSV file: {csv_file}")
        with open(csv_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["published", "text"])
    else:
        print(f"CSV file already exists: {csv_file}")
    return folder, csv_file
if __name__ == "__main__":
    ...