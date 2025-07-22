import streamlit as st
import requests
from PIL import Image
import io
from datetime import datetime
import pandas as pd
import os

# --- Utility Function to Log Search ---
def log_search_history(user_name, size, search_query, num_results, results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = "search_history.csv"
    top_results = "; ".join([f"{r['title']} ({r['link']})" for r in results[:3]])
    entry = {
        "Timestamp": timestamp,
        "User Name": user_name,
        "Size": size,
        "Search Query": search_query,
        "Results Found": num_results,
        "Top Results": top_results
    }
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    else:
        df = pd.DataFrame([entry])
    df.to_csv(filename, index=False)

# --- Google Search API Settings ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# --- Google Image Search ---
def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}&searchType=image"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        return results
    return []

# --- Streamlit UI ---
st.title("👗 Fashion Finder v3.1")
st.markdown("Find your dream outfit at the right price, size, and store!")

# --- User Inputs ---
user_name = st.text_input("Your Name", key="user_name")
size = st.text_input("Your Size (EU)", key="user_size")
uploaded_image = st.file_uploader("Upload an image of the product", type=["jpg", "jpeg", "png"])
keywords = st.text_input("Enter brand/product keywords (e.g., Zara floral red dress)")

if st.button("Search"):
    if uploaded_image and keywords:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        with st.spinner("Searching the web..."):
            search_results = google_search(keywords)
            if search_results:
                links_table = []
                for item in search_results:
                    title = item.get("title", "No Title")
                    link = item.get("link", "")
                    display_link = f"[Link]({link})"
                    links_table.append({
                        "Match Type": "Approximate",
                        "Title": title,
                        "Product Link": display_link,
                        "Price": "❓",
                        "Sizes Available": "❓"
                    })

                df = pd.DataFrame(links_table)
                st.markdown("### Top Matches Found:")
                st.write(df.to_markdown(index=False), unsafe_allow_html=True)

                # Save search history
                log_search_history(user_name, size, keywords, len(search_results), search_results)
            else:
                st.warning("No results found.")
    else:
        st.error("Please upload an image and enter keywords.")

# --- Option to View Recent History ---
if st.checkbox("Show My Last 3 Searches"):
    if os.path.exists("search_history.csv"):
        df = pd.read_csv("search_history.csv")
        user_df = df[df["User Name"] == user_name].tail(3)
        st.dataframe(user_df)
    else:
        st.info("No search history found.")
