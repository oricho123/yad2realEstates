"""Scraping callback handlers for the dashboard."""

import pandas as pd
from dash import callback, Input, Output, State
import dash
from typing import Tuple, Dict, Any
import time

from src.data.loaders import PropertyDataLoader


class ScrapingCallbackManager:
    """Manages scraping-related callbacks."""

    def __init__(self, app: dash.Dash):
        """
        Initialize the scraping callback manager.

        Args:
            app: Dash application instance
        """
        self.app = app

    def register_all_callbacks(self) -> None:
        """Register all scraping callbacks."""
        self._register_scraping_callback()
        self._register_button_state_callback()

    def _register_scraping_callback(self) -> None:
        """Register the main scraping callback."""

        @self.app.callback(
            [Output('current-dataset', 'data'),
             Output('scrape-status', 'children'),
             Output('scrape-button', 'disabled'),
             Output('loading-state', 'data'),
             Output('global-loading-overlay', 'style')],
            [Input('scrape-button', 'n_clicks')],
            [State('search-city-dropdown', 'value'),
             State('search-area', 'value'),
             State('search-min-price', 'value'),
             State('search-max-price', 'value'),
             State('search-min-rooms', 'value'),
             State('search-max-rooms', 'value'),
             State('search-min-sqm', 'value'),
             State('search-max-sqm', 'value'),
             State('loading-state', 'data')],
            prevent_initial_call=True
        )
        def handle_scrape_request(n_clicks, city, area, min_price, max_price,
                                  min_rooms, max_rooms, min_sqm, max_sqm, loading_state):
            """
            Handle new data scraping requests.

            Args:
                n_clicks: Number of button clicks
                city: Selected city ID
                area: Area ID
                min_price: Minimum price filter
                max_price: Maximum price filter
                min_rooms: Minimum rooms filter
                max_rooms: Maximum rooms filter
                min_sqm: Minimum square meters filter
                max_sqm: Maximum square meters filter
                loading_state: Current loading state

            Returns:
                Tuple of updated components and data
            """
            from dash import html

            try:
                if not n_clicks:
                    # No action needed
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

                # Start loading state
                loading_state = {'loading': True}
                loading_overlay_style = {'position': 'fixed', 'top': '0', 'left': '0', 'right': '0',
                                         'bottom': '0', 'background': 'rgba(0,0,0,0.7)', 'display': 'flex',
                                         'align-items': 'center', 'justify-content': 'center', 'z-index': '9999'}

                # Create search description
                search_desc = f"City: {city}, Area: {area}, Price: ₪{min_price:,}-₪{max_price:,}"

                # Status message during scraping
                status_message = html.Div([
                    html.I(className="fas fa-spinner fa-spin",
                           style={'margin-right': '10px'}),
                    f"Searching for properties... {search_desc}"
                ], style={'color': '#007bff', 'font-weight': '500'})

                # Actually run the scraper with the search parameters
                from src.scraping import Yad2Scraper, ScrapingParams
                from src.config.settings import AppSettings

                try:
                    # Ensure data directory exists
                    AppSettings.ensure_directories()

                    # Delete old data files before scraping new data
                    from pathlib import Path
                    data_dir = Path(AppSettings.DATA_DIRECTORY)
                    if data_dir.exists():
                        # Delete old CSV and JSON files
                        for pattern in ['real_estate_listings_*.csv', 'raw_api_response_*.json']:
                            for old_file in data_dir.glob(pattern):
                                try:
                                    old_file.unlink()
                                    print(
                                        f"🗑️  Deleted old file: {old_file.name}")
                                except Exception as e:
                                    print(
                                        f"⚠️  Could not delete {old_file}: {e}")

                    # Initialize scraper with data directory
                    scraper = Yad2Scraper(
                        str(AppSettings.DATA_DIRECTORY))

                    # Prepare scraping parameters with API filters
                    from src.config.constants import ScrapingConfiguration

                    # Create ScrapingParams object with the provided filters
                    scraping_params = ScrapingParams(
                        city=city,
                        area=area,
                        top_area=ScrapingConfiguration.DEFAULT_TOP_AREA,
                        min_price=min_price if min_price is not None else None,
                        max_price=max_price if max_price is not None else None,
                        min_rooms=min_rooms if min_rooms is not None and min_rooms != 'any' else None,
                        max_rooms=max_rooms if max_rooms is not None and max_rooms != 'any' else None,
                        min_square_meters=min_sqm if min_sqm is not None else None,
                        max_square_meters=max_sqm if max_sqm is not None else None
                    )

                    print(
                        f"DEBUG: Scraping with API parameters: {scraping_params}")

                    # Run the scraper using the new interface
                    result = scraper.scrape(scraping_params)

                    if result.success and result.csv_path:
                        # Load the freshly scraped data
                        data_loader = PropertyDataLoader()
                        property_data = data_loader.load_property_listings(
                            result.csv_path)
                        df = property_data.data

                        # Success message
                        total_scraped = len(df)
                        success_message = html.Div([
                            html.I(className="fas fa-check-circle",
                                   style={'margin-right': '10px', 'color': '#28a745'}),
                            f"Successfully scraped {total_scraped} properties matching your search criteria"
                        ], style={'color': '#28a745', 'font-weight': '500'})

                        # Return updated data and status
                        records_data = df.to_dict('records')
                        print(
                            f"DEBUG: Returning {len(records_data)} records to current-dataset store")
                        print(
                            f"DEBUG: Sample record keys: {list(records_data[0].keys()) if records_data else 'No records'}")

                        return (
                            records_data,
                            success_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )
                    else:
                        # Scraping failed - provide more specific error message
                        if result.error_message:
                            error_msg = f"Scraping failed: {result.error_message}"
                        else:
                            error_msg = "No data returned from API. The search parameters may be too restrictive or the API may be temporarily unavailable."

                        error_message = html.Div([
                            html.I(className="fas fa-exclamation-triangle",
                                   style={'margin-right': '10px', 'color': '#dc3545'}),
                            error_msg
                        ], style={'color': '#dc3545', 'font-weight': '500'})

                        return (
                            [],
                            error_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )

                except Exception as scraping_error:
                    # If scraping fails, fallback to loading existing data
                    print(f"Scraping failed with error: {scraping_error}")

                    data_loader = PropertyDataLoader()
                    latest_file = data_loader.find_latest_data_file()

                    if latest_file:
                        property_data = data_loader.load_property_listings(
                            str(latest_file))
                        df = property_data.data

                        # Apply basic filtering based on search parameters (only if values are provided)
                        filtered_df = df.copy()

                        if min_price is not None:
                            filtered_df = filtered_df[filtered_df['price']
                                                      >= min_price]
                        if max_price is not None:
                            filtered_df = filtered_df[filtered_df['price']
                                                      <= max_price]
                        if min_rooms is not None and min_rooms != 'any':
                            filtered_df = filtered_df[filtered_df['rooms']
                                                      >= min_rooms]
                        if max_rooms is not None and max_rooms != 'any':
                            filtered_df = filtered_df[filtered_df['rooms']
                                                      <= max_rooms]
                        if min_sqm is not None:
                            filtered_df = filtered_df[filtered_df['square_meters'] >= min_sqm]
                        if max_sqm is not None:
                            filtered_df = filtered_df[filtered_df['square_meters'] <= max_sqm]

                        # Warning message about using existing data
                        warning_message = html.Div([
                            html.I(className="fas fa-exclamation-triangle",
                                   style={'margin-right': '10px', 'color': '#ffc107'}),
                            f"Could not scrape new data. Using existing data - found {len(filtered_df)} matching properties."
                        ], style={'color': '#ffc107', 'font-weight': '500'})

                        # Return filtered existing data
                        return (
                            filtered_df.to_dict('records'),
                            warning_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )
                    else:
                        # No data file found and scraping failed
                        error_message = html.Div([
                            html.I(className="fas fa-exclamation-triangle",
                                   style={'margin-right': '10px', 'color': '#dc3545'}),
                            f"Scraping failed: {str(scraping_error)}. No existing data found."
                        ], style={'color': '#dc3545', 'font-weight': '500'})

                        return (
                            [],
                            error_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )

            except Exception as e:
                # Error handling
                error_message = html.Div([
                    html.I(className="fas fa-exclamation-triangle",
                           style={'margin-right': '10px', 'color': '#dc3545'}),
                    f"Error during search: {str(e)}"
                ], style={'color': '#dc3545', 'font-weight': '500'})

                return (
                    [],
                    error_message,
                    False,  # Re-enable button
                    {'loading': False},
                    {'display': 'none'}  # Hide loading overlay
                )

    def _register_button_state_callback(self) -> None:
        """Register the button state update callback."""

        @self.app.callback(
            [Output('scrape-button-icon', 'className'),
             Output('scrape-button-text', 'children'),
             Output('scrape-button', 'style')],
            [Input('loading-state', 'data')]
        )
        def update_button_loading_state(loading_state):
            """
            Update button appearance based on loading state.

            Args:
                loading_state: Current loading state data

            Returns:
                Tuple of button style updates
            """
            from src.config.styles import DashboardStyles

            if loading_state and loading_state.get('loading', False):
                # Loading state
                return (
                    "fas fa-spinner fa-spin",
                    "Searching...",
                    {**DashboardStyles.SCRAPE_BUTTON,
                        'opacity': '0.7', 'cursor': 'not-allowed'}
                )
            else:
                # Normal state
                return (
                    "fas fa-search",
                    "Search Properties",
                    DashboardStyles.SCRAPE_BUTTON
                )
