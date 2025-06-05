"""Search components for new property data scraping."""

from dash import html, dcc
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
                       style={'margin-right': '10px'}),
                "Search New Properties"
            ], style=DashboardStyles.SEARCH_HEADER),

            html.Div([
                # City selection
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marker-alt",
                               style={'margin-right': '5px'}),
                        "City:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='search-city-dropdown',
                        options=self.city_options,
                        value=9500,  # Default to Kiryat Bialik
                        clearable=False,
                        style={'border-radius': '8px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Area selection dropdown
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map",
                               style={'margin-right': '5px'}),
                        "Area:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='search-area',
                        options=self.area_options,
                        # Default to area code 6 (matches Kiryat Bialik area_code)
                        value=6,
                        clearable=True,
                        placeholder="Select area...",
                        style={'border-radius': '8px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Price range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign",
                               style={'margin-right': '5px'}),
                        "Min Price:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-price',
                        type='number',
                        value=1000000,
                        step=25000,
                        placeholder=PriceInputFormatter.format_placeholder(
                            1000000),
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    )
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign",
                               style={'margin-right': '5px'}),
                        "Max Price:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-price',
                        type='number',
                        value=2000000,
                        step=25000,
                        placeholder=PriceInputFormatter.format_placeholder(
                            2000000),
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    )
                ], style=DashboardStyles.SEARCH_FILTER),

                # Room range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed",
                               style={'margin-right': '5px'}),
                        "Min Rooms:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-rooms',
                        type='number',
                        value=1,
                        placeholder="Min Rooms",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed",
                               style={'margin-right': '5px'}),
                        "Max Rooms:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-rooms',
                        type='number',
                        value=10,
                        placeholder="Max Rooms",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Square meters range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined",
                               style={'margin-right': '5px'}),
                        "Min SQM:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-sqm',
                        type='number',
                        value=30,
                        placeholder="Min Square Meters",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined",
                               style={'margin-right': '5px'}),
                        "Max SQM:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-sqm',
                        type='number',
                        value=300,
                        placeholder="Max Square Meters",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Floor range inputs
                html.Div([
                    html.Label([
                        html.I(className="fas fa-building",
                               style={'margin-right': '5px'}),
                        "Min Floor:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-min-floor',
                        type='number',
                        value=None,
                        placeholder="Min Floor",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                html.Div([
                    html.Label([
                        html.I(className="fas fa-building",
                               style={'margin-right': '5px'}),
                        "Max Floor:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Input(
                        id='search-max-floor',
                        type='number',
                        value=None,
                        placeholder="Max Floor",
                        style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                               'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                ], style=DashboardStyles.SEARCH_FILTER),

                # Search button
                html.Div([
                    html.Button([
                        html.Span(id='scrape-button-icon', className="fas fa-search",
                                  style={'margin-right': '8px'}),
                        html.Span(id='scrape-button-text',
                                  children="Search Properties")
                    ],
                        id='scrape-button',
                        n_clicks=0,
                        style=DashboardStyles.SCRAPE_BUTTON,
                        className="button-hover"
                    ),
                ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})

            ], style=DashboardStyles.SEARCH_CONTROLS),

            # Search status display
            html.Div(id='scrape-status',
                     style={'margin-top': '15px', 'text-align': 'center'})

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
