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

# Page configuration optimized for Zalando-style design
st.set_page_config(
    page_title="Product Price Finder",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Zalando-inspired design system
def add_zalando_design():
    """Add Zalando-inspired design system with their color palette and typography"""
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Zalando Color Palette */
    :root {
        --zalando-orange: #FF6900;
        --zalando-orange-light: #FF8533;
        --zalando-orange-dark: #E55A00;
        --zalando-black: #1A1A1A;
        --zalando-dark-grey: #404040;
        --zalando-medium-grey: #8C8C8C;
        --zalando-light-grey: #F5F5F5;
        --zalando-white: #FFFFFF;
        --zalando-border: #E8E8E8;
        --zalando-success: #2ECC71;
        --zalando-error: #E74C3C;
    }
    
    /* Global Styles - Zalando Typography */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--zalando-white);
        color: var(--zalando-black);
    }
    
    /* Remove default Streamlit margins */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header - Clean Zalando Style */
    .zalando-header {
        background: var(--zalando-white);
        padding: 2rem 0;
        margin-bottom: 3rem;
        border-bottom: 1px solid var(--zalando-border);
    }
    
    .zalando-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--zalando-black);
        margin: 0;
        text-align: center;
    }
    
    .zalando-header p {
        font-size: 1.1rem;
        font-weight: 400;
        color: var(--zalando-medium-grey);
        margin: 0.5rem 0 0 0;
        text-align: center;
    }
    
    /* Orange accent line */
    .orange-accent {
        width: 60px;
        height: 3px;
        background: var(--zalando-orange);
        margin: 1rem auto;
        border-radius: 2px;
    }
    
    /* Section Cards - Minimal with lots of breathing room */
    .zalando-section {
        background: var(--zalando-white);
        border: 1px solid var(--zalando-border);
        border-radius: 8px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .zalando-section h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--zalando-black);
        margin: 0 0 1.5rem 0;
    }
    
    /* Product Result Cards - Zalando Style */
    .product-card {
        background: var(--zalando-white);
        border: 1px solid var(--zalando-border);
        border-radius: 8px;
        padding: 0;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
        overflow: hidden;
    }
    
    .product-card:hover {
        border-color: var(--zalando-orange);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .product-card-image {
        width: 100%;
        height: 200px;
        background: var(--zalando-light-grey);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    
    .product-card-content {
        padding: 1.5rem;
    }
    
    .store-badge {
        display: inline-block;
        background: var(--zalando-light-grey);
        color: var(--zalando-dark-grey);
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .product-title {
        font-size: 1rem;
        font-weight: 500;
        color: var(--zalando-black);
        line-height: 1.4;
        margin: 0 0 1rem 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    /* Price Display - Zalando Style */
    .price-display {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0 1.5rem 0;
    }
    
    .price-current {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--zalando-black);
    }
    
    .price-badge {
        background: var(--zalando-orange);
        color: var(--zalando-white);
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        text-transform: uppercase;
    }
    
    .no-price {
        font-size: 0.9rem;
        color: var(--zalando-medium-grey);
        font-style: italic;
    }
    
    /* Buttons - Zalando Style */
    .zalando-btn {
        display: inline-block;
        background: var(--zalando-black);
        color: var(--zalando-white);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.8rem 2rem;
        border-radius: 4px;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: none;
        cursor: pointer;
    }
    
    .zalando-btn:hover {
        background: var(--zalando-orange);
        color: var(--zalando-white);
        text-decoration: none;
        transform: translateY(-1px);
    }
    
    .zalando-btn-primary {
        background: var(--zalando-orange);
        color: var(--zalando-white);
    }
    
    .zalando-btn-primary:hover {
        background: var(--zalando-orange-dark);
        color: var(--zalando-white);
    }
    
    /* Upload Section */
    .upload-area {
        border: 2px dashed var(--zalando-border);
        border-radius: 8px;
        padding: 3rem 2rem;
        text-align: center;
        background: var(--zalando-light-grey);
        margin: 2rem 0;
        transition: all 0.2s ease;
    }
    
    .upload-area:hover {
        border-color: var(--zalando-orange);
        background: rgba(255, 105, 0, 0.02);
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 1px solid var(--zalando-border) !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--zalando-orange) !important;
        box-shadow: 0 0 0 2px rgba(255, 105, 0, 0.1) !important;
    }
    
    /* Loading State */
    .search-progress {
        text-align: center;
        padding: 3rem 2rem;
        background: var(--zalando-white);
        border: 1px solid var(--zalando-border);
        border-radius: 8px;
        margin: 2rem 0;
    }
    
    .search-progress h4 {
        color: var(--zalando-black);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .search-progress p {
        color: var(--zalando-medium-grey);
        font-size: 0.9rem;
    }
    
    /* Tips Section */
    .tips-section {
        background: var(--zalando-light-grey);
        border-left: 4px solid var(--zalando-orange);
        padding: 2rem;
        border-radius: 0 8px 8px 0;
        margin: 2rem 0;
    }
    
    .tips-section h3 {
        color: var(--zalando-black);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .tips-section ul {
        color: var(--zalando-dark-grey);
        line-height: 1.6;
    }
    
    .tips-section li {
        margin-bottom: 0.5rem;
    }
    
    /* Results Header */
    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid var(--zalando-border);
        margin-bottom: 2rem;
    }
    
    .results-count {
        font-size: 0.9rem;
        color: var(--zalando-medium-grey);
    }
    
    /* Success/Error Messages */
    .success-message {
        background: rgba(46, 204, 113, 0.1);
        border: 1px solid var(--zalando-success);
        color: var(--zalando-success);
        padding: 1rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-message {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid var(--zalando-error);
        color: var(--zalando-error);
        padding: 1rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Footer */
    .zalando-footer {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid var(--zalando-border);
        color: var(--zalando-medium-grey);
        font-size: 0.9rem;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .zalando-header h1 {
            font-size: 2rem;
        }
        
        .zalando-section {
            padding: 1.5rem;
        }
        
        .product-card-content {
            padding: 1rem;
        }
        
        .upload-area {
            padding: 2rem 1rem;
        }
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

add_zalando_design()

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
        st.markdown("""
        <div class="error-message">
            ⚠️ API credentials not configured. Please contact the app administrator.
        </div>
        """, unsafe_allow_html=True)
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
        # Return the most reasonable price
        extracted_prices.sort()
        if len(extracted_prices) > 1:
            return f"{extracted_prices[0]:.2f}"
        else:
            return f"{extracted_prices[0]:.2f}"
    
    return None

def search_similar_products(api_key, cse_id, query, num_results=15):
    """Enhanced search with better filtering for shopping results"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': f"{query} shop buy price store fashion",
            'num': min(num_results, 10),
            'safe': 'active',
            'gl': 'us',
            'cr': 'countryUS',
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
            continue
    
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
    """Zalando-style result display"""
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
    
    # Separate results with and without prices
    results_with_price = [r for r in results if r['price']]
    results_without_price = [r for r in results if not r['price']]
    
    # Results header - Zalando style
    total_results = len(results)
    price_results = len(results_with_price)
    
    st.markdown(f"""
    <div class="results-header">
        <h2 style="margin: 0; font-weight: 600; color: var(--zalando-black);">Similar Products</h2>
        <div class="results-count">{total_results} products found • {price_results} with pricing</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display results with prices first
    if results_with_price:
        # Sort by price
        results_with_price.sort(key=lambda x: float(x['price']))
        
        for result in results_with_price:
            display_product_card(result, has_price=True)
    
    # Display results without prices
    if results_without_price:
        if results_with_price:  # Add separator if we showed priced items first
            st.markdown("<div style='margin: 2rem 0; border-top: 1px solid var(--zalando-border);'></div>", unsafe_allow_html=True)
        
        for result in results_without_price[:5]:  # Limit to 5
            display_product_card(result, has_price=False)

def display_product_card(result, has_price=False):
    """Display individual product card in Zalando style"""
    # Truncate long titles
    display_title = result['title'][:85] + '...' if len(result['title']) > 85 else result['title']
    display_snippet = result['snippet'][:120] + '...' if len(result['snippet']) > 120 else result['snippet']
    
    # Price display
    if has_price:
        price_html = f"""
        <div class="price-display">
            <span class="price-current">€{result['price']}</span>
            <span class="price-badge">Best Price</span>
        </div>
        """
    else:
        price_html = '<div class="no-price">Price available on site</div>'
    
    # Product card HTML
    st.markdown(f"""
    <div class="product-card">
        <div class="product-card-content">
            <div class="store-badge">{result['store']}</div>
            <h4 class="product-title">{display_title}</h4>
            {price_html}
            <p style="color: var(--zalando-medium-grey); font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.5rem 0;">
                {display_snippet}
            </p>
            <a href="{result['url']}" target="_blank" class="zalando-btn">
                View Product
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function with Zalando-inspired design"""
    init_session_state()
    
    # Check API credentials
    api_key, cse_id = get_api_credentials()
    if not api_key or not cse_id:
        return
    
    # Header - Zalando style
    st.markdown("""
    <div class="zalando-header">
        <h1>Product Price Finder</h1>
        <div class="orange-accent"></div>
        <p>Find the same product at better prices across the web</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("""
    <div class="zalando-section">
        <h3>Upload Your Product</h3>
    """, unsafe_allow_html=True)
    
    # File uploader with custom styling
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload a clear image of the product you're looking for"
    )
    
    # Camera input
    camera_image = st.camera_input("📸 Or take a photo with your camera")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Use camera image if available, otherwise use uploaded file
    image_to_process = camera_image if camera_image else uploaded_file
    
    if image_to_process:
        # Display uploaded image in a clean way
        image = Image.open(image_to_process)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Your Product", width=300)
        
        # Product Details Section
        st.markdown("""
        <div class="zalando-section">
            <h3>Product Details</h3>
        """, unsafe_allow_html=True)
        
        search_terms = st.text_area(
            "Describe your product",
            placeholder="Example: red summer dress from Zalando, size M, floral pattern",
            help="Be specific for better results - include brand, color, style, size",
            height=80
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.selectbox(
                "Results to show",
                options=[10, 15, 20],
                index=1
            )
        
        with col2:
            search_focus = st.selectbox(
                "Search priority",
                options=["Best Match", "Lowest Price", "Brand Focus"]
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Search button
        search_button = st.button("Find Similar Products", type="primary", use_container_width=True)
        
        if search_button:
            # Generate search query
            search_query = extract_product_keywords(search_terms)
            
            # Modify query based on search focus
            if search_focus == "Lowest Price":
                search_query += " price sale discount"
            elif search_focus == "Brand Focus":
                search_query += " brand official store"
            
            # Show progress with Zalando styling
            st.markdown("""
            <div class="search-progress">
                <h4>🔍 Searching for similar products...</h4>
                <p>This may take a few moments</p>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Progress simulation
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 25:
                    status_text.text("🖼️ Analyzing your product image...")
                elif i < 50:
                    status_text.text("🔍 Searching online stores...")
                elif i < 75:
                    status_text.text("💰 Extracting price information...")
                else:
                    status_text.text("📊 Organizing results...")
                time.sleep(0.03)
            
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
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Found {len(processed_results)} similar products ({results_with_price} with pricing information)
                    </div>
                    """, unsafe_allow_html=True)
                    display_results(processed_results)
                else:
                    st.markdown("""
                    <div class="error-message">
                        🤔 Found some results but they weren't relevant enough. Try more specific search terms.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                progress_bar.empty()
                status_text.empty()
                st.markdown("""
                <div class="error-message">
                    ❌ No results found. Please try different search terms or check your internet connection.
                </div>
                """, unsafe_allow_html=True)
    
    # Display previous results if available
    elif st.session_state.search_results:
        st.markdown("### Previous Search Results")
        display_results(st.session_state.search_results)
    else:
        # Show usage tips in Zalando style
        st.markdown("""
        <div class="tips-section">
            <h3>💡 How to get the best results</h3>
            <ul>
                <li><strong>Upload a clear product image</strong> - avoid blurry or cropped photos</li>
                <li><strong>Add specific details</strong> - include brand, color, style, or product name</li>
                <li><strong>Be descriptive</strong> - "red summer dress from Zalando" works better than just "dress"</li>
                <li><strong>Perfect for finding:</strong> sold-out items, better prices, different sizes/colors</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="zalando-footer">
        <p>Made with ❤️ for smart shopping</p>
        <p>Find better deals across the web • Save money on your favorite products</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
