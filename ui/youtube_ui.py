import streamlit as st
from main import yotutbe_main
import altair as alt


class YoutubeUI:
    def __init__(self, url):
        """
        Initialize the AmazonUI class with the given URL.
        
        Args:
            url (str): The Amazon product URL.
        """
        self.url = url

    def display_youtube_details(self,video_details):
        """
        Display YouTube video details with thumbnail on the right and details on the left.
        """
        # Extract video details
        video_title = video_details.get("video_title", "N/A")
        video_link = video_details.get("video_link", "#")
        channel_title = video_details.get("channel_title", "N/A")
        channel_link = video_details.get("channel_link", "#")
        total_views = video_details.get("total_views", "0")
        total_comments = video_details.get("total_comments", "0")
        thumbnail_url = video_details.get("thumbnail_url", "")

        # Streamlit layout
        st.markdown("### YouTube Video Details")

        # Use Streamlit columns for layout
        col1, col2 = st.columns([1, 3])  # 3:2 width ratio

        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, caption="Thumbnail", use_container_width =True)
            else:
                st.write("No Thumbnail Available")
        with col2:
            st.markdown(f"### [{video_title}]({video_link})")
            st.markdown(f"**Channel:** [{channel_title}]({channel_link})")
            st.markdown(f"**Views:** {total_views}")
            st.markdown(f"**Comments:** {total_comments}")



    def display_sentiment_analysis(self):
        """
        Display the sentiment analysis results as a bar chart or show a processing message while scraping.
        """
        # Display the processing message and spinner while sentiment data is being fetched
        with st.spinner('Processing reviews... Please wait.'):
            url_type, sentiment_data = yotutbe_main()  # Assuming this function fetches the sentiment data
            
        # Once data is available, display the chart
        if sentiment_data is not None:
            st.write("---")
            chart = (
                alt.Chart(sentiment_data)
                .mark_bar()
                .encode(
                    x=alt.X('Sentiment_Label:N', title='Sentiment', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('Count:Q', title='Number of Reviews/Comments'),
                    color='Sentiment_Label:N',
                    tooltip=['Sentiment_Label', 'Count'],
                )
                .properties(width=600, height=400)
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.error("No sentiment data available.")

