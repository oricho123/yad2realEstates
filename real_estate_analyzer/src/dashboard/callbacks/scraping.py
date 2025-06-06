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
        self._register_load_saved_filters_callback()
        self._register_interval_disable_callback()

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

                        # Save the search filters for reloading on page refresh
                        storage_payload['search_filters'] = {
                            'city': city,
                            'area': area,
                            'min_price': min_price,
                            'max_price': max_price,
                            'min_rooms': min_rooms,
                            'max_rooms': max_rooms,
                            'min_sqm': min_sqm,
                            'max_sqm': max_sqm,
                            'min_floor': min_floor,
                            'max_floor': max_floor
                        }

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
        """Register client-side callback to integrate scraped data with browser storage.

        TODO: Optimize to not run any storage checks after initial page load for better performance.
        """

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
                    // Check if we've already loaded to prevent duplicate loading
                    if (window._data_loaded) {
                        console.log("Storage integration: data already loaded, skipping");
                        return window.dash_clientside.no_update;
                    }
                    
                    if (window.dash_clientside && window.dash_clientside.storage) {
                        try {
                            const stored_data = window.dash_clientside.storage.load_data();
                            if (stored_data && stored_data.data && stored_data.data.length > 0) {
                                console.log(`Auto-loaded ${stored_data.data.length} properties from localStorage on page load`);
                                window._data_loaded = true;
                                return stored_data.data;
                            } else {
                                console.log("No stored data found on page load");
                            }
                        } catch (error) {
                            console.error("Failed to auto-load data:", error);
                        }
                    }
                    window._data_loaded = true; // Mark as checked even if no data
                } else if (n_intervals > 1) {
                    // Don't reload data on subsequent triggers
                    console.log(`Storage integration callback triggered with n_intervals=${n_intervals}, ignoring`);
                } else {
                    console.log(`Storage integration callback triggered with n_intervals=${n_intervals} (unexpected)`);
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
        """Register callback to handle area updates from city selection and saved filters."""

        clientside_callback(
            """
            function(selected_city, n_intervals) {
                console.log(`City-to-area callback: city=${selected_city}, n_intervals=${n_intervals}`);
                
                // Initialize tracking if not exists
                if (window._city_area_initial_load === undefined) {
                    window._city_area_initial_load = true;
                }
                
                // Handle city selection changes (user interactions) - has higher priority
                if (selected_city !== undefined && selected_city !== null && !window._city_area_initial_load) {
                    // Map of city values to their corresponding area codes
                    const cityToAreaMap = {
                        9500: 6,     // קרית ביאליק (Kiryat Bialik) -> אזור הקריות
                        8200: 6,     // קרית מוצקין (Kiryat Motzkin) -> אזור הקריות
                        4000: 5,     // חיפה (Haifa) -> אזור חיפה והסביבה
                        '0874': 91,  // מגדל העמק (Migdal HaEmek) -> אזור נצרת - שפרעם והסביבה
                        874: 91      // Also support numeric version of 0874
                    };
                    
                    const area = cityToAreaMap[selected_city];
                    if (area !== undefined) {
                        console.log(`✅ Setting area ${area} for city ${selected_city} (user change)`);
                        return area;
                    } else {
                        console.log(`❌ No area mapping found for city ${selected_city}, available mappings:`, Object.keys(cityToAreaMap));
                        return window.dash_clientside.no_update;
                    }
                }

                // On initial page load, try to load saved area from storage
                if (window._city_area_initial_load && n_intervals === 1) {
                    console.log("City-to-area: handling initial page load");
                    
                    if (window.dash_clientside && window.dash_clientside.storage) {
                        try {
                            const stored_data = window.dash_clientside.storage.load_data();
                            if (stored_data && stored_data.search_filters && stored_data.search_filters.area !== undefined) {
                                console.log("Loading saved area from storage:", stored_data.search_filters.area);
                                // Mark initial load as complete after a delay to allow all initial callbacks to process
                                setTimeout(() => { window._city_area_initial_load = false; }, 100);
                                return stored_data.search_filters.area;
                            }
                        } catch (error) {
                            console.error("Failed to load saved area:", error);
                        }
                    }
                    // If no saved area, fall back to default
                    console.log("No saved area found, using default (6)");
                    // Mark initial load as complete after a delay
                    setTimeout(() => { window._city_area_initial_load = false; }, 100);
                    return 6;
                }

                console.log(`City-to-area: no action needed (initial_load=${window._city_area_initial_load})`);
                return window.dash_clientside.no_update;
            }
            """,
            Output('search-area', 'value'),
            [Input('search-city-dropdown', 'value'),
             Input('auto-load-trigger', 'n_intervals')],
            prevent_initial_call=False  # Allow initial call for auto-load
        )

    def _register_load_saved_filters_callback(self) -> None:
        """Register client-side callback to load saved search filters on page load."""

        # Add a flag to track if filters have been loaded
        clientside_callback(
            """
            function(n_intervals) {
                // Prevent multiple runs - only run on exact first trigger
                if (n_intervals !== 1) {
                    console.log(`Load saved filters: skipping n_intervals=${n_intervals}`);
                    return Array(9).fill(window.dash_clientside.no_update);
                }
                
                // Check if we've already loaded (prevent multiple runs)
                if (window._filters_loaded) {
                    console.log("Load saved filters: already loaded, skipping");
                    return Array(9).fill(window.dash_clientside.no_update);
                }
                
                console.log("Load saved filters: attempting to load on first page load");
                
                if (window.dash_clientside && window.dash_clientside.storage) {
                    try {
                        const stored_data = window.dash_clientside.storage.load_data();
                        if (stored_data && stored_data.search_filters) {
                            const filters = stored_data.search_filters;
                            console.log("Loading saved search filters on page load:", filters);
                            
                            // Mark as loaded to prevent subsequent runs
                            window._filters_loaded = true;
                            
                            // Return all the filter values except area (handled by city-to-area callback)
                            return [
                                filters.city || 9500,                    // search-city-dropdown
                                filters.min_price || 1000000,           // search-min-price
                                filters.max_price || 2000000,           // search-max-price
                                filters.min_rooms || 1,                 // search-min-rooms
                                filters.max_rooms || 10,                // search-max-rooms
                                filters.min_sqm || 30,                  // search-min-sqm
                                filters.max_sqm || 300,                 // search-max-sqm
                                filters.min_floor,                      // search-min-floor (can be null)
                                filters.max_floor                       // search-max-floor (can be null)
                            ];
                        } else {
                            console.log("No saved search filters found on page load");
                            window._filters_loaded = true; // Mark as checked
                        }
                    } catch (error) {
                        console.error("Failed to load saved search filters:", error);
                        window._filters_loaded = true; // Mark as checked even on error
                    }
                }
                
                // Return no_update for all outputs if not loading
                return Array(9).fill(window.dash_clientside.no_update);
            }
            """,
            [Output('search-city-dropdown', 'value'),
             Output('search-min-price', 'value'),
             Output('search-max-price', 'value'),
             Output('search-min-rooms', 'value'),
             Output('search-max-rooms', 'value'),
             Output('search-min-sqm', 'value'),
             Output('search-max-sqm', 'value'),
             Output('search-min-floor', 'value'),
             Output('search-max-floor', 'value')],
            # Only trigger on page load
            [Input('auto-load-trigger', 'n_intervals')],
            prevent_initial_call=False  # Allow initial call for auto-load
        )

    def _register_interval_disable_callback(self) -> None:
        """Register callback to disable the auto-load interval after first run."""

        clientside_callback(
            """
            function(n_intervals) {
                // After first trigger, disable the interval to prevent any future triggers
                if (n_intervals >= 1) {
                    console.log(`Disabling auto-load trigger after n_intervals=${n_intervals}`);
                    return true;  // Set disabled=True
                }
                return false;  // Keep enabled
            }
            """,
            Output('auto-load-trigger', 'disabled'),
            [Input('auto-load-trigger', 'n_intervals')],
            prevent_initial_call=False
        )
