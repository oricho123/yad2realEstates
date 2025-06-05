"""Enhanced scatter plot visualization component for property analysis."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from src.config.constants import ChartConfiguration, ValueAnalysisConstants
from src.visualization.hover_data import PropertyHoverData, HoverTemplate


class PropertyScatterPlot:
    """Enhanced scatter plot with trend analysis and value scoring."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property data."""
        self.data = data

    def create_enhanced_scatter_plot(self) -> go.Figure:
        """
        Create an enhanced scatter plot with trend lines, median lines, and value analysis.

        Returns:
            go.Figure: Plotly figure with enhanced scatter plot
        """
        if len(self.data) == 0:
            return px.scatter(title="No data available")

        # Prepare data with value analysis
        plot_df = self._prepare_plot_data()

        # Create the scatter plot
        fig = self._create_base_scatter_plot(plot_df)

        # Add enhancements
        self._add_trend_line(fig, plot_df)
        self._add_median_lines(fig, plot_df)
        self._update_styling_and_hover(fig, plot_df)

        return fig

    def _prepare_plot_data(self) -> pd.DataFrame:
        """Prepare data with value analysis and indexing."""
        plot_df = self.data.copy().reset_index(drop=True)
        plot_df['property_index'] = range(len(plot_df))
        return self._calculate_value_analysis(plot_df)

    def _create_base_scatter_plot(self, plot_df: pd.DataFrame) -> go.Figure:
        """Create the base scatter plot with color categories."""
        return px.scatter(
            plot_df,
            x='square_meters',
            y='price',
            color='value_category',
            size='rooms',
            size_max=ChartConfiguration.SIZE_MAX,
            color_discrete_map=self._get_value_category_colors(),
            labels={
                'square_meters': 'Square Meters',
                'price': 'Price (₪)',
                'value_category': 'Market Value Analysis'
            },
            title='Property Size vs Price with Market Value Analysis'
        )

    def _calculate_value_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend line and value scores for properties."""
        result_df = df.copy(deep=True)
        x, y = result_df['square_meters'].values, result_df['price'].values

        try:
            # Fit trend line and calculate value metrics
            z = np.polyfit(x, y, ValueAnalysisConstants.POLYNOMIAL_DEGREE)
            trend_line_y = np.poly1d(z)(x)

            result_df['predicted_price'] = trend_line_y
            result_df['value_score'] = (y - trend_line_y) / trend_line_y * 100
            result_df['savings_amount'] = trend_line_y - y
            result_df['value_category'] = result_df['value_score'].apply(
                self._categorize_property_value)

        except Exception:
            # Fallback if trend calculation fails
            result_df['value_score'] = 0
            result_df['value_category'] = 'Unknown'
            result_df['predicted_price'] = y.copy()
            result_df['savings_amount'] = 0

        return result_df

    def _categorize_property_value(self, value_score: float) -> str:
        """Categorize property based on value score."""
        thresholds = ValueAnalysisConstants
        if value_score < thresholds.EXCELLENT_DEAL_THRESHOLD:
            return 'Excellent Deal'
        elif value_score < thresholds.GOOD_DEAL_THRESHOLD:
            return 'Good Deal'
        elif value_score < thresholds.FAIR_PRICE_THRESHOLD:
            return 'Fair Price'
        elif value_score < thresholds.ABOVE_MARKET_THRESHOLD:
            return 'Above Market'
        else:
            return 'Overpriced'

    def _get_value_category_colors(self) -> Dict[str, str]:
        """Get color mapping for value categories."""
        return {
            'Excellent Deal': '#28a745',
            'Good Deal': '#20c997',
            'Fair Price': '#6c757d',
            'Above Market': '#fd7e14',
            'Overpriced': '#dc3545'
        }

    def _add_trend_line(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add trend line to the scatter plot."""
        if 'predicted_price' in df.columns:
            fig.add_scatter(
                x=df['square_meters'],
                y=df['predicted_price'],
                mode='lines',
                name='Market Trend',
                line=dict(color='rgba(102, 126, 234, 0.6)',
                          width=2, dash='dash'),
                hoverinfo='skip',
                showlegend=True
            )

    def _add_median_lines(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add median reference lines to the scatter plot."""
        median_price = df['price'].median()
        median_sqm = df['square_meters'].median()

        fig.add_vline(
            x=median_sqm,
            line_dash="dot",
            line_color="rgba(102, 126, 234, 0.6)",
            annotation_text=f"Median Size: {median_sqm:.0f}sqm",
            annotation_position="top"
        )

        fig.add_hline(
            y=median_price,
            line_dash="dot",
            line_color="rgba(102, 126, 234, 0.6)",
            annotation_text=f"Median Price: ₪{median_price:,.0f}",
            annotation_position="right"
        )

    def _update_styling_and_hover(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Update scatter plot styling and hover templates."""
        # Prepare hover data
        custom_data = [PropertyHoverData.from_row(
            row).to_list() for _, row in df.iterrows()]

        # Update each trace with correct hover data mapping
        for trace in fig.data:
            if hasattr(trace, 'marker') and hasattr(trace, 'x'):
                trace_custom_data = self._get_trace_hover_data(
                    trace, df, custom_data)
                trace.customdata = trace_custom_data
                trace.update(
                    marker=dict(
                        opacity=ChartConfiguration.OPACITY,
                        line=dict(width=ChartConfiguration.LINE_WIDTH,
                                  color=ChartConfiguration.LINE_COLOR)
                    ),
                    hovertemplate=HoverTemplate.build_property_hover_template()
                )

        self._update_layout(fig)

    def _get_trace_hover_data(self, trace, df: pd.DataFrame, custom_data: list) -> list:
        """Get correctly mapped hover data for a specific trace."""
        trace_indices = []
        if hasattr(trace, 'x') and hasattr(trace, 'y'):
            for x_val, y_val in zip(trace.x, trace.y):
                matching_rows = df[(df['square_meters'] == x_val) & (
                    df['price'] == y_val)]
                if not matching_rows.empty:
                    trace_indices.append(matching_rows.index[0])

        return [custom_data[idx] for idx in trace_indices] if trace_indices else []

    def _update_layout(self, fig: go.Figure) -> None:
        """Update the figure layout."""
        fig.update_layout(
            clickmode='event+select',
            hoverdistance=100,
            hovermode='closest',
            dragmode='zoom',
            plot_bgcolor='rgba(240,240,240,0.2)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Roboto, sans-serif"),
            xaxis=dict(title_font=dict(size=14),
                       tickfont=dict(size=12), gridcolor='#eee'),
            yaxis=dict(title_font=dict(size=14),
                       tickfont=dict(size=12), gridcolor='#eee'),
            title=dict(font=dict(size=16), x=0.5, y=0.95,
                       xanchor='center', yanchor='top'),
            margin=dict(l=40, r=40, t=120, b=40),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.08, xanchor="right", x=1,
                bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(0,0,0,0.1)", borderwidth=1
            )
        )

    def get_value_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of value analysis results."""
        if len(self.data) == 0:
            return {'total_properties': 0, 'value_categories': {}}

        df_with_analysis = self._calculate_value_analysis(self.data.copy())
        value_counts = df_with_analysis['value_category'].value_counts(
        ).to_dict()
        total = len(df_with_analysis)
        value_percentages = {
            cat: (count / total) * 100 for cat, count in value_counts.items()}

        return {
            'total_properties': total,
            'value_categories': value_counts,
            'value_percentages': value_percentages,
            'average_value_score': df_with_analysis['value_score'].mean(),
            'median_value_score': df_with_analysis['value_score'].median()
        }
