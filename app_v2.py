import streamlit as st
from datetime import datetime
import urllib.parse
import base64

# Set page config
st.set_page_config(page_title="Fashion Finder v2", layout="centered")

# Initialize session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Title
st.title("🧵 Fashion Finder v2")
st.write("Your AI-powered Knight in Shining Armour 👗")

# User info
st.subheader("🙋 User Profile")
user_name = st.text_input("Your Name")
user_size = st.selectbox("Your Size (EU)", ["32", "34", "36", "38", "40", "42", "44", "46", "48", "50"])

# Upload image
st.subheader("📸 Upload Your Outfit")
uploaded_image = st.file_uploader("Upload image of your dream outfit", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

    # Create reverse search URL (Google Images upload fallback)
    st.markdown("### 🔍 Try Google Reverse Image Search")
    st.markdown("1. Open [Google Images](https://images.google.com/)")
    st.markdown("2. Upload this image to find similar products.")

    # Collect product name
    st.subheader("📝 Product Info")
    product_name = st.text_input("Product Name or Brand (if known)")

    st.subheader("💰 Found a Match?")
    with st.form("match_form"):
        match_title = st.text_input("Matching Product Title")
        match_price = st.text_input("Price (€)")
        match_store = st.text_input("Store / Website")
        match_link = st.text_input("Buy Link (URL)")
        submitted = st.form_submit_button("💾 Save This Match")

        if submitted:
            match_record = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "user": user_name,
                "size": user_size,
                "item": product_name or "N/A",
                "match": match_title,
                "price": match_price,
                "store": match_store,
                "link": match_link
            }
            st.session_state.search_history.append(match_record)
            st.success("✅ Match saved!")

# View history
if st.session_state.search_history:
    st.subheader("📜 Search History (Session)")
    for entry in st.session_state.search_history:
        st.markdown(f"**🧍 {entry['user']} (Size {entry['size']})** searched *{entry['item']}*")
        st.markdown(f"➡️ Match: **{entry['match']}** for {entry['price']} at [{entry['store']}]({entry['link']})")
        st.markdown("---")
