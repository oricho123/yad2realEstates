"""Interactive map visualization component for property data."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional

from src.config.constants import MapConfiguration, ChartConfiguration
from src.visualization.hover_data import MapHoverData, HoverTemplate
from src.utils import TrendAnalyzer


class PropertyMapView:
    """Interactive map visualization for property locations."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property data."""
        self.data = data
        self.config = MapConfiguration()

    def create_map_figure(self) -> go.Figure:
        """
        Create an interactive map visualization of properties.

        Returns:
            go.Figure: Plotly figure with property map
        """
        if len(self.data) == 0:
            return self._create_empty_map("No data available for map")

        # Filter out properties without coordinates
        map_df = self.data.dropna(subset=['lat', 'lng']).copy()

        if len(map_df) == 0:
            return self._create_empty_map("No properties with location data")

        # Add market value analysis to the data
        map_df = self._add_value_analysis(map_df)

        # Create the scatter mapbox plot with value score coloring
        fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lng',
            color='value_score',
            size='rooms',
            size_max=ChartConfiguration.SCATTER_SIZE_MAX,
            hover_data=['neighborhood', 'price', 'square_meters', 'rooms',
                        'condition_text', 'value_category', 'savings_amount'],
            color_continuous_scale='thermal',
            color_continuous_midpoint=0,  # Center the scale at 0
            zoom=self.config.DEFAULT_ZOOM,
            height=self.config.DEFAULT_HEIGHT,
            labels={
                'value_score': 'Market Value Score (%)',
                'lat': 'Latitude',
                'lng': 'Longitude',
                'value_category': 'Value Category'
            }
        )

        # Update layout for better appearance
        center_lat, center_lon = self._calculate_map_center(map_df)
        fig.update_layout(
            mapbox_style=self.config.MAPBOX_STYLE,
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=self.config.DEFAULT_ZOOM
            ),
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            title={
                'text': 'Property Locations by Market Value Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            coloraxis_colorbar=dict(
                title="Value Score (%)",
                title_font=dict(size=13),
                tickfont=dict(size=11),
                ticksuffix="%"
            )
        )

        # Add custom hover template and click functionality
        self._update_hover_template(fig, map_df)

        return fig

    def _add_value_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market value analysis to the map data."""
        try:
            # Use centralized LOWESS-based value analysis
            return TrendAnalyzer.calculate_complete_value_analysis(df)
        except Exception as e:
            # Fallback: add empty value analysis columns
            result_df = df.copy()
            result_df['value_score'] = 0
            result_df['value_category'] = 'Unknown'
            result_df['predicted_price'] = df.get('price', 0)
            result_df['savings_amount'] = 0
            return result_df

    def _create_empty_map(self, message: str) -> go.Figure:
        """Create an empty map with a message."""
        fig = go.Figure()
        fig.update_layout(
            title=message,
            geo=dict(projection_type='natural earth'),
            height=self.config.DEFAULT_HEIGHT
        )
        return fig

    def _calculate_map_center(self, map_df: pd.DataFrame) -> tuple[float, float]:
        """Calculate the center point for the map."""
        center_lat = map_df['lat'].mean()
        center_lon = map_df['lng'].mean()

        # Use default center if calculation fails
        if pd.isna(center_lat) or pd.isna(center_lon):
            center_lat = self.config.DEFAULT_CENTER_LAT
            center_lon = self.config.DEFAULT_CENTER_LNG

        return center_lat, center_lon

    def _update_hover_template(self, fig: go.Figure, map_df: pd.DataFrame) -> None:
        """Update the hover template with custom data."""
        # Create structured hover data objects
        hover_data_objects = [MapHoverData.from_row(
            row) for _, row in map_df.iterrows()]

        # Convert to list format for Plotly
        custom_data = [hover_data.to_list()
                       for hover_data in hover_data_objects]

        # Update traces with custom hover template
        fig.update_traces(
            customdata=custom_data,
            hovertemplate=HoverTemplate.build_map_hover_template(),
            text=map_df['square_meters']
        )

    def get_property_locations_summary(self) -> Dict[str, Any]:
        """Get summary statistics about property locations."""
        if len(self.data) == 0:
            return {'total_properties': 0, 'with_location': 0, 'coverage_percentage': 0}

        total_properties = len(self.data)
        with_location = len(self.data.dropna(subset=['lat', 'lng']))
        coverage_percentage = (
            with_location / total_properties) * 100 if total_properties > 0 else 0

        return {
            'total_properties': total_properties,
            'with_location': with_location,
            'coverage_percentage': round(coverage_percentage, 1)
        }

    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> bool:
        """Validate if coordinates are reasonable for the region."""
        # Basic validation for Israel coordinates
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return False

        # More specific validation for Israel region
        israel_bounds = {
            'lat_min': 29.5, 'lat_max': 33.4,
            'lng_min': 34.3, 'lng_max': 35.9
        }

        return (israel_bounds['lat_min'] <= lat <= israel_bounds['lat_max'] and
                israel_bounds['lng_min'] <= lng <= israel_bounds['lng_max'])
