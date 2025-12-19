"""
Streamlit Web Interface for AliBaba Scraper
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os

from scraper import AliBabaScraper

# Page configuration
st.set_page_config(
    page_title="AliBaba Product Scraper",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6F00;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-bottom: 1rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .stButton button {
        background-color: #FF6F00;
        color: white;
        font-weight: bold;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = AliBabaScraper()
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame()
if 'scraping_complete' not in st.session_state:
    st.session_state.scraping_complete = False

# App header
st.markdown('<h1 class="main-header">🛍️ AliBaba Product Scraper</h1>', unsafe_allow_html=True)
st.markdown("Extract product data from AliBaba.com with ease!")

# Sidebar
with st.sidebar:
    st.image("https://img.alicdn.com/tfs/TB1PjO.TUT1gK0jSZFhXXaAtVXa-194-63.png", width=150)
    st.markdown("### 🔧 Settings")
    
    # Search parameters
    keyword = st.text_input("Search Keyword", value="smart watch")
    pages = st.slider("Number of Pages", min_value=1, max_value=10, value=3)
    
    st.markdown("---")
    st.markdown("### 📊 Options")
    get_details = st.checkbox("Extract Detailed Information", value=False)
    save_data = st.checkbox("Save to File", value=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This tool extracts product data from AliBaba.com.
    
    Features:
    • Product listings
    • Prices & MOQ
    • Supplier info
    • Export to CSV/Excel
    """)

# Main content area
tab1, tab2, tab3 = st.tabs(["🔍 Scraper", "📊 Analytics", "📁 Export"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h3 class="sub-header">Start Scraping</h3>', unsafe_allow_html=True)
        
        if st.button("🚀 Start Scraping", use_container_width=True):
            with st.spinner(f"Scraping AliBaba for '{keyword}'..."):
                try:
                    # Initialize scraper
                    scraper = st.session_state.scraper
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Scrape products
                    products_df = scraper.search_products(keyword, pages)
                    
                    if not products_df.empty:
                        # Update progress
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        # Store in session state
                        st.session_state.products_df = products_df
                        st.session_state.scraping_complete = True
                        
                        # Show success message
                        st.success(f"✅ Successfully scraped {len(products_df)} products!")
                        
                        # Display sample data
                        st.markdown("### 📋 Sample Data")
                        st.dataframe(products_df.head(10), use_container_width=True)
                        
                        # Show statistics
                        stats = scraper.get_stats()
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Products Scraped", stats['products_scraped'])
                        with col2:
                            st.metric("Pages Scraped", stats['pages_scraped'])
                        with col3:
                            st.metric("Errors", stats['errors'])
                        
                    else:
                        st.error("No products found. Please try a different keyword.")
                        
                except Exception as e:
                    st.error(f"Error during scraping: {str(e)}")
    
    with col2:
        st.markdown('<h3 class="sub-header">Quick Stats</h3>', unsafe_allow_html=True)
        
        if not st.session_state.products_df.empty:
            df = st.session_state.products_df
            
            # Stats cards
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Products", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Unique Suppliers", df['supplier'].nunique())
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            # Extract numeric prices (simplified)
            price_counts = df['price'].value_counts().head(3)
            st.write("Top Prices:")
            for price, count in price_counts.items():
                st.write(f"• {price}: {count}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if not st.session_state.products_df.empty:
        df = st.session_state.products_df
        
        st.markdown("### 📈 Data Analytics")
        
        # Row 1: Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Suppliers distribution
            supplier_counts = df['supplier'].value_counts().head(10)
            fig1 = px.bar(
                x=supplier_counts.index,
                y=supplier_counts.values,
                title="Top 10 Suppliers",
                labels={'x': 'Supplier', 'y': 'Number of Products'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Price distribution (simplified)
            price_data = df['price'].value_counts().head(10)
            fig2 = px.pie(
                names=price_data.index,
                values=price_data.values,
                title="Price Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Row 2: Data preview
        st.markdown("### 📋 Detailed View")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            selected_supplier = st.selectbox(
                "Filter by Supplier",
                ["All"] + list(df['supplier'].unique())
            )
        
        with col2:
            min_products = st.slider("Minimum Products", 1, len(df), 1)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_supplier != "All":
            filtered_df = filtered_df[filtered_df['supplier'] == selected_supplier]
        
        # Display filtered data
        st.dataframe(filtered_df, use_container_width=True)

with tab3:
    if not st.session_state.products_df.empty:
        st.markdown("### 📁 Export Data")
        
        df = st.session_state.products_df
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"alibaba_products_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel Export
            excel_buffer = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
            df.to_excel(excel_buffer, index=False)
            excel_buffer.save()
            
            with open('temp.xlsx', 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"alibaba_products_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            # JSON Export
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"alibaba_products_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Data preview
        st.markdown("### 👀 Preview Export Data")
        st.dataframe(df.head(20), use_container_width=True)
        
        # Data statistics
        st.markdown("### 📊 Export Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Total Rows:** {len(df)}")
        with col2:
            st.info(f"**Total Columns:** {len(df.columns)}")
        with col3:
            st.info(f"**File Size:** ~{len(csv) / 1024:.1f} KB")
    else:
        st.info("👈 Start scraping to export data")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit & Python</p>
    <p>For educational purposes only • Respect robots.txt</p>
</div>
""", unsafe_allow_html=True)
