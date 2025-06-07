"""Filter components for dashboard data filtering."""
from src.utils.formatters import NumberFormatter

import pandas as pd
from dash import html, dcc
from typing import Dict, Any

from src.config.styles import DashboardStyles


class FilterComponentManager:
    """Manages filter components for property data filtering."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the filter component manager with data.

        Args:
            data: Property data to configure filter options
        """
        # Extract the underlying DataFrame if it's a PropertyDataFrame
        if hasattr(data, 'data'):
            self.data = data.data
        else:
            self.data = data
        self.filter_options = self._generate_filter_options()

    def create_filter_section(self) -> html.Div:
        """
        Create the complete filter controls section.

        Returns:
            Filter section with all controls
        """
        return html.Div([
            # Click instruction
            html.Div([
                html.I(className="fas fa-hand-pointer",
                       style={'marginRight': '8px'}),
                "Click on any point in the charts below to open the property listing on Yad2"
            ], style=DashboardStyles.CLICK_INSTRUCTION, className="fade-in"),

            # Filter controls grid
            html.Div([
                # Price range slider
                html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign",
                               style={'marginRight': '5px'}),
                        "Price Range:"
                    ], style=DashboardStyles.LABEL),
                    dcc.RangeSlider(
                        id='price-range-slider',
                        min=self.filter_options['price']['min'],
                        max=self.filter_options['price']['max'],
                        value=self.filter_options['price']['value'],
                        marks=self.filter_options['price']['marks'],
                        tooltip={'placement': 'bottom',
                                 'always_visible': True},
                        allowCross=False
                    )
                ], style=DashboardStyles.FILTER),

                # Square meters range slider
                html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined",
                               style={'marginRight': '5px'}),
                        "Size (SQM):"
                    ], style=DashboardStyles.LABEL),
                    dcc.RangeSlider(
                        id='sqm-range-slider',
                        min=self.filter_options['sqm']['min'],
                        max=self.filter_options['sqm']['max'],
                        value=self.filter_options['sqm']['value'],
                        marks=self.filter_options['sqm']['marks'],
                        tooltip={'placement': 'bottom',
                                 'always_visible': True},
                        allowCross=False
                    )
                ], style=DashboardStyles.FILTER),

                # Neighborhood filter
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marker-alt",
                               style={'marginRight': '5px'}),
                        "Neighborhood:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='neighborhood-filter',
                        options=self.filter_options['neighborhoods'],
                        value='all',
                        clearable=False
                    )
                ], style=DashboardStyles.FILTER),

                # Exclude neighborhoods filter
                html.Div([
                    html.Label([
                        html.I(className="fas fa-times-circle",
                               style={'marginRight': '5px'}),
                        "Exclude Areas:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='exclude-neighborhoods-filter',
                        options=self.filter_options['exclude_neighborhoods'],
                        value=[],
                        multi=True,
                        placeholder="Select areas to exclude..."
                    )
                ], style=DashboardStyles.FILTER),

                # Rooms range slider
                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed",
                               style={'marginRight': '5px'}),
                        "Number of Rooms:"
                    ], style=DashboardStyles.LABEL),
                    dcc.RangeSlider(
                        id='rooms-range-slider',
                        min=self.filter_options['rooms']['min'],
                        max=self.filter_options['rooms']['max'],
                        value=self.filter_options['rooms']['value'],
                        marks=self.filter_options['rooms']['marks'],
                        tooltip={'placement': 'bottom',
                                 'always_visible': True},
                        allowCross=False,
                        step=0.5
                    )
                ], style=DashboardStyles.FILTER),

                # Floor range slider
                html.Div([
                    html.Label([
                        html.I(className="fas fa-building",
                               style={'marginRight': '5px'}),
                        "Floor:"
                    ], style=DashboardStyles.LABEL),
                    dcc.RangeSlider(
                        id='floor-range-slider',
                        min=self.filter_options['floors']['min'],
                        max=self.filter_options['floors']['max'],
                        value=self.filter_options['floors']['value'],
                        marks=self.filter_options['floors']['marks'],
                        tooltip={'placement': 'bottom',
                                 'always_visible': True},
                        allowCross=False,
                        step=1
                    )
                ], style=DashboardStyles.FILTER),

                # Condition filter
                html.Div([
                    html.Label([
                        html.I(className="fas fa-hammer",
                               style={'marginRight': '5px'}),
                        "Property Condition:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='condition-filter',
                        options=self.filter_options['conditions'],
                        value='all',
                        clearable=False
                    )
                ], style=DashboardStyles.FILTER),

                # Ad type filter
                html.Div([
                    html.Label([
                        html.I(className="fas fa-user-tag",
                               style={'marginRight': '5px'}),
                        "Ad Type:"
                    ], style=DashboardStyles.LABEL),
                    dcc.Dropdown(
                        id='ad-type-filter',
                        options=self.filter_options['ad_types'],
                        value='all',
                        clearable=False
                    )
                ], style=DashboardStyles.FILTER),

            ], style=DashboardStyles.FILTER_CONTAINER, className="fade-in filter-container-responsive")

        ])

    def _generate_filter_options(self) -> Dict[str, Any]:
        """
        Generate filter options based on the data.

        Returns:
            Dictionary of filter options for all filters
        """
        # Handle both DataFrame and PropertyDataFrame
        if hasattr(self.data, 'is_empty'):
            is_empty = self.data.is_empty
        else:
            is_empty = self.data.empty

        if is_empty:
            return self._get_empty_filter_options()

        # Price range options
        price_min = int(self.data['price'].min())
        price_max = int(self.data['price'].max())
        price_step = max(10000, int((price_max - price_min) / 20))

        # Square meters options
        sqm_min = int(self.data['square_meters'].min())
        sqm_max = int(self.data['square_meters'].max())
        sqm_step = max(5, int((sqm_max - sqm_min) / 20))

        # Rooms options
        rooms_min = float(self.data['rooms'].min())
        rooms_max = float(self.data['rooms'].max())

        # Floor options - handle potential missing/null floor data
        floor_data = self.data['floor'].dropna()
        if not floor_data.empty:
            floor_min = int(floor_data.min())
            floor_max = int(floor_data.max())
        else:
            floor_min = 0
            floor_max = 40

        return {
            'price': {
                'min': price_min,
                'max': price_max,
                'value': [price_min, price_max],
                'marks': NumberFormatter.create_price_marks(price_min, price_max, num_marks=5)
            },
            'sqm': {
                'min': sqm_min,
                'max': sqm_max,
                'value': [sqm_min, sqm_max],
                'marks': NumberFormatter.create_number_marks(sqm_min, sqm_max, num_marks=5, suffix="m²")
            },
            'neighborhoods': [{'label': 'All Neighborhoods', 'value': 'all'}] + [
                {'label': n, 'value': n} for n in sorted(self.data['neighborhood'].dropna().unique())
            ],
            'exclude_neighborhoods': [
                {'label': n, 'value': n} for n in sorted(self.data['neighborhood'].dropna().unique())
            ],
            'rooms': {
                'min': rooms_min,
                'max': rooms_max,
                'value': [rooms_min, rooms_max],
                'marks': {i: str(i) for i in range(int(rooms_min), int(rooms_max) + 1)}
            },
            'floors': {
                'min': floor_min,
                'max': floor_max,
                'value': [floor_min, floor_max],
                # Limit marks to avoid clutter
                'marks': {i: str(i) for i in range(floor_min, min(floor_max + 1, floor_min + 21))}
            },
            'conditions': [{'label': 'All Conditions', 'value': 'all'}] + [
                {'label': ct, 'value': ct} for ct in sorted(self.data['condition_text'].dropna().unique())
            ],
            'ad_types': [{'label': 'All', 'value': 'all'}] + [
                {'label': at, 'value': at} for at in sorted(self.data['ad_type'].unique())
            ]
        }

    def _get_empty_filter_options(self) -> Dict[str, Any]:
        """
        Get default filter options when no data is available.

        Returns:
            Default filter options structure
        """
        return {
            'price': {
                'min': 0,
                'max': 5000000,
                'value': [0, 5000000],
                'marks': NumberFormatter.create_price_marks(0, 5000000, num_marks=5)
            },
            'sqm': {
                'min': 0,
                'max': 500,
                'value': [0, 500],
                'marks': NumberFormatter.create_number_marks(0, 500, num_marks=5, suffix="m²")
            },
            'neighborhoods': [{'label': 'All Neighborhoods', 'value': 'all'}],
            'exclude_neighborhoods': [],
            'rooms': {
                'min': 1,
                'max': 10,
                'value': [1, 10],
                'marks': {i: str(i) for i in range(1, 11)}
            },
            'floors': {
                'min': 0,
                'max': 20,
                'value': [0, 20],
                'marks': {i: str(i) for i in range(0, 21)}
            },
            'conditions': [{'label': 'All Conditions', 'value': 'all'}],
            'ad_types': [{'label': 'All', 'value': 'all'}]
        }
