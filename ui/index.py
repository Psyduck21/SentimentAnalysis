import streamlit as st
from streamlit_option_menu import option_menu
from url_details import fetch_amazon_product_details, fetch_youtube_video_details
from .amazon_ui import AmazonUI
from .youtube_ui import YoutubeUI
from main import remove_files, match_url


def home():
    # Render the navigation menu
    selected = option_menu(
        menu_title=None,
        # menu_icon="menu-up",
        options=['YouTube','Amazon', 'About', 'Contact'],
        icons=["youtube","amazon", "info-circle", "envelope"],
        default_index=0,
        orientation="horizontal",
    )

    # Amazon Section
    if selected == 'Amazon':
        st.title("Amazon Product Reviews Analysis")
        st.subheader("Enter Your URL")
        input_url = st.text_input(label="Enter your Amazon URL", value="", label_visibility="collapsed")

        with open("./textfiles/url.txt", "w") as f:
            f.write(input_url)
        if input_url:
            if st.button('Process'):
                if match_url(input_url) == "Amazon":
                    details = fetch_amazon_product_details(input_url)
                    amazon_ui = AmazonUI(input_url)
                    amazon_ui.display_amazon_details(details)
                    st.write("---")
                    amazon_ui.display_sentiment_analysis()
                else:
                    st.write("**INVALID URL** : Please enter the amazon url")

            # Clear Button
        if st.button("Clear"):
            remove_files()
            input_url = ""
            st.success("Cleared all temporary files and reset the input area.")

        st.write("---")

    # YouTube Section
    elif selected == 'YouTube':
        st.title("YouTube Video Comment Analysis")
        st.subheader("Enter Your URL")
        input_url = st.text_input(label="Enter your YouTube URL", value="", label_visibility="collapsed")
        with open("./textfiles/url.txt", "w") as f:
            f.write(input_url)
        if input_url:
            if st.button('Process'):
                if match_url(input_url) == "YouTube":
                    details = fetch_youtube_video_details(input_url)
                    youtube_ui = YoutubeUI(input_url)
                    youtube_ui.display_youtube_details(details)
                    youtube_ui.display_sentiment_analysis()
                else:
                    st.write("**INVALID URL** : Please enter the Youtube url")
        # Clear Button
        if st.button("Clear"):
            remove_files()
            input_url = ""
            st.success("Cleared all temporary files and reset the input area.")

        st.write("---")
        
    # About Section
    elif selected == "About":
        st.title("About the App")
        st.write(
            """
            This application provides sentiment analysis for:
            - **Amazon Product Reviews**
            - **YouTube Video Comments**
            """
        )

    # Contact Section
    elif selected == "Contact":
        st.markdown("""
    - **Email**: [📧 akshat.prj@gmail.com](mailto:akshat.prj@gmail.com)
    - **Github**: [🐱 Akshat's GitHub](https://github.com/yourgithubusername)
    - **LinkedIn**: [🔗 Akshat's LinkedIn](https://www.linkedin.com/in/yourlinkedinprofile/)
    """)


