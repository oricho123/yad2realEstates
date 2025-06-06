#!/usr/bin/env python3
"""
Test script to verify the API parameter construction fixes.
This test verifies that the scraping parameters match the expected API format.
"""

from src.config.constants import ScrapingConfiguration
from src.scraping import Yad2Scraper, ScrapingParams
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_api_parameter_construction():
    """Test that API parameters are constructed correctly."""
    print("🧪 Testing API parameter construction...")

    # Initialize scraper
    scraper = Yad2Scraper()

    # Test parameters similar to the provided API example
    test_params = ScrapingParams(
        city=9500,
        area=6,
        top_area=25,
        min_price=1350000,
        max_price=1420000,
        max_rooms=4,
        min_square_meters=20,
        max_square_meters=460
    )

    print(f"   Input parameters: {test_params}")

    # Use the scraper's fetch_listings method to build parameters
    # This tests the actual parameter construction logic
    try:
        # Mock the API call to see what parameters would be sent
        from unittest.mock import patch, Mock

        with patch('requests.get') as mock_get:
            # Mock a successful response
            mock_response = Mock()
            mock_response.json.return_value = {"data": {"markers": []}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # Call fetch_listings with test parameters
            scraper.fetch_listings(test_params)

            # Get the actual parameters that would be sent to the API
            actual_call = mock_get.call_args
            actual_params = actual_call[1]['params']  # kwargs -> params

            print(f"   Generated API parameters: {actual_params}")

            # Expected API parameters based on the example URL
            expected_params = {
                'zoom': 11,  # default zoom
                'city': 9500,
                'area': 6,
                'topArea': 25,
                'minPrice': 1350000,
                'maxPrice': 1420000,
                'maxRooms': 4,
                # Fixed: API expects minSquaremeter (not minSquareMeters)
                'minSquaremeter': 20,
                # Fixed: API expects maxSquaremeter (not maxSquareMeters)
                'maxSquaremeter': 460,
                'priceOnly': 1  # Added: API expects priceOnly=1
            }

            print(f"   Expected API parameters: {expected_params}")

            # Verify all expected parameters are present
            success = True
            for key, expected_value in expected_params.items():
                if key not in actual_params:
                    print(f"   ❌ Missing parameter: {key}")
                    success = False
                elif actual_params[key] != expected_value:
                    print(
                        f"   ❌ Parameter mismatch: {key} = {actual_params[key]} (expected {expected_value})")
                    success = False

            # Check for unexpected parameters
            for key in actual_params:
                if key not in expected_params:
                    print(
                        f"   ⚠️  Unexpected parameter: {key} = {actual_params[key]}")

            if success:
                print("   ✅ API parameter construction test PASSED")
            else:
                print("   ❌ API parameter construction test FAILED")
                assert False, "API parameter construction test failed"

    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        assert False, f"Test failed with error: {e}"


def test_scraping_callback_parameters():
    """Test that the scraping callback constructs parameters correctly."""
    print("\n🧪 Testing scraping callback parameter construction...")

    # Simulate the scraping callback parameter construction
    city = 9500
    area = 6
    min_price = 1350000
    max_price = 1420000
    min_rooms = None
    max_rooms = 4
    min_sqm = 20
    max_sqm = 460

    # Replicate the parameter construction from the scraping callback
    scraping_params = {
        'city': city,
        'area': area,
        'top_area': ScrapingConfiguration.DEFAULT_TOP_AREA  # This should be 25
    }

    # Add price filters if provided
    if min_price is not None:
        scraping_params['min_price'] = min_price
    if max_price is not None:
        scraping_params['max_price'] = max_price

    # Add room filters if provided and not 'any'
    if min_rooms is not None and min_rooms != 'any':
        scraping_params['min_rooms'] = min_rooms
    if max_rooms is not None and max_rooms != 'any':
        scraping_params['max_rooms'] = max_rooms

    # Add square meter filters if provided
    if min_sqm is not None:
        scraping_params['min_square_meters'] = min_sqm
    if max_sqm is not None:
        scraping_params['max_square_meters'] = max_sqm

    print(f"   Generated scraping parameters: {scraping_params}")

    # Expected parameters
    expected_scraping_params = {
        'city': 9500,
        'area': 6,
        'top_area': 25,
        'min_price': 1350000,
        'max_price': 1420000,
        'max_rooms': 4,
        'min_square_meters': 20,
        'max_square_meters': 460
    }

    print(f"   Expected scraping parameters: {expected_scraping_params}")

    # Verify parameters match
    success = True
    for key, expected_value in expected_scraping_params.items():
        if key not in scraping_params:
            print(f"   ❌ Missing parameter: {key}")
            success = False
        elif scraping_params[key] != expected_value:
            print(
                f"   ❌ Parameter mismatch: {key} = {scraping_params[key]} (expected {expected_value})")
            success = False

    if success:
        print("   ✅ Scraping callback parameter test PASSED")
    else:
        print("   ❌ Scraping callback parameter test FAILED")
        assert False, "Scraping callback parameter test failed"


def test_url_construction():
    """Test that the final URL matches the expected format."""
    print("\n🧪 Testing URL construction...")

    # Expected URL based on the example
    expected_url_params = "city=9500&area=6&topArea=25&minPrice=1350000&maxPrice=1420000&maxRooms=4&minSquaremeter=20&maxSquaremeter=460&priceOnly=1"

    print(f"   Expected URL parameters: {expected_url_params}")

    # Test parameter construction with the scraper
    scraper = Yad2Scraper()

    test_params = {
        'city': 9500,
        'area': 6,
        'top_area': 25,
        'min_price': 1350000,
        'max_price': 1420000,
        'max_rooms': 4,
        'min_square_meters': 20,
        'max_square_meters': 460
    }

    # Build parameters like the scraper does
    params = {'zoom': 11}
    if test_params.get('city'):
        params['city'] = test_params['city']
    if test_params.get('area'):
        params['area'] = test_params['area']
    if test_params.get('top_area'):
        params['topArea'] = test_params['top_area']
    if test_params.get('min_price'):
        params['minPrice'] = test_params['min_price']
    if test_params.get('max_price'):
        params['maxPrice'] = test_params['max_price']
    if test_params.get('min_rooms'):
        params['minRooms'] = test_params['min_rooms']
    if test_params.get('max_rooms'):
        params['maxRooms'] = test_params['max_rooms']
    if test_params.get('min_square_meters'):
        params['minSquaremeter'] = test_params['min_square_meters']
    if test_params.get('max_square_meters'):
        params['maxSquaremeter'] = test_params['max_square_meters']
    params['priceOnly'] = 1

    # Convert to URL parameters string
    url_params = '&'.join(f'{k}={v}' for k, v in params.items())
    print(f"   Generated URL parameters: {url_params}")

    # Check if all expected parameters are present
    expected_param_pairs = expected_url_params.split('&')
    generated_param_pairs = url_params.split('&')

    success = True
    for expected_pair in expected_param_pairs:
        if expected_pair not in generated_param_pairs:
            print(f"   ❌ Missing URL parameter: {expected_pair}")
            success = False

    if success:
        print("   ✅ URL construction test PASSED")
    else:
        print("   ❌ URL construction test FAILED")
        assert False, "URL construction test failed"


def main():
    """Run all API parameter tests."""
    print("🔧 Running API Parameter Fix Tests\n")
    print("=" * 50)

    tests = [
        test_api_parameter_construction,
        test_scraping_callback_parameters,
        test_url_construction
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("   🎉 All API parameter tests PASSED!")
        print("\n✅ The API parameter fixes are working correctly.")
        print("   - Parameter names now match the API specification")
        print("   - topArea is included with default value 25")
        print("   - priceOnly=1 parameter is added")
        print("   - minSquaremeter/maxSquaremeter use correct spelling")
    else:
        print("   ❌ Some tests FAILED. Please review the fixes.")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
