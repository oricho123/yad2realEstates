"""Shared hover data structures and templates for all visualization components."""

import pandas as pd
from typing import List
from dataclasses import dataclass
from enum import IntEnum


class HoverDataFields(IntEnum):
    """Enum for hover data field indices to prevent magic numbers."""
    CITY = 0
    NEIGHBORHOOD = 1
    ROOMS = 2
    PRICE = 3
    PRICE_PER_SQM = 4
    CONDITION_TEXT = 5
    AD_TYPE = 6
    STREET_DISPLAY = 7
    FLOOR = 8
    FULL_URL = 9
    VALUE_SCORE = 10
    VALUE_CATEGORY = 11
    PREDICTED_PRICE = 12
    SAVINGS_AMOUNT = 13


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
    VALUE_SCORE = 8
    VALUE_CATEGORY = 9
    PREDICTED_PRICE = 10
    SAVINGS_AMOUNT = 11


class AnalyticsHoverDataFields(IntEnum):
    """Enum for analytics charts hover data field indices."""
    AVG_SIZE = 0
    AVG_PRICE_PER_SQM = 1


@dataclass
class PropertyHoverData:
    """Structured data for property hover information."""
    city: str
    neighborhood: str
    rooms: int
    price: int
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

    def to_list(self) -> List:
        """Convert to list for Plotly customdata."""
        return [
            self.city, self.neighborhood, self.rooms, self.price, self.price_per_sqm,
            self.condition_text, self.ad_type, self.street_display, self.floor,
            self.full_url, self.value_score, self.value_category,
            self.predicted_price, self.savings_amount
        ]

    @classmethod
    def from_row(cls, row: pd.Series) -> 'PropertyHoverData':
        """Create PropertyHoverData from a DataFrame row."""
        street_display = (
            row['street'] if pd.notna(row['street']) and str(row['street']).strip() != ''
            else row['neighborhood']
        )

        return cls(
            city=str(row['city']) if pd.notna(
                row['city']) else 'Unknown',
            neighborhood=str(row['neighborhood']) if pd.notna(
                row['neighborhood']) else 'Unknown',
            rooms=int(row['rooms']) if pd.notna(row['rooms']) else 0,
            price=int(round(row['price'])) if pd.notna(row['price']) else 0,
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
    value_score: float
    value_category: str
    predicted_price: int
    savings_amount: int

    def to_list(self) -> List:
        """Convert to list for Plotly customdata."""
        return [
            self.neighborhood, self.price, self.rooms, self.condition_text,
            self.ad_type, self.street_display, self.floor, self.full_url,
            self.value_score, self.value_category, self.predicted_price, self.savings_amount
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
class AnalyticsHoverData:
    """Structured data for analytics charts hover information."""
    avg_size: float
    avg_price_per_sqm: float

    def to_list(self) -> List:
        """Convert to list for Plotly customdata."""
        return [self.avg_size, self.avg_price_per_sqm]


class HoverTemplate:
    """Builder for hover templates with named field access."""

    @staticmethod
    def build_property_hover_template() -> str:
        """Build hover template for scatter plot."""
        return (
            f'<b>🏡 %{{customdata[{HoverDataFields.NEIGHBORHOOD}]}}</b><br>'
            f'<i>🏙️ %{{customdata[{HoverDataFields.CITY}]}}</i><br>'
            f'<i>📍 %{{customdata[{HoverDataFields.STREET_DISPLAY}]}}</i><br><br>'
            '<b>📊 Property Details:</b><br>'
            f'<b>Actual Price:</b> ₪%{{customdata[{HoverDataFields.PRICE}]:,.0f}}<br>'
            '<b>Size:</b> %{x} sqm<br>'
            f'<b>Price/sqm:</b> ₪%{{customdata[{HoverDataFields.PRICE_PER_SQM}]:,.0f}}<br>'
            f'<b>Rooms:</b> %{{customdata[{HoverDataFields.ROOMS}]}} | %{{customdata[{HoverDataFields.CONDITION_TEXT}]}}<br><br>'
            '<b>💡 Market Value Analysis:</b><br>'
            f'<b>Expected Price:</b> ₪%{{customdata[{HoverDataFields.PREDICTED_PRICE}]:,.0f}}<br>'
            f'<b>Value Score:</b> %{{customdata[{HoverDataFields.VALUE_SCORE}]}}%<br>'
            f'<b>Assessment:</b> %{{customdata[{HoverDataFields.VALUE_CATEGORY}]}}<br>'
            f'<b>Savings/Premium:</b> ₪%{{customdata[{HoverDataFields.SAVINGS_AMOUNT}]:,.0f}}<br><br>'
            '<b>👆 Click to view listing</b><extra></extra>'
        )

    @staticmethod
    def build_map_hover_template() -> str:
        """Build hover template for map visualization."""
        return (
            f'<b>🏡 %{{customdata[{MapHoverDataFields.NEIGHBORHOOD}]}}</b><br>'
            f'<i>📍 %{{customdata[{MapHoverDataFields.STREET_DISPLAY}]}}</i><br><br>'
            '<b>📊 Property Details:</b><br>'
            f'<b>Price:</b> ₪%{{customdata[{MapHoverDataFields.PRICE}]:,.0f}}<br>'
            '<b>Size:</b> %{text} sqm<br>'
            f'<b>Rooms:</b> %{{customdata[{MapHoverDataFields.ROOMS}]}}<br>'
            f'<b>Condition:</b> %{{customdata[{MapHoverDataFields.CONDITION_TEXT}]}}<br><br>'
            '<b>💡 Market Value Analysis:</b><br>'
            f'<b>Expected Price:</b> ₪%{{customdata[{MapHoverDataFields.PREDICTED_PRICE}]:,.0f}}<br>'
            f'<b>Value Score:</b> %{{customdata[{MapHoverDataFields.VALUE_SCORE}]}}%<br>'
            f'<b>Assessment:</b> %{{customdata[{MapHoverDataFields.VALUE_CATEGORY}]}}<br>'
            f'<b>Savings/Premium:</b> ₪%{{customdata[{MapHoverDataFields.SAVINGS_AMOUNT}]:,.0f}}<br><br>'
            '<b>👆 Click to view listing</b><extra></extra>'
        )

    @staticmethod
    def build_analytics_hover_template() -> str:
        """Build hover template for analytics charts."""
        return (
            '<b>%{x}</b><br>'
            '<b>Avg Total Price:</b> ₪%{y:,.0f}<br>'
            f'<b>Avg Size:</b> %{{customdata[{AnalyticsHoverDataFields.AVG_SIZE}]:.0f}} sqm<br>'
            f'<b>Avg Price/sqm:</b> ₪%{{customdata[{AnalyticsHoverDataFields.AVG_PRICE_PER_SQM}]:,.0f}}<br>'
            '<b>Properties:</b> %{text}<br>'
            '<b>Real Affordability:</b> %{marker.color:.0f}/100<br>'
            '<br><i>Higher score = more affordable</i><extra></extra>'
        )
