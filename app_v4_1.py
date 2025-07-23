import streamlit as st
import requests
from urllib.parse import quote_plus
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Fashion Finder v4.1", layout="wide")
st.title("👗 FashionFinder v4.1")

# --- User Input ---
st.markdown("### Enter Product Details")
user_name = st.text_input("Your Name")
product_name = st.text_input("Product Name or Keywords (e.g., 'Zara green summer dress')")
product_link = st.text_input("(Optional) Product Link from Zalando")
preferred_size = st.selectbox("Preferred Size", options=["", "XS", "S", "M", "L", "XL", "XXL"])
st.divider()

# --- Google Search Config ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# --- Search Trigger ---
if st.button("🔍 Find Alternatives"):
    if not product_name:
        st.warning("Please enter a product name or keyword to search.")
    else:
        query = quote_plus(product_name + " buy online")
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])

            if not items:
                st.info("No search results found. Try different keywords.")
            else:
                results = []
                for item in items:
                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")

                    # Basic logic to detect EU relevance (this can be improved)
                    is_eu = any(domain in link for domain in [".nl", ".de", ".fr", ".eu", ".be", ".es", ".it"]) or "EUR" in snippet

                    results.append({
                        "Match Type": "Approximate",
                        "Title": title,
                        "Link": link,
                        "Snippet": snippet,
                        "EU Based?": "Yes" if is_eu else "No"
                    })

                df = pd.DataFrame(results)
                st.success("Search complete! Displaying top results below:")

                def make_clickable(val):
                    return f'<a href="{val}" target="_blank">Link</a>'

                df_display = df.copy()
                df_display["Link"] = df_display["Link"].apply(make_clickable)
                st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

                # Save session history locally
                history_row = {
                    "User": user_name,
                    "Product Name": product_name,
                    "Zalando Link": product_link,
                    "Preferred Size": preferred_size,
                    "Results Count": len(df),
                }
                try:
                    existing = pd.read_csv("history.csv")
                    existing = pd.concat([existing, pd.DataFrame([history_row])], ignore_index=True)
                    existing.to_csv("history.csv", index=False)
                except FileNotFoundError:
                    pd.DataFrame([history_row]).to_csv("history.csv", index=False)

                st.toast("Search session saved to local history ✅")
        else:
            st.error(f"Google API Error: {response.status_code}")
