"""Search components for new property data scraping."""

from dash import html, dcc, clientside_callback, Input, Output
from typing import List, Dict, Any

from src.config.styles import DashboardStyles
from src.config.constants import CityOptions, AreaOptions
from src.utils.formatters import PriceInputFormatter


class SearchComponentManager:
    """Manages search form components for property data scraping."""

    def __init__(self):
        """Initialize the search component manager."""
        self.city_options = self._get_city_options()
        self.area_options = self._get_area_options()

    def create_search_section(self) -> html.Div:
        """
        Create the complete search controls section.

        Returns:
            Search section with all controls
        """
        return html.Div([
            html.Div([
                html.I(className="fas fa-search",
                       style={'marginRight': '10px'}),
                "Search New Properties"
            ], style=DashboardStyles.SEARCH_HEADER),

            html.Div([
                # Location autocomplete section
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marker-alt",
                               style={'marginRight': '5px'}),
                        "Location:"
                    ], style=DashboardStyles.LABEL),
                    html.Div(id="autocomplete-container",
                             style={'position': 'relative'}),
                    # Store for selected location
                    dcc.Store(id="location-selection-store"),
                    dcc.Input(id="dummy-autocomplete-trigger",
                              style={"display": "none"}),  # Hidden input to trigger JS init
                ], style=DashboardStyles.SEARCH_FILTER),

                # Price range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign",
                               style={'marginRight': '5px'}),
                        "Min Price:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-price',
                        type='number',
                        value=1000000,
                        step=25000,
                        placeholder=PriceInputFormatter.format_placeholder(
                            1000000),
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    )
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign",
                               style={'marginRight': '5px'}),
                        "Max Price:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-price',
                        type='number',
                        value=2000000,
                        step=25000,
                        placeholder=PriceInputFormatter.format_placeholder(
                            2000000),
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    )
                ], style=DashboardStyles.SEARCH_FILTER),

                # Room range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed",
                               style={'marginRight': '5px'}),
                        "Min Rooms:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-rooms',
                        type='number',
                        value=1,
                        placeholder="Min Rooms",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed",
                               style={'marginRight': '5px'}),
                        "Max Rooms:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-rooms',
                        type='number',
                        value=10,
                        placeholder="Max Rooms",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Square meters range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined",
                               style={'marginRight': '5px'}),
                        "Min SQM:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-sqm',
                        type='number',
                        value=30,
                        placeholder="Min Square Meters",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined",
                               style={'marginRight': '5px'}),
                        "Max SQM:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-sqm',
                        type='number',
                        value=300,
                        placeholder="Max Square Meters",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Floor range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-building",
                               style={'marginRight': '5px'}),
                        "Min Floor:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-floor',
                        type='number',
                        value=None,
                        placeholder="Min Floor",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-building",
                               style={'marginRight': '5px'}),
                        "Max Floor:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-floor',
                        type='number',
                        value=None,
                        placeholder="Max Floor",
                        style={'width': '100%', 'padding': '12px', 'borderRadius': '8px',
                               'border': '2px solid #e9ecef', 'fontSize': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Search button
                html.Div([
                    html.Button([
                        html.Span(id='scrape-button-icon', className="fas fa-search",
                                  style={'marginRight': '8px'}),
                        html.Span(id='scrape-button-text',
                                  children="Search Properties")
                    ],
                        id='scrape-button',
                        n_clicks=0,
                        style=DashboardStyles.SCRAPE_BUTTON,
                        className="button-hover"
                    ),
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'})

            ], style=DashboardStyles.SEARCH_CONTROLS, className="search-controls-responsive"),

            # Search status display
            html.Div(id='scrape-status',
                     style={'marginTop': '15px', 'textAlign': 'center'})

        ], style=DashboardStyles.SEARCH_CONTAINER)

    def _get_city_options(self) -> List[Dict[str, Any]]:
        """
        Get city options for the dropdown from constants.

        Returns:
            List of city options with labels and values
        """
        return [
            {
                'label': f"{city['label']} (Area Code: {city['area_code']})",
                'value': city['value']
            }
            for city in CityOptions.CITIES
        ]

    def _get_area_options(self) -> List[Dict[str, Any]]:
        """
        Get area options for the dropdown from constants.

        Returns:
            List of area options with labels and values
        """
        options = []
        for area in AreaOptions.AREAS:
            # Convert None values to 'all' to avoid Dash dropdown issues
            value = area['value'] if area['value'] is not None else 'all'
            options.append({
                'label': area['label'],
                'value': value
            })
        return options

    def register_autocomplete_callbacks(self, app):
        """Register the autocomplete callbacks."""

        # Trigger JS initialization after layout renders
        clientside_callback(
            """
            function(container_id) {
                if (window.dash_clientside && window.dash_clientside.clientside) {
                    return window.dash_clientside.clientside.initAutocomplete(container_id);
                }
                return "";
            }
            """,
            Output("dummy-autocomplete-trigger", "value"),
            Input("autocomplete-container", "id")
        )

        # Handle location selection updates
        clientside_callback(
            """
            function(trigger_value) {
                // Listen for custom autocomplete selection events
                const input = document.getElementById("autocomplete-input");
                if (input && !input.hasAttribute('data-listener-added')) {
                    input.setAttribute('data-listener-added', 'true');
                    
                    input.addEventListener('autocomplete-selection', function(event) {
                        if (window.dash_clientside && window.dash_clientside.set_props) {
                            window.dash_clientside.set_props('location-selection-store', {
                                data: event.detail
                            });
                        }
                    });
                }
                return window.dash_clientside.no_update;
            }
            """,
            Output("location-selection-store", "data"),
            Input("dummy-autocomplete-trigger", "value"),
            prevent_initial_call=True
        )
