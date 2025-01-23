from googleapiclient.discovery import build
import json
import csv
from utils.utils import setup_youtube, video_details

# Load API key from credentials.json
with open("./json/credentials.json", "r") as file:
    key = json.load(file)
API_KEY = key["api_key"]

def get_all_comments(video_id, api_key):
    # Build YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Initialize variables
    all_comments = []
    next_page_token = None

    # Fetch top-level comments and their replies
    while True:
        try:
            # Fetch comment threads
            comment_thread_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=next_page_token,
                maxResults=100,
            )
            comment_thread_response = comment_thread_request.execute()

            # Extract comments
            for item in comment_thread_response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                all_comments.append({
                    "published_at": top_comment["publishedAt"],
                    "text": top_comment["textOriginal"]
                })

            # Check for more pages of comments
            next_page_token = comment_thread_response.get("nextPageToken")
            if not next_page_token:
                break  # Exit loop if no more pages

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return all_comments

def youtube_scarpping(video_url):
    """
    Scrapes comments from a YouTube video and saves them to a CSV file.

    Args:
        video_url (str): The YouTube video URL.

    Returns:
        str: The filename of the saved CSV file.
    """
    VIDEO_ID = video_details(video_url)  # Extract video ID
    FOLDER, FILENAME = setup_youtube(VIDEO_ID)  # Folder and filename setup
    comments = get_all_comments(VIDEO_ID, API_KEY)  # Fetch comments

    # Write comments to CSV
    with open(FILENAME, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["published_at", "text"])
        writer.writeheader()
        writer.writerows(comments)

    print(f"Saved {len(comments)} comments to {FILENAME}.")
    return VIDEO_ID,FILENAME,FOLDER
