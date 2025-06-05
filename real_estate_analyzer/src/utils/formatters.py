"""Formatting utilities for numbers, currency, and display values."""

import pandas as pd
from typing import Union, Dict, Optional


class NumberFormatter:
    """Utility class for formatting numbers and currency values."""

    @staticmethod
    def format_currency(value: Union[float, int], currency: str = '₪',
                        short_form: bool = True, decimals: int = 0) -> str:
        """
        Format currency values for display with optional short form.

        Args:
            value: Numeric value to format
            currency: Currency symbol (default: ₪)
            short_form: Use K/M notation for large numbers
            decimals: Number of decimal places for short form

        Returns:
            str: Formatted currency string
        """
        if pd.isna(value) or value is None:
            return 'N/A'

        value = float(value)

        if short_form:
            if abs(value) >= 1000000:
                formatted_value = value / 1000000
                if decimals == 0 and formatted_value == int(formatted_value):
                    return f"{currency}{int(formatted_value)}M"
                else:
                    return f"{currency}{formatted_value:.{decimals}f}M"
            elif abs(value) >= 1000:
                formatted_value = value / 1000
                if decimals == 0 and formatted_value == int(formatted_value):
                    return f"{currency}{int(formatted_value)}K"
                else:
                    return f"{currency}{formatted_value:.{decimals}f}K"
            else:
                return f"{currency}{value:,.0f}"
        else:
            return f"{currency}{value:,.0f}"

    @staticmethod
    def format_number(value: Union[float, int], short_form: bool = True,
                      decimals: int = 0) -> str:
        """
        Format numbers with optional short form notation.

        Args:
            value: Numeric value to format
            short_form: Use K/M notation for large numbers
            decimals: Number of decimal places for short form

        Returns:
            str: Formatted number string
        """
        if pd.isna(value) or value is None:
            return 'N/A'

        value = float(value)

        if short_form:
            if abs(value) >= 1000000:
                formatted_value = value / 1000000
                if decimals == 0 and formatted_value == int(formatted_value):
                    return f"{int(formatted_value)}M"
                else:
                    return f"{formatted_value:.{decimals}f}M"
            elif abs(value) >= 1000:
                formatted_value = value / 1000
                if decimals == 0 and formatted_value == int(formatted_value):
                    return f"{int(formatted_value)}K"
                else:
                    return f"{formatted_value:.{decimals}f}K"
            else:
                return f"{value:,.0f}"
        else:
            return f"{value:,.0f}"

    @staticmethod
    def create_price_marks(min_value: float, max_value: float,
                           num_marks: int = 5, short_form: bool = True) -> Dict[int, str]:
        """
        Create price marks for sliders with proper formatting.

        Args:
            min_value: Minimum value
            max_value: Maximum value
            num_marks: Number of marks to create
            short_form: Use K/M notation

        Returns:
            Dict[int, str]: Dictionary mapping values to formatted strings
        """
        if max_value <= min_value:
            # Use 1 decimal for better precision
            return {int(min_value): NumberFormatter.format_currency(min_value, short_form=short_form, decimals=1)}

        step = (max_value - min_value) / \
            (num_marks - 1) if num_marks > 1 else 0
        marks = {}

        for i in range(num_marks):
            value = min_value + (i * step)
            if i == num_marks - 1:  # Last mark should be exact max
                value = max_value
            # Use 1 decimal place for better precision in M/K ranges
            marks[int(value)] = NumberFormatter.format_currency(
                value, short_form=short_form, decimals=1)

        return marks

    @staticmethod
    def create_number_marks(min_value: float, max_value: float,
                            num_marks: int = 5, short_form: bool = False,
                            suffix: str = "") -> Dict[int, str]:
        """
        Create number marks for sliders with proper formatting.

        Args:
            min_value: Minimum value
            max_value: Maximum value
            num_marks: Number of marks to create
            short_form: Use K/M notation
            suffix: Suffix to add (e.g., "m²")

        Returns:
            Dict[int, str]: Dictionary mapping values to formatted strings
        """
        if max_value <= min_value:
            return {int(min_value): f"{NumberFormatter.format_number(min_value, short_form=short_form)}{suffix}"}

        step = (max_value - min_value) / \
            (num_marks - 1) if num_marks > 1 else 0
        marks = {}

        for i in range(num_marks):
            value = min_value + (i * step)
            if i == num_marks - 1:  # Last mark should be exact max
                value = max_value
            marks[int(
                value)] = f"{NumberFormatter.format_number(value, short_form=short_form)}{suffix}"

        return marks


class PriceInputFormatter:
    """Utilities for formatting price inputs and placeholders."""

    @staticmethod
    def format_placeholder(value: Union[float, int]) -> str:
        """Format placeholder text for price inputs."""
        return NumberFormatter.format_currency(value, short_form=True, decimals=1)

    @staticmethod
    def get_step_value(price_range: float) -> int:
        """Get appropriate step value for price inputs based on range."""
        if price_range >= 10000000:  # 10M+
            return 100000  # 100K steps
        elif price_range >= 5000000:  # 5M+
            return 50000   # 50K steps
        elif price_range >= 1000000:  # 1M+
            return 25000   # 25K steps
        else:
            return 10000   # 10K steps
