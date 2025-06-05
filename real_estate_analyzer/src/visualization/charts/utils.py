"""Utilities and helper functions for chart creation."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List, Tuple

from src.config.constants import ChartConfiguration


class ChartUtils:
    """Utility functions for chart creation and data preparation."""

    @staticmethod
    def create_empty_figure(title: str, height: int = None) -> go.Figure:
        """
        Create an empty figure with a title.
        
        Args:
            title: Title for the empty figure
            height: Optional height override
            
        Returns:
            go.Figure: Empty plotly figure
        """
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="",
            yaxis_title="",
            height=height or ChartConfiguration.DEFAULT_HEIGHT,
            showlegend=False
        )
        return fig

    @staticmethod
    def prepare_street_display(df: pd.DataFrame) -> pd.Series:
        """
        Prepare street display text for hover templates.
        
        Args:
            df: DataFrame with street and neighborhood columns
            
        Returns:
            pd.Series: Formatted street display text
        """
        return df.apply(lambda row: 
            f"{row['street']}" if pd.notna(row['street']) and row['street'].strip() != '' 
            else f"{row['neighborhood']}", axis=1)

    @staticmethod
    def prepare_custom_data_for_hover(df: pd.DataFrame, columns: List[str]) -> np.ndarray:
        """
        Prepare custom data array for hover templates.
        
        Args:
            df: Source DataFrame
            columns: List of column names to include
            
        Returns:
            np.ndarray: Custom data array for plotly traces
        """
        data_columns = []
        for col in columns:
            if col in df.columns:
                if col in ['price', 'price_per_sqm', 'predicted_price', 'savings_amount']:
                    data_columns.append(df[col].round(0))
                elif col == 'value_score':
                    data_columns.append(df[col].round(1))
                else:
                    data_columns.append(df[col].fillna('Not specified'))
            else:
                # Handle missing columns gracefully
                data_columns.append(pd.Series(['Not available'] * len(df)))
        
        return np.column_stack(data_columns)

    @staticmethod
    def calculate_trend_line(x_data: np.ndarray, y_data: np.ndarray, degree: int = 1) -> Tuple[np.ndarray, bool]:
        """
        Calculate trend line for scatter plots.
        
        Args:
            x_data: X axis data
            y_data: Y axis data
            degree: Polynomial degree for trend line
            
        Returns:
            Tuple[np.ndarray, bool]: Trend line y values and success flag
        """
        try:
            z = np.polyfit(x_data, y_data, degree)
            trend_line_y = np.poly1d(z)(x_data)
            return trend_line_y, True
        except Exception:
            return np.zeros_like(y_data), False

    @staticmethod
    def apply_standard_layout_styling(fig: go.Figure, title: str = None) -> None:
        """
        Apply standard layout styling to a figure.
        
        Args:
            fig: Plotly figure to style
            title: Optional title override
        """
        layout_updates = {
            'plot_bgcolor': 'rgba(240,240,240,0.2)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': dict(family="Roboto, sans-serif"),
            'xaxis': dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='#eee'
            ),
            'yaxis': dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='#eee'
            ),
            'margin': dict(l=40, r=40, t=60, b=40)
        }
        
        if title:
            layout_updates['title'] = dict(text=title, font=dict(size=16))
        
        fig.update_layout(**layout_updates)

    @staticmethod
    def apply_standard_marker_styling(fig: go.Figure) -> None:
        """
        Apply standard marker styling to scatter plots.
        
        Args:
            fig: Plotly figure to style
        """
        fig.update_traces(
            marker=dict(
                opacity=ChartConfiguration.OPACITY,
                line=dict(
                    width=ChartConfiguration.LINE_WIDTH, 
                    color=ChartConfiguration.LINE_COLOR
                )
            ),
            selector=dict(mode='markers')
        )

    @staticmethod
    def get_color_scale(chart_type: str = 'default') -> str:
        """
        Get appropriate color scale for different chart types.
        
        Args:
            chart_type: Type of chart (default, heatmap, diverging)
            
        Returns:
            str: Color scale name
        """
        color_scales = {
            'default': ChartConfiguration.COLOR_SCALE,
            'heatmap': 'RdYlBu_r',
            'diverging': 'RdBu',
            'sequential': 'viridis',
            'categorical': 'Set3'
        }
        
        return color_scales.get(chart_type, ChartConfiguration.COLOR_SCALE)

    @staticmethod
    def format_hover_template(template_config: Dict[str, Any]) -> str:
        """
        Create standardized hover template.
        
        Args:
            template_config: Configuration for hover template
            
        Returns:
            str: Formatted hover template string
        """
        base_template = '<b>{title}</b><br>'
        
        if 'location' in template_config:
            base_template += '<i>{location}</i><br><br>'
        
        for section in template_config.get('sections', []):
            base_template += f'<b>{section["title"]}:</b><br>'
            for item in section['items']:
                base_template += f'<b>{item["label"]}:</b> {item["value"]}<br>'
            base_template += '<br>'
        
        if template_config.get('click_instruction', True):
            base_template += '<b>Click to view listing</b>'
        
        base_template += '<extra></extra>'
        
        return base_template

    @staticmethod
    def filter_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
        """
        Filter outliers from dataset for better visualization.
        
        Args:
            df: Input DataFrame
            column: Column to filter outliers on
            method: Method to use ('iqr', 'zscore', 'percentile')
            
        Returns:
            pd.DataFrame: DataFrame with outliers removed
        """
        if len(df) == 0 or column not in df.columns:
            return df
        
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        elif method == 'percentile':
            lower_bound = df[column].quantile(0.05)
            upper_bound = df[column].quantile(0.95)
            return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        elif method == 'zscore':
            from scipy import stats
            z_scores = np.abs(stats.zscore(df[column].fillna(df[column].mean())))
            return df[z_scores < 3]
        
        return df

    @staticmethod
    def calculate_optimal_bins(data: pd.Series, max_bins: int = 50) -> int:
        """
        Calculate optimal number of bins for histograms.
        
        Args:
            data: Data series for histogram
            max_bins: Maximum number of bins
            
        Returns:
            int: Optimal number of bins
        """
        n = len(data.dropna())
        
        # Sturges' rule
        sturges = int(np.ceil(np.log2(n) + 1))
        
        # Square root choice
        sqrt_choice = int(np.ceil(np.sqrt(n)))
        
        # Use the minimum of the two, but cap at max_bins
        optimal = min(sturges, sqrt_choice, max_bins)
        
        return max(optimal, 5)  # Minimum of 5 bins

    @staticmethod
    def format_currency(value: float, currency: str = '₪', short_form: bool = True) -> str:
        """
        Format currency values for display.
        
        Args:
            value: Numeric value to format
            currency: Currency symbol
            short_form: Use K/M notation for large numbers
            
        Returns:
            str: Formatted currency string
        """
        # Use the enhanced formatter from utils
        from src.utils.formatters import NumberFormatter
        return NumberFormatter.format_currency(value, currency=currency, short_form=short_form)

    @staticmethod
    def get_responsive_layout(chart_type: str = 'default') -> Dict[str, Any]:
        """
        Get responsive layout configuration for different chart types.
        
        Args:
            chart_type: Type of chart
            
        Returns:
            Dict[str, Any]: Layout configuration
        """
        base_config = {
            'autosize': True,
            'margin': dict(l=40, r=40, t=60, b=40),
            'font': dict(family="Roboto, sans-serif", size=12)
        }
        
        if chart_type == 'mobile':
            base_config.update({
                'margin': dict(l=20, r=20, t=40, b=20),
                'font': dict(size=10),
                'legend': dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            })
        
        return base_config 