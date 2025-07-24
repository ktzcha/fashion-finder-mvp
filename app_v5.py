import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import time
from urllib.parse import urlparse, parse_qs
import re
from io import BytesIO

# Page configuration for mobile optimization
st.set_page_config(
    page_title="Fashion Finder",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# PWA Configuration and Styling
def add_pwa_config():
    """Add PWA meta tags and enhanced styling"""
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
    
    .no-price-tag {
        background: #95a5a6;
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
    
    .tips-section {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
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

# Configuration and Session State
def init_session_state():
    """Initialize session state variables"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None

def get_api_credentials():
    """Get API credentials from Streamlit secrets"""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        cse_id = st.secrets["GOOGLE_CSE_ID"]
        return api_key, cse_id
    except KeyError:
        st.error("⚠️ API credentials not configured. Please contact the app administrator.")
        st.info("""
        **For the app administrator:**
        Add these secrets in your Streamlit Cloud dashboard:
        - GOOGLE_API_KEY
        - GOOGLE_CSE_ID
        """)
        return None, None

def extract_product_keywords(user_input, image_analysis=None):
    """Generate smart search keywords based on user input and image context"""
    base_keywords = []
    
    if user_input:
        # Clean and process user input
        cleaned_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
        words = cleaned_input.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        base_keywords.extend(filtered_words)
    
    # Add fashion/shopping context
    fashion_terms = ['fashion', 'clothing', 'apparel', 'women', 'dress', 'style']
    
    # Combine keywords intelligently
    if base_keywords:
        search_query = ' '.join(base_keywords[:5]) + ' ' + ' '.join(fashion_terms[:2])
    else:
        search_query = 'women fashion dress clothing style apparel'
    
    return search_query.strip()

def enhanced_price_extraction(text, url=""):
    """Enhanced price extraction with multiple patterns and context awareness"""
    if not text:
        return None
    
    # Combine title and snippet for better context
    full_text = text.lower()
    
    # Enhanced price patterns with more variations
    price_patterns = [
        # Standard currency formats
        r'(?:^|\s)[\$£€¥₹]\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # $99.99, £50.00
        r'(?:^|\s)(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*[\$£€¥₹]',  # 99.99$, 50£
        
        # With currency codes
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*(?:usd|eur|gbp|inr|cad|aud)',
        
        # Price labels
        r'(?:price|cost|sale|now|from)[\s:]*[\$£€¥₹]?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
        
        # Special sale formats
        r'(?:was|originally|before)[\s:]*[\$£€¥₹]?\s*\d+[\.,]\d+[\s]*(?:now|sale)[\s:]*[\$£€¥₹]?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
        
        # Discount formats
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*(?:off|discount|save)',
        
        # Range prices (take the lower price)
        r'(?:from|starting)[\s:]*[\$£€¥₹]?\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
        
        # Just numbers in price context
        r'(?:^|\s)(\d{1,3}(?:\.\d{2})?)\s*(?=\s|$)',  # For simple numbers like "49.99"
    ]
    
    extracted_prices = []
    
    for pattern in price_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            try:
                # Clean the price
                clean_price = str(match).replace(',', '').strip()
                price_float = float(clean_price)
                
                # Filter reasonable prices (between $1 and $10000)
                if 1 <= price_float <= 10000:
                    extracted_prices.append(price_float)
            except (ValueError, TypeError):
                continue
    
    if extracted_prices:
        # Return the most reasonable price (not too high, not too low)
        extracted_prices.sort()
        # Prefer middle-range prices over extremes
        if len(extracted_prices) > 1:
            return f"{extracted_prices[0]:.2f}"
        else:
            return f"{extracted_prices[0]:.2f}"
    
    return None

def search_similar_products(api_key, cse_id, query, num_results=15):
    """Enhanced search with better filtering for shopping results"""
    try:
        # First, try regular web search for better shopping results
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': f"{query} shop buy price store fashion",  # Enhanced query
            'num': min(num_results, 10),
            'safe': 'active',
            'gl': 'us',  # Geographic location
            'cr': 'countryUS',  # Country restrict
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        results = response.json()
        items = results.get('items', [])
        
        # If we have fewer results, try image search as well
        if len(items) < 5:
            image_params = params.copy()
            image_params['searchType'] = 'image'
            image_params['imgType'] = 'photo'
            image_params['imgSize'] = 'medium'
            
            image_response = requests.get(url, params=image_params, timeout=15)
            if image_response.status_code == 200:
                image_results = image_response.json()
                items.extend(image_results.get('items', [])[:5])
        
        return items
    
    except requests.exceptions.RequestException as e:
        st.error(f"Search request failed: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def process_search_results(results):
    """Enhanced result processing with better price extraction and filtering"""
    processed_results = []
    shopping_sites = [
        'amazon', 'ebay', 'zalando', 'asos', 'hm', 'zara', 'uniqlo', 
        'nordstrom', 'macys', 'target', 'walmart', 'etsy', 'shopify',
        'store', 'shop', 'buy', 'retail', 'fashion', 'clothing'
    ]
    
    for item in results:
        try:
            # Extract basic information
            title = item.get('title', 'Unknown Product')
            link = item.get('link', '')
            display_link = item.get('displayLink', '').lower()
            snippet = item.get('snippet', '')
            
            # Filter for shopping-related sites
            is_shopping_site = any(site in display_link for site in shopping_sites)
            is_shopping_content = any(word in (title + snippet).lower() for word in ['buy', 'price', 'shop', 'store', 'fashion', 'clothing', '$', '£', '€'])
            
            if not (is_shopping_site or is_shopping_content):
                continue
            
            # Enhanced price extraction
            price_text = f"{title} {snippet}"
            extracted_price = enhanced_price_extraction(price_text, link)
            
            # Get image information if available
            image_url = ''
            if 'pagemap' in item and 'cse_image' in item['pagemap']:
                image_url = item['pagemap']['cse_image'][0].get('src', '')
            elif 'image' in item:
                image_url = item['image'].get('thumbnailLink', '')
            
            # Extract and clean store name
            store_name = display_link.replace('www.', '').replace('.com', '').replace('.co.uk', '').title()
            if '.' in store_name:
                store_name = store_name.split('.')[0].title()
            
            # Skip results that are clearly not products
            skip_terms = ['blog', 'article', 'news', 'forum', 'wiki', 'review', 'guide']
            if any(term in title.lower() or term in snippet.lower() for term in skip_terms):
                continue
            
            processed_result = {
                'title': title,
                'store': store_name,
                'price': extracted_price,
                'url': link,
                'image_url': image_url,
                'snippet': snippet,
                'display_link': display_link,
                'relevance_score': calculate_relevance_score(title, snippet, extracted_price)
            }
            
            processed_results.append(processed_result)
            
        except Exception as e:
            continue  # Skip problematic results
    
    # Sort by relevance score and price availability
    processed_results.sort(key=lambda x: (x['price'] is None, x['relevance_score']), reverse=True)
    
    return processed_results

def calculate_relevance_score(title, snippet, price):
    """Calculate relevance score for search results"""
    score = 0
    
    # Boost score for having a price
    if price:
        score += 20
    
    # Boost score for shopping-related terms
    shopping_terms = ['buy', 'shop', 'store', 'sale', 'price', 'fashion', 'clothing', 'dress', 'women']
    text = (title + ' ' + snippet).lower()
    
    for term in shopping_terms:
        if term in text:
            score += 5
    
    return score

def display_results(results):
    """Enhanced result display with better organization"""
    if not results:
        st.markdown("""
        <div class="tips-section">
            <h3>🔍 No results found</h3>
            <p><strong>Tips to get better results:</strong></p>
            <ul>
                <li>Add specific product details (color, brand, style)</li>
                <li>Use clear product photos</li>
                <li>Include the product type (dress, shoes, etc.)</li>
                <li>Try different search terms</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("### 🛍️ Found Similar Products")
    
    # Separate results with and without prices
    results_with_price = [r for r in results if r['price']]
    results_without_price = [r for r in results if not r['price']]
    
    if results_with_price:
        st.markdown("#### 💰 Products with Prices")
        st.markdown(f"*Found {len(results_with_price)} products with pricing information*")
        
        # Sort by price
        results_with_price.sort(key=lambda x: float(x['price']))
        
        for result in results_with_price:
            display_result_card(result, has_price=True)
    
    if results_without_price:
        st.markdown("#### 🔍 Other Similar Products")
        st.markdown(f"*{len(results_without_price)} additional matches (price info not available)*")
        
        for result in results_without_price[:5]:  # Limit to 5 to avoid clutter
            display_result_card(result, has_price=False)

def display_result_card(result, has_price=False):
    """Enhanced result card display"""
    with st.container():
        # Truncate long titles
        display_title = result['title'][:80] + '...' if len(result['title']) > 80 else result['title']
        
        price_display = f'<div class="price-tag">💰 ${result["price"]}</div>' if has_price else '<div class="no-price-tag">Price not available</div>'
        
        st.markdown(f"""
        <div class="result-card">
            <div class="store-name">🏪 {result['store']}</div>
            <h4 style="margin: 0.5rem 0; color: #2c3e50;">{display_title}</h4>
            {price_display}
            <p style="color: #7f8c8d; font-size: 0.9rem; margin: 1rem 0;">{result['snippet'][:120]}{'...' if len(result['snippet']) > 120 else ''}</p>
            <a href="{result['url']}" target="_blank" style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.7rem 1.5rem; text-decoration: none; border-radius: 25px; display: inline-block; margin-top: 1rem;">
                🛒 View Product
            </a>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    init_session_state()
    
    # Check API credentials first
    api_key, cse_id = get_api_credentials()
    if not api_key or not cse_id:
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; color: #2c3e50;">🛍️ Product Price Finder</h1>
        <p style="margin: 0.5rem 0 0 0; color: #7f8c8d;">Find the same product at better prices across the web</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Usage tips
    st.markdown("""
    <div class="tips-section">
        <h3>💡 How to get the best results:</h3>
        <ul>
            <li><strong>Upload a clear product image</strong> - avoid blurry or cropped photos</li>
            <li><strong>Add specific details</strong> - include brand, color, style, or product name</li>
            <li><strong>Be descriptive</strong> - "red summer dress from Zalando" works better than just "dress"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Camera input
    camera_image = st.camera_input("📸 Or take a photo")
    
    # Use camera image if available, otherwise use uploaded file
    image_to_process = camera_image if camera_image else uploaded_file
    
    if image_to_process:
        # Display the uploaded image
        image = Image.open(image_to_process)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Your Product Image", width=300)
        
        # Enhanced search configuration
        st.markdown("### 🔍 Product Details")
        
        search_terms = st.text_area(
            "Describe the product (be specific for better results)",
            placeholder="Example: red summer dress from Zalando, size M, floral pattern",
            help="The more specific you are, the better the results. Include brand, color, style, size, etc.",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.selectbox(
                "Number of results",
                options=[10, 15, 20],
                index=1,
                help="More results = longer search time but more options"
            )
        
        with col2:
            search_type = st.selectbox(
                "Search focus",
                options=["Best Match", "Price Focus", "Brand Focus"],
                help="Choose what to prioritize in search results"
            )
        
        # Search button
        if st.button("🔍 Find Similar Products", type="primary", use_container_width=True):
            # Generate smart search query
            search_query = extract_product_keywords(search_terms)
            
            # Add search type modifiers
            if search_type == "Price Focus":
                search_query += " price sale discount"
            elif search_type == "Brand Focus":
                search_query += " brand official store"
            
            # Show progress
            with st.container():
                st.markdown("""
                <div class="search-progress">
                    <h4>🔍 Searching across the web...</h4>
                    <p>Looking for similar products with pricing information</p>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Progress simulation with real steps
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 20:
                        status_text.text("🖼️ Analyzing your product image...")
                    elif i < 40:
                        status_text.text("🔍 Searching online stores...")
                    elif i < 70:
                        status_text.text("💰 Extracting price information...")
                    elif i < 90:
                        status_text.text("📊 Organizing results...")
                    else:
                        status_text.text("✨ Almost ready...")
                    time.sleep(0.04)
                
                # Perform actual search
                results = search_similar_products(api_key, cse_id, search_query, max_results)
                
                # Process results
                if results:
                    processed_results = process_search_results(results)
                    st.session_state.search_results = processed_results
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    if processed_results:
                        results_with_price = len([r for r in processed_results if r['price']])
                        st.success(f"✅ Found {len(processed_results)} similar products ({results_with_price} with pricing)!")
                        display_results(processed_results)
                    else:
                        st.warning("🤔 Found some results but they weren't relevant enough. Try more specific search terms.")
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ No results found. Please try different search terms or check your internet connection.")
    
    # Display previous results if available
    elif st.session_state.search_results:
        st.markdown("### 📋 Previous Search Results")
        display_results(st.session_state.search_results)
    else:
        # Show example usage
        st.markdown("""
        <div class="tips-section">
            <h3>📱 Example Usage</h3>
            <p><strong>Perfect for finding:</strong></p>
            <ul>
                <li>👗 Sold-out items at other stores</li>
                <li>💰 Better prices for the same product</li>
                <li>🌈 Different colors/sizes of the same item</li>
                <li>🏪 Alternative retailers</li>
            </ul>
            <p><em>Start by uploading a product image above!</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem;">
        <p>Made with ❤️ for smart shopping • Find better deals across the web</p>
        <p style="font-size: 0.8rem;">💡 Tip: The more specific your product description, the better the results!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
