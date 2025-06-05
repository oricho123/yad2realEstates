"""Filter callback handlers for the dashboard."""

import pandas as pd
from dash import callback, Input, Output
import dash
from typing import Tuple, List, Dict, Any

from src.analysis.filters import PropertyDataFilter


class FilterCallbackManager:
    """Manages filter-related callbacks."""
    
    def __init__(self, app: dash.Dash):
        """
        Initialize the filter callback manager.
        
        Args:
            app: Dash application instance
        """
        self.app = app
        
    def register_all_callbacks(self) -> None:
        """Register all filter callbacks."""
        self._register_filter_update_callback()
        
    def _register_filter_update_callback(self) -> None:
        """Register the filter range update callback."""
        
        @self.app.callback(
            [Output('price-range-slider', 'min'),
             Output('price-range-slider', 'max'),
             Output('price-range-slider', 'value'),
             Output('price-range-slider', 'marks'),
             Output('sqm-range-slider', 'min'),
             Output('sqm-range-slider', 'max'),
             Output('sqm-range-slider', 'value'),
             Output('sqm-range-slider', 'marks'),
             Output('neighborhood-filter', 'options'),
             Output('neighborhood-filter', 'value'),
             Output('exclude-neighborhoods-filter', 'options'),
             Output('exclude-neighborhoods-filter', 'value'),
             Output('rooms-range-slider', 'min'),
             Output('rooms-range-slider', 'max'),
             Output('rooms-range-slider', 'value'),
             Output('rooms-range-slider', 'marks'),
             Output('condition-filter', 'options'),
             Output('condition-filter', 'value'),
             Output('ad-type-filter', 'options'),
             Output('ad-type-filter', 'value')],
            [Input('current-dataset', 'data')]
        )
        def update_filter_ranges(current_data):
            """
            Update filter ranges and options based on current dataset.
            
            Args:
                current_data: Current property data
                
            Returns:
                Tuple of updated filter configurations
            """
            try:
                # Convert current data back to DataFrame
                if not current_data:
                    return self._get_empty_filter_config()
                    
                df = pd.DataFrame(current_data)
                
                if df.empty:
                    return self._get_empty_filter_config()
                
                # Clean data for analysis
                clean_df = df.dropna(subset=['price', 'square_meters', 'rooms'])
                
                if clean_df.empty:
                    return self._get_empty_filter_config()
                
                # Create filter manager to get options
                data_filter = PropertyDataFilter(clean_df)
                filter_options = data_filter.get_filter_options(clean_df)
                
                return (
                    # Price range slider
                    filter_options['price_min'],
                    filter_options['price_max'],
                    [filter_options['price_min'], filter_options['price_max']],
                    filter_options['price_marks'],
                    
                    # Square meters range slider
                    filter_options['sqm_min'],
                    filter_options['sqm_max'],
                    [filter_options['sqm_min'], filter_options['sqm_max']],
                    filter_options['sqm_marks'],
                    
                    # Neighborhood filters
                    filter_options['neighborhoods'],
                    'all',  # Default neighborhood value
                    filter_options['exclude_neighborhoods_options'],
                    [],     # Default exclude neighborhoods value
                    
                    # Rooms range slider
                    filter_options['rooms_min'],
                    filter_options['rooms_max'],
                    [filter_options['rooms_min'], filter_options['rooms_max']],
                    filter_options['rooms_marks'],
                    
                    # Condition filter
                    filter_options['conditions'],
                    'all',  # Default condition value
                    
                    # Ad type filter
                    filter_options['ad_types'],
                    'all'   # Default ad type value
                )
                
            except Exception as e:
                print(f"Error in filter update callback: {str(e)}")
                return self._get_empty_filter_config()
    
    def _get_empty_filter_config(self) -> Tuple:
        """
        Get empty filter configuration when no data is available.
        
        Returns:
            Tuple of empty filter configurations
        """
        # Import formatter for better formatting
        from src.utils.formatters import NumberFormatter
        
        return (
            # Price range slider
            0, 5000000, [0, 5000000], NumberFormatter.create_price_marks(0, 5000000, num_marks=3),
            
            # Square meters range slider  
            0, 500, [0, 500], NumberFormatter.create_number_marks(0, 500, num_marks=3, suffix="m²"),
            
            # Neighborhood filters
            [{'label': 'All Neighborhoods', 'value': 'all'}], 'all',
            [], [],
            
            # Rooms range slider
            1, 10, [1, 10], {1: '1', 10: '10'},
            
            # Condition filter
            [{'label': 'All Conditions', 'value': 'all'}], 'all',
            
            # Ad type filter
            [{'label': 'All', 'value': 'all'}], 'all'
        ) 