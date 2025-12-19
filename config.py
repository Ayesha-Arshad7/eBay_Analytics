"""
Configuration settings for AliBaba Scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Scraping settings
SCRAPING_SETTINGS = {
    'MAX_PAGES': 10,
    'REQUEST_DELAY': (2, 5),  # Random delay between requests
    'TIMEOUT': 30,
    'MAX_RETRIES': 3,
    'USER_AGENT_ROTATION': True,
}

# File settings
FILE_SETTINGS = {
    'OUTPUT_DIR': 'data',
    'MAX_FILE_SIZE_MB': 10,
    'SUPPORTED_FORMATS': ['csv', 'excel', 'json'],
}

# Streamlit settings
STREAMLIT_CONFIG = {
    'PAGE_TITLE': 'AliBaba Scraper',
    'PAGE_ICON': '🛍️',
    'LAYOUT': 'wide',
    'INITIAL_SIDEBAR_STATE': 'expanded',
}

# API settings (if needed)
API_SETTINGS = {
    'PROXY_SERVICE': os.getenv('PROXY_SERVICE', None),
    'CAPTCHA_SERVICE': os.getenv('CAPTCHA_SERVICE', None),
}

# Validation patterns
VALIDATION = {
    'URL_PATTERN': r'https?://(?:www\.)?alibaba\.com/.*',
    'EMAIL_PATTERN': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}
