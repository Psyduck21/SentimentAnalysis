import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from googletrans import Translator
from textblob import TextBlob
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from joblib import load
import logging
from logging.handlers import RotatingFileHandler
import warnings
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
import re

warnings.filterwarnings("ignore")

# Constants for sentiment analysis model and vectorizer
MODEL_PATH = "./model/sentiment_analysis.pkl"
VECTORIZER_PATH = "./model/countvectorizer.pkl"
LABEL_MAP = {0: "Negative", 2: "Positive"}

# Initialize Google Translator and AI4Bharat transliterator
translator = Translator()
# transliterator = XlitEngine("hi")

# Set up logging with rotation
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app_log.log")

handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Load sentiment analysis model and vectorizer
MODEL = load(MODEL_PATH)
VECTORIZER = load(VECTORIZER_PATH)

# Download stopwords
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """Remove digits, emojis, and extra characters from text."""
    text = re.sub(r'\d+', '', text)
    text = re.sub(
        "["  # Remove emojis
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002500-\U00002BEF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", '', text, flags=re.UNICODE)
    text = re.sub(r'[^\w\s]', '', text)  # Remove special symbols
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text


def transliterate_and_translate(text):
    """Transliterate text using Indic Transliterate and translate it to English."""
    try:
        # Detect the language of the input text
        detected_lang = GoogleTranslator(source='auto', target='en').detect(text)
        logger.info(f"Detected Language: {detected_lang}")
        
        if detected_lang != "en":
            # Transliterate the text if it's in Hindi or similar languages
            if detected_lang in ["hi", "mr", "bn", "gu", "ta", "te", "kn", "ml", "pa"]:
                transliterated = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
            else:
                transliterated = text  # No transliteration for unsupported languages

            # Translate the transliterated text to English
            translated_text = GoogleTranslator(source=detected_lang, target="en").translate(transliterated)
            return translated_text
        
        # If the text is already in English, return it as is
        return text

    except Exception as e:
        logger.error(f"Error during transliteration/translation: {e}", exc_info=True)
        return text  # Fallback to the original text


def process_text(text):
    """Remove stop words and correct spelling."""
    filtered_words = [word for word in text.split() if word.lower() not in stop_words]
    filtered_text = " ".join(filtered_words)
    blob = TextBlob(filtered_text)
    corrected_text = str(blob.correct())
    return corrected_text


# def batch_process(data, func, batch_size=100):
#     """Process data in batches for efficiency."""
#     results = []
#     for i in range(0, len(data), batch_size):
#         batch = data[i:i + batch_size]
#         with ThreadPoolExecutor() as executor:
#             batch_results = list(executor.map(func, batch))
#         results.extend(batch_results)
#     return results


def normalize_dataframe(dataframe, text_column, output_file):
    """Normalize a dataframe including text cleaning, transliteration, and translation."""
    try:
        logger.info(f"Starting normalization for {text_column}")
        dataframe = dataframe.sample(frac=1, random_state=42).reset_index(drop=True)
        print("Cleaning the text")
        dataframe[text_column] = dataframe[text_column].apply(clean_text)
        # dataframe[text_column] = batch_process(dataframe[text_column], transliterate_and_translate)
        # dataframe[text_column] = batch_process(dataframe[text_column], process_text)
        dataframe = dataframe[dataframe[text_column] != '']
        print("Transliterating and translating the text")
        dataframe[text_column] = dataframe[text_column].apply(transliterate_and_translate)
        # logging.info("Cleaning the text")
        dataframe[text_column] = dataframe[text_column].apply(process_text)
        dataframe.dropna(subset=[text_column], inplace=True)
        dataframe.to_csv(output_file, index=False)
        logger.info(f"Processing completed! File saved as '{output_file}'.")
    except Exception as e:
        logger.error(f"An error occurred during normalization: {e}")
        raise RuntimeError(f"An error occurred: {e}")


def predict_input_text(input_text):
    """Predict sentiment for input text."""
    try:
        input_vector = VECTORIZER.transform([input_text])
        prediction = MODEL.predict(input_vector)
        logger.info(f"Predicted sentiment: {LABEL_MAP.get(prediction[0], 'Unknown')}")
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during sentiment prediction: {e}")
        return -1  # Fallback for errors


def normalize_reviews(dataframe):
    """Normalize reviews and predict sentiments."""
    normalize_dataframe(dataframe, text_column='review', output_file='reviews.csv')
    df = pd.read_csv("reviews.csv")
    df.dropna(inplace=True)
    # df['Sentiment'] = batch_process(df['review'], predict_input_text)
    df['Sentiment'] = df['review'].apply(predict_input_text)
    df['Sentiment_Label'] = df['Sentiment'].map(LABEL_MAP)
    sentiment_counts = df['Sentiment_Label'].value_counts()
    return sentiment_counts.reset_index(name="Count").rename(columns={"index": "Sentiment"})


def normalize_comments(dataframe):
    """Normalize YouTube comments and predict sentiments."""
    normalize_dataframe(dataframe, text_column='text', output_file='comments.csv')
    df = pd.read_csv("comments.csv")
    df.dropna(inplace=True)
    # df['Sentiment'] = batch_process(df['text'], predict_input_text)
    df['Sentiment'] = df['text'].apply(predict_input_text)
    df['Sentiment_Label'] = df['Sentiment'].map(LABEL_MAP)
    sentiment_counts = df['Sentiment_Label'].value_counts()
    return sentiment_counts.reset_index(name="Count").rename(columns={"index": "Sentiment"})
