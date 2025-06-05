#!/usr/bin/env python3
"""
Real Estate Analyzer - Main Entry Point
Replaces the monolithic real_estate_analyzer.py with modular architecture
"""
import argparse
import sys
from pathlib import Path

# Import local modules using relative imports
from src.dashboard.app import create_real_estate_app
from src.data.models import PropertyDataFrame
from src.data.loaders import PropertyDataLoader
from src.config.settings import AppSettings


def parse_arguments():
    """Parse command line arguments with enhanced options"""
    parser = argparse.ArgumentParser(
        description='Real Estate Price Analyzer - Modular Architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run with default settings
  %(prog)s --port 8080 --debug                # Run on port 8080 in debug mode
  %(prog)s --data-dir /path/to/data          # Use custom data directory
        """
    )

    # Data options
    parser.add_argument(
        '--data-dir',
        type=str,
        default=str(AppSettings.DATA_DIRECTORY),
        help='Directory containing scraped real estate data'
    )

    # Server options
    parser.add_argument(
        '--port',
        type=int,
        default=AppSettings.SERVER_PORT,
        help=f'Port to run the web server on (default: {AppSettings.SERVER_PORT})'
    )

    parser.add_argument(
        '--host',
        type=str,
        default=AppSettings.SERVER_HOST,
        help=f'Host to bind the server to (default: {AppSettings.SERVER_HOST})'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        default=AppSettings.DEBUG_MODE,
        help='Run in debug mode with hot reloading'
    )

    # Data filtering options
    parser.add_argument(
        '--min-properties',
        type=int,
        default=1,
        help='Minimum number of properties required to start dashboard'
    )

    return parser.parse_args()


def load_initial_data(data_directory: str, min_properties: int = 1) -> PropertyDataFrame:
    """Load initial property data for the dashboard"""
    print("🔍 Loading Real Estate Data...")
    print(f"📁 Data directory: {data_directory}")

    # Initialize data loader
    loader = PropertyDataLoader(Path(data_directory))

    # Try to find and load the latest data file
    latest_file = loader.find_latest_data_file()

    if latest_file is None:
        print("⚠️  No existing data files found.")
        print("💡 Tip: Run the scraper first from the UI")
        return loader.create_empty_dataframe()

    print(f"📄 Loading data from: {latest_file.name}")

    # Load the data
    try:
        property_data = loader.load_property_listings(str(latest_file))

        if len(property_data) < min_properties:
            print(
                f"⚠️  Found only {len(property_data)} properties (minimum: {min_properties})")
            print("💡 The dashboard will start with limited functionality")
        else:
            print(f"✅ Successfully loaded {len(property_data)} properties")

            # Show data quality summary
            valid_props = len(property_data.get_valid_properties())
            location_props = len(property_data.get_properties_with_location())

            print(f"📊 Data Quality Summary:")
            print(
                f"   • Valid properties: {valid_props}/{len(property_data)} ({(valid_props/len(property_data)*100):.1f}%)")
            print(
                f"   • Properties with location: {location_props}/{len(property_data)} ({(location_props/len(property_data)*100):.1f}%)")

        return property_data

    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        print("🔄 Starting with empty dataset")
        return loader.create_empty_dataframe()


def main():
    """Main application entry point"""
    print("🏠 Real Estate Analyzer - Modular Architecture")
    print("=" * 50)

    # Parse command line arguments
    args = parse_arguments()

    # Setup application settings
    if args.debug:
        # AppSettings.DEBUG_MODE = True
        print("🐛 Debug mode enabled")

    # Load initial data
    try:
        initial_data = load_initial_data(args.data_dir, args.min_properties)
    except Exception as e:
        print(f"❌ Failed to load initial data: {str(e)}")
        print("🔄 Starting with empty dataset")
        loader = PropertyDataLoader()
        initial_data = loader.create_empty_dataframe()

    # Create and configure the dashboard application
    print("\n🚀 Starting Real Estate Dashboard...")
    print(f"🌐 Server will start on: http://{args.host}:{args.port}")

    try:
        # Create the modular dashboard app
        dashboard_app = create_real_estate_app(initial_data)

        print("✅ Dashboard application created successfully")
        print("\n🎯 Dashboard Features Available:")
        print("   • Interactive property filtering and visualization")
        print("   • Dual-view scatter plot and map interface")
        print("   • Advanced analytics dashboard")
        print("   • New data scraping capabilities")
        print("   • Best deals identification")
        print("   • Market insights and recommendations")

        print(f"\n🎉 Open your browser to: http://{args.host}:{args.port}")
        print("⏹️  Press Ctrl+C to stop the server")

        # Start the server
        dashboard_app.run(
            debug=args.debug,
            port=args.port,
            host=args.host
        )

    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {str(e)}")
        print("💡 Try running with --debug for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()
