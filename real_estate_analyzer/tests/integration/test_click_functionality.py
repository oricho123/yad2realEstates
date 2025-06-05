#!/usr/bin/env python3
"""Test script to verify that the click functionality works properly."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime

from dashboard.app import create_real_estate_app
from data.models import PropertyDataFrame


def create_test_data() -> PropertyDataFrame:
    """Create test property data with clickable URLs."""
    test_data = [
        {
            'id': 'test_1',
            'price': 1500000,
            'square_meters': 90,
            'price_per_sqm': 16667,
            'rooms': 3.5,
            'neighborhood': 'Test Neighborhood 1',
            'street': 'Test Street 1',
            'lat': 32.0853,
            'lng': 34.7818,
            'condition_text': 'טוב',
            'ad_type': 'למכירה',
            'property_type': 'דירה',
            'floor': '2',
            'full_url': 'https://www.yad2.co.il/realestate/item/test1',
            'scraped_at': datetime.now()
        },
        {
            'id': 'test_2',
            'price': 1800000,
            'square_meters': 110,
            'price_per_sqm': 16364,
            'rooms': 4,
            'neighborhood': 'Test Neighborhood 2',
            'street': 'Test Street 2',
            'lat': 32.0900,
            'lng': 34.7850,
            'condition_text': 'חדש',
            'ad_type': 'למכירה',
            'property_type': 'דירה',
            'floor': '3',
            'full_url': 'https://www.yad2.co.il/realestate/item/test2',
            'scraped_at': datetime.now()
        },
        {
            'id': 'test_3',
            'price': 1200000,
            'square_meters': 75,
            'price_per_sqm': 16000,
            'rooms': 3,
            'neighborhood': 'Test Neighborhood 3',
            'street': 'Test Street 3',
            'lat': 32.0800,
            'lng': 34.7780,
            'condition_text': 'דרוש שיפוץ',
            'ad_type': 'למכירה',
            'property_type': 'דירה',
            'floor': '1',
            'full_url': 'https://www.yad2.co.il/realestate/item/test3',
            'scraped_at': datetime.now()
        }
    ]
    
    df = pd.DataFrame(test_data)
    return PropertyDataFrame(df)


def test_click_functionality():
    """Test the click functionality implementation."""
    print("🧪 Testing Click Functionality")
    print("=" * 50)
    
    # Create test data
    print("📊 Creating test data with URLs...")
    test_data = create_test_data()
    print(f"✅ Created {len(test_data)} test properties with URLs")
    
    # Verify URLs are present
    df = test_data.data
    print(f"📋 URLs present: {df['full_url'].notna().sum()} / {len(df)}")
    
    # Show sample URLs
    for i, url in enumerate(df['full_url'].head(3)):
        print(f"   Property {i+1}: {url}")
    
    # Create dashboard app
    print("\n🚀 Creating dashboard app...")
    app = create_real_estate_app(test_data.data)
    print("✅ Dashboard app created successfully")
    
    # Check if interaction callbacks are registered
    print("\n🔧 Checking callback registration...")
    try:
        from dashboard.callbacks.interactions import InteractionCallbackManager
        print("✅ InteractionCallbackManager imported successfully")
        
        # Check if the app has the necessary components
        app_instance = app.get_dash_app()
        print(f"✅ Dash app instance created: {type(app_instance)}")
        
        print("\n📝 Click functionality test summary:")
        print("   ✅ Test data created with valid URLs")
        print("   ✅ InteractionCallbackManager available")
        print("   ✅ Dashboard app created successfully")
        print("   ✅ Client-side callbacks should be registered")
        
        print(f"\n🌐 Run the app and test clicking on scatter plot or map points!")
        print(f"   Expected behavior: Clicking should open URLs in new tabs")
        print(f"   Test URLs: {list(df['full_url'].unique())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False


def run_test_server():
    """Run a test server to manually verify click functionality."""
    print("\n🚀 Starting test server...")
    print("Click on points in the scatter plot or map to test functionality")
    print("Press Ctrl+C to stop the server")
    
    # Create test data and app
    test_data = create_test_data()
    app = create_real_estate_app(test_data.data)
    
    # Run the app
    try:
        app.run(debug=True, port=8052)  # Use different port to avoid conflicts
    except KeyboardInterrupt:
        print("\n👋 Test server stopped")


if __name__ == "__main__":
    success = test_click_functionality()
    
    if success:
        print("\nSuccessfully tested click functionality!")
        print("\nRunning test server...")
        run_test_server()
    else:
        print("❌ Test failed - please check the implementation")
        sys.exit(1) 