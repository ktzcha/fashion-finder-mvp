import streamlit as st
import requests
import json
from io import BytesIO
from PIL import Image

# --- CONFIG ---
GOOGLE_API_KEY = "AIzaSyAHsTjNeUH_PzRmuwxoF2eW0wFjqIBf0Uk"
GOOGLE_CX = "60fb72f0c109b47ea"  # You need this from your Google CSE setup

# --- STREAMLIT SETUP ---
st.set_page_config("Fashion Finder v3 (Google Only)", layout="wide")
st.title("👗 Fashion Finder v3 - Google Image Search Only")

# --- USER UPLOAD ---
uploaded_img = st.file_uploader("Upload an image of the product you want to find", type=["jpg", "jpeg", "png"])

if uploaded_img:
    st.image(uploaded_img, use_container_width=True, caption="Your Uploaded Image")

    # --- PREP IMAGE FOR SEARCH ---
    st.info("Searching similar images on Google...")

    # NOTE: Google Custom Search API does NOT accept direct image uploads.
    # So we simulate a visual search by using placeholder keywords. We will replace this with Perplexity-style logic later.

    # For now, simulate image-based search with a fixed keyword (or let user input it)
    query = st.text_input("Optional: Type keywords related to the image (brand, type, color)", value="dress fashion", help="Since Google Custom Search can't do direct image uploads, we use keywords for now.")
    if query:
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "searchType": "image",
            "q": query,
            "num": 10
        }
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)

        if response.status_code == 200:
            data = response.json()
            results = []

            for item in data.get("items", []):
                results.append({
                    "Match Type": "Google Image",
                    "Price": "N/A",
                    "Sizes": "N/A",
                    "Product Link": item["link"]
                })

            if results:
                st.success(f"Found {len(results)} visually similar results!")
                st.dataframe(results)
            else:
                st.warning("No results found.")
        else:
            st.error(f"Search failed. Error code: {response.status_code}")
