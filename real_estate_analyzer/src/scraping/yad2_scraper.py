"""Modernized Yad2 real estate scraper following modular architecture."""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class ScrapingParams:
    """Type-safe parameters for scraping."""
    city: Optional[Union[int, str]] = None
    area: Optional[Union[int, str]] = None
    top_area: Optional[Union[int, str]] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rooms: Optional[float] = None
    max_rooms: Optional[float] = None
    min_square_meters: Optional[int] = None
    max_square_meters: Optional[int] = None
    min_floor: Optional[int] = None
    max_floor: Optional[int] = None
    zoom: int = 11


@dataclass
class ScrapingResult:
    """Type-safe result of scraping operation for browser storage."""
    success: bool
    listings_data: List[Dict[str, Any]]
    raw_data: Optional[Dict[str, Any]]
    listings_count: int
    error_message: Optional[str] = None
    scraped_params: Optional[ScrapingParams] = None


class Yad2Scraper:
    """Modernized scraper for Yad2 real estate API data with browser storage."""

    def __init__(self):
        """Initialize the scraper with configuration."""
        # Setup logging
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

    def fetch_listings(self, params: ScrapingParams) -> Optional[Dict[str, Any]]:
        """
        Fetch real estate listings from Yad2 API.

        Args:
            params: Structured scraping parameters

        Returns:
            JSON response data or None if failed
        """
        # Build query parameters from dataclass
        query_params = {'zoom': params.zoom}

        if params.city:
            query_params['city'] = params.city
        if params.area:
            query_params['area'] = params.area
        if params.top_area:
            query_params['topArea'] = params.top_area
        if params.min_price:
            query_params['minPrice'] = params.min_price
        if params.max_price:
            query_params['maxPrice'] = params.max_price
        if params.min_rooms:
            query_params['minRooms'] = params.min_rooms
        if params.max_rooms:
            query_params['maxRooms'] = params.max_rooms
        if params.min_square_meters:
            query_params['minSquaremeter'] = params.min_square_meters
        if params.max_square_meters:
            query_params['maxSquaremeter'] = params.max_square_meters
        if params.min_floor:
            query_params['minFloor'] = params.min_floor
        if params.max_floor:
            query_params['maxFloor'] = params.max_floor

        # Add priceOnly=1 parameter as required by API
        query_params['priceOnly'] = 1

        try:
            self.logger.info(f"Fetching listings with params: {query_params}")

            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=query_params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            listings_count = len(data.get('data', {}).get('markers', []))
            self.logger.info(f"Successfully fetched {listings_count} listings")
            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching listings: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {str(e)}")
            return None

    def parse_listings(self, api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response and extract listing information.

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
                listing = self._parse_single_listing(marker)
                if listing:
                    parsed_listings.append(listing)
            except Exception as e:
                self.logger.warning(
                    f"Error parsing listing {marker.get('orderId', 'unknown')}: {str(e)}")
                continue

        self.logger.info(
            f"Successfully parsed {len(parsed_listings)} listings")
        return parsed_listings

    def _parse_single_listing(self, marker: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a single listing marker."""
        # Extract nested data
        address = marker.get('address', {})
        coords = address.get('coords', {})
        house = address.get('house', {})
        additional_details = marker.get('additionalDetails', {})
        property_condition = additional_details.get('propertyCondition', {})
        metadata = marker.get('metaData', {})

        # Build listing data
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

            # Timestamp
            'scraped_at': datetime.now().isoformat()
        }

        # Calculate derived fields
        self._calculate_derived_fields(listing)

        return listing

    def _calculate_derived_fields(self, listing: Dict[str, Any]) -> None:
        """Calculate derived fields for a listing."""
        # Price per square meter
        if listing['price'] and listing['square_meters']:
            listing['price_per_sqm'] = listing['price'] / \
                listing['square_meters']
        else:
            listing['price_per_sqm'] = None

        # Square meters per room
        if listing['square_meters'] and listing['rooms']:
            listing['sqm_per_room'] = listing['square_meters'] / \
                listing['rooms']
        else:
            listing['sqm_per_room'] = None

        # Full listing URL
        if listing['token']:
            listing['full_url'] = f"https://www.yad2.co.il/realestate/item/{listing['token']}"
        else:
            listing['full_url'] = None

        # Condition text mapping
        condition_map = {
            1: "חדש מיידי הבונה",
            2: "חדש/משופץ",
            3: "במצב טוב",
            4: "דרוש שיפוץ",
            5: "דרוש שיפוץ כללי"
        }
        listing['condition_text'] = condition_map.get(
            listing['condition_id'], 'לא ידוע')

    def prepare_for_storage(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare listings data for browser storage by ensuring JSON serialization compatibility.

        Args:
            listings: List of parsed listing dictionaries

        Returns:
            List of storage-ready listing dictionaries
        """
        if not listings:
            self.logger.warning("No listings to prepare for storage")
            return []

        storage_ready_listings = []

        for listing in listings:
            # Create a copy to avoid modifying original data
            storage_listing = listing.copy()

            # Ensure all datetime objects are converted to ISO strings
            if 'scraped_at' in storage_listing:
                if isinstance(storage_listing['scraped_at'], datetime):
                    storage_listing['scraped_at'] = storage_listing['scraped_at'].isoformat(
                    )

            # Handle None values that might cause issues in JSON
            for key, value in storage_listing.items():
                if value is None:
                    # Explicitly keep as None for JSON
                    storage_listing[key] = None
                elif isinstance(value, float) and pd.isna(value):
                    storage_listing[key] = None  # Convert NaN to None

            storage_ready_listings.append(storage_listing)

        self.logger.info(
            f"Prepared {len(storage_ready_listings)} listings for browser storage")
        return storage_ready_listings

    def scrape(self, params: ScrapingParams) -> ScrapingResult:
        """
        Main method to scrape data and prepare for browser storage.

        Args:
            params: Structured scraping parameters

        Returns:
            ScrapingResult with data ready for browser storage
        """
        try:
            # Fetch data from API
            raw_data = self.fetch_listings(params)
            if not raw_data:
                return ScrapingResult(
                    success=False,
                    listings_data=[],
                    raw_data=None,
                    listings_count=0,
                    error_message="Failed to fetch data from API",
                    scraped_params=params
                )

            # Parse listings
            listings = self.parse_listings(raw_data)

            # Prepare listings for browser storage
            storage_ready_listings = self.prepare_for_storage(listings)

            # Add rate limiting delay
            time.sleep(self.request_delay)

            return ScrapingResult(
                success=True,
                listings_data=storage_ready_listings,
                raw_data=raw_data,
                listings_count=len(storage_ready_listings),
                scraped_params=params
            )

        except Exception as e:
            self.logger.error(f"Scraping failed: {str(e)}")
            return ScrapingResult(
                success=False,
                listings_data=[],
                raw_data=None,
                listings_count=0,
                error_message=str(e),
                scraped_params=params
            )
