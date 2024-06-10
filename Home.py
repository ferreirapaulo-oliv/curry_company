import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="📠",
    layout = 'wide'
)

#Image_path = 'C:\\Users\\User\\Documents\\repos\\ftc_python\\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width = 100)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown(' ## Fastest and Best Delivery in Town')
st.sidebar.markdown("""---""")

st.write("Cury Company Growth Dashboard")

st.markdown("""
            The Growth Dashboard was built to track delivery driver's and restaurant's metrics.
            ## How to use this Growth Dashboard?

            - Company View:
                - Managerial View: General behavior metrics
                - Tactical View: Weekly growth indicators
                - Geographical View: Geolocation insights
            - Delivery View:
                - Weekly growth monitoring
            - Restaurant View:
                - Weekly growth indicators for restaurants
            ### Ask for help
                - Email: ferreirapaulo.oliv@gmail.com
                - Discord: @itscape
            """)