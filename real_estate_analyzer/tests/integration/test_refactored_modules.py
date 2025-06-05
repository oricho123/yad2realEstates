#!/usr/bin/env python3
"""Test script for refactored modules to ensure they work correctly."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Import our new modules
    from src.config.constants import PropertyValidation, ChartConfiguration, ValueAnalysisConstants
    from src.config.settings import AppSettings
    from src.data.models import PropertyDataFrame, PropertyListing, PropertyFilters
    from src.data.loaders import PropertyDataLoader
    from src.analysis.filters import PropertyDataFilter
    from src.analysis.market_analysis import MarketAnalyzer
    from src.analysis.value_analysis import ValueAnalyzer
    from src.analysis.statistical import StatisticalCalculator

    print("✅ All module imports successful!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def create_test_data():
    """Create sample data for testing."""
    print("\n🔧 Creating test data...")

    # Create sample property data
    np.random.seed(42)  # For reproducible results
    n_properties = 20

    # Generate realistic property data
    base_price_per_sqm = 15000  # Base price per sqm

    data = {
        'id': [f'prop_{i}' for i in range(n_properties)],
        'price': np.random.uniform(800000, 2500000, n_properties),
        'square_meters': np.random.uniform(50, 150, n_properties),
        'rooms': np.random.choice([2, 2.5, 3, 3.5, 4, 4.5, 5], n_properties),
        'neighborhood': np.random.choice(['Center', 'North', 'South', 'East', 'West'], n_properties),
        'condition_text': np.random.choice(['חדש מיידי הבונה', 'חדש/משופץ', 'במצב טוב'], n_properties),
        'ad_type': np.random.choice(['private', 'commercial'], n_properties),
        'property_type': np.random.choice(['apartment', 'house'], n_properties),
        'lat': np.random.uniform(32.0, 33.0, n_properties),
        'lng': np.random.uniform(34.5, 35.5, n_properties),
        'street': [f'Test Street {i}' for i in range(n_properties)],
        'floor': [f'{i%10}' for i in range(n_properties)],
        'full_url': [f'https://example.com/property/{i}' for i in range(n_properties)]
    }

    df = pd.DataFrame(data)

    # Calculate realistic price_per_sqm
    df['price_per_sqm'] = df['price'] / df['square_meters']

    print(f"✅ Created test dataset with {len(df)} properties")
    return df


def test_data_models():
    """Test data models and validation."""
    print("\n📊 Testing Data Models...")

    # Test PropertyListing
    listing = PropertyListing(
        id="test_1",
        price=1500000,
        square_meters=100,
        rooms=3.5,
        neighborhood="Test Area"
    )

    assert listing.is_valid(), "PropertyListing validation failed"
    assert listing.calculate_sqm_per_room() == 100/3.5, "SQM per room calculation failed"
    print("✅ PropertyListing model works correctly")

    # Test PropertyDataFrame
    test_df = create_test_data()
    property_df = PropertyDataFrame(test_df)

    assert not property_df.is_empty, "PropertyDataFrame should not be empty"
    valid_properties = property_df.get_valid_properties()
    assert len(valid_properties.data) > 0, "Should have valid properties"
    print("✅ PropertyDataFrame model works correctly")

    # Test PropertyFilters
    filters = PropertyFilters(
        min_price=1000000,
        max_price=2000000,
        neighborhoods=["Center", "North"]
    )

    filtered_df = property_df.apply_filters(filters)
    assert len(filtered_df.data) <= len(
        property_df.data), "Filtering should reduce or maintain data size"
    print("✅ PropertyFilters work correctly")


def test_data_loader():
    """Test data loading functionality."""
    print("\n📁 Testing Data Loader...")

    # Test with sample data
    test_df = create_test_data()

    # Save test data to temporary file
    temp_csv = Path("temp_test_data.csv")
    test_df.to_csv(temp_csv, index=False)

    try:
        loader = PropertyDataLoader()
        loaded_data = loader.load_property_listings(str(temp_csv))

        assert not loaded_data.is_empty, "Loaded data should not be empty"
        assert len(loaded_data.data) > 0, "Should load some properties"
        print("✅ PropertyDataLoader works correctly")

    finally:
        # Clean up temp file
        if temp_csv.exists():
            temp_csv.unlink()


def test_analysis_modules():
    """Test all analysis modules."""
    print("\n🔬 Testing Analysis Modules...")

    test_df = create_test_data()

    # Test PropertyDataFilter
    print("  Testing PropertyDataFilter...")
    filter_engine = PropertyDataFilter(test_df)

    filter_params = {
        'price_range': [1000000, 2000000],
        'sqm_range': [70, 120],
        'neighborhood': 'all',
        'exclude_neighborhoods': [],
        'rooms_range': [2.5, 4.5],
        'condition': 'all',
        'ad_type': 'all'
    }

    filtered_data = filter_engine.apply_all_filters(filter_params)
    assert len(filtered_data) <= len(
        test_df), "Filtering should reduce or maintain data size"

    filter_options = filter_engine.get_filter_options(test_df)
    assert 'neighborhoods' in filter_options, "Should provide filter options"
    print("    ✅ PropertyDataFilter works correctly")

    # Test MarketAnalyzer
    print("  Testing MarketAnalyzer...")
    market_analyzer = MarketAnalyzer(test_df)

    insights = market_analyzer.generate_market_insights()
    assert 'basic_stats' in insights, "Should generate basic statistics"
    assert 'recommendations' in insights, "Should generate recommendations"

    ranking = market_analyzer.get_neighborhood_ranking()
    assert not ranking.empty, "Should generate neighborhood ranking"
    print("    ✅ MarketAnalyzer works correctly")

    # Test ValueAnalyzer
    print("  Testing ValueAnalyzer...")
    value_analyzer = ValueAnalyzer(test_df)

    scores_df = value_analyzer.calculate_value_scores()
    assert 'value_score' in scores_df.columns, "Should add value scores"
    assert 'value_category' in scores_df.columns, "Should add value categories"

    best_deals = value_analyzer.get_best_deals(max_deals=5)
    assert len(best_deals) <= 5, "Should return requested number of deals"

    distribution = value_analyzer.get_value_distribution()
    assert sum(distribution.values()) == len(
        test_df), "Distribution should sum to total properties"

    trend_analysis = value_analyzer.get_trend_analysis()
    assert 'slope' in trend_analysis, "Should provide trend analysis"
    print("    ✅ ValueAnalyzer works correctly")

    # Test StatisticalCalculator
    print("  Testing StatisticalCalculator...")
    stats_calculator = StatisticalCalculator(test_df)

    summary_stats = stats_calculator.calculate_summary_statistics()
    assert 'price_stats' in summary_stats, "Should calculate price statistics"
    assert 'data_quality' in summary_stats, "Should calculate data quality metrics"

    correlation_matrix = stats_calculator.calculate_correlation_matrix()
    assert not correlation_matrix.empty, "Should generate correlation matrix"

    outliers = stats_calculator.identify_statistical_outliers('price')
    assert isinstance(outliers, pd.Series), "Should identify outliers"
    print("    ✅ StatisticalCalculator works correctly")


def test_configuration():
    """Test configuration modules."""
    print("\n⚙️  Testing Configuration...")

    # Test constants
    assert PropertyValidation.MIN_PRICE >= 0, "Min price should be non-negative"
    assert ChartConfiguration.DEFAULT_HEIGHT > 0, "Chart height should be positive"
    assert ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD < 0, "Excellent deals should be below market"
    print("✅ Constants are properly configured")

    # Test settings
    AppSettings.ensure_directories()
    assert AppSettings.DATA_DIRECTORY.exists(), "Data directory should be created"
    print("✅ Settings work correctly")


def run_comprehensive_test():
    """Run all tests."""
    print("🚀 Starting Comprehensive Module Testing")
    print("=" * 50)

    try:
        test_configuration()
        test_data_models()
        test_data_loader()
        test_analysis_modules()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! ")
        print("✨ Refactored modules are working correctly!")
        print("✅ Ready to proceed with integration or Phase 2")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
