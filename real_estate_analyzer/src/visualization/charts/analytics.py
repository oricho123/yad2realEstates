"""Analytics charts component for advanced property insights."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional

from src.config.constants import ChartConfiguration, ValueAnalysisConstants
from src.visualization.hover_data import AnalyticsHoverData, HoverTemplate


class PropertyAnalyticsCharts:
    """Advanced analytics charts for deeper property insights."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property data."""
        self.data = data

    def create_analytics_dashboard(self) -> Dict[str, go.Figure]:
        """
        Create complete analytics dashboard with multiple chart types.

        Returns:
            Dict[str, go.Figure]: Dictionary of chart names to figures
        """
        if len(self.data) == 0:
            return self._create_empty_charts()

        analytics_df = self.data.copy()

        return {
            'price_histogram': self.create_price_histogram(analytics_df),
            'price_boxplot': self.create_price_boxplot(analytics_df),
            'neighborhood_comparison': self.create_neighborhood_comparison(analytics_df),
            'room_efficiency': self.create_room_efficiency_chart(analytics_df),
            'neighborhood_ranking': self.create_neighborhood_ranking(analytics_df)
        }

    def create_price_histogram(self, df: pd.DataFrame = None) -> go.Figure:
        """Create price distribution histogram."""
        if df is None:
            df = self.data

        if len(df) == 0:
            return self._create_empty_figure("Price Distribution - No data available")

        fig = px.histogram(
            df,
            x='price',
            nbins=20,
            title='Property Price Distribution',
            labels={'price': 'Price (₪)', 'count': 'Number of Properties'},
            color_discrete_sequence=['#667eea']
        )

        fig.update_layout(
            xaxis_title='Price (₪)',
            yaxis_title='Number of Properties',
            bargap=0.1,
            title_x=0.5,
            height=ChartConfiguration.DEFAULT_HEIGHT
        )

        return fig

    def create_price_boxplot(self, df: pd.DataFrame = None) -> go.Figure:
        """Create price per SQM box plot by neighborhood."""
        if df is None:
            df = self.data

        if len(df) == 0 or 'neighborhood' not in df.columns:
            return self._create_empty_figure("Price/SQM Distribution - No data available")

        if len(df['neighborhood'].unique()) <= 1:
            return self._create_empty_figure("Need multiple neighborhoods for comparison")

        # Limit to top 8 neighborhoods by count to avoid clutter
        top_neighborhoods = df['neighborhood'].value_counts().head(8).index
        boxplot_df = df[df['neighborhood'].isin(top_neighborhoods)]

        fig = px.box(
            boxplot_df,
            x='neighborhood',
            y='price_per_sqm',
            title='Price/SQM Distribution by Neighborhood',
            labels={
                'price_per_sqm': 'Price per SQM (₪)', 'neighborhood': 'Neighborhood'},
            color='neighborhood',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_layout(
            xaxis_title='Neighborhood',
            yaxis_title='Price per SQM (₪)',
            xaxis={'tickangle': 45},
            title_x=0.5,
            height=ChartConfiguration.DEFAULT_HEIGHT,
            showlegend=False
        )

        return fig

    def create_neighborhood_comparison(self, df: pd.DataFrame = None) -> go.Figure:
        """Create neighborhood comparison chart."""
        if df is None:
            df = self.data

        if len(df) == 0 or 'neighborhood' not in df.columns:
            return self._create_empty_figure("Neighborhood Comparison - No data available")

        # Calculate neighborhood statistics
        neighborhood_stats = df.groupby('neighborhood').agg({
            'price': 'mean',
            'price_per_sqm': 'mean',
            'square_meters': 'mean'
        }).round(0).reset_index()

        # Filter neighborhoods with enough data
        property_counts = df['neighborhood'].value_counts()
        neighborhood_stats['property_count'] = neighborhood_stats['neighborhood'].map(
            property_counts)
        neighborhood_stats = neighborhood_stats[neighborhood_stats['property_count']
                                                >= ValueAnalysisConstants.MIN_PROPERTIES_FOR_RANKING]

        if len(neighborhood_stats) == 0:
            return self._create_empty_figure("Not enough data for neighborhood comparison")

        fig = px.bar(
            neighborhood_stats,
            x='neighborhood',
            y='price',
            color='price_per_sqm',
            title='Average Property Price by Neighborhood',
            labels={
                'price': 'Average Price (₪)', 'neighborhood': 'Neighborhood', 'price_per_sqm': 'Avg Price/SQM'},
            color_continuous_scale='viridis'
        )

        fig.update_layout(
            xaxis={'tickangle': 45},
            title_x=0.5,
            height=ChartConfiguration.DEFAULT_HEIGHT
        )

        return fig

    def create_room_efficiency_chart(self, df: pd.DataFrame = None) -> go.Figure:
        """Create room efficiency analysis chart."""
        if df is None:
            df = self.data

        if len(df) == 0:
            return self._create_empty_figure("Room Efficiency - No data available")

        # Calculate room efficiency (sqm per room)
        efficiency_df = df.copy()
        efficiency_df['sqm_per_room'] = efficiency_df['square_meters'] / \
            efficiency_df['rooms']
        efficiency_df = efficiency_df.dropna(subset=['sqm_per_room'])

        if len(efficiency_df) == 0:
            return self._create_empty_figure("No room efficiency data available")

        fig = px.scatter(
            efficiency_df,
            x='rooms',
            y='sqm_per_room',
            color='price_per_sqm',
            size='square_meters',
            title='Room Efficiency Analysis',
            labels={
                'rooms': 'Number of Rooms',
                'sqm_per_room': 'Square Meters per Room',
                'price_per_sqm': 'Price/SQM (₪)'
            },
            color_continuous_scale='viridis'
        )

        fig.update_layout(
            title_x=0.5,
            height=ChartConfiguration.DEFAULT_HEIGHT
        )

        return fig

    def create_neighborhood_ranking(self, df: pd.DataFrame = None) -> go.Figure:
        """Create neighborhood affordability ranking chart."""
        if df is None:
            df = self.data

        if len(df) == 0 or 'neighborhood' not in df.columns:
            return self._create_empty_figure("Neighborhood Ranking - No data available")

        # Calculate neighborhood statistics
        neighborhood_stats = df.groupby('neighborhood').agg({
            'price': ['mean', 'median', 'count'],
            'price_per_sqm': ['mean', 'median'],
            'square_meters': 'mean',
            'rooms': 'mean'
        }).round(0)

        # Flatten column names
        neighborhood_stats.columns = ['avg_price', 'median_price', 'count',
                                      'avg_price_per_sqm', 'median_price_per_sqm', 'avg_size', 'avg_rooms']
        neighborhood_stats = neighborhood_stats.reset_index()

        # Filter neighborhoods with sufficient data
        neighborhood_stats = neighborhood_stats[neighborhood_stats['count']
                                                >= ValueAnalysisConstants.MIN_PROPERTIES_FOR_RANKING]

        if len(neighborhood_stats) == 0:
            return self._create_empty_figure("Not enough data for neighborhood ranking")

        # Calculate real affordability score
        max_avg_price = neighborhood_stats['avg_price'].max()
        min_avg_price = neighborhood_stats['avg_price'].min()

        if max_avg_price == min_avg_price:
            neighborhood_stats['affordability_score'] = 50  # Default score
        else:
            neighborhood_stats['affordability_score'] = (
                (max_avg_price - neighborhood_stats['avg_price']) / (max_avg_price - min_avg_price) * 100)

        # Add efficiency scoring
        overall_avg_size = df['square_meters'].mean()
        neighborhood_stats['size_adjusted_price_per_sqm'] = neighborhood_stats['avg_price_per_sqm'] * (
            neighborhood_stats['avg_size'] / overall_avg_size)

        max_adjusted_price_per_sqm = neighborhood_stats['size_adjusted_price_per_sqm'].max(
        )
        min_adjusted_price_per_sqm = neighborhood_stats['size_adjusted_price_per_sqm'].min(
        )

        if max_adjusted_price_per_sqm == min_adjusted_price_per_sqm:
            efficiency_score = 50
        else:
            efficiency_score = ((max_adjusted_price_per_sqm - neighborhood_stats['size_adjusted_price_per_sqm']) / (
                max_adjusted_price_per_sqm - min_adjusted_price_per_sqm) * 100)

        # Combined affordability score
        neighborhood_stats['real_affordability_score'] = (
            neighborhood_stats['affordability_score'] * ValueAnalysisConstants.AFFORDABILITY_WEIGHT +
            efficiency_score * ValueAnalysisConstants.EFFICIENCY_WEIGHT
        )

        # Sort by affordability score
        neighborhood_stats = neighborhood_stats.sort_values(
            'real_affordability_score', ascending=False)

        # Create ranking chart
        fig = px.bar(
            neighborhood_stats.head(10),
            x='neighborhood',
            y='avg_price',
            color='real_affordability_score',
            title='Real Neighborhood Affordability Ranking',
            labels={
                'avg_price': 'Average Total Price (₪)',
                'neighborhood': 'Neighborhood',
                'real_affordability_score': 'Real Affordability Score'
            },
            color_continuous_scale='RdYlGn',
            text='count'
        )

        # Add property count as text
        fig.update_traces(
            texttemplate='%{text} properties', textposition="outside")

        # Create structured hover data
        analytics_hover_data = [
            AnalyticsHoverData(
                avg_size=row['avg_size'],
                avg_price_per_sqm=row['avg_price_per_sqm']
            )
            for _, row in neighborhood_stats.head(10).iterrows()
        ]

        # Convert to list format for Plotly
        custom_data = [hover_data.to_list()
                       for hover_data in analytics_hover_data]

        # Add comprehensive hover data
        fig.update_traces(
            hovertemplate=HoverTemplate.build_analytics_hover_template(),
            customdata=custom_data
        )

        fig.update_layout(
            xaxis={'tickangle': 45},
            height=400,
            title_x=0.5,
            showlegend=False
        )

        return fig

    def _create_empty_charts(self) -> Dict[str, go.Figure]:
        """Create empty charts when no data is available."""
        return {
            'price_histogram': self._create_empty_figure("Price Distribution - No data available"),
            'price_boxplot': self._create_empty_figure("Price/SQM Distribution - No data available"),
            'neighborhood_comparison': self._create_empty_figure("Neighborhood Comparison - No data available"),
            'room_efficiency': self._create_empty_figure("Room Efficiency - No data available"),
            'neighborhood_ranking': self._create_empty_figure("Neighborhood Ranking - No data available")
        }

    def _create_empty_figure(self, title: str) -> go.Figure:
        """Create an empty figure with a title."""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="",
            yaxis_title="",
            height=ChartConfiguration.DEFAULT_HEIGHT,
            showlegend=False
        )
        return fig

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary statistics for analytics dashboard."""
        if len(self.data) == 0:
            return {'total_properties': 0, 'analytics_available': False}

        return {
            'total_properties': len(self.data),
            'analytics_available': True,
            'unique_neighborhoods': self.data['neighborhood'].nunique() if 'neighborhood' in self.data.columns else 0,
            'price_range': {
                'min': self.data['price'].min(),
                'max': self.data['price'].max(),
                'mean': self.data['price'].mean()
            },
            'size_range': {
                'min': self.data['square_meters'].min(),
                'max': self.data['square_meters'].max(),
                'mean': self.data['square_meters'].mean()
            }
        }
