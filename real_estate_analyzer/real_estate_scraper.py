import requests
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any

class RealEstateScraper:
    """Scraper for Yad2 real estate API data"""
    
    def __init__(self, output_dir: str = "scraped_real_estate"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = "https://gw.yad2.co.il/realestate-feed/forsale/map"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'he,en-US;q=0.9,en-IL;q=0.8,en;q=0.7,he-IL;q=0.6',
            'Connection': 'keep-alive',
            'Origin': 'https://www.yad2.co.il',
            'Referer': 'https://www.yad2.co.il/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        
    def fetch_listings(self, 
                      city: Optional[int] = None,
                      area: Optional[int] = None, 
                      top_area: Optional[int] = None,
                      min_price: Optional[int] = None,
                      max_price: Optional[int] = None,
                      min_rooms: Optional[float] = None,
                      max_rooms: Optional[float] = None,
                      min_square_meters: Optional[int] = None,
                      max_square_meters: Optional[int] = None,
                      zoom: int = 11) -> Optional[Dict[str, Any]]:
        """
        Fetch real estate listings from Yad2 API
        
        Args:
            city: City ID (e.g., 9500 for specific city)
            area: Area ID 
            top_area: Top area ID
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rooms: Minimum number of rooms
            max_rooms: Maximum number of rooms
            min_square_meters: Minimum property size
            max_square_meters: Maximum property size
            zoom: Map zoom level
            
        Returns:
            JSON response data or None if failed
        """
        
        # Build query parameters
        params = {'zoom': zoom}
        if city: params['city'] = city
        if area: params['area'] = area  
        if top_area: params['topArea'] = top_area
        if min_price: params['minPrice'] = min_price
        if max_price: params['maxPrice'] = max_price
        if min_rooms: params['minRooms'] = min_rooms
        if max_rooms: params['maxRooms'] = max_rooms
        if min_square_meters: params['minSquareMeters'] = min_square_meters
        if max_square_meters: params['maxSquareMeters'] = max_square_meters
        
        try:
            self.logger.info(f"Fetching listings with params: {params}")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            self.logger.info(f"Successfully fetched {len(data.get('data', {}).get('markers', []))} listings")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching listings: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {str(e)}")
            return None
            
    def parse_listings(self, api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response and extract listing information
        
        Args:
            api_data: Raw API response data
            
        Returns:
            List of parsed listing dictionaries
        """
        
        if not api_data or 'data' not in api_data:
            self.logger.warning("No data found in API response")
            return []
            
        markers = api_data.get('data', {}).get('markers', [])
        if not markers:
            self.logger.warning("No markers found in API response")
            return []
            
        parsed_listings = []
        
        for marker in markers:
            try:
                # Extract address information
                address = marker.get('address', {})
                coords = address.get('coords', {})
                house = address.get('house', {})
                
                # Extract additional details
                additional_details = marker.get('additionalDetails', {})
                property_condition = additional_details.get('propertyCondition', {})
                
                # Extract metadata
                metadata = marker.get('metaData', {})
                
                # Extract basic info
                listing = {
                    'id': marker.get('orderId'),
                    'token': marker.get('token'),
                    'price': marker.get('price'),
                    'ad_type': marker.get('adType'),
                    'category_id': marker.get('categoryId'),
                    'subcategory_id': marker.get('subcategoryId'),
                    
                    # Property details
                    'rooms': additional_details.get('roomsCount'),
                    'square_meters': additional_details.get('squareMeter'),
                    'square_meters_built': metadata.get('squareMeterBuild'),
                    'property_type': additional_details.get('property', {}).get('text'),
                    'condition_id': property_condition.get('id'),
                    
                    # Address and location
                    'city': address.get('city', {}).get('text'),
                    'area': address.get('area', {}).get('text'),
                    'neighborhood': address.get('neighborhood', {}).get('text'),
                    'street': address.get('street', {}).get('text'),
                    'house_number': house.get('number'),
                    'floor': house.get('floor'),
                    'lat': coords.get('lat'),
                    'lng': coords.get('lon'),
                    
                    # Images
                    'cover_image': metadata.get('coverImage'),
                    'image_count': len(metadata.get('images', [])),
                    
                    # Calculated fields
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Calculate price per square meter
                if listing['price'] and listing['square_meters']:
                    listing['price_per_sqm'] = listing['price'] / listing['square_meters']
                else:
                    listing['price_per_sqm'] = None
                    
                # Calculate square meters per room
                if listing['square_meters'] and listing['rooms']:
                    listing['sqm_per_room'] = listing['square_meters'] / listing['rooms']
                else:
                    listing['sqm_per_room'] = None
                    
                # Generate full listing URL
                if listing['token']:
                    listing['full_url'] = f"https://www.yad2.co.il/realestate/item/{listing['token']}"
                else:
                    listing['full_url'] = None
                    
                # Add condition text mapping (common values)
                condition_map = {
                    1: "חדש מיידי הבונה",
                    2: "חדש/משופץ", 
                    3: "במצב טוב",
                    4: "דרוש שיפוץ",
                    5: "דרוש שיפוץ כללי"
                }
                listing['condition_text'] = condition_map.get(listing['condition_id'], 'לא ידוע')
                    
                parsed_listings.append(listing)
                
            except Exception as e:
                self.logger.warning(f"Error parsing listing {marker.get('orderId', 'unknown')}: {str(e)}")
                continue
                
        self.logger.info(f"Successfully parsed {len(parsed_listings)} listings")
        return parsed_listings
        
    def save_raw_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save raw API response to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_api_response_{timestamp}.json"
            
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Saved raw data to {file_path}")
        return str(file_path)
        
    def save_listings_csv(self, listings: List[Dict[str, Any]], filename: str = None) -> str:
        """Save parsed listings to CSV file"""
        if not listings:
            self.logger.warning("No listings to save")
            return ""
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_estate_listings_{timestamp}.csv"
            
        file_path = self.output_dir / filename
        
        df = pd.DataFrame(listings)
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        self.logger.info(f"Saved {len(listings)} listings to {file_path}")
        return str(file_path)
        
    def scrape_and_save(self, **kwargs) -> tuple[str, str]:
        """
        Main method to scrape data and save both raw and processed results
        
        Args:
            **kwargs: Parameters to pass to fetch_listings
            
        Returns:
            Tuple of (csv_path, json_path)
        """
        
        # Fetch data from API
        raw_data = self.fetch_listings(**kwargs)
        if not raw_data:
            self.logger.error("Failed to fetch data from API")
            return "", ""
            
        # Save raw data
        json_path = self.save_raw_data(raw_data)
        
        # Parse listings
        listings = self.parse_listings(raw_data)
        
        # Save processed data
        csv_path = self.save_listings_csv(listings)
        
        # Add rate limiting delay
        time.sleep(self.request_delay)
        
        return csv_path, json_path


def main():
    """Example usage of the scraper"""
    
    # Initialize scraper
    scraper = RealEstateScraper()
    
    # Example search parameters (from your provided URL)
    search_params = {
        'city': 9500,
        'area': 6, 
        'top_area': 25,
        'min_price': 1350000,
        'max_price': 1420000
    }
    
    print("Starting real estate data collection...")
    print(f"Search parameters: {search_params}")
    
    # Scrape and save data
    csv_path, json_path = scraper.scrape_and_save(**search_params)
    
    if csv_path:
        print(f"\n✅ Success!")
        print(f"📊 CSV data saved to: {csv_path}")
        print(f"📄 Raw JSON saved to: {json_path}")
        
        # Show a preview of the data
        try:
            df = pd.read_csv(csv_path)
            print(f"\n📈 Found {len(df)} listings")
            print(f"💰 Price range: ₪{df['price'].min():,.0f} - ₪{df['price'].max():,.0f}")
            print(f"📏 Size range: {df['square_meters'].min():.0f} - {df['square_meters'].max():.0f} sqm")
            print(f"�� Price/sqm range: ₪{df['price_per_sqm'].min():,.0f} - ₪{df['price_per_sqm'].max():,.0f}")
            
            print("\n🏠 Sample listings:")
            print(df[['price', 'rooms', 'square_meters', 'price_per_sqm', 'neighborhood']].head())
            
        except Exception as e:
            print(f"Error loading CSV for preview: {e}")
    else:
        print("❌ Failed to collect data")


if __name__ == "__main__":
    main() 