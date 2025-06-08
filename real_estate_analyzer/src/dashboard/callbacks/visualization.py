"""Visualization callback handlers for the dashboard."""

import pandas as pd
from dash import Input, Output
import dash
from typing import Tuple, Dict, Any

from src.analysis.filters import PropertyDataFilter
from src.analysis.statistical import StatisticalCalculator
from src.visualization.charts.factory import PropertyVisualizationFactory
from src.visualization.components.tables import PropertyTableComponents


class VisualizationCallbackManager:
    """Manages all visualization-related callbacks."""

    def __init__(self, app: dash.Dash):
        """
        Initialize the visualization callback manager.

        Args:
            app: Dash application instance
        """
        self.app = app

    def register_all_callbacks(self) -> None:
        """Register all visualization callbacks."""
        self._register_main_visualization_callback()

    def _register_main_visualization_callback(self) -> None:
        """Register the main visualization update callback."""

        @self.app.callback(
            [Output('price-sqm-scatter', 'figure'),
             Output('property-map', 'figure'),
             Output('price-histogram', 'figure'),
             Output('price-boxplot', 'figure'),
             Output('neighborhood-comparison', 'figure'),
             Output('room-efficiency', 'figure'),
             Output('neighborhood-ranking', 'figure'),
             Output('best-deals-table', 'children'),
             Output('market-insights', 'children'),
             Output('summary-stats', 'children')],
            [Input('price-range-slider', 'value'),
             Input('sqm-range-slider', 'value'),
             Input('neighborhood-filter', 'value'),
             Input('exclude-neighborhoods-filter', 'value'),
             Input('rooms-range-slider', 'value'),
             Input('floor-range-slider', 'value'),
             Input('condition-filter', 'value'),
             Input('ad-type-filter', 'value'),
             Input('current-dataset', 'data')]
        )
        def update_visualizations(price_range, sqm_range, neighborhood, exclude_neighborhoods,
                                  rooms, floors_range, condition, ad_type, current_data):
            """
            Update all visualizations based on filter changes.

            Args:
                price_range: Selected price range
                sqm_range: Selected square meters range
                neighborhood: Selected neighborhood
                exclude_neighborhoods: Neighborhoods to exclude
                rooms: Selected room range
                floors_range: Selected floor range
                condition: Selected property condition
                ad_type: Selected ad type
                current_data: Current property data

            Returns:
                Tuple of updated visualization components
            """
            print("DEBUG: Visualization callback triggered")
            print(f"DEBUG: current_data type: {type(current_data)}")
            print(f"DEBUG: current_data is None: {current_data is None}")
            print(
                f"DEBUG: current_data length: {len(current_data) if current_data else 'N/A'}")
            if current_data:
                print(
                    f"DEBUG: First few items: {current_data[:2] if len(current_data) >= 2 else current_data}")
            try:
                # Convert current data back to DataFrame
                if not current_data:
                    print(
                        "DEBUG: No current data available, returning empty visualizations")
                    # Return empty visualizations if no data
                    return self._get_empty_visualizations()

                df = pd.DataFrame(current_data)
                print(
                    f"DEBUG: Created DataFrame with {len(df)} rows and columns: {list(df.columns)}")

                # Apply filters to data
                filter_params = {
                    'price_range': price_range,
                    'sqm_range': sqm_range,
                    'neighborhood': neighborhood,
                    'exclude_neighborhoods': exclude_neighborhoods,
                    'rooms': rooms,
                    'floors': floors_range,
                    'condition': condition,
                    'ad_type': ad_type
                }

                # Filter the data
                data_filter = PropertyDataFilter(df)
                filtered_df = data_filter.apply_all_filters(filter_params)
                print(
                    f"DEBUG: After filtering: {len(filtered_df)} properties remain")

                # If no data after filtering, return empty visualizations
                if filtered_df.empty:
                    print(
                        "DEBUG: No data after filtering, returning empty visualizations")
                    return self._get_empty_visualizations()

                # Create visualization factory with filtered data
                viz_factory = PropertyVisualizationFactory(filtered_df)

                # Generate all charts
                charts = viz_factory.create_all_charts()

                # Create table components
                table_components = PropertyTableComponents(filtered_df)

                # Generate summary statistics
                stats_calculator = StatisticalCalculator(filtered_df)
                summary_stats = stats_calculator.calculate_summary_statistics()

                # Count new properties
                new_count = filtered_df.get(
                    'is_new', pd.Series([False] * len(filtered_df))).sum()

                # Return all visualizations
                return (
                    charts['scatter_plot'],
                    charts['map_view'],
                    charts['price_histogram'],
                    charts['price_boxplot'],
                    charts['neighborhood_comparison'],
                    charts['room_efficiency'],
                    charts['neighborhood_ranking'],
                    charts['best_deals_table'],
                    charts['market_insights'],
                    self._create_summary_stats_display(
                        summary_stats, len(filtered_df), new_count)
                )

            except Exception as e:
                print(f"ERROR in visualization callback: {str(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                return self._get_empty_visualizations()

    def _get_empty_visualizations(self) -> Tuple:
        """
        Get empty visualization components when no data is available.

        Returns:
            Tuple of empty visualization components
        """
        from src.visualization.charts.utils import ChartUtils
        from dash import html

        empty_figure = ChartUtils.create_empty_figure("No data available")
        empty_div = html.Div("No data available to display",
                             style={'textAlign': 'center', 'padding': '20px', 'color': '#666'})

        return (
            empty_figure,  # scatter plot
            empty_figure,  # map
            empty_figure,  # histogram
            empty_figure,  # boxplot
            empty_figure,  # neighborhood comparison
            empty_figure,  # room efficiency
            empty_figure,  # neighborhood ranking
            empty_div,     # best deals table
            empty_div,     # market insights
            empty_div      # summary stats
        )

    def _create_summary_stats_display(self, stats: Dict[str, Any], data_count: int, new_count: int = 0) -> Any:
        """
        Create the summary statistics display component.

        Args:
            stats: Summary statistics dictionary
            data_count: Number of properties in current view
            new_count: Number of new properties in current view

        Returns:
            HTML component with summary statistics
        """
        from dash import html
        from src.config.styles import SummaryStyles

        if not stats:
            return html.Div("No statistics available",
                            style={'textAlign': 'center', 'padding': '20px', 'color': '#666'})

        # Extract key statistics with correct nested structure
        price_stats = stats.get('price_stats', {})
        size_stats = stats.get('size_stats', {})
        efficiency_stats = stats.get('efficiency_stats', {})
        data_quality = stats.get('data_quality', {})

        return html.Div([
            html.Div([
                # Data count card
                html.Div([
                    html.H4("Properties", style=SummaryStyles.LABEL),
                    html.P(f"{data_count:,}", style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

                # New properties card
                html.Div([
                    html.H4("New ⭐", style=SummaryStyles.LABEL),
                    html.P(f"{new_count:,}", style={**SummaryStyles.VALUE,
                           'color': '#28a745' if new_count > 0 else SummaryStyles.VALUE.get('color', '#333')})
                ], style=SummaryStyles.CARD),

                # Average price card
                html.Div([
                    html.H4("Avg Price", style=SummaryStyles.LABEL),
                    html.P(f"₪{price_stats.get('avg_price', 0):,.0f}",
                           style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

                # Price per SQM card
                html.Div([
                    html.H4("Avg Price/SQM", style=SummaryStyles.LABEL),
                    html.P(
                        f"₪{price_stats.get('avg_price_per_sqm', 0):,.0f}", style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

                # Average size card
                html.Div([
                    html.H4("Avg Size", style=SummaryStyles.LABEL),
                    html.P(f"{size_stats.get('avg_size', 0):.0f}m²",
                           style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

                # Average rooms card
                html.Div([
                    html.H4("Avg Rooms", style=SummaryStyles.LABEL),
                    html.P(f"{size_stats.get('avg_rooms', 0):.1f}",
                           style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

                # Data quality card
                html.Div([
                    html.H4("Data Quality", style=SummaryStyles.LABEL),
                    html.P(
                        f"{data_quality.get('completeness_score', 0):.0f}%", style=SummaryStyles.VALUE)
                ], style=SummaryStyles.CARD),

            ], style=SummaryStyles.CONTAINER)
        ])
