import streamlit as st
from main import amazon_main
import altair as alt


class AmazonUI:
    def __init__(self, url):
        """
        Initialize the AmazonUI class with the given URL.
        
        Args:
            url (str): The Amazon product URL.
        """
        self.url = url

    def display_amazon_details(self, details):
        """
        Display the details of the Amazon product with the image on the left 
        and the product information (title, rating, price) on the right.

        Args:
            details (dict): A dictionary containing product details, including
                            title, image URL, rating, and price.
        """
        if details:
            # Create two columns: one for the image and one for the details
            col1, col2 = st.columns([1, 2])  # Adjust column widths as needed
            
            with col1:
                # Display the product image
                st.image(details['img'], width=400)

            with col2:
                # Display product details
                st.markdown(f"### [**{details['title']}**]({self.url})")
                st.write(f"**Rating:** {details['rating']}")
                st.write(f"**Price:** {details['price']}")
        else:
            st.error("No product details available.")


    def display_sentiment_analysis(self):
        """
        Display the sentiment analysis results as a bar chart or show a processing message while scraping.
        """
        # Display the processing message and spinner while sentiment data is being fetched
        with st.spinner('Processing reviews... Please wait.'):
            url_type, sentiment_data = amazon_main()  # Assuming this function fetches the sentiment data
            
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

