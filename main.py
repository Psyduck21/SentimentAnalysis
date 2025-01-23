import os
import shutil
import re
import pandas as pd
import logging
from utils.utils import read_url, video_details
from webscrapping.youtube_scrapping import youtube_scarpping
from webscrapping.amazon_scrapping import amazon_scrapping
from standardizing_data import normalize_comments, normalize_reviews
from logging.handlers import RotatingFileHandler
import warnings
warnings.filterwarnings("ignore")

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


def match_url(url):
    """
    Matches a given URL to determine if it's a YouTube or Amazon URL.
    
    Args:
        url (str): The URL to validate.

    Returns:
        str: The type of URL ('YouTube', 'Amazon', or 'Invalid').
    """
    youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)(/.*)?$"
    amazon_pattern = r"^(https?://)?(www\.)?amazon\.(com|in|co\.[a-z]{2})(/.*)?$"

    logger.info(f"Matching URL: {url}")
    if re.match(youtube_pattern, url, re.IGNORECASE):
        logger.info("URL matched: YouTube")
        return "YouTube"
    elif re.match(amazon_pattern, url, re.IGNORECASE):
        logger.info("URL matched: Amazon")
        return "Amazon"
    else:
        logger.warning(f"Invalid URL: {url}")
        return "Invalid"




def amazon_main():
    url = read_url("./textfiles/url.txt")  # Read the URL from the file
    url_type = match_url(url)  # Determine URL type
    # Folder path based on URL type
    folder_name = None
    if url_type == "Amazon":
        PRODUCT_ID, FILENAME, FOLDER = amazon_scrapping(url)
        with open("./textfiles/id.txt" , "w") as f:
            f.write(PRODUCT_ID)
        df = pd.read_csv(FILENAME)
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
        logging.info(df.head())
        sentiment_count = normalize_reviews(df)
        result = "Amazon", sentiment_count
        return result
    else:
        raise ValueError("Inavlid Url . Please enter a Valid Amazon url")

def yotutbe_main():
    url = read_url("./textfiles/url.txt")  # Read the URL from the file
    url_type = match_url(url)
    if url_type == "YouTube":
        VIDEOID,FILENAME, FOLDER = youtube_scarpping(url)
        df = pd.read_csv(FILENAME)
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
        logging.info(df.head())
        sentiment_count = normalize_comments(df)
        result = "YouTube", sentiment_count
    else:
        raise ValueError("Invalid URL. Please provide a valid YouTube URL.")
    
    return result

def remove_files():
    with open("./textfiles/id.txt", "r") as file:
        fid = file.read().strip()
    FOLDER = f"./webscrapping/{fid}"
    # Delete folder after analysis
    if FOLDER and os.path.exists(FOLDER):
        try:
            shutil.rmtree(FOLDER)  # Removes the folder and all its contents
            logger.info(f"Folder {FOLDER} has been deleted.")
        except Exception as e:
            logger.info(f"Error deleting folder {FOLDER}: {e}")
    else:
        print(f"can't find {FOLDER}")
    
    # Clear URL from file
    try:
        with open("./textfiles/url.txt", "w") as u:
            u.write("")  # Clear the content of the file
        with open("./textfiles/id.txt", "w") as file:
            file.write("")
        logger.info("URL has been cleared from the text file.")
    except Exception as e:
        logger.info(f"Error clearing URL from file: {e}")

    file_img = f"./images/{fid}_image.jpg"
    if os.path.exists(file_img):
            try:
                os.remove(file_img)
                logging.info("image file removed")
            except Exception as e:
                logging.error(f"Error deleting file {file_img}")
    files_to_delete = ["reviews.csv", "comments.csv"]
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                logging.info(f"File {file} has been deleted.")
            except Exception as e:
                logging.error(f"Error deleting file {file}: {e}")