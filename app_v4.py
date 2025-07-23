import streamlit as st
import requests
from PIL import Image
import io
import base64

# Session State Initialization
if "name" not in st.session_state:
    st.session_state.name = ""
if "size" not in st.session_state:
    st.session_state.size = ""

st.set_page_config(page_title="Fashion Finder V4", layout="centered")
st.title("🧥 Fashion Finder V4")
st.write("Upload a fashion item and we’ll help you find it at a better price or in your size.")

# Input: User Info (once per session)
with st.expander("👤 Your Info"):
    st.session_state.name = st.text_input("Your Name", value=st.session_state.name)
    st.session_state.size = st.text_input("Your Size (EU)", value=st.session_state.size)

# Upload Image
uploaded_file = st.file_uploader("Upload an image of the dress", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    st.write("🔍 Searching visually similar items...")

    # Encode image to base64
    buffered = io.BytesIO()
    image_rgb = image.convert("RGB")
    image_rgb.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    API_KEY = st.secrets["GOOGLE_API_KEY"]
    CSE_ID = st.secrets["CSE_ID"]
    SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "searchType": "image",
        "q": "fashion outfit",  # Can be replaced with more dynamic values in later versions
    }
    response = requests.get(SEARCH_URL, params=params)
    results = response.json()

    if "items" in results:
        table = []
        for item in results["items"]:
            table.append({
                "Match": "Approximate",
                "Price": "N/A",  # Price scraping placeholder
                "Sizes": "N/A",  # Size scraping placeholder
                "Link": f"[View Product]({item['link']})"
            })
        st.write("🎯 Found the following similar items:")
        st.write(f"Your size: {st.session_state.size}")
        st.markdown("Click links to check product details:")
        st.write(" ")
        st.dataframe(table, use_container_width=True)
    else:
        st.warning("No similar items found. Try another image.")
else:
    st.info("Please upload an image to begin search.")
