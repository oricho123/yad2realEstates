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
        self._register_load_saved_filters_callback()
        self._register_initialization_callback()

    def _register_scraping_callback(self) -> None:
        """Register the main scraping callback for browser storage."""

        @self.app.callback(
            [Output('scraped-data-store', 'data'),
             Output('scrape-status', 'children'),
             Output('scrape-button', 'disabled'),
             Output('loading-state', 'data'),
             Output('global-loading-overlay', 'style')],
            [Input('scrape-button', 'n_clicks')],
            [State('location-selection-store', 'data'),
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
        def handle_scrape_request(n_clicks, location_data, min_price, max_price,
                                  min_rooms, max_rooms, min_sqm, max_sqm,
                                  min_floor, max_floor, loading_state):
            """
            Handle new data scraping requests for browser storage.

            Args:
                n_clicks: Number of button clicks
                location_data: Selected location data from autocomplete
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

                # Extract location parameters from autocomplete selection
                city = None
                area = None
                hood = None
                top_area = None
                location_desc = "All Locations"

                if location_data:
                    location_type = location_data.get('type')
                    if location_type == 'city':
                        city = location_data.get('cityId')
                        area = location_data.get('areaId')
                        top_area = location_data.get('topAreaId')
                        location_desc = f"City: {location_data.get('fullText', '')}"
                    elif location_type == 'area':
                        area = location_data.get('areaId')
                        top_area = location_data.get('topAreaId')
                        location_desc = f"Area: {location_data.get('fullText', '')}"
                    elif location_type == 'hood':
                        city = location_data.get('cityId')
                        area = location_data.get('areaId')
                        hood = location_data.get('hoodId')
                        top_area = location_data.get('topAreaId')
                        location_desc = f"Neighborhood: {location_data.get('fullText', '')}"

                # Start loading state
                loading_state = {'loading': True}
                loading_overlay_style = {'position': 'fixed', 'top': '0', 'left': '0', 'right': '0',
                                         'bottom': '0', 'background': 'rgba(0,0,0,0.7)', 'display': 'flex',
                                         'alignItems': 'center', 'justifyContent': 'center', 'zIndex': '9999'}

                # Create search description
                search_desc = f"{location_desc}, Price: ₪{min_price:,}-₪{max_price:,}"

                # Status message during scraping
                status_message = html.Div([
                    html.I(className="fas fa-spinner fa-spin",
                           style={'marginRight': '10px'}),
                    f"Searching for properties... {search_desc}"
                ], style={'color': '#007bff', 'fontWeight': '500'})

                # Run the scraper with browser storage integration
                from src.scraping import Yad2Scraper, ScrapingParams

                try:
                    # Initialize scraper (no file directory needed)
                    scraper = Yad2Scraper()

                    # Create ScrapingParams object with the provided filters
                    scraping_params = ScrapingParams(
                        city=city,
                        area=area,
                        neighborhood=hood,  # Add neighborhood support
                        top_area=top_area,
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
                            'location_data': location_data,
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
                                   style={'marginRight': '10px', 'color': '#28a745'}),
                            f"Successfully scraped {result.listings_count} properties matching your search criteria"
                        ], style={'color': '#28a745', 'fontWeight': '500'})

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
                                   style={'marginRight': '10px', 'color': '#dc3545'}),
                            error_msg
                        ], style={'color': '#dc3545', 'fontWeight': '500'})

                        return (
                            {},  # Empty data
                            error_message,
                            False,  # Re-enable button
                            {'loading': False},
                            {'display': 'none'}  # Hide loading overlay
                        )

                except Exception as scraping_error:
                    print(f"Scraping failed with error: {scraping_error}")
                    return self._create_error_response(f"Scraping failed: {str(scraping_error)}")

            except Exception as e:
                return self._create_error_response(f"Error during search: {str(e)}")

    def _create_error_response(self, error_msg: str) -> tuple:
        """Create standardized error response for scraping callbacks."""
        error_message = html.Div([
            html.I(className="fas fa-exclamation-triangle",
                   style={'marginRight': '10px', 'color': '#dc3545'}),
            error_msg
        ], style={'color': '#dc3545', 'fontWeight': '500'})

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
            function(scraped_data_payload, init_data) {
                // Shared utility to load storage data with error handling
                function loadStorageData() {
                    if (!window.dash_clientside || !window.dash_clientside.storage) return null;
                    try {
                        return window.dash_clientside.storage.load_data();
                    } catch (error) {
                        console.error("Failed to load storage data:", error);
                        return null;
                    }
                }
                
                // Shared utility to set prevention flags
                function setPreventionFlag(flagName, logMessage) {
                    window[flagName] = true;
                    if (logMessage) console.log(logMessage);
                }
                
                
                // Handle new scraped data FIRST (higher priority)
                if (scraped_data_payload && scraped_data_payload.data) {
                    try {
                        const data = scraped_data_payload.data;
                        
                        if (data && data.length > 0) {
                            // NEW: Detect new properties before saving
                            let processedPayload = scraped_data_payload;
                            let newCount = 0;
                            
                            if (window.dash_clientside && window.dash_clientside.storage) {
                                 
                                 if (window.dash_clientside.storage.detect_new_properties) {
                                     try {
                                         const detectionResult = window.dash_clientside.storage.detect_new_properties(scraped_data_payload);
                                         if (detectionResult && detectionResult.processedData) {
                                             processedPayload = detectionResult.processedData;
                                             newCount = detectionResult.newCount || 0;
                                             console.log(`Detected ${newCount} new properties out of ${data.length} total`);
                                         } else {
                                             console.warn("Detection failed, using original data");
                                         }
                                     } catch (detectionError) {
                                         console.error("Error in new property detection:", detectionError);
                                         console.log("Falling back to original data");
                                     }
                                 } else {
                                     console.warn("detect_new_properties function not available, using original data");
                                 }
                                 
                                 const hadExistingData = window.dash_clientside.storage.has_data();
                                 if (hadExistingData) {
                                     window.dash_clientside.storage.clear_data();
                                 }
                                 
                                 const success = window.dash_clientside.storage.save_data(processedPayload);
                                 if (success) {
                                     const action = hadExistingData ? "overrode" : "saved";
                                     const newInfo = newCount > 0 ? ` (${newCount} NEW)` : "";
                                     console.log(`Successfully ${action} storage with ${data.length} properties${newInfo}`);
                                 } else {
                                     console.error("Failed to save new data to localStorage");
                                 }
                             } else {
                                 console.warn("dash_clientside.storage not available");
                             }
                            // Add new status to the data before returning (since it's not stored anymore)
                            let finalData = processedPayload.data;
                            if (window.dash_clientside && window.dash_clientside.storage && 
                                window.dash_clientside.storage.add_new_status_to_data) {
                                finalData = window.dash_clientside.storage.add_new_status_to_data(processedPayload.data);
                            }
                            
                            console.log(`DEBUG: Returning ${finalData ? finalData.length : 'undefined'} properties to visualization`);
                            return finalData;
                        }
                    } catch (error) {
                        console.error("Failed to save scraped data to storage:", error);
                        return [];
                    }
                }

                // Handle auto-load on page startup ONLY if no new data was scraped
                // Check if initialization has been triggered and data hasn't been loaded yet
                if (init_data && init_data.initialized && !window._data_loaded) {
                    const stored_data = loadStorageData();
                    if (stored_data && stored_data.data && stored_data.data.length > 0) {
                        // Add new status to existing properties on-the-fly
                        let processedData = stored_data.data;
                        if (window.dash_clientside && window.dash_clientside.storage && 
                            window.dash_clientside.storage.add_new_status_to_data) {
                            processedData = window.dash_clientside.storage.add_new_status_to_data(stored_data.data);
                        }
                        
                        console.log(`Auto-loaded ${processedData.length} properties on page load`);
                        setPreventionFlag('_data_loaded');
                        return processedData;
                    }
                    setPreventionFlag('_data_loaded');
                }
                
                return window.dash_clientside.no_update;
            }
            """,
            Output('current-dataset', 'data'),
            [Input('scraped-data-store', 'data'),
             Input('init-trigger', 'data')],
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

    def _register_load_saved_filters_callback(self) -> None:
        """Register client-side callback to load saved search filters on page load."""

        clientside_callback(
            """
            function(init_data) {
                // Shared utility to load storage data with error handling
                function loadStorageData() {
                    if (!window.dash_clientside || !window.dash_clientside.storage) return null;
                    try {
                        return window.dash_clientside.storage.load_data();
                    } catch (error) {
                        console.error("Failed to load storage data:", error);
                        return null;
                    }
                }
                
                // Shared utility to set prevention flags
                function setPreventionFlag(flagName, logMessage) {
                    window[flagName] = true;
                    if (logMessage) console.log(logMessage);
                }
                
                
                // Only run when initialization is triggered and filters haven't been loaded yet
                if (!init_data || !init_data.initialized || window._filters_loaded) {
                    return Array(8).fill(window.dash_clientside.no_update);
                }
                
                const stored_data = loadStorageData();
                if (stored_data && stored_data.search_filters) {
                    const filters = stored_data.search_filters;
                    console.log("Loading saved search filters:", filters);
                    
                    setPreventionFlag('_filters_loaded');
                    
                    // Load location data if available and set autocomplete input
                    if (filters.location_data && filters.location_data.fullText) {
                        setTimeout(() => {
                            const input = document.getElementById("autocomplete-input");
                            if (input) {
                                input.value = filters.location_data.fullText;
                                // Store the selection data
                                if (window.dash_clientside && window.dash_clientside.set_props) {
                                    window.dash_clientside.set_props('location-selection-store', {
                                        data: filters.location_data
                                    });
                                }
                            }
                        }, 500); // Delay to ensure autocomplete input is created
                    }
                    
                    return [
                        filters.min_price || 1000000,
                        filters.max_price || 2000000,
                        filters.min_rooms || 1,
                        filters.max_rooms || 10,
                        filters.min_sqm || 30,
                        filters.max_sqm || 300,
                        filters.min_floor,
                        filters.max_floor
                    ];
                }
                
                setPreventionFlag('_filters_loaded');
                return Array(8).fill(window.dash_clientside.no_update);
            }
            """,
            [Output('search-min-price', 'value'),
             Output('search-max-price', 'value'),
             Output('search-min-rooms', 'value'),
             Output('search-max-rooms', 'value'),
             Output('search-min-sqm', 'value'),
             Output('search-max-sqm', 'value'),
             Output('search-min-floor', 'value'),
             Output('search-max-floor', 'value')],
            [Input('init-trigger', 'data')],
            prevent_initial_call=False  # Allow initial call for auto-load
        )

    def _register_initialization_callback(self) -> None:
        """Register callback to trigger initialization once layout is loaded."""

        clientside_callback(
            """
            function(current_dataset) {
                // This callback fires once when the current-dataset store is created
                // We use it to trigger initialization logic
                return {'initialized': true};
            }
            """,
            Output('init-trigger', 'data'),
            Input('current-dataset', 'id'),
            prevent_initial_call=False
        )
