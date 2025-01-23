import streamlit as st
from ui.index import home
from main import remove_files

# Set up page configuration
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="🔍",
    layout="wide",
)

# Run the main app
if __name__ == "__main__":
    home()

