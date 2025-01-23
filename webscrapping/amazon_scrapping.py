import os
import csv
import time
import random
import requests
import json
from bs4 import BeautifulSoup
import re
import logging
from logging.handlers import RotatingFileHandler
from utils.utils import product_details, setup_amazon, read_url

# Create logs directory if it doesn't exist
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Define the log file path
log_file = os.path.join(log_dir, "app_log.log")

# Create a rotating file handler (log rotation after 5MB)
handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=3
)

# Set log format (including timestamp, log level, and message)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Set up logging with the handler
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)  # Log level can be adjusted (e.g., DEBUG, INFO)
logger.addHandler(handler)

# Constants
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
]
STAR_MAP = {
    1: "one_star",
    2: "two_star",
    3: "three_star",
    4: "four_star",
    5: "five_star"
}

# Load cookies from file
with open("./json/cookies.json", "r") as file:
    cookie_dic = json.load(file)
cookies = {cookie["name"]: cookie["value"] for cookie in cookie_dic}

# Save HTML content
def save_html(html_content, folder, filename):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    logger.info(f"Saved HTML content to {file_path}")

# Load HTML files
def load_html(folder):
    html_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    html_files.append(f.read())
    logger.info(f"Loaded {len(html_files)} HTML files from {folder}")
    return html_files

# Fetch and process HTML response
def session_response(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    logger.info(f"Fetching URL: {url}")
    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    if response.status_code == 200:
        logger.info("Successfully fetched the page.")
        return response.text
    else:
        logger.error(f"Failed to fetch page. Status code: {response.status_code}")
        response.raise_for_status()

def writing_csv(reviews, category, csv_file):
    with open(csv_file, "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        for review in reviews:
            writer.writerow([category, review])
    logger.info(f"Saved {len(reviews)} reviews under category {category} to CSV.")

def extracting_total_reviews(soup):
    """
    Extracts the total number of reviews from the given BeautifulSoup object.
    """
    try:
        # Locate the target div using its data-hook attribute
        div_tag = soup.find('div', {'data-hook': 'cr-filter-info-review-rating-count'})
        if div_tag:
            # Extract and clean the text
            raw_text = div_tag.get_text(strip=True)
            logging.info(f"Raw total reviews text: {raw_text}")
            
            # Match and extract review count using regex
            match = re.search(r"(\d[\d,]*)\s+total ratings,.*?(\d[\d,]*)\s+with reviews", raw_text)
            if match:
                total_ratings = int(match.group(1).replace(",", ""))
                reviews_with_text = int(match.group(2).replace(",", ""))
                logging.info(f"Total ratings: {total_ratings}, Reviews with text: {reviews_with_text}")
                return reviews_with_text
        logging.warning("Unable to find the 'cr-filter-info-review-rating-count' div.")
        return -1
    except Exception as e:
        logging.error(f"Error while extracting total reviews: {e}")
        return -1


def fetch_and_save_pages(product_title, product_id, star_type, HTML_FOLDER):
    """
    Fetches and saves pages of reviews for a specific star rating.
    """
    folder = os.path.join(HTML_FOLDER, star_type)
    os.makedirs(folder, exist_ok=True)

    # Fetch the first page to determine total reviews
    first_page_url = (
        f"https://www.amazon.in/{product_title}/product-reviews/{product_id}/"
        f"?ie=UTF8&filterByStar={star_type}&pageNumber=1&reviewerType=all_reviews&pageSize=10&sortBy=recent"
    )
    try:
        response_text = session_response(first_page_url)
        save_html(response_text, folder, "page_1.html")
        logging.info(f"Saved first page HTML for {star_type} reviews.")

        soup = BeautifulSoup(response_text, 'html.parser')
        total_reviews = extracting_total_reviews(soup)
        logging.info(f"Total reviews for {star_type}: {total_reviews}")
        
        if total_reviews == -1:
            logging.warning(f"Failed to determine total reviews for {star_type}. Skipping...")
            return

        total_pages = total_reviews // 10 + (1 if total_reviews % 10 != 0 else 0)
        total_pages = min(total_pages, 10)  # Optional: Limit to 10 pages
        logging.info(f"Total pages for {star_type}: {total_pages}")

        for page_no in range(2, total_pages + 1):
            logging.info(f"Fetching page {page_no} for {star_type} reviews...")
            url = (
                f"https://www.amazon.in/{product_title}/product-reviews/{product_id}/"
                f"?ie=UTF8&filterByStar={star_type}&pageNumber={page_no}&reviewerType=all_reviews&pageSize=10&sortBy=recent"
            )
            response_text = session_response(url)
            save_html(response_text, folder, f"page_{page_no}.html")
            logging.info(f"Saved page {page_no} HTML for {star_type} reviews.")
            time.sleep(random.uniform(1, 3))
    except Exception as e:
        logging.error(f"Error while fetching pages for {star_type}: {e}")

def extract_reviews_from_html(html_content):
    """
    Extracts reviews from HTML content.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        review_spans = soup.find_all("span", {"data-hook": "review-body"})
        reviews = [span.get_text(strip=True) for span in review_spans]
        logging.info(f"Extracted {len(reviews)} reviews from the HTML content.")
        return reviews
    except Exception as e:
        logging.error(f"Error while extracting reviews from HTML: {e}")
        return []
    
# Main scraping process
def amazon_scrapping(product_url):
    """
    Scrapes reviews from the given Amazon product URL. If the folder and CSV file for the product already exist, 
    it loads the saved data instead of fetching it again.
    """
    product_id, product_title = product_details(product_url)
    folder, csv_file = setup_amazon(product_id)
        # Step 1: Save required HTML files
    for star_rating, star_type in STAR_MAP.items():
            logging.info(f"Fetching reviews for {star_type}...")
            fetch_and_save_pages(product_title, product_id, star_type, folder)

    # Step 2: Load saved HTML files and extract reviews
    for star_rating, star_type in STAR_MAP.items():
        logging.info(f"Extracting reviews for {star_type}...")
        folder_path = os.path.join(folder, star_type)
        html_files = load_html(folder_path)
        if not html_files:
            logging.warning(f"No HTML files found in folder {folder_path}. Skipping extraction for {star_type}.")
            continue
        for html in html_files:
            reviews = extract_reviews_from_html(html)
            if reviews:
                writing_csv(reviews, star_type, csv_file)
            else:
                logging.warning(f"No reviews extracted from HTML file in {folder_path}.")
    return product_id, csv_file, folder

# Run the scraper
if __name__ == "__main__":
    product_url = read_url("url.txt")
    amazon_scrapping(product_url)