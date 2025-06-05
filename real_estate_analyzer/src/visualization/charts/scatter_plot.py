"""Enhanced scatter plot visualization component for property analysis."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum

from src.config.constants import ChartConfiguration, ValueAnalysisConstants


class HoverDataFields(IntEnum):
    """Enum for hover data field indices to prevent magic numbers."""
    NEIGHBORHOOD = 0
    ROOMS = 1
    PRICE_PER_SQM = 2
    CONDITION_TEXT = 3
    AD_TYPE = 4
    STREET_DISPLAY = 5
    FLOOR = 6
    FULL_URL = 7
    VALUE_SCORE = 8
    VALUE_CATEGORY = 9
    PREDICTED_PRICE = 10
    SAVINGS_AMOUNT = 11


class MapHoverDataFields(IntEnum):
    """Enum for map hover data field indices."""
    NEIGHBORHOOD = 0
    PRICE = 1
    ROOMS = 2
    CONDITION_TEXT = 3
    AD_TYPE = 4
    STREET_DISPLAY = 5
    FLOOR = 6
    FULL_URL = 7


class AnalyticsHoverDataFields(IntEnum):
    """Enum for analytics charts hover data field indices."""
    AVG_SIZE = 0
    AVG_PRICE_PER_SQM = 1


@dataclass
class PropertyHoverData:
    """Structured data for property hover information."""
    neighborhood: str
    rooms: int
    price_per_sqm: int
    condition_text: str
    ad_type: str
    street_display: str
    floor: str
    full_url: str
    value_score: float
    value_category: str
    predicted_price: int
    savings_amount: int

    def to_list(self) -> list:
        """Convert to list for Plotly customdata."""
        return [
            self.neighborhood,
            self.rooms,
            self.price_per_sqm,
            self.condition_text,
            self.ad_type,
            self.street_display,
            self.floor,
            self.full_url,
            self.value_score,
            self.value_category,
            self.predicted_price,
            self.savings_amount
        ]

    @classmethod
    def from_row(cls, row: pd.Series) -> 'PropertyHoverData':
        """Create PropertyHoverData from a DataFrame row."""
        street_display = (
            row['street'] if pd.notna(row['street']) and str(row['street']).strip() != ''
            else row['neighborhood']
        )

        return cls(
            neighborhood=str(row['neighborhood']) if pd.notna(
                row['neighborhood']) else 'Unknown',
            rooms=int(row['rooms']) if pd.notna(row['rooms']) else 0,
            price_per_sqm=int(round(row['price_per_sqm'])) if pd.notna(
                row['price_per_sqm']) else 0,
            condition_text=str(row['condition_text']) if pd.notna(
                row['condition_text']) else 'Not specified',
            ad_type=str(row['ad_type']) if pd.notna(
                row['ad_type']) else 'Unknown',
            street_display=str(street_display),
            floor=str(row['floor']) if pd.notna(
                row['floor']) else 'Not specified',
            full_url=str(row['full_url']) if pd.notna(row['full_url']) else '',
            value_score=round(float(row['value_score']), 1) if pd.notna(
                row['value_score']) else 0.0,
            value_category=str(row['value_category']) if pd.notna(
                row['value_category']) else 'Unknown',
            predicted_price=int(round(row['predicted_price'])) if pd.notna(
                row['predicted_price']) else 0,
            savings_amount=int(round(row['savings_amount'])) if pd.notna(
                row['savings_amount']) else 0
        )


@dataclass
class MapHoverData:
    """Structured data for map hover information."""
    neighborhood: str
    price: int
    rooms: int
    condition_text: str
    ad_type: str
    street_display: str
    floor: str
    full_url: str

    def to_list(self) -> list:
        """Convert to list for Plotly customdata."""
        return [
            self.neighborhood,
            self.price,
            self.rooms,
            self.condition_text,
            self.ad_type,
            self.street_display,
            self.floor,
            self.full_url
        ]

    @classmethod
    def from_row(cls, row: pd.Series) -> 'MapHoverData':
        """Create MapHoverData from a DataFrame row."""
        street_display = (
            row['street'] if pd.notna(row['street']) and str(row['street']).strip() != ''
            else row['neighborhood']
        )

        return cls(
            neighborhood=str(row['neighborhood']) if pd.notna(
                row['neighborhood']) else 'Unknown',
            price=int(round(row['price'])) if pd.notna(row['price']) else 0,
            rooms=int(row['rooms']) if pd.notna(row['rooms']) else 0,
            condition_text=str(row['condition_text']) if pd.notna(
                row['condition_text']) else 'Not specified',
            ad_type=str(row['ad_type']) if pd.notna(
                row['ad_type']) else 'Unknown',
            street_display=str(street_display),
            floor=str(row['floor']) if pd.notna(
                row['floor']) else 'Not specified',
            full_url=str(row['full_url']) if pd.notna(row['full_url']) else ''
        )


@dataclass
class AnalyticsHoverData:
    """Structured data for analytics charts hover information."""
    avg_size: float
    avg_price_per_sqm: float

    def to_list(self) -> list:
        """Convert to list for Plotly customdata."""
        return [
            self.avg_size,
            self.avg_price_per_sqm
        ]


class HoverTemplate:
    """Builder for hover templates with named field access."""

    @staticmethod
    def build_property_hover_template() -> str:
        """Build hover template using named field references."""
        template = (
            f'<b>🏡 %{{customdata[{HoverDataFields.NEIGHBORHOOD}]}}</b><br>'
            f'<i>📍 %{{customdata[{HoverDataFields.STREET_DISPLAY}]}}</i><br>'
            '<br>'
            '<b>📊 Property Details:</b><br>'
            '<b>Actual Price:</b> ₪%{y:,.0f}<br>'
            '<b>Size:</b> %{x} sqm<br>'
            f'<b>Price/sqm:</b> ₪%{{customdata[{HoverDataFields.PRICE_PER_SQM}]:,.0f}}<br>'
            f'<b>Rooms:</b> %{{customdata[{HoverDataFields.ROOMS}]}} | %{{customdata[{HoverDataFields.CONDITION_TEXT}]}}<br>'
            '<br>'
            '<b>💡 Market Value Analysis:</b><br>'
            f'<b>Expected Price:</b> ₪%{{customdata[{HoverDataFields.PREDICTED_PRICE}]:,.0f}}<br>'
            f'<b>Value Score:</b> %{{customdata[{HoverDataFields.VALUE_SCORE}]}}%<br>'
            f'<b>Assessment:</b> %{{customdata[{HoverDataFields.VALUE_CATEGORY}]}}<br>'
            f'<b>Savings/Premium:</b> ₪%{{customdata[{HoverDataFields.SAVINGS_AMOUNT}]:,.0f}}<br>'
            '<br>'
            '<i>💭 Value Score Explanation:</i><br>'
            '<i>Based on size vs price trend.</i><br>'
            '<i>Negative = Below market (good deal)</i><br>'
            '<i>Positive = Above market (expensive)</i><br>'
            '<br>'
            '<b>👆 Click to view listing</b>'
            '<extra></extra>'
        )

        return template

    @staticmethod
    def build_map_hover_template() -> str:
        """Build hover template for map visualization."""
        template = (
            f'<b>🏡 %{{customdata[{MapHoverDataFields.NEIGHBORHOOD}]}}</b><br>'
            f'<i>📍 %{{customdata[{MapHoverDataFields.STREET_DISPLAY}]}}</i><br>'
            '<br>'
            f'<b>Price:</b> ₪%{{customdata[{MapHoverDataFields.PRICE}]:,.0f}}<br>'
            '<b>Size:</b> %{text} sqm<br>'
            '<b>Price/sqm:</b> ₪%{marker.color:,.0f}<br>'
            f'<b>Rooms:</b> %{{customdata[{MapHoverDataFields.ROOMS}]}}<br>'
            f'<b>Condition:</b> %{{customdata[{MapHoverDataFields.CONDITION_TEXT}]}}<br>'
            '<br>'
            '<b>👆 Click to view listing</b>'
            '<extra></extra>'
        )
        return template

    @staticmethod
    def build_analytics_hover_template() -> str:
        """Build hover template for analytics charts."""
        template = (
            '<b>%{x}</b><br>'
            '<b>Avg Total Price:</b> ₪%{y:,.0f}<br>'
            f'<b>Avg Size:</b> %{{customdata[{AnalyticsHoverDataFields.AVG_SIZE}]:.0f}} sqm<br>'
            f'<b>Avg Price/sqm:</b> ₪%{{customdata[{AnalyticsHoverDataFields.AVG_PRICE_PER_SQM}]:,.0f}}<br>'
            '<b>Properties:</b> %{text}<br>'
            '<b>Real Affordability:</b> %{marker.color:.0f}/100<br>'
            '<br><i>Higher score = more affordable</i>'
            '<extra></extra>'
        )
        return template


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

        plot_df = self.data.copy()

        # Calculate trend line and value scores
        plot_df = self._calculate_value_analysis(plot_df)

        # Create the enhanced scatter plot
        fig = px.scatter(
            plot_df,
            x='square_meters',
            y='price',
            color='value_category',
            size='rooms',
            size_max=ChartConfiguration.SIZE_MAX,
            color_discrete_map=self._get_value_category_colors(),
            hover_data=['neighborhood', 'rooms',
                        'condition_text', 'price_per_sqm', 'value_score'],
            labels={'square_meters': 'Square Meters',
                    'price': 'Price (₪)',
                    'value_category': 'Market Value Analysis'},
            title='Property Size vs Price with Market Value Analysis<br><sub>Value Score: % above/below expected price for property size | Trend line shows market expectation</sub>'
        )

        # Add trend line
        self._add_trend_line(fig, plot_df)

        # Add median reference lines
        self._add_median_lines(fig, plot_df)

        # Update hover template and styling
        self._update_scatter_styling(fig, plot_df)

        return fig

    def _calculate_value_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend line and value scores for properties."""
        x = df['square_meters'].values
        y = df['price'].values

        try:
            # Fit polynomial trend line (linear for now)
            z = np.polyfit(x, y, ValueAnalysisConstants.POLYNOMIAL_DEGREE)
            trend_line_y = np.poly1d(z)(x)

            # Calculate value score: percentage above/below trend line
            df['predicted_price'] = trend_line_y
            df['value_score'] = ((y - trend_line_y) / trend_line_y * 100)
            df['savings_amount'] = trend_line_y - y  # Actual savings in NIS

            # Categorize properties based on value score
            df['value_category'] = df['value_score'].apply(
                self._categorize_property_value)

        except Exception:
            # Fallback if trend calculation fails
            df['value_score'] = 0
            df['value_category'] = 'Unknown'
            df['predicted_price'] = y.copy()
            df['savings_amount'] = 0

        return df

    def _categorize_property_value(self, value_score: float) -> str:
        """Categorize property based on value score."""
        if value_score < ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD:
            return 'Excellent Deal'
        elif value_score < ValueAnalysisConstants.GOOD_DEAL_THRESHOLD:
            return 'Good Deal'
        elif value_score < ValueAnalysisConstants.FAIR_PRICE_THRESHOLD:
            return 'Fair Price'
        elif value_score < ValueAnalysisConstants.ABOVE_MARKET_THRESHOLD:
            return 'Above Market'
        else:
            return 'Overpriced'

    def _get_value_category_colors(self) -> Dict[str, str]:
        """Get color mapping for value categories."""
        return {
            'Excellent Deal': '#28a745',  # Green
            'Good Deal': '#20c997',       # Teal
            'Fair Price': '#6c757d',      # Gray
            'Above Market': '#fd7e14',    # Orange
            'Overpriced': '#dc3545'       # Red
        }

    def _add_trend_line(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add trend line to the scatter plot."""
        if 'predicted_price' in df.columns:
            fig.add_scatter(
                x=df['square_meters'],
                y=df['predicted_price'],
                mode='lines',
                name='Market Trend',
                line=dict(color='rgba(102, 126, 234, 0.8)',
                          width=3, dash='dash'),
                hoverinfo='skip'
            )

    def _add_median_lines(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add median reference lines to the scatter plot."""
        median_price = df['price'].median()
        median_sqm = df['square_meters'].median()

        # Vertical line for median square meters
        fig.add_vline(
            x=median_sqm,
            line_dash="dot",
            line_color="rgba(102, 126, 234, 0.6)",
            annotation_text=f"Median Size: {median_sqm:.0f}sqm",
            annotation_position="top"
        )

        # Horizontal line for median price
        fig.add_hline(
            y=median_price,
            line_dash="dot",
            line_color="rgba(102, 126, 234, 0.6)",
            annotation_text=f"Median Price: ₪{median_price:,.0f}",
            annotation_position="right"
        )

    def _update_scatter_styling(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Update scatter plot styling and hover templates."""
        # Create structured hover data objects
        hover_data_objects = [PropertyHoverData.from_row(
            row) for _, row in df.iterrows()]

        # Convert to list format for Plotly
        custom_data = [hover_data.to_list()
                       for hover_data in hover_data_objects]

        # Update traces with enhanced hover template
        fig.update_traces(
            marker=dict(
                opacity=ChartConfiguration.OPACITY,
                line=dict(width=ChartConfiguration.LINE_WIDTH,
                          color=ChartConfiguration.LINE_COLOR)
            ),
            customdata=custom_data,
            hovertemplate=HoverTemplate.build_property_hover_template(),
            selector=dict(mode='markers')
        )

        # Update layout
        fig.update_layout(
            clickmode='event+select',
            hoverdistance=100,
            hovermode='closest',
            dragmode='zoom',
            plot_bgcolor='rgba(240,240,240,0.2)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Roboto, sans-serif"),
            xaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='#eee'
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='#eee'
            ),
            title=dict(
                font=dict(size=16),
                x=0.5,  # Center the title
                y=0.95,  # Move title down slightly to prevent overlap
                xanchor='center',
                yanchor='top'
            ),
            # Increased top margin for title space
            margin=dict(l=40, r=40, t=120, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,  # Move legend higher to avoid title overlap
                xanchor="right",
                x=1,
                # Add background for better visibility
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            )
        )

    def get_value_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of value analysis results."""
        if len(self.data) == 0:
            return {'total_properties': 0, 'value_categories': {}}

        df_with_analysis = self._calculate_value_analysis(self.data.copy())

        # Count properties by value category
        value_counts = df_with_analysis['value_category'].value_counts(
        ).to_dict()

        # Calculate percentage distribution
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
