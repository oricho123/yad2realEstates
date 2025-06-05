# #!/usr/bin/env python3
# """Main entry point for the refactored Real Estate Analyzer."""

# from src.dashboard.app import create_real_estate_app
# from src.data.models import PropertyDataFrame
# from src.data.loaders import PropertyDataLoader
# from src.config.settings import AppSettings
# import sys
# import argparse
# from pathlib import Path

# # Add the real_estate_analyzer directory to the path
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))


# def parse_arguments():
#     """Parse command line arguments."""
#     parser = argparse.ArgumentParser(description='Real Estate Price Analyzer')
#     parser.add_argument('--output-dir', default='scraped_real_estate',
#                         help='Directory to save scraped data')
#     parser.add_argument('--city', type=int, default=9500,
#                         help='City ID to scrape')
#     parser.add_argument('--area', type=int, default=6,
#                         help='Area ID to scrape')
#     parser.add_argument('--top-area', type=int, default=25,
#                         help='Top area ID to scrape')
#     parser.add_argument('--min-price', type=int, default=1350000,
#                         help='Minimum price filter')
#     parser.add_argument('--max-price', type=int, default=1420000,
#                         help='Maximum price filter')
#     parser.add_argument('--skip-scrape', action='store_true',
#                         help='Skip scraping and use existing data')
#     parser.add_argument('--port', type=int, default=8051,
#                         help='Port to run the web server on')
#     return parser.parse_args()


# def load_data(output_dir: str) -> PropertyDataFrame:
#     """Load property data from CSV files."""
#     loader = PropertyDataLoader(Path(output_dir))

#     # Try to find the latest data file
#     latest_file = loader.find_latest_data_file()

#     if latest_file and latest_file.exists():
#         print(f"Loading data from: {latest_file}")
#         try:
#             return loader.load_property_listings(str(latest_file))
#         except Exception as e:
#             print(f"Error loading data: {e}")
#             print("Creating empty dataset")
#             return loader.create_empty_dataframe()
#     else:
#         print("No existing data found. Creating empty dataset.")
#         return loader.create_empty_dataframe()


# def main():
#     """Main entry point."""
#     args = parse_arguments()

#     # Ensure directories exist
#     AppSettings.ensure_directories()

#     # Load data
#     property_data = load_data(args.output_dir)

#     if property_data.is_empty:
#         print("\n⚠️  No data loaded. Starting with empty dataset.")
#         print("Use the 'Scrape New Data' feature in the dashboard to collect property listings.")
#     else:
#         print(f"✅ Loaded {len(property_data)} properties for analysis")

#     # Create and run the modular dashboard app
#     print(f"\n🚀 Starting Real Estate Analyzer Dashboard...")
#     print(f"🌐 Dashboard will be available at: http://127.0.0.1:{args.port}/")

#     app = create_real_estate_app(property_data.data)
#     app.run(debug=AppSettings.DEBUG_MODE,
#             port=args.port, host=AppSettings.SERVER_HOST)


# if __name__ == "__main__":
#     main()
