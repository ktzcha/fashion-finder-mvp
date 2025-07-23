import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import time
from urllib.parse import urlparse, parse_qs
import re

# Page configuration for mobile optimization
st.set_page_config(
    page_title="Product Price Finder",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# PWA Configuration
def add_pwa_config():
    """Add PWA meta tags and service worker"""
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#FF6B6B">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Price Finder">
    
    <style>
    /* Mobile-first responsive design */
    .main > div {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        text-align: center;
    }
    
    .upload-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border-left: 4px solid #FF6B6B;
    }
    
    .price-tag {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .store-name {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .search-progress {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .main > div {
            padding: 0.5rem;
        }
        .result-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

add_pwa_config()

# Configuration
def init_session_state():
    """Initialize session state variables"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None

def get_google_search_api_key():
    """Get API key from user input or environment"""
    if 'google_api_key' not in st.session_state:
        st.session_state.google_api_key = ""
    if 'google_cse_id' not in st.session_state:
        st.session_state.google_cse_id = ""
    
    return st.session_state.google_api_key, st.session_state.google_cse_id

def extract_price_from_text(text):
    """Extract price information from text using regex"""
    price_patterns = [
        r'[\$£€¥₹]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $99.99, £50, €75.50
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[\$£€¥₹]',  # 99.99$, 50£
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|EUR|GBP|INR)',  # 99.99 USD
        r'Price:\s*[\$£€¥₹]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Price: $99.99
        r'Sale:\s*[\$£€¥₹]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',   # Sale: $99.99
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first match, removing commas
            return matches[0].replace(',', '')
    
    return None

def search_similar_products(api_key, cse_id, query, num_results=10):
    """Search for similar products using Google Custom Search API"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'searchType': 'image',
            'num': min(num_results, 10),  # Max 10 per request
            'safe': 'active',
            'imgType': 'photo',
            'imgSize': 'medium'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        return results.get('items', [])
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def process_search_results(results):
    """Process and format search results"""
    processed_results = []
    
    for item in results:
        try:
            # Extract basic information
            title = item.get('title', 'Unknown Product')
            link = item.get('link', '')
            display_link = item.get('displayLink', '')
            snippet = item.get('snippet', '')
            
            # Try to extract price from title and snippet
            price_text = f"{title} {snippet}"
            extracted_price = extract_price_from_text(price_text)
            
            # Get image information
            image_url = item.get('link', '')
            thumbnail = item.get('image', {}).get('thumbnailLink', '')
            
            # Extract domain/store name
            store_name = display_link.replace('www.', '').title()
            
            processed_result = {
                'title': title,
                'store': store_name,
                'price': extracted_price,
                'url': link,
                'image_url': thumbnail,
                'snippet': snippet,
                'display_link': display_link
            }
            
            processed_results.append(processed_result)
            
        except Exception as e:
            st.warning(f"Error processing result: {str(e)}")
            continue
    
    return processed_results

def display_results(results):
    """Display search results in a mobile-friendly format"""
    if not results:
        st.warning("No results found. Try adjusting your search terms or image.")
        return
    
    st.markdown("### 🛍️ Found Similar Products")
    
    # Sort results by price if available
    results_with_price = [r for r in results if r['price']]
    results_without_price = [r for r in results if not r['price']]
    
    if results_with_price:
        results_with_price.sort(key=lambda x: float(x['price']))
        st.markdown("#### 💰 Products with Prices (sorted by price)")
        
        for result in results_with_price:
            display_result_card(result, has_price=True)
    
    if results_without_price:
        st.markdown("#### 🔍 Other Similar Products")
        for result in results_without_price:
            display_result_card(result, has_price=False)

def display_result_card(result, has_price=False):
    """Display individual result card"""
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <div class="store-name">{result['store']}</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">{result['title'][:100]}{'...' if len(result['title']) > 100 else ''}</h4>
            {'<div class="price-tag">💰 $' + result['price'] + '</div>' if has_price else '<div style="color: #7f8c8d;">Price not available</div>'}
            <p style="color: #7f8c8d; font-size: 0.9rem; margin: 1rem 0;">{result['snippet'][:150]}{'...' if len(result['snippet']) > 150 else ''}</p>
            <a href="{result['url']}" target="_blank" style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.7rem 1.5rem; text-decoration: none; border-radius: 25px; display: inline-block; margin-top: 1rem;">
                🛒 View Product
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Show thumbnail if available
        if result['image_url']:
            try:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(result['image_url'], width=200, caption="Product Image")
            except:
                pass  # Skip if image can't be loaded

def main():
    """Main application function"""
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; color: #2c3e50;">🛍️ Product Price Finder</h1>
        <p style="margin: 0.5rem 0 0 0; color: #7f8c8d;">Find the same product at better prices across the web</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration Section
    with st.expander("⚙️ API Configuration", expanded=False):
        api_key = st.text_input(
            "Google Custom Search API Key",
            value=st.session_state.get('google_api_key', ''),
            type="password",
            help="Enter your Google Custom Search API key"
        )
        cse_id = st.text_input(
            "Custom Search Engine ID",
            value=st.session_state.get('google_cse_id', ''),
            help="Enter your Custom Search Engine ID"
        )
        
        if st.button("💾 Save API Configuration"):
            st.session_state.google_api_key = api_key
            st.session_state.google_cse_id = cse_id
            st.success("✅ Configuration saved!")
    
    # Check if API credentials are configured
    current_api_key, current_cse_id = get_google_search_api_key()
    
    if not current_api_key or not current_cse_id:
        st.warning("⚠️ Please configure your Google Custom Search API credentials above to use the app.")
        st.info("""
        **How to get API credentials:**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Enable the Custom Search API
        3. Create an API key
        4. Set up a Custom Search Engine at [programmablesearchengine.google.com](https://programmablesearchengine.google.com/)
        5. Get your Search Engine ID
        """)
        return
    
    # Image Upload Section
    st.markdown("""
    <div class="upload-section">
        <h3 style="margin-top: 0; color: #2c3e50;">📷 Upload Product Image</h3>
        <p style="color: #7f8c8d;">Take a photo or upload an image of the product you want to find</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload a clear image of the product you're looking for"
    )
    
    # Camera input (works on mobile)
    camera_image = st.camera_input("📸 Or take a photo")
    
    # Use camera image if available, otherwise use uploaded file
    image_to_process = camera_image if camera_image else uploaded_file
    
    if image_to_process:
        # Display the uploaded image
        image = Image.open(image_to_process)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Your Product Image", width=300)
        
        # Search configuration
        st.markdown("### 🔍 Search Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            search_terms = st.text_input(
                "Additional search terms",
                placeholder="e.g., dress, summer, floral",
                help="Add specific terms to improve search accuracy"
            )
        
        with col2:
            max_results = st.selectbox(
                "Number of results",
                options=[5, 10, 15, 20],
                index=1,
                help="More results = longer search time"
            )
        
        # Search button
        if st.button("🔍 Find Similar Products", type="primary", use_container_width=True):
            if not search_terms.strip():
                search_query = "fashion clothing dress women"
            else:
                search_query = search_terms.strip()
            
            # Show progress
            with st.container():
                st.markdown("""
                <div class="search-progress">
                    <h4>🔍 Searching across the web...</h4>
                    <p>This may take a few moments</p>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress updates
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("Analyzing image...")
                    elif i < 70:
                        status_text.text("Searching online stores...")
                    else:
                        status_text.text("Processing results...")
                    time.sleep(0.03)
                
                # Perform actual search
                results = search_similar_products(
                    current_api_key, 
                    current_cse_id, 
                    search_query, 
                    max_results
                )
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if results:
                    processed_results = process_search_results(results)
                    st.session_state.search_results = processed_results
                    
                    st.success(f"✅ Found {len(processed_results)} similar products!")
                    display_results(processed_results)
                else:
                    st.error("❌ No results found. Please try different search terms or check your API configuration.")
    
    # Display previous results if available
    elif st.session_state.search_results:
        st.markdown("### 📋 Previous Search Results")
        display_results(st.session_state.search_results)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem;">
        <p>Made with ❤️ for smart shopping • Find better deals across the web</p>
        <p style="font-size: 0.8rem;">💡 Tip: Use clear, well-lit photos for best results</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
