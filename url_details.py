import requests
import random
import json
from bs4 import BeautifulSoup
import os
from utils.utils import product_details, video_details
from googleapiclient.discovery import build



USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
]

with open("./json/cookies.json", "r") as file:
    cookie_dic = json.load(file)
cookies = {cookie["name"]: cookie["value"] for cookie in cookie_dic}

with open("./json/credentials.json", "r") as f:
    data = json.load(f)
    API_KEY = data['api_key']
    
def session_response(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    if response.status_code == 200:
        print("Successfully fetched the page.")
        return response.text
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        response.raise_for_status()


def fetch_amazon_product_details(url):
    response = session_response(url)

    soup = BeautifulSoup(response, "html.parser")
    pid, ptitle = product_details(url)
    symbol = soup.find('span', class_="a-price-symbol")
    value = soup.find('span', class_="a-price-whole")
    price = symbol.text + value.text
    rating = soup.find('span', class_="a-size-small a-color-base")
    rating = rating.text
    img_divs = soup.find('div', class_="imgTagWrapper")
    img_tag = img_divs.find("img")
    if img_tag and img_tag.get("src"):  # Ensure 'img' tag and 'src' exist
        img_url = img_tag["src"]

        # Download the image
        img_data = requests.get(img_url).content
        img_path = os.path.join("./images", f"{pid}_image.jpg")

        # Save the image locally
        with open(img_path, "wb") as f:
            f.write(img_data)

    return {
        "title" : ptitle,
        "rating": rating,
        "price" : price,
        "img" : img_path
        }

def fetch_youtube_video_details(url):
    """Fetch YouTube video details along with channel icon using YouTube Data API v3."""
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        video_id = video_details(url)
        # Fetch video details
        video_response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
        if not video_response["items"]:
            return {"error": f"No video found for ID: {video_id}"}

        video_data = video_response["items"][0]
        snippet = video_data["snippet"]
        stats = video_data.get("statistics", {})
        channel_id = snippet.get("channelId", "")

        # Fetch channel details for the icon
        channel_response = youtube.channels().list(part="snippet", id=channel_id).execute()
        if not channel_response["items"]:
            return {"error": f"No channel found for ID: {channel_id}"}
        
        channel_data = channel_response["items"][0]["snippet"]
        channel_icon = channel_data.get("thumbnails", {}).get("default", {}).get("url", "")

        return {
            "video_title": snippet.get("title", "N/A"),
            "video_link": f"https://www.youtube.com/watch?v={video_id}",
            "channel_title": snippet.get("channelTitle", "N/A"),
            "channel_link": f"https://www.youtube.com/channel/{channel_id}",
            "total_views": stats.get("viewCount", "0"),
            "total_comments": stats.get("commentCount", "0"),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "channel_icon": channel_icon,
        }
    except Exception as e:
        return {"error": str(e)}


# VIDEO_ID = video_details("https://www.youtube.com/watch?v=Fs4vYQRK0U8")
# details = fetch_youtube_video_details(video_id=VIDEO_ID, api_key=API_KEY)
# print(details)