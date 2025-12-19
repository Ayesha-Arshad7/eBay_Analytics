"""
AliBaba Product Scraper - Core Module
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time
import random
import re
from datetime import datetime
import json
from typing import List, Dict, Optional, Tuple


class AliBabaScraper:
    """Main scraper class for AliBaba products"""
    
    def __init__(self, use_proxies: bool = False):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://www.alibaba.com"
        self.use_proxies = use_proxies
        self.stats = {
            'products_scraped': 0,
            'pages_scraped': 0,
            'errors': 0
        }
        
    def get_headers(self) -> Dict:
        """Generate random headers for request"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.alibaba.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }
    
    def search_products(self, keyword: str, pages: int = 5) -> pd.DataFrame:
        """
        Search products on AliBaba
        
        Args:
            keyword: Search term
            pages: Number of pages to scrape
            
        Returns:
            DataFrame with product listings
        """
        all_products = []
        
        for page in range(1, pages + 1):
            try:
                print(f"Scraping page {page}/{pages} for '{keyword}'...")
                
                # Construct search URL
                search_url = f"{self.base_url}/trade/search?SearchText={keyword}&page={page}"
                
                # Send request
                response = self.session.get(
                    search_url,
                    headers=self.get_headers(),
                    timeout=15
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find product containers
                products = self._parse_search_page(soup)
                
                if products:
                    all_products.extend(products)
                    self.stats['pages_scraped'] += 1
                    self.stats['products_scraped'] += len(products)
                    
                    print(f"Found {len(products)} products on page {page}")
                
                # Respectful delay
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error scraping page {page}: {str(e)}")
                self.stats['errors'] += 1
                continue
        
        # Create DataFrame
        if all_products:
            df = pd.DataFrame(all_products)
            df['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return df
        else:
            return pd.DataFrame()
    
    def _parse_search_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse search results page"""
        products = []
        
        # Try different selectors for AliBaba's dynamic classes
        selectors = [
            'div[data-content*="product"]',
            '.item-content',
            '.product-card',
            '.organic-list',
            'div[component="product"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                break
        
        if not items:
            return products
        
        for item in items[:20]:  # Limit to 20 products per page
            try:
                product = self._extract_product_data(item)
                if product:
                    products.append(product)
            except:
                continue
        
        return products
    
    def _extract_product_data(self, item) -> Optional[Dict]:
        """Extract product data from HTML element"""
        try:
            # Extract title
            title_elem = item.find(['h2', 'h3', 'h4'], class_=re.compile(r'title|name|product', re.I))
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            
            # Extract price
            price_elem = item.find(class_=re.compile(r'price|cost|amount', re.I))
            price = price_elem.get_text(strip=True) if price_elem else "Price NA"
            
            # Extract MOQ
            moq_elem = item.find(string=re.compile(r'MOQ|Min.*Order', re.I))
            moq = moq_elem.strip() if moq_elem else "MOQ NA"
            
            # Extract supplier
            supplier_elem = item.find(class_=re.compile(r'supplier|seller|company', re.I))
            supplier = supplier_elem.get_text(strip=True) if supplier_elem else "Supplier NA"
            
            # Extract link
            link_elem = item.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = self.base_url + link
            else:
                link = "#"
            
            # Extract image
            img_elem = item.find('img', src=True)
            img_url = img_elem['src'] if img_elem else ""
            if img_url and not img_url.startswith('http'):
                img_url = 'https:' + img_url
            
            # Extract rating if available
            rating_elem = item.find(class_=re.compile(r'rating|star|review', re.I))
            rating = rating_elem.get_text(strip=True) if rating_elem else "No Rating"
            
            return {
                'title': title,
                'price': price,
                'moq': moq,
                'supplier': supplier,
                'link': link,
                'image_url': img_url,
                'rating': rating,
                'source': 'Alibaba'
            }
            
        except Exception as e:
            return None
    
    def get_product_details(self, product_url: str) -> Dict:
        """Get detailed product information"""
        try:
            response = self.session.get(
                product_url,
                headers=self.get_headers(),
                timeout=20
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = {
                'url': product_url,
                'description': self._extract_description(soup),
                'specifications': self._extract_specifications(soup),
                'shipping_info': self._extract_shipping(soup),
                'images': self._extract_images(soup),
                'response_time': self._extract_response_time(soup),
                'detail_scraped_at': datetime.now().isoformat()
            }
            
            return details
            
        except Exception as e:
            print(f"Error getting details for {product_url}: {str(e)}")
            return {}
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        selectors = [
            '.product-description',
            '.detail-desc',
            '[data-content="description"]',
            '.description-content'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)[:1000]
        
        return "Description not available"
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict:
        """Extract product specifications"""
        specs = {}
        
        # Try to find specification table
        spec_table = soup.find('table', class_=re.compile(r'spec|parameter', re.I))
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    specs[key] = value
        
        return specs if specs else {"status": "No specifications found"}
    
    def _extract_shipping(self, soup: BeautifulSoup) -> str:
        """Extract shipping information"""
        shipping_selectors = [
            '.shipping-info',
            '.logistics-content',
            '.delivery-info'
        ]
        
        for selector in shipping_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)[:500]
        
        return "Shipping information not available"
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images"""
        images = []
        img_tags = soup.find_all('img', src=re.compile(r'product|detail|gallery', re.I))
        
        for img in img_tags[:10]:  # Limit to 10 images
            src = img.get('src', '')
            if src and not src.startswith('data:'):
                if not src.startswith('http'):
                    src = 'https:' + src
                images.append(src)
        
        return images
    
    def _extract_response_time(self, soup: BeautifulSoup) -> str:
        """Extract supplier response time"""
        rt_selectors = [
            'span:contains("response")',
            'div:contains("Response Time")',
            'li:contains("response")'
        ]
        
        for selector in rt_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text(strip=True)
            except:
                continue
        
        return "Response time not specified"
    
    def save_to_file(self, df: pd.DataFrame, filename: str = None):
        """Save DataFrame to file"""
        if df.empty:
            print("No data to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alibaba_products_{timestamp}"
        
        # Save as CSV
        csv_file = f"{filename}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Save as Excel
        excel_file = f"{filename}.xlsx"
        df.to_excel(excel_file, index=False)
        
        # Save as JSON
        json_file = f"{filename}.json"
        df.to_json(json_file, orient='records', indent=2)
        
        print(f"Data saved to:")
        print(f"  - {csv_file}")
        print(f"  - {excel_file}")
        print(f"  - {json_file}")
        
        return {
            'csv': csv_file,
            'excel': excel_file,
            'json': json_file
        }
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return self.stats
