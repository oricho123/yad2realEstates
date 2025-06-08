"""Enhanced scatter plot visualization component for property analysis."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from src.config.constants import ChartConfiguration
from src.visualization.hover_data import PropertyHoverData, HoverTemplate
from src.utils import TrendAnalyzer


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
        self._add_median_lines(fig, plot_df)
        self._update_styling_and_hover(fig, plot_df)

        return fig

    def _prepare_plot_data(self) -> pd.DataFrame:
        """Prepare data with value analysis and indexing."""
        plot_df = self.data.copy().reset_index(drop=True)
        plot_df['property_index'] = range(len(plot_df))
        return self._calculate_value_analysis(plot_df)

    def _create_base_scatter_plot(self, plot_df: pd.DataFrame) -> go.Figure:
        """Create the base scatter plot with color categories and built-in trendline."""
        # Separate new and regular properties
        is_new_series = plot_df.get('is_new', pd.Series(
            [False] * len(plot_df), index=plot_df.index))
        new_properties = plot_df[is_new_series]
        regular_properties = plot_df[~is_new_series]

        # Always use ALL data for trendline to represent complete market picture
        fig = px.scatter(
            plot_df,
            x='square_meters',
            y='price',
            color='value_category',
            size='rooms',
            size_max=ChartConfiguration.SIZE_MAX,
            color_discrete_map=self._get_value_category_colors(),
            trendline="lowess",
            trendline_scope="overall",
            labels={
                'square_meters': 'Square Meters',
                'price': 'Price (₪)',
                'value_category': 'Market Value Analysis'
            },
            title='Property Size vs Price with Market Value Analysis'
        )

        # Hide ALL original markers since we'll add them back separately with proper styling
        for trace in fig.data:
            if hasattr(trace, 'mode') and trace.mode == 'markers':
                trace.visible = False  # Hide original markers, keep trendline

        # Add regular properties back as proper markers
        if not regular_properties.empty:
            for category in regular_properties['value_category'].unique():
                category_data = regular_properties[regular_properties['value_category'] == category]

                fig.add_trace(go.Scatter(
                    x=category_data['square_meters'],
                    y=category_data['price'],
                    mode='markers',
                    marker=dict(
                        size=category_data['rooms'] * 3 + 4,
                        color=self._get_value_category_colors()[category],
                        opacity=ChartConfiguration.OPACITY,
                        line=dict(width=ChartConfiguration.LINE_WIDTH,
                                  color=ChartConfiguration.LINE_COLOR)
                    ),
                    name=category,
                    showlegend=True,
                    meta={'is_new_property': False}
                ))

        # Add new properties as star symbols if any exist
        if not new_properties.empty:
            for category in new_properties['value_category'].unique():
                category_data = new_properties[new_properties['value_category'] == category]

                fig.add_trace(go.Scatter(
                    x=category_data['square_meters'],
                    y=category_data['price'],
                    mode='markers',
                    marker=dict(
                        size=category_data['rooms'] * 3 + 4,
                        color=self._get_value_category_colors()[category],
                        line=dict(width=2, color='gold'),
                        opacity=0.9
                    ),
                    name=f'NEW {category}',
                    showlegend=True,
                    # Use meta flag instead of name checking
                    meta={'is_new_property': True}
                    # Note: hover template will be set in _update_styling_and_hover
                ))

        # Move trendline to front so it's visible above markers
        self._bring_trendline_to_front(fig)

        return fig

    def _bring_trendline_to_front(self, fig: go.Figure) -> None:
        """Move trendline traces to the front so they appear above markers."""
        # Find trendline traces (they have mode='lines')
        trendline_traces = []
        other_traces = []

        for trace in fig.data:
            if hasattr(trace, 'mode') and trace.mode == 'lines':
                trendline_traces.append(trace)
            else:
                other_traces.append(trace)

        # Reorder: other traces first, then trendlines on top
        fig.data = tuple(other_traces + trendline_traces)

    def _calculate_value_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate LOWESS trend line and value scores for properties using centralized utility."""
        return TrendAnalyzer.calculate_complete_value_analysis(df)

    def _get_value_category_colors(self) -> Dict[str, str]:
        """Get color mapping for value categories."""
        return {
            'Excellent Deal': '#28a745',
            'Good Deal': '#20c997',
            'Fair Price': '#6c757d',
            'Above Market': '#fd7e14',
            'Overpriced': '#dc3545'
        }

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

                # Use detailed hover template, with "NEW" indicator for new properties
                is_new_property = hasattr(trace, 'meta') and trace.meta and trace.meta.get(
                    'is_new_property', False)
                if is_new_property:
                    base_template = HoverTemplate.build_property_hover_template()
                    new_template = '🆕 NEW<br>' + base_template
                    trace.update(hovertemplate=new_template)
                else:
                    trace.update(
                        hovertemplate=HoverTemplate.build_property_hover_template())

                # Apply styling only to non-new properties (new properties keep their star styling)
                if not is_new_property:
                    trace.update(
                        marker=dict(
                            opacity=ChartConfiguration.OPACITY,
                            line=dict(width=ChartConfiguration.LINE_WIDTH,
                                      color=ChartConfiguration.LINE_COLOR)
                        )
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
            clickmode='event',
            hoverdistance=20,
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
