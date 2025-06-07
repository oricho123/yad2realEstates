"""Main Dash application factory for the Real Estate Analyzer dashboard."""


import sys
from pathlib import Path
import requests

import dash
import pandas as pd
from flask import request, jsonify
from src.config.settings import AppSettings, DashConfiguration
from src.config.styles import CustomCSS
from src.dashboard.callbacks.filtering import FilterCallbackManager
from src.dashboard.callbacks.interactions import InteractionCallbackManager
from src.dashboard.callbacks.scraping import ScrapingCallbackManager
from src.dashboard.callbacks.storage import StorageCallbackManager
from src.dashboard.callbacks.visualization import VisualizationCallbackManager
from src.dashboard.layout import DashboardLayoutManager

# Add paths to access the modules
current_dir = Path(__file__).parent.parent.parent  # Go to yad2listings root
real_estate_dir = current_dir / "real_estate_analyzer"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(real_estate_dir))


class RealEstateDashboardApp:
    """Main dashboard application class for Real Estate Analyzer."""

    def __init__(self, initial_data: pd.DataFrame):
        """
        Initialize the dashboard application.

        Args:
            initial_data: DataFrame with property data to initialize the dashboard
        """
        self.initial_data = initial_data
        self.app = None
        self._setup_app()
        self._register_callbacks()
        self._register_proxy_routes()

    def _setup_app(self) -> None:
        """Set up the Dash application with configuration and layout."""
        # Get correct path to assets folder
        assets_path = Path(__file__).parent.parent.parent / 'assets'

        # Create Dash app with configuration
        self.app = dash.Dash(
            __name__,
            title="Real Estate Price Analyzer",
            external_stylesheets=DashConfiguration.EXTERNAL_STYLESHEETS,
            suppress_callback_exceptions=DashConfiguration.SUPPRESS_CALLBACK_EXCEPTIONS,
            meta_tags=DashConfiguration.META_TAGS,
            assets_folder=str(assets_path)  # Correct path to assets folder
        )

        # Set custom CSS with animations
        self.app.index_string = CustomCSS.get_dash_index_string()

        # Create layout manager and set layout
        layout_manager = DashboardLayoutManager(self.initial_data)
        self.app.layout = layout_manager.create_main_layout()

        # Initialize storage manager after app is created
        self.storage_manager = StorageCallbackManager(self.app)

    def _register_callbacks(self) -> None:
        """Register all dashboard callbacks."""
        # Initialize callback managers
        scraping_callbacks = ScrapingCallbackManager(self.app)
        filter_callbacks = FilterCallbackManager(self.app)
        visualization_callbacks = VisualizationCallbackManager(self.app)
        interaction_callbacks = InteractionCallbackManager(self.app)

        # Register callbacks
        scraping_callbacks.register_all_callbacks()
        filter_callbacks.register_all_callbacks()
        visualization_callbacks.register_all_callbacks()
        interaction_callbacks.register_all_callbacks()

        # Register storage callbacks
        self.storage_manager.register_all_callbacks()
        self.storage_manager.register_storage_display_callbacks()

        # Register autocomplete callbacks
        from src.dashboard.components.search import SearchComponentManager
        search_manager = SearchComponentManager()
        search_manager.register_autocomplete_callbacks(self.app)

    def _register_proxy_routes(self) -> None:
        """Register proxy routes for external API calls."""

        @self.app.server.route("/proxy_yad2_autocomplete")
        def proxy_yad2_autocomplete():
            """Proxy route to avoid CORS issues with Yad2 autocomplete API."""
            text = request.args.get("text", "")

            if len(text) < 2:
                return jsonify({"cities": [], "areas": [], "hoods": [], "topAreas": [], "streets": []})

            try:
                # Headers to mimic a browser request
                headers = {
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

                # Make request to Yad2 API
                response = requests.get(
                    f"https://gw.yad2.co.il/address-autocomplete/realestate/v2?text={text}",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    return jsonify(response.json())
                else:
                    print(
                        f"Yad2 API returned status code: {response.status_code}")
                    return jsonify({"cities": [], "areas": [], "hoods": [], "topAreas": [], "streets": []}), 500

            except Exception as e:
                print(f"Error fetching from Yad2 API: {e}")
                return jsonify({"cities": [], "areas": [], "hoods": [], "topAreas": [], "streets": []}), 500

    def run(self, debug: bool = None, port: int = None, host: str = None) -> None:
        """
        Run the dashboard application.

        Args:
            debug: Debug mode (uses AppSettings.DEBUG_MODE if None)
            port: Port to run on (uses AppSettings.SERVER_PORT if None)
            host: Host to bind to (uses AppSettings.SERVER_HOST if None)
        """
        debug = debug if debug is not None else AppSettings.DEBUG_MODE
        port = port if port is not None else AppSettings.SERVER_PORT
        host = host if host is not None else AppSettings.SERVER_HOST

        self.app.run(debug=debug, port=port, host=host)

    def get_dash_app(self) -> dash.Dash:
        """Get the underlying Dash app instance."""
        return self.app


def create_real_estate_app(initial_data: pd.DataFrame) -> RealEstateDashboardApp:
    """
    Factory function to create a configured Real Estate Dashboard application.

    Args:
        initial_data: DataFrame with property data to initialize the dashboard

    Returns:
        Configured RealEstateDashboardApp instance
    """
    return RealEstateDashboardApp(initial_data)
