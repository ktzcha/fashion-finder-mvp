import streamlit as st
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Fashion Finder", layout="centered")

st.title("👗 Visual Fashion Finder MVP")
st.write("Upload an image of the fashion item you're searching for. We’ll help you search similar items.")

# Image upload
uploaded_image = st.file_uploader("📷 Upload image of outfit or product", type=["jpg", "jpeg", "png"])

if uploaded_image:
    # Show the uploaded image
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    
    # Ask user to enter optional title
    product_title = st.text_input("📝 Optional: Enter product name or brand (if known)")

    # Save image details (mock)
    st.success("Image received! Now searching...")

    # Generate Google Lens / image search link
    st.markdown("### 🔍 Try visual search via Google:")
    st.markdown("1. Open [Google Images](https://images.google.com/)")
    st.markdown("2. Upload this image and check matching results.")

    st.markdown("---")
    st.subheader("🛍️ Manual Match Results (paste your own below)")
    
    with st.form("results_form"):
        match_title = st.text_input("Matching Product Title")
        match_price = st.text_input("Price (e.g. €49.99)")
        match_store = st.text_input("Store / Website")
        match_link = st.text_input("Buy Link (URL)")
        submitted = st.form_submit_button("Save")

        if submitted:
            st.success("✅ Match saved! (in memory only for now)")
            st.markdown(f"**🛍️ {match_title}** - {match_price} from [{match_store}]({match_link})")

