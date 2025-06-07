#!/usr/bin/env python3
"""
Real Estate Analyzer - Main Entry Point
Replaces the monolithic real_estate_analyzer.py with modular architecture
"""
import argparse
import sys

# Import local modules using relative imports
from src.dashboard.app import create_real_estate_app
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

    # Data options (kept for backward compatibility but not used with simple storage)
    parser.add_argument(
        '--data-dir',
        type=str,
        default=str(AppSettings.DATA_DIRECTORY),
        help='Directory containing scraped real estate data (not used with browser storage)'
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

    # Data filtering options (kept for backward compatibility but not used with simple storage)
    parser.add_argument(
        '--min-properties',
        type=int,
        default=1,
        help='Minimum number of properties required to start dashboard (not used with browser storage)'
    )

    return parser.parse_args()


# File loading logic removed - simple storage approach uses browser localStorage only


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

    # Load initial data (simplified for browser storage approach)
    try:
        # For simple storage approach, always start with empty data
        # Users' data will auto-load from browser storage if it exists
        print(
            "🔄 Starting with empty dataset - user data will auto-load from browser storage")
        loader = PropertyDataLoader()
        initial_data = loader.create_empty_dataframe()
    except Exception as e:
        print(f"❌ Failed to initialize data loader: {str(e)}")
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
