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

# Page configuration optimized for Fashion Finder
st.set_page_config(
    page_title="Fashion Finder",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Zalando-inspired design system (maintained from v5.1)
def add_zalando_design():
    """Add Zalando-inspired design system with Fashion Finder branding"""
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
    
    /* Header - Clean Zalando Style with Fashion Finder branding */
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
    
    /* EU-specific store badge */
    .store-badge-eu {
        background: linear-gradient(45deg, #003399, #FFCC00);
        color: white;
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
    
    /* Price Display - Zalando Style with EUR focus */
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
    
    .price-badge-eur {
        background: linear-gradient(45deg, #2ECC71, #27AE60);
        color: white;
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
    
    /* EU Market Badge */
    .eu-market-badge {
        background: linear-gradient(45deg, #003399, #FFCC00);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-left: 0.5rem;
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
    """Generate smart search keywords optimized for Dutch/EU market"""
    base_keywords = []
    
    if user_input:
        # Clean and process user input
        cleaned_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
        words = cleaned_input.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        base_keywords.extend(filtered_words)
    
    # Add EU-focused fashion terms
    fashion_terms = ['fashion', 'clothing', 'dames', 'women', 'dress', 'style', 'kleding']
    eu_terms = ['EUR', 'euro', 'Netherlands', 'Europe', 'shipping']
    
    # Combine keywords intelligently for EU market
    if base_keywords:
        search_query = ' '.join(base_keywords[:5]) + ' ' + ' '.join(fashion_terms[:3]) + ' ' + ' '.join(eu_terms[:2])
    else:
        search_query = 'women fashion dress clothing style EUR Netherlands Europe'
    
    return search_query.strip()

def enhanced_price_extraction_eur(text, url=""):
    """Enhanced price extraction with EUR currency focus"""
    if not text:
        return None, None
    
    full_text = text.lower()
    
    # Enhanced price patterns with EUR priority
    eur_patterns = [
        # EUR currency formats (priority)
        r'€\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # €99.99
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*€',  # 99.99€
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*eur(?:o|os)?',  # 99.99 euro
        r'€\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # € 99.99
    ]
    
    other_currency_patterns = [
        # Other currencies
        r'[\$£¥₹]\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # $99.99, £50.00
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*[\$£¥₹]',  # 99.99$, 50£
        r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*(?:usd|gbp|inr|cad|aud)',
    ]
    
    # Try EUR patterns first
    for pattern in eur_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            try:
                clean_price = str(match).replace(',', '').strip()
                price_float = float(clean_price)
                if 1 <= price_float <= 10000:
                    return f"{price_float:.2f}", "EUR"
            except (ValueError, TypeError):
                continue
    
    # Fall back to other currencies
    for pattern in other_currency_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            try:
                clean_price = str(match).replace(',', '').strip()
                price_float = float(clean_price)
                if 1 <= price_float <= 10000:
                    return f"{price_float:.2f}", "OTHER"
            except (ValueError, TypeError):
                continue
    
    return None, None

def search_similar_products_eu(api_key, cse_id, query, num_results=15):
    """Enhanced search optimized for Dutch/EU market"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        
        # EU-optimized search parameters
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': f"{query} shop buy price store fashion EUR",
            'num': min(num_results, 10),
            'safe': 'active',
            'gl': 'nl',  # Geographic location: Netherlands
            'hl': 'en',  # Interface language: English (for broader results)
            'cr': 'countryNL|countryDE|countryBE|countryFR|countryUK',  # EU countries
            'lr': 'lang_en|lang_nl',  # Language restriction
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        results = response.json()
        items = results.get('items', [])
        
        # If fewer results, try image search
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

def process_search_results_eu(results):
    """Enhanced result processing for EU market with commerce-only filtering"""
    processed_results = []
    
    # EU-focused shopping sites (Phase 1: Dutch/EU market optimization)
    eu_shopping_sites = [
        'zalando.nl', 'zalando.de', 'zalando.be', 'zalando.fr',
        'bol.com', 'wehkamp.nl', 'hm.com', 'zara.com', 'asos.com',
        'aboutyou.nl', 'aboutyou.de', 'esprit.nl', 'mango.com',
        'uniqlo.com', 'cos.com', 'stories.com', 'monki.com',
        'amazon.nl', 'amazon.de', 'etos.nl', 'douglas.nl'
    ]
    
    # Generic shopping indicators
    commerce_indicators = ['shop', 'store', 'buy', 'retail', 'fashion', 'clothing', 'webshop']
    
    # Sites to exclude (Phase 1: Purchase-only results filtering)
    exclude_sites = [
        'reddit', 'forum', 'blog', 'wiki', 'review', 'discussion', 
        'pinterest', 'instagram', 'facebook', 'twitter', 'youtube',
        'news', 'article', 'guide', 'tips', 'howto'
    ]
    
    for item in results:
        try:
            title = item.get('title', 'Unknown Product')
            link = item.get('link', '')
            display_link = item.get('displayLink', '').lower()
            snippet = item.get('snippet', '')
            
            # Phase 1: Commerce-only filtering
            is_excluded = any(exclude in display_link or exclude in title.lower() for exclude in exclude_sites)
            if is_excluded:
                continue
            
            # Check if it's a commerce site
            is_eu_site = any(site in display_link for site in eu_shopping_sites)
            is_commerce_site = any(indicator in display_link or indicator in (title + snippet).lower() 
                                 for indicator in commerce_indicators)
            has_purchase_indicators = any(word in (title + snippet).lower() 
                                        for word in ['buy', 'price', 'shop', 'store', 'sale', 'EUR', '€'])
            
            if not (is_eu_site or is_commerce_site or has_purchase_indicators):
                continue
            
            # Enhanced price extraction with EUR focus
            price_text = f"{title} {snippet}"
            extracted_price, currency = enhanced_price_extraction_eur(price_text, link)
            
            # Get image information
            image_url = ''
            if 'pagemap' in item and 'cse_image' in item['pagemap']:
                image_url = item['pagemap']['cse_image'][0].get('src', '')
            elif 'image' in item:
                image_url = item['image'].get('thumbnailLink', '')
            
            # Extract and clean store name
            store_name = display_link.replace('www.', '').replace('.com', '').replace('.nl', '').replace('.de', '').replace('.co.uk', '')
            if '.' in store_name:
                store_name = store_name.split('.')[0]
            store_name = store_name.title()
            
            # Determine if it's an EU store
            is_eu_store = any(eu_site.split('.')[0] in display_link for eu_site in eu_shopping_sites)
            
            processed_result = {
                'title': title,
                'store': store_name,
                'price': extracted_price,
                'currency': currency,
                'url': link,
                'image_url': image_url,
                'snippet': snippet,
                'display_link': display_link,
                'is_eu_store': is_eu_store,
                'relevance_score': calculate_relevance_score_eu(title, snippet, extracted_price, currency, is_eu_store)
            }
            
            processed_results.append(processed_result)
            
        except Exception as e:
            continue
    
    # Sort by EU stores first, then by price availability, then by relevance
    processed_results.sort(key=lambda x: (
        not x['is_eu_store'],  # EU stores first
        x['currency'] != 'EUR' if x['currency'] else True,  # EUR prices first
        x['price'] is None,  # Items with prices first
        -x['relevance_score']  # Higher relevance first
    ))
    
    return processed_results

def calculate_relevance_score_eu(title, snippet, price, currency, is_eu_store):
    """Calculate relevance score with EU market focus"""
    score = 0
    
    # Boost for EU stores
    if is_eu_store:
        score += 30
    
    # Boost for EUR pricing
    if currency == 'EUR':
        score += 25
    elif price:
        score += 15
    
    # Boost for fashion/shopping terms
    shopping_terms = ['buy', 'shop', 'store', 'sale', 'price', 'fashion', 'clothing', 'dress', 'women', 'dames']
    text = (title + ' ' + snippet).lower()
    
    for term in shopping_terms:
        if term in text:
            score += 5
    
    return score

def display_results_eu(results):
    """Enhanced result display with EU market focus"""
    if not results:
        st.markdown("""
        <div class="tips-section">
            <h3>🔍 No results found</h3>
            <p><strong>Tips for better results:</strong></p>
            <ul>
                <li>Add specific product details (color, brand, style)</li>
                <li>Include brand names popular in Netherlands</li>
                <li>Try Dutch terms like "dames jurk" or "kleding"</li>
                <li>Use clear, well-lit product photos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Separate EU and non-EU results
    eu_results = [r for r in results if r['is_eu_store']]
    other_results = [r for r in results if not r['is_eu_store']]
    
    # Count results with EUR pricing
    eur_results = len([r for r in results if r['currency'] == 'EUR'])
    total_results = len(results)
    
    # Results header
    st.markdown(f"""
    <div class="results-header">
        <h2 style="margin: 0; font-weight: 600; color: var(--zalando-black);">Fashion Finder Results</h2>
        <div class="results-count">
            {total_results} products found • {len(eu_results)} from EU stores • {eur_results} with EUR pricing
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display EU results first
    if eu_results:
        st.markdown("### 🇪🇺 European Stores (Ships to Netherlands)")
        for result in eu_results:
            display_product_card_eu(result)
    
    # Display other results
    if other_results and len(other_results) > 0:
        if eu_results:
            st.markdown("<div style='margin: 2rem 0; border-top: 1px solid var(--zalando-border);'></div>", unsafe_allow_html=True)
        st.markdown("### 🌍 International Stores")
        for result in other_results[:5]:  # Limit international results
            display_product_card_eu(result)

def display_product_card_eu(result):
    """Display product card with EU market enhancements"""
    display_title = result['title'][:85] + '...' if len(result['title']) > 85 else result['title']
    display_snippet = result['snippet'][:120] + '...' if len(result['snippet']) > 120 else result['snippet']
    
    # Enhanced price display with currency
    if result['price']:
        if result['currency'] == 'EUR':
            price_html = f"""
            <div class="price-display">
                <span class="price-current">€{result['price']}</span>
                <span class="price-badge price-badge-eur">EUR Price</span>
            </div>
            """
        else:
            price_html = f"""
            <div class="price-display">
                <span class="price-current">{result['price']}</span>
                <span class="price-badge">Price Available</span>
            </div>
            """
    else:
        price_html = '<div class="no-price">Check price on site</div>'
    
    # Store badge with EU indicator
    store_badge_class = "store-badge store-badge-eu" if result['is_eu_store'] else "store-badge"
    eu_indicator = '<span class="eu-market-badge">EU</span>' if result['is_eu_store'] else ''
    
    st.markdown(f"""
    <div class="product-card">
        <div class="product-card-content">
            <div class="{store_badge_class}">{result['store']} {eu_indicator}</div>
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
    """Main Fashion Finder application function"""
    init_session_state()
    
    # Check API credentials
    api_key, cse_id = get_api_credentials()
    if not api_key or not cse_id:
        return
    
    # Header with Fashion Finder branding
    st.markdown("""
    <div class="zalando-header">
        <h1>👗 Fashion Finder</h1>
        <div class="orange-accent"></div>
        <p>Find the same fashion items at better prices across European stores</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("""
    <div class="zalando-section">
        <h3>Upload Your Fashion Item</h3>
        <p style="color: var(--zalando-medium-grey); margin-bottom: 1.5rem;">
            Upload a clear photo of the clothing item you want to find alternatives for
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload a clear image of the fashion item you're looking for"
    )
    
    # Camera input
    camera_image = st.camera_input("📸 Or take a photo with your camera")
    
    # Use camera image if available, otherwise use uploaded file
    image_to_process = camera_image if camera_image else uploaded_file
    
    if image_to_process:
        # Display uploaded image
        image = Image.open(image_to_process)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Your Fashion Item", width=300)
        
        # Product Details Section
        st.markdown("""
        <div class="zalando-section">
            <h3>Product Details</h3>
            <p style="color: var(--zalando-medium-grey); margin-bottom: 1.5rem;">
                Describe your item for better search results in European stores
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        search_terms = st.text_area(
            "Describe your fashion item",
            placeholder="Example: red summer dress from Zalando, size M, floral pattern, cotton",
            help="Be specific - include brand, color, style, size, material. Dutch terms like 'dames jurk' also work well.",
            height=80
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.selectbox(
                "Results to show",
                options=[10, 15, 20],
                index=1,
                help="More results = longer search time"
            )
        
        with col2:
            search_focus = st.selectbox(
                "Search priority",
                options=["EU Stores First", "Lowest EUR Price", "Brand Focus"],
                help="Choose what to prioritize - EU stores are recommended for Netherlands"
            )
        
        # Search button
        search_button = st.button("🔍 Find Fashion Alternatives", type="primary", use_container_width=True)
        
        if search_button:
            # Generate EU-optimized search query
            search_query = extract_product_keywords(search_terms)
            
            # Modify query based on search focus
            if search_focus == "Lowest EUR Price":
                search_query += " EUR price sale discount"
            elif search_focus == "Brand Focus":
                search_query += " brand official store"
            elif search_focus == "EU Stores First":
                search_query += " Nederland Europe EU shipping"
            
            # Show progress
            st.markdown("""
            <div class="search-progress">
                <h4>🔍 Searching European fashion stores...</h4>
                <p>Looking for similar items with EUR pricing</p>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Progress simulation
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 25:
                    status_text.text("🖼️ Analyzing your fashion item...")
                elif i < 50:
                    status_text.text("🇪🇺 Searching European stores...")
                elif i < 75:
                    status_text.text("💰 Finding EUR prices...")
                else:
                    status_text.text("📊 Organizing results...")
                time.sleep(0.03)
            
            # Perform EU-optimized search
            results = search_similar_products_eu(api_key, cse_id, search_query, max_results)
            
            # Process results with EU focus
            if results:
                processed_results = process_search_results_eu(results)
                st.session_state.search_results = processed_results
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                if processed_results:
                    eu_stores = len([r for r in processed_results if r['is_eu_store']])
                    eur_prices = len([r for r in processed_results if r['currency'] == 'EUR'])
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Found {len(processed_results)} fashion alternatives ({eu_stores} from EU stores, {eur_prices} with EUR pricing)
                    </div>
                    """, unsafe_allow_html=True)
                    display_results_eu(processed_results)
                else:
                    st.markdown("""
                    <div class="error-message">
                        🤔 Found some results but they weren't relevant fashion items. Try more specific descriptions.
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
        st.markdown("### Previous Fashion Finder Results")
        display_results_eu(st.session_state.search_results)
    else:
        # Show usage tips for Fashion Finder
        st.markdown("""
        <div class="tips-section">
            <h3>💡 How Fashion Finder works</h3>
            <ul>
                <li><strong>Upload a clear fashion photo</strong> - dresses, tops, shoes, accessories</li>
                <li><strong>Add specific details</strong> - brand, color, style, size, material</li>
                <li><strong>Focus on European stores</strong> - better shipping and return options for Netherlands</li>
                <li><strong>Perfect for finding:</strong> sold-out items, better EUR prices, different sizes/colors</li>
                <li><strong>Works with Dutch terms</strong> - try "dames jurk", "kleding", "schoenen"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with Fashion Finder branding
    st.markdown("""
    <div class="zalando-footer">
        <p><strong>Fashion Finder</strong> - Made with ❤️ for smart fashion shopping</p>
        <p>Find better deals on European fashion • Optimized for Netherlands market</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
