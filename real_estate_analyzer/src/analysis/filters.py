"""Data filtering utilities for property analysis."""

import pandas as pd
from typing import Dict, Any, List, Optional
import logging
from src.utils.formatters import NumberFormatter

from src.data.models import PropertyDataFrame, PropertyFilters
from src.config.constants import PropertyValidation

logger = logging.getLogger(__name__)


class PropertyDataFilter:
    """Handles filtering operations on property data."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property DataFrame."""
        self.original_data = data.copy()

    def apply_all_filters(self, filter_params: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply all filters to the property data.

        Args:
            filter_params: Dictionary containing filter parameters from the dashboard

        Returns:
            Filtered DataFrame
        """
        filtered_df = self.original_data.copy()

        logger.info(
            f"Starting filter process with {len(filtered_df)} properties")

        # Apply price range filter
        if 'price_range' in filter_params and filter_params['price_range']:
            filtered_df = self._apply_price_filter(
                filtered_df, filter_params['price_range'])

        # Apply size filter
        if 'sqm_range' in filter_params and filter_params['sqm_range']:
            filtered_df = self._apply_size_filter(
                filtered_df, filter_params['sqm_range'])

        # Apply neighborhood filter
        if 'neighborhood' in filter_params:
            filtered_df = self._apply_neighborhood_filter(
                filtered_df, filter_params['neighborhood'])

        # Apply exclude neighborhoods filter
        if 'exclude_neighborhoods' in filter_params:
            filtered_df = self._apply_exclude_neighborhoods_filter(
                filtered_df, filter_params['exclude_neighborhoods'])

        # Apply rooms filter
        if 'rooms' in filter_params and filter_params['rooms']:
            filtered_df = self._apply_rooms_filter(
                filtered_df, filter_params['rooms'])

        # Apply floor filter
        if 'floors' in filter_params and filter_params['floors']:
            filtered_df = self._apply_floor_filter(
                filtered_df, filter_params['floors'])

        # Apply condition filter
        if 'condition' in filter_params:
            filtered_df = self._apply_condition_filter(
                filtered_df, filter_params['condition'])

        # Apply ad type filter
        if 'ad_type' in filter_params:
            filtered_df = self._apply_ad_type_filter(
                filtered_df, filter_params['ad_type'])

        logger.info(
            f"Filter process complete: {len(filtered_df)} properties remaining")

        return filtered_df

    def _apply_price_filter(self, df: pd.DataFrame, price_range: List[float]) -> pd.DataFrame:
        """Apply price range filter."""
        if not price_range or len(price_range) != 2:
            return df

        price_min, price_max = price_range
        if price_min is None or price_max is None:
            return df

        before_count = len(df)
        filtered_df = df[
            (df['price'] >= price_min) &
            (df['price'] <= price_max)
        ]

        logger.debug(
            f"Price filter ({price_min:,.0f}-{price_max:,.0f}): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_size_filter(self, df: pd.DataFrame, sqm_range: List[float]) -> pd.DataFrame:
        """Apply square meters range filter."""
        if not sqm_range or len(sqm_range) != 2:
            return df

        sqm_min, sqm_max = sqm_range
        if sqm_min is None or sqm_max is None:
            return df

        before_count = len(df)
        filtered_df = df[
            (df['square_meters'] >= sqm_min) &
            (df['square_meters'] <= sqm_max)
        ]

        logger.debug(
            f"Size filter ({sqm_min:.0f}-{sqm_max:.0f}sqm): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_neighborhood_filter(self, df: pd.DataFrame, neighborhood: str) -> pd.DataFrame:
        """Apply neighborhood filter."""
        if not neighborhood or neighborhood == 'all' or 'neighborhood' not in df.columns:
            return df

        before_count = len(df)
        filtered_df = df[df['neighborhood'] == neighborhood]

        logger.debug(
            f"Neighborhood filter ('{neighborhood}'): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_exclude_neighborhoods_filter(self, df: pd.DataFrame, exclude_neighborhoods: List[str]) -> pd.DataFrame:
        """Apply exclude neighborhoods filter."""
        if not exclude_neighborhoods or len(exclude_neighborhoods) == 0 or 'neighborhood' not in df.columns:
            return df

        before_count = len(df)
        filtered_df = df[~df['neighborhood'].isin(exclude_neighborhoods)]

        logger.debug(
            f"Exclude neighborhoods filter: {before_count} → {len(filtered_df)} properties (excluded: {exclude_neighborhoods})")
        return filtered_df

    def _apply_rooms_filter(self, df: pd.DataFrame, rooms_range: List[float]) -> pd.DataFrame:
        """Apply rooms range filter."""
        if not rooms_range or len(rooms_range) != 2 or 'rooms' not in df.columns:
            return df

        rooms_min, rooms_max = rooms_range
        if rooms_min is None or rooms_max is None:
            return df

        before_count = len(df)
        filtered_df = df[
            (df['rooms'] >= rooms_min) &
            (df['rooms'] <= rooms_max)
        ]

        logger.debug(
            f"Rooms filter ({rooms_min:.1f}-{rooms_max:.1f}): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_floor_filter(self, df: pd.DataFrame, floors_range: List[float]) -> pd.DataFrame:
        """Apply floor range filter."""
        if not floors_range or len(floors_range) != 2 or 'floor' not in df.columns:
            return df

        floors_min, floors_max = floors_range
        if floors_min is None or floors_max is None:
            return df

        before_count = len(df)
        filtered_df = df[
            (df['floor'] >= floors_min) &
            (df['floor'] <= floors_max)
        ]

        logger.debug(
            f"Floor filter ({floors_min:.0f}-{floors_max:.0f}): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_condition_filter(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """Apply condition filter."""
        if not condition or condition == 'all' or 'condition_text' not in df.columns:
            return df

        before_count = len(df)
        filtered_df = df[df['condition_text'] == condition]

        logger.debug(
            f"Condition filter ('{condition}'): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def _apply_ad_type_filter(self, df: pd.DataFrame, ad_type: str) -> pd.DataFrame:
        """Apply ad type filter."""
        if not ad_type or ad_type == 'all' or 'ad_type' not in df.columns:
            return df

        before_count = len(df)
        filtered_df = df[df['ad_type'] == ad_type]

        logger.debug(
            f"Ad type filter ('{ad_type}'): {before_count} → {len(filtered_df)} properties")
        return filtered_df

    def clean_data_for_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare data for analysis by removing invalid records.

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame ready for analysis
        """
        cleaned_df = df.copy()
        initial_count = len(cleaned_df)

        # Critical fields that must have valid data
        critical_fields = ['square_meters', 'price', 'price_per_sqm']

        for col in critical_fields:
            if col in cleaned_df.columns:
                # Convert to numeric
                cleaned_df[col] = pd.to_numeric(
                    cleaned_df[col], errors='coerce')

                # Remove rows with missing critical data
                before_count = len(cleaned_df)
                cleaned_df = cleaned_df[cleaned_df[col].notna()]
                removed_count = before_count - len(cleaned_df)

                if removed_count > 0:
                    logger.info(
                        f"Removed {removed_count} properties with missing/invalid {col} data")

        # Handle rooms field more leniently
        if 'rooms' in cleaned_df.columns:
            cleaned_df['rooms'] = pd.to_numeric(
                cleaned_df['rooms'], errors='coerce')
            rooms_missing = cleaned_df['rooms'].isna().sum()

            if rooms_missing > 0:
                if rooms_missing / len(cleaned_df) < 0.05:  # Less than 5% missing
                    median_rooms = cleaned_df['rooms'].median()
                    cleaned_df['rooms'] = cleaned_df['rooms'].fillna(
                        median_rooms)
                    logger.info(
                        f"Filled {rooms_missing} missing room values with median: {median_rooms}")
                else:
                    # Remove properties with missing room data if too many
                    cleaned_df = cleaned_df[cleaned_df['rooms'].notna()]
                    logger.info(
                        f"Removed {rooms_missing} properties with missing room data")

        final_count = len(cleaned_df)
        removed_total = initial_count - final_count

        if removed_total > 0:
            quality_percentage = (final_count / initial_count) * 100
            logger.info(
                f"Data cleaning complete: removed {removed_total} invalid properties ({quality_percentage:.1f}% data quality)")

        return cleaned_df

    def get_filter_options(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate filter options based on the current dataset.

        Args:
            df: DataFrame to analyze for filter options

        Returns:
            Dictionary containing filter options for the dashboard
        """
        if len(df) == 0:
            return self._get_empty_filter_options()

        # Price range
        price_min = df['price'].min()
        price_max = df['price'].max()

        price_marks = NumberFormatter.create_price_marks(
            price_min, price_max, num_marks=3)

        # Size range
        sqm_min = df['square_meters'].min()
        sqm_max = df['square_meters'].max()
        sqm_marks = NumberFormatter.create_number_marks(
            sqm_min, sqm_max, num_marks=3, suffix="m²")

        # Rooms range
        rooms_min = df['rooms'].min()
        rooms_max = df['rooms'].max()
        rooms_marks = {
            int(rooms_min): f"{rooms_min:.0f}",
            int(rooms_max): f"{rooms_max:.0f}"
        }

        # Floor range - handle potential missing/null floor data
        floor_data = df['floor'].dropna(
        ) if 'floor' in df.columns else pd.Series([])
        if not floor_data.empty:
            floor_min = int(floor_data.min())
            floor_max = int(floor_data.max())
            floor_marks = {
                floor_min: str(floor_min),
                floor_max: str(floor_max)
            }
        else:
            floor_min = 0
            floor_max = 40
            floor_marks = {0: '0', 40: '40'}

        # Neighborhood options
        neighborhoods = [{'label': 'All Neighborhoods', 'value': 'all'}] + [
            {'label': n, 'value': n} for n in sorted(df['neighborhood'].dropna().unique())
        ]

        # Exclude neighborhood options
        exclude_neighborhoods_options = [
            {'label': n, 'value': n} for n in sorted(df['neighborhood'].dropna().unique())
        ]

        # Condition options
        conditions = [{'label': 'All Conditions', 'value': 'all'}] + [
            {'label': ct, 'value': ct} for ct in sorted(df['condition_text'].dropna().unique())
        ]

        # Ad type options
        ad_types = [{'label': 'All', 'value': 'all'}] + [
            {'label': at, 'value': at} for at in sorted(df['ad_type'].unique())
        ]

        return {
            'price_min': price_min,
            'price_max': price_max,
            'price_marks': price_marks,
            'sqm_min': sqm_min,
            'sqm_max': sqm_max,
            'sqm_marks': sqm_marks,
            'rooms_min': rooms_min,
            'rooms_max': rooms_max,
            'rooms_marks': rooms_marks,
            'floor_min': floor_min,
            'floor_max': floor_max,
            'floor_marks': floor_marks,
            'neighborhoods': neighborhoods,
            'exclude_neighborhoods_options': exclude_neighborhoods_options,
            'conditions': conditions,
            'ad_types': ad_types
        }

    def _get_empty_filter_options(self) -> Dict[str, Any]:
        """Return empty filter options when no data is available."""
        # Import formatter here to avoid circular imports
        from src.utils.formatters import NumberFormatter

        return {
            'price_min': 0,
            'price_max': 5000000,
            'price_marks': NumberFormatter.create_price_marks(0, 5000000, num_marks=3),
            'sqm_min': 0,
            'sqm_max': 200,
            'sqm_marks': NumberFormatter.create_number_marks(0, 200, num_marks=3, suffix="m²"),
            'rooms_min': 1,
            'rooms_max': 10,
            'rooms_marks': {1: "1", 10: "10"},
            'floor_min': 0,
            'floor_max': 40,
            'floor_marks': {0: '0', 40: '40'},
            'neighborhoods': [{'label': 'No data', 'value': 'none'}],
            'exclude_neighborhoods_options': [],
            'conditions': [{'label': 'No data', 'value': 'none'}],
            'ad_types': [{'label': 'No data', 'value': 'none'}]
        }
