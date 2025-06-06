"""Scraping callback handlers for the dashboard with browser storage integration."""

import pandas as pd
from datetime import datetime
from dash import Input, Output, State, html, clientside_callback
import dash


from src.storage.simple_storage import SimpleStorageManager


class ScrapingCallbackManager:
    """Manages scraping-related callbacks with browser storage integration."""

    def __init__(self, app: dash.Dash):
        """
        Initialize the scraping callback manager.

        Args:
            app: Dash application instance
        """
        self.app = app
        self.storage_manager = SimpleStorageManager()

    def register_all_callbacks(self) -> None:
        """Register all scraping callbacks."""
        self._register_scraping_callback()
        self._register_storage_integration_callback()
        self._register_button_state_callback()
        self._register_city_to_area_callback()

    def _register_scraping_callback(self) -> None:
        """Register the main scraping callback for browser storage."""

        @self.app.callback(
            [Output('scraped-data-store', 'data'),
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
             State('search-min-floor', 'value'),
             State('search-max-floor', 'value'),
             State('loading-state', 'data')],
            prevent_initial_call=True
        )
        def handle_scrape_request(n_clicks, city, area, min_price, max_price,
                                  min_rooms, max_rooms, min_sqm, max_sqm,
                                  min_floor, max_floor, loading_state):
            """
            Handle new data scraping requests for browser storage.

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
                min_floor: Minimum floor filter
                max_floor: Maximum floor filter
                loading_state: Current loading state

            Returns:
                Tuple with scraped data and status information
            """

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
                area_display = "All Areas" if area == 'all' else area
                search_desc = f"City: {city}, Area: {area_display}, Price: ₪{min_price:,}-₪{max_price:,}"

                # Status message during scraping
                status_message = html.Div([
                    html.I(className="fas fa-spinner fa-spin",
                           style={'margin-right': '10px'}),
                    f"Searching for properties... {search_desc}"
                ], style={'color': '#007bff', 'font-weight': '500'})

                # Run the scraper with browser storage integration
                from src.scraping import Yad2Scraper, ScrapingParams
                from src.config.constants import ScrapingConfiguration

                try:
                    # Initialize scraper (no file directory needed)
                    scraper = Yad2Scraper()

                    # Create ScrapingParams object with the provided filters
                    scraping_params = ScrapingParams(
                        city=city,
                        area=area if area != 'all' else None,
                        top_area=ScrapingConfiguration.DEFAULT_TOP_AREA,
                        min_price=min_price if min_price is not None else None,
                        max_price=max_price if max_price is not None else None,
                        min_rooms=min_rooms if min_rooms is not None and min_rooms != 'any' else None,
                        max_rooms=max_rooms if max_rooms is not None and max_rooms != 'any' else None,
                        min_square_meters=min_sqm if min_sqm is not None else None,
                        max_square_meters=max_sqm if max_sqm is not None else None,
                        min_floor=min_floor if min_floor is not None else None,
                        max_floor=max_floor if max_floor is not None else None
                    )

                    print(
                        f"DEBUG: Scraping with parameters: {scraping_params}")

                    # Run the scraper using the new browser storage interface
                    result = scraper.scrape(scraping_params)

                    if result.success and result.listings_data:
                        # Prepare simple storage payload with fresh metadata
                        storage_payload = self.storage_manager.prepare_data_for_storage(
                            pd.DataFrame(result.listings_data)
                        )

                        # Ensure the payload has current timestamp to mark it as new data
                        storage_payload['scraped_at'] = datetime.now(
                        ).isoformat()
                        storage_payload['is_new_data'] = True

                        # Success message
                        success_message = html.Div([
                            html.I(className="fas fa-check-circle",
                                   style={'margin-right': '10px', 'color': '#28a745'}),
                            f"Successfully scraped {result.listings_count} properties matching your search criteria"
                        ], style={'color': '#28a745', 'font-weight': '500'})

                        print(
                            f"DEBUG: Returning {len(result.listings_data)} records for browser storage")

                        return (
                            storage_payload,  # Scraped data with metadata for storage
                            success_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )
                    else:
                        # Scraping failed - provide error message
                        error_msg = result.error_message or "No data returned from API. The search parameters may be too restrictive."

                        error_message = html.Div([
                            html.I(className="fas fa-exclamation-triangle",
                                   style={'margin-right': '10px', 'color': '#dc3545'}),
                            error_msg
                        ], style={'color': '#dc3545', 'font-weight': '500'})

                        return (
                            {},  # Empty data
                            error_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )

                except Exception as scraping_error:
                    print(f"Scraping failed with error: {scraping_error}")

                    # Scraping failed - provide error message
                    error_message = html.Div([
                        html.I(className="fas fa-exclamation-triangle",
                               style={'margin-right': '10px', 'color': '#dc3545'}),
                        f"Scraping failed: {str(scraping_error)}"
                    ], style={'color': '#dc3545', 'font-weight': '500'})

                    return (
                        {},  # Empty data
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
                    {},  # Empty data
                    error_message,
                    False,  # Re-enable button
                    {'loading': False},
                    {'display': 'none'}  # Hide loading overlay
                )

    def _register_storage_integration_callback(self) -> None:
        """Register client-side callback to integrate scraped data with browser storage."""

        clientside_callback(
            """
            function(scraped_data_payload, n_intervals) {
                // Handle new scraped data FIRST (higher priority)
                if (scraped_data_payload && scraped_data_payload.data) {
                    try {
                        // Extract data from the simple storage payload
                        const data = scraped_data_payload.data;
                        
                        if (data && data.length > 0) {
                                                         // Clear existing storage first to ensure complete override
                             if (window.dash_clientside && window.dash_clientside.storage) {
                                 const hadExistingData = window.dash_clientside.storage.has_data();
                                 if (hadExistingData) {
                                     console.log("Clearing existing storage before saving new data");
                                     window.dash_clientside.storage.clear_data();
                                 }
                                 
                                 // Save the new scraped data
                                 const success = window.dash_clientside.storage.save_data(scraped_data_payload);
                                 if (success) {
                                     const action = hadExistingData ? "overrode" : "saved";
                                     console.log(`Successfully ${action} storage with ${data.length} new properties`);
                                 } else {
                                     console.error("Failed to save new data to localStorage");
                                 }
                             }
                            
                            // Return the new data to populate current-dataset
                            return data;
                        }
                    } catch (error) {
                        console.error("Failed to save scraped data to storage:", error);
                        return [];
                    }
                }

                // Handle auto-load on page startup ONLY if no new data was scraped
                if (n_intervals === 1) {
                    if (window.dash_clientside && window.dash_clientside.storage) {
                        try {
                            const stored_data = window.dash_clientside.storage.load_data();
                            if (stored_data && stored_data.data && stored_data.data.length > 0) {
                                console.log(`Auto-loaded ${stored_data.data.length} properties from localStorage`);
                                return stored_data.data;
                            }
                        } catch (error) {
                            console.error("Failed to auto-load data:", error);
                        }
                    }
                }
                
                return window.dash_clientside.no_update;
            }
            """,
            Output('current-dataset', 'data'),
            [Input('scraped-data-store', 'data'),
             Input('auto-load-trigger', 'n_intervals')],
            prevent_initial_call=False  # Allow initial call for auto-load
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

    def _register_city_to_area_callback(self) -> None:
        """Register callback to automatically set area based on selected city."""

        @self.app.callback(
            Output('search-area', 'value'),
            [Input('search-city-dropdown', 'value')],
            prevent_initial_call=True
        )
        def update_area_from_city(selected_city):
            """
            Update area dropdown value based on selected city's area code.

            Args:
                selected_city: The selected city value

            Returns:
                The area code corresponding to the selected city
            """
            if selected_city is None:
                return None

            from src.config.constants import CityOptions

            # Find the selected city and get its area_code
            for city in CityOptions.CITIES:
                if city['value'] == selected_city:
                    # Convert area_code to appropriate type (string to int if needed)
                    area_code = city['area_code']
                    try:
                        # Try to convert to int if it's a numeric string
                        return int(area_code)
                    except (ValueError, TypeError):
                        # If it's not numeric, return as string
                        return area_code

            # If city not found, return None
            return None
