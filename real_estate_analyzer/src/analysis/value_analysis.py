"""Property value analysis and scoring utilities."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import logging

from src.config.constants import ValueAnalysisConstants
from src.utils import TrendAnalyzer

logger = logging.getLogger(__name__)


class ValueAnalyzer:
    """Handles property value analysis and scoring."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property DataFrame."""
        self.data = data.copy()
        self._trend_coefficients = None

    def calculate_value_scores(self) -> pd.DataFrame:
        """
        Calculate value scores for all properties based on LOWESS market trend.

        Returns:
            DataFrame with value scores and categories added
        """
        if len(self.data) < 3:
            logger.warning("Insufficient data for value analysis")
            return self._add_empty_value_data()

        try:
            # Use centralized LOWESS-based trend analysis
            result_df = TrendAnalyzer.calculate_complete_value_analysis(
                self.data)

            # Store trend coefficients for backward compatibility (approximate from LOWESS)
            x = self.data['square_meters'].values
            y = result_df['predicted_price'].values
            try:
                self._trend_coefficients = np.polyfit(
                    x, y, 1)  # Linear approximation
            except:
                self._trend_coefficients = [0, np.mean(y)]

            # Rename predicted_price to trend_price for compatibility
            result_df['trend_price'] = result_df['predicted_price']

            return result_df

        except Exception as e:
            logger.error(f"Error calculating value scores: {e}")
            return self._add_empty_value_data()

    def _categorize_properties(self, value_scores: np.ndarray) -> List[str]:
        """Categorize properties based on value scores."""
        categories = []

        for score in value_scores:
            if score <= ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD:
                categories.append("Excellent Deal")
            elif score <= ValueAnalysisConstants.GOOD_DEAL_THRESHOLD:
                categories.append("Good Deal")
            elif score <= ValueAnalysisConstants.FAIR_PRICE_THRESHOLD:
                categories.append("Fair Price")
            elif score <= ValueAnalysisConstants.ABOVE_MARKET_THRESHOLD:
                categories.append("Above Market")
            else:
                categories.append("Overpriced")

        return categories

    def get_best_deals(self, max_deals: int = 10) -> pd.DataFrame:
        """
        Get the best deals (most undervalued properties).

        Args:
            max_deals: Maximum number of deals to return

        Returns:
            DataFrame with best deals sorted by value score
        """
        if len(self.data) == 0:
            return pd.DataFrame()

        # Calculate value scores if not already done
        if 'value_score' not in self.data.columns:
            data_with_scores = self.calculate_value_scores()
        else:
            data_with_scores = self.data.copy()

        # Filter only good deals
        good_deals = data_with_scores[
            data_with_scores['value_score'] <= ValueAnalysisConstants.GOOD_DEAL_THRESHOLD
        ].copy()

        if len(good_deals) == 0:
            return pd.DataFrame()

        # Calculate savings amount and percentage
        good_deals['savings_amount'] = good_deals['trend_price'] - \
            good_deals['price']
        good_deals['savings_percentage'] = abs(good_deals['value_score'])

        # Sort by value score (most negative = best deal)
        best_deals = good_deals.sort_values('value_score').head(max_deals)

        return best_deals[[
            'neighborhood', 'price', 'square_meters', 'rooms', 'condition_text',
            'value_score', 'value_category', 'savings_amount', 'savings_percentage',
            'full_url'
        ]]

    def get_value_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of properties by value category.

        Returns:
            Dictionary with value category counts
        """
        if 'value_category' not in self.data.columns:
            data_with_scores = self.calculate_value_scores()
        else:
            data_with_scores = self.data.copy()

        if len(data_with_scores) == 0:
            return {
                "Excellent Deal": 0,
                "Good Deal": 0,
                "Fair Price": 0,
                "Above Market": 0,
                "Overpriced": 0
            }

        value_counts = data_with_scores['value_category'].value_counts()

        return {
            "Excellent Deal": value_counts.get("Excellent Deal", 0),
            "Good Deal": value_counts.get("Good Deal", 0),
            "Fair Price": value_counts.get("Fair Price", 0),
            "Above Market": value_counts.get("Above Market", 0),
            "Overpriced": value_counts.get("Overpriced", 0)
        }

    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Get market trend analysis data.

        Returns:
            Dictionary with trend analysis information
        """
        if self._trend_coefficients is None or len(self.data) < 3:
            return {
                'has_trend': False,
                'slope': 0,
                'intercept': 0,
                'correlation': 0,
                'r_squared': 0,
                'trend_direction': 'Insufficient data'
            }

        try:
            x = self.data['square_meters'].values
            y = self.data['price'].values

            # Calculate correlation
            correlation = np.corrcoef(x, y)[0, 1]

            # Calculate R-squared
            trend_y = np.poly1d(self._trend_coefficients)(x)
            ss_res = np.sum((y - trend_y) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            # Determine trend direction
            slope = self._trend_coefficients[0]
            if slope > 0:
                trend_direction = "Positive (larger properties cost more)"
            elif slope < 0:
                trend_direction = "Negative (larger properties cost less)"
            else:
                trend_direction = "Flat (size doesn't affect price)"

            return {
                'has_trend': True,
                'slope': slope,
                'intercept': self._trend_coefficients[1] if len(self._trend_coefficients) > 1 else 0,
                'correlation': correlation,
                'r_squared': r_squared,
                'trend_direction': trend_direction
            }

        except Exception as e:
            logger.warning(f"Error calculating trend analysis: {e}")
            return {
                'has_trend': False,
                'slope': 0,
                'intercept': 0,
                'correlation': 0,
                'r_squared': 0,
                'trend_direction': 'Error calculating trend'
            }

    def calculate_property_efficiency(self) -> pd.DataFrame:
        """
        Calculate efficiency metrics for properties.

        Returns:
            DataFrame with efficiency calculations
        """
        if len(self.data) == 0 or 'rooms' not in self.data.columns:
            return self.data.copy()

        result_df = self.data.copy()

        # Calculate square meters per room
        result_df['sqm_per_room'] = result_df['square_meters'] / \
            result_df['rooms']
        result_df['sqm_per_room'] = result_df['sqm_per_room'].replace(
            [np.inf, -np.inf], np.nan)

        # Calculate price per room
        result_df['price_per_room'] = result_df['price'] / result_df['rooms']
        result_df['price_per_room'] = result_df['price_per_room'].replace(
            [np.inf, -np.inf], np.nan)

        # Calculate efficiency score (higher sqm per room at lower price per sqm = better)
        if len(result_df) > 1:
            # Normalize sqm_per_room (higher is better)
            sqm_per_room_norm = (
                (result_df['sqm_per_room'] - result_df['sqm_per_room'].min()) /
                (result_df['sqm_per_room'].max() -
                 result_df['sqm_per_room'].min())
            ).fillna(0.5)

            # Normalize price_per_sqm (lower is better)
            price_per_sqm_norm = 1 - (
                (result_df['price_per_sqm'] - result_df['price_per_sqm'].min()) /
                (result_df['price_per_sqm'].max() -
                 result_df['price_per_sqm'].min())
            ).fillna(0.5)

            # Combined efficiency score
            result_df['efficiency_score'] = (
                sqm_per_room_norm + price_per_sqm_norm) / 2 * 100
        else:
            # Neutral score for single property
            result_df['efficiency_score'] = 50

        return result_df

    def _add_empty_value_data(self) -> pd.DataFrame:
        """Add empty value analysis columns to dataframe."""
        result_df = self.data.copy()
        result_df['value_score'] = 0
        result_df['value_category'] = "No Analysis"
        result_df['trend_price'] = result_df['price'] if 'price' in result_df.columns else 0
        return result_df

    def get_market_median_data(self) -> Dict[str, float]:
        """
        Calculate market median values for reference lines.

        Returns:
            Dictionary with median price and size values
        """
        if len(self.data) == 0:
            return {
                'median_price': 0,
                'median_size': 0,
                'median_price_per_sqm': 0
            }

        return {
            'median_price': self.data['price'].median(),
            'median_size': self.data['square_meters'].median(),
            'median_price_per_sqm': self.data['price_per_sqm'].median()
        }

    def identify_outliers(self, method: str = 'iqr') -> pd.DataFrame:
        """
        Identify outlier properties using statistical methods.

        Args:
            method: Method to use ('iqr' or 'zscore')

        Returns:
            DataFrame with outlier flags
        """
        if len(self.data) < 4:
            result_df = self.data.copy()
            result_df['is_outlier'] = False
            result_df['outlier_reason'] = None
            return result_df

        result_df = self.data.copy()
        result_df['is_outlier'] = False
        result_df['outlier_reason'] = None

        try:
            if method == 'iqr':
                # IQR method for price per sqm
                Q1 = self.data['price_per_sqm'].quantile(0.25)
                Q3 = self.data['price_per_sqm'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                price_outliers = (
                    (self.data['price_per_sqm'] < lower_bound) |
                    (self.data['price_per_sqm'] > upper_bound)
                )

                result_df.loc[price_outliers, 'is_outlier'] = True
                result_df.loc[
                    self.data['price_per_sqm'] < lower_bound, 'outlier_reason'
                ] = 'Unusually low price/sqm'
                result_df.loc[
                    self.data['price_per_sqm'] > upper_bound, 'outlier_reason'
                ] = 'Unusually high price/sqm'

            elif method == 'zscore':
                # Z-score method
                from scipy import stats
                z_scores = np.abs(stats.zscore(self.data['price_per_sqm']))
                outliers = z_scores > 2  # 2 standard deviations

                result_df.loc[outliers, 'is_outlier'] = True
                result_df.loc[outliers,
                              'outlier_reason'] = 'Statistical outlier (Z-score > 2)'

        except Exception as e:
            logger.warning(f"Error identifying outliers: {e}")

        return result_df
