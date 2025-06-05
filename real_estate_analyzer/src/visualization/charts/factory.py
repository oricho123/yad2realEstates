"""Chart factory for creating all types of property visualizations."""

import pandas as pd
from typing import Dict, Any, Optional, Union, List
import plotly.graph_objects as go
from dash import html

from .map_view import PropertyMapView
from .scatter_plot import PropertyScatterPlot
from .analytics import PropertyAnalyticsCharts
from ..components.tables import PropertyTableComponents


class PropertyVisualizationFactory:
    """Factory class for creating all types of property visualizations."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the factory with property data.
        
        Args:
            data: DataFrame or PropertyDataFrame containing property listings
        """
        # Extract underlying DataFrame if it's a PropertyDataFrame
        if hasattr(data, 'data'):
            self.data = data.data
        else:
            self.data = data
        
        # Initialize component classes
        self.map_view = PropertyMapView(self.data)
        self.scatter_plot = PropertyScatterPlot(self.data)
        self.analytics = PropertyAnalyticsCharts(self.data)
        self.tables = PropertyTableComponents(self.data)

    def create_all_charts(self) -> Dict[str, Union[go.Figure, html.Div]]:
        """
        Create all chart types at once.
        
        Returns:
            Dict containing all chart figures and components
        """
        if len(self.data) == 0:
            return self._create_empty_dashboard()
        
        # Create all main visualizations
        charts = {}
        
        # Main visualizations
        charts['scatter_plot'] = self.scatter_plot.create_enhanced_scatter_plot()
        charts['map_view'] = self.map_view.create_map_figure()
        
        # Analytics charts
        analytics_charts = self.analytics.create_analytics_dashboard()
        charts.update(analytics_charts)
        
        # Table components
        charts['best_deals_table'] = self.tables.create_best_deals_table()
        charts['market_insights'] = self.tables.create_market_insights_summary()
        charts['summary_stats'] = self.tables.create_summary_statistics_cards()
        
        return charts

    def create_chart_by_type(self, chart_type: str, **kwargs) -> Union[go.Figure, html.Div]:
        """
        Create a specific chart type.
        
        Args:
            chart_type: Type of chart to create
            **kwargs: Additional parameters for chart creation
            
        Returns:
            Chart figure or HTML component
        """
        chart_creators = {
            'scatter_plot': self.scatter_plot.create_enhanced_scatter_plot,
            'map_view': self.map_view.create_map_figure,
            'price_histogram': self.analytics.create_price_histogram,
            'price_boxplot': self.analytics.create_price_boxplot,
            'neighborhood_comparison': self.analytics.create_neighborhood_comparison,
            'room_efficiency': self.analytics.create_room_efficiency_chart,
            'neighborhood_ranking': self.analytics.create_neighborhood_ranking,
            'best_deals_table': self.tables.create_best_deals_table,
            'market_insights': self.tables.create_market_insights_summary,
            'summary_stats': self.tables.create_summary_statistics_cards
        }
        
        if chart_type not in chart_creators:
            raise ValueError(f"Unknown chart type: {chart_type}")
        
        creator = chart_creators[chart_type]
        
        # Pass kwargs if the function accepts them
        try:
            return creator(**kwargs)
        except TypeError:
            # Function doesn't accept kwargs, call without them
            return creator()

    def get_chart_dependencies(self) -> Dict[str, Any]:
        """
        Get information about chart dependencies and data requirements.
        
        Returns:
            Dict with dependency information
        """
        return {
            'total_properties': len(self.data),
            'has_location_data': self._has_location_data(),
            'has_neighborhood_data': self._has_neighborhood_data(),
            'data_quality': self._assess_data_quality(),
            'supported_charts': self._get_supported_charts()
        }

    def update_data(self, new_data: pd.DataFrame) -> None:
        """
        Update the data for all chart components.
        
        Args:
            new_data: New property data
        """
        self.data = new_data
        
        # Update all component instances
        self.map_view = PropertyMapView(new_data)
        self.scatter_plot = PropertyScatterPlot(new_data)
        self.analytics = PropertyAnalyticsCharts(new_data)
        self.tables = PropertyTableComponents(new_data)

    def get_chart_summaries(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary information for all chart types.
        
        Returns:
            Dict with summary info for each chart type
        """
        summaries = {}
        
        if len(self.data) > 0:
            summaries['map_view'] = self.map_view.get_property_locations_summary()
            summaries['scatter_plot'] = self.scatter_plot.get_value_analysis_summary()
            summaries['analytics'] = self.analytics.get_analytics_summary()
        
        return summaries

    def _create_empty_dashboard(self) -> Dict[str, Union[go.Figure, html.Div]]:
        """Create empty charts when no data is available."""
        from .utils import ChartUtils
        
        empty_fig = ChartUtils.create_empty_figure("No data available")
        empty_div = html.Div("No data available for analysis")
        
        return {
            'scatter_plot': empty_fig,
            'map_view': empty_fig,
            'price_histogram': empty_fig,
            'price_boxplot': empty_fig,
            'neighborhood_comparison': empty_fig,
            'room_efficiency': empty_fig,
            'neighborhood_ranking': empty_fig,
            'best_deals_table': empty_div,
            'market_insights': empty_div,
            'summary_stats': empty_div
        }

    def _has_location_data(self) -> bool:
        """Check if data has location information."""
        if len(self.data) == 0:
            return False
        
        return not self.data[['lat', 'lng']].isna().all().all()

    def _has_neighborhood_data(self) -> bool:
        """Check if data has neighborhood information."""
        if len(self.data) == 0:
            return False
        
        return 'neighborhood' in self.data.columns and not self.data['neighborhood'].isna().all()

    def _assess_data_quality(self) -> Dict[str, Any]:
        """Assess the quality of the data for visualization."""
        if len(self.data) == 0:
            return {'quality_score': 0, 'issues': ['No data available']}
        
        issues = []
        quality_score = 100
        
        # Check for required columns
        required_columns = ['price', 'square_meters', 'price_per_sqm']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
            quality_score -= 30
        
        # Check for missing data
        if not missing_columns:
            missing_data_pct = self.data[required_columns].isna().sum().sum() / (len(self.data) * len(required_columns)) * 100
            if missing_data_pct > 5:
                issues.append(f"High missing data percentage: {missing_data_pct:.1f}%")
                quality_score -= 20
        
        # Check for location data
        if not self._has_location_data():
            issues.append("No location data available for map visualization")
            quality_score -= 15
        
        # Check for neighborhood data
        if not self._has_neighborhood_data():
            issues.append("No neighborhood data available for neighborhood analysis")
            quality_score -= 10
        
        # Check data volume
        if len(self.data) < 10:
            issues.append("Insufficient data for meaningful analysis")
            quality_score -= 25
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'total_properties': len(self.data),
            'completeness': self._calculate_completeness()
        }

    def _calculate_completeness(self) -> Dict[str, float]:
        """Calculate data completeness for key fields."""
        if len(self.data) == 0:
            return {}
        
        completeness = {}
        key_fields = ['price', 'square_meters', 'neighborhood', 'lat', 'lng', 'rooms', 'condition_text']
        
        for field in key_fields:
            if field in self.data.columns:
                completeness[field] = (1 - self.data[field].isna().sum() / len(self.data)) * 100
            else:
                completeness[field] = 0
        
        return completeness

    def _get_supported_charts(self) -> List[str]:
        """Get list of supported chart types based on available data."""
        base_charts = ['scatter_plot', 'price_histogram', 'summary_stats', 'market_insights']
        
        if self._has_location_data():
            base_charts.append('map_view')
        
        if self._has_neighborhood_data():
            base_charts.extend(['price_boxplot', 'neighborhood_comparison', 'neighborhood_ranking'])
        
        if len(self.data) >= 5:  # Need minimum data for value analysis
            base_charts.append('best_deals_table')
        
        if 'rooms' in self.data.columns and not self.data['rooms'].isna().all():
            base_charts.append('room_efficiency')
        
        return base_charts

    @staticmethod
    def get_available_chart_types() -> Dict[str, str]:
        """Get all available chart types and their descriptions."""
        return {
            'scatter_plot': 'Enhanced scatter plot with trend analysis and value scoring',
            'map_view': 'Interactive map showing property locations and prices',
            'price_histogram': 'Price distribution histogram',
            'price_boxplot': 'Price per square meter distribution by neighborhood',
            'neighborhood_comparison': 'Average property prices by neighborhood',
            'room_efficiency': 'Room efficiency analysis (square meters per room)',
            'neighborhood_ranking': 'Neighborhood affordability ranking',
            'best_deals_table': 'Table of properties with best value scores',
            'market_insights': 'Market analysis summary and recommendations',
            'summary_stats': 'Summary statistics cards'
        } 