"""Centralized trend analysis utilities using LOWESS for consistent market value calculations."""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
from statsmodels.nonparametric.smoothers_lowess import lowess
import logging

from src.config.constants import ValueAnalysisConstants

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Centralized LOWESS-based trend analysis for consistent value calculations across the application."""

    @staticmethod
    def calculate_lowess_trend(
        x_data: np.ndarray,
        y_data: np.ndarray,
        frac: float = 0.6666666
    ) -> Tuple[np.ndarray, bool]:
        """
        Calculate LOWESS trend line for given x and y data.

        Args:
            x_data: Array of x values (e.g., square_meters)
            y_data: Array of y values (e.g., price)
            frac: Fraction of data used for smoothing (default matches Plotly's LOWESS)

        Returns:
            Tuple of (predicted_y_values, success_flag)
        """
        try:
            if len(x_data) < 3 or len(y_data) < 3 or len(x_data) != len(y_data):
                logger.warning("Insufficient data for LOWESS calculation")
                return np.zeros_like(y_data), False

            # Sort by x values for proper LOWESS calculation
            sorted_indices = np.argsort(x_data)
            x_sorted = x_data[sorted_indices]
            y_sorted = y_data[sorted_indices]

            # Apply LOWESS smoothing
            lowess_result = lowess(
                y_sorted, x_sorted, frac=frac, return_sorted=False)

            # Map LOWESS predictions back to original order
            predicted_values = np.zeros_like(y_data)
            predicted_values[sorted_indices] = lowess_result

            return predicted_values, True

        except Exception as e:
            logger.error(f"LOWESS calculation failed: {e}")
            return np.zeros_like(y_data), False

    @staticmethod
    def calculate_value_scores(
        actual_prices: np.ndarray,
        predicted_prices: np.ndarray
    ) -> np.ndarray:
        """
        Calculate value scores as percentage difference from predicted prices.

        Args:
            actual_prices: Array of actual property prices
            predicted_prices: Array of LOWESS-predicted prices

        Returns:
            Array of value scores (negative = good deal, positive = overpriced)
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            value_scores = (actual_prices - predicted_prices) / \
                predicted_prices * 100
            # Handle division by zero
            value_scores = np.where(np.isfinite(value_scores), value_scores, 0)

        return value_scores

    @staticmethod
    def categorize_value_scores(value_scores: np.ndarray) -> np.ndarray:
        """
        Categorize properties based on value scores using consistent thresholds.

        Args:
            value_scores: Array of value scores

        Returns:
            Array of value category strings
        """
        categories = np.full(len(value_scores), 'Fair Price', dtype=object)

        # Apply thresholds
        categories[value_scores <=
                   ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD] = 'Excellent Deal'
        categories[(value_scores > ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD) &
                   (value_scores <= ValueAnalysisConstants.GOOD_DEAL_THRESHOLD)] = 'Good Deal'
        categories[(value_scores > ValueAnalysisConstants.GOOD_DEAL_THRESHOLD) &
                   (value_scores <= ValueAnalysisConstants.FAIR_PRICE_THRESHOLD)] = 'Fair Price'
        categories[(value_scores > ValueAnalysisConstants.FAIR_PRICE_THRESHOLD) &
                   (value_scores <= ValueAnalysisConstants.ABOVE_MARKET_THRESHOLD)] = 'Above Market'
        categories[value_scores >
                   ValueAnalysisConstants.ABOVE_MARKET_THRESHOLD] = 'Overpriced'

        return categories

    @staticmethod
    def calculate_complete_value_analysis(
        df: pd.DataFrame,
        x_column: str = 'square_meters',
        y_column: str = 'price'
    ) -> pd.DataFrame:
        """
        Perform complete LOWESS-based value analysis on a DataFrame.

        Args:
            df: DataFrame with property data
            x_column: Column name for x-axis data (default: 'square_meters')
            y_column: Column name for y-axis data (default: 'price')

        Returns:
            DataFrame with added value analysis columns
        """
        result_df = df.copy()

        if len(df) < 3:
            logger.warning("Insufficient data for value analysis")
            result_df['value_score'] = 0
            result_df['value_category'] = 'Unknown'
            result_df['predicted_price'] = result_df[y_column] if y_column in df.columns else 0
            result_df['savings_amount'] = 0
            return result_df

        try:
            x_data = df[x_column].values
            y_data = df[y_column].values

            # Calculate LOWESS trend
            predicted_prices, success = TrendAnalyzer.calculate_lowess_trend(
                x_data, y_data)

            if success:
                # Calculate value scores
                value_scores = TrendAnalyzer.calculate_value_scores(
                    y_data, predicted_prices)

                # Categorize properties
                value_categories = TrendAnalyzer.categorize_value_scores(
                    value_scores)

                # Add analysis columns
                result_df['value_score'] = value_scores
                result_df['value_category'] = value_categories
                result_df['predicted_price'] = predicted_prices
                result_df['savings_amount'] = predicted_prices - y_data

            else:
                # Fallback values
                result_df['value_score'] = 0
                result_df['value_category'] = 'Unknown'
                result_df['predicted_price'] = y_data
                result_df['savings_amount'] = 0

        except Exception as e:
            logger.error(f"Complete value analysis failed: {e}")
            result_df['value_score'] = 0
            result_df['value_category'] = 'Unknown'
            result_df['predicted_price'] = result_df[y_column] if y_column in df.columns else 0
            result_df['savings_amount'] = 0

        return result_df

    @staticmethod
    def get_trend_statistics(
        x_data: np.ndarray,
        y_data: np.ndarray,
        predicted_prices: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculate trend statistics for LOWESS analysis.

        Args:
            x_data: Array of x values
            y_data: Array of actual y values
            predicted_prices: Array of LOWESS-predicted values

        Returns:
            Dictionary with trend statistics
        """
        try:
            # Calculate correlation
            correlation = np.corrcoef(x_data, y_data)[
                0, 1] if len(x_data) > 1 else 0

            # Calculate R-squared equivalent for LOWESS
            ss_res = np.sum((y_data - predicted_prices) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            # Approximate slope by comparing endpoints of trend
            if len(predicted_prices) > 1:
                # Get sorted order for slope calculation
                sorted_indices = np.argsort(x_data)
                x_sorted = x_data[sorted_indices]
                pred_sorted = predicted_prices[sorted_indices]

                # Calculate approximate slope
                slope = (pred_sorted[-1] - pred_sorted[0]) / (x_sorted[-1] -
                                                              x_sorted[0]) if x_sorted[-1] != x_sorted[0] else 0
            else:
                slope = 0

            # Determine trend direction
            if slope > 0:
                trend_direction = "Positive (larger properties cost more)"
            elif slope < 0:
                trend_direction = "Negative (larger properties cost less)"
            else:
                trend_direction = "Flat (size doesn't affect price)"

            return {
                'has_trend': True,
                'slope': slope,
                'correlation': correlation,
                'r_squared': r_squared,
                'trend_direction': trend_direction
            }

        except Exception as e:
            logger.warning(f"Error calculating trend statistics: {e}")
            return {
                'has_trend': False,
                'slope': 0,
                'correlation': 0,
                'r_squared': 0,
                'trend_direction': 'Unable to calculate'
            }
