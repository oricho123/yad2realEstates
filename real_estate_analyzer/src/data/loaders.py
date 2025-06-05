"""Data loading and validation utilities."""
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

from src.config.constants import PropertyValidation
from src.data.models import PropertyDataFrame

logger = logging.getLogger(__name__)


class PropertyDataLoader:
    """Handles loading and validating property data."""
    
    def __init__(self, data_directory: Optional[Path] = None):
        """Initialize the data loader."""
        self.data_directory = data_directory or Path("data/scraped")
        self.data_directory = Path(self.data_directory)
    
    def load_property_listings(self, csv_path: str) -> PropertyDataFrame:
        """Load and prepare property listings from CSV."""
        try:
            raw_data = pd.read_csv(csv_path)
            initial_count = len(raw_data)
            logger.info(f"Loaded {initial_count} raw records from {csv_path}")
            
            # Apply data quality validation
            validated_data = self._validate_property_data(raw_data)
            
            # Create PropertyDataFrame
            property_df = PropertyDataFrame(validated_data)
            
            final_count = len(property_df)
            quality_percentage = (final_count / initial_count) * 100 if initial_count > 0 else 0
            
            logger.info(f"Data quality: {final_count}/{initial_count} properties validated ({quality_percentage:.1f}%)")
            
            return property_df
            
        except Exception as e:
            logger.error(f"Error loading property data: {str(e)}")
            raise
    
    def _validate_property_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply data quality validation to property listings."""
        validated_df = df.copy()
        
        # Remove properties with invalid price
        validated_df = validated_df[
            validated_df['price'].notna() &
            (validated_df['price'] > PropertyValidation.MIN_PRICE)
        ]
        
        # Remove properties with invalid square meters
        validated_df = validated_df[
            validated_df['square_meters'].notna() &
            (validated_df['square_meters'] >= PropertyValidation.MIN_SQUARE_METERS)
        ]
        
        # Calculate price per sqm if not exists
        if 'price_per_sqm' not in validated_df.columns:
            validated_df['price_per_sqm'] = validated_df['price'] / validated_df['square_meters']
        
        # Remove unrealistic price per sqm
        validated_df = validated_df[
            (validated_df['price_per_sqm'] >= PropertyValidation.MIN_REALISTIC_PRICE_PER_SQM) &
            (validated_df['price_per_sqm'] <= PropertyValidation.MAX_REALISTIC_PRICE_PER_SQM)
        ]
        
        # Clean coordinate data
        validated_df['lat'] = pd.to_numeric(validated_df['lat'], errors='coerce')
        validated_df['lng'] = pd.to_numeric(validated_df['lng'], errors='coerce')
        
        return validated_df
    
    def find_latest_data_file(self) -> Optional[Path]:
        """Find the most recent CSV data file."""
        if not self.data_directory.exists():
            return None
        
        csv_files = list(self.data_directory.glob("real_estate_listings_*.csv"))
        if not csv_files:
            return None
        
        return max(csv_files, key=lambda f: f.stat().st_mtime)
    
    def create_empty_dataframe(self) -> PropertyDataFrame:
        """Create an empty PropertyDataFrame with correct structure."""
        empty_df = pd.DataFrame(columns=[
            'price', 'square_meters', 'price_per_sqm', 'lat', 'lng',
            'neighborhood', 'rooms', 'condition_text', 'ad_type',
            'property_type', 'street', 'floor', 'full_url'
        ])
        return PropertyDataFrame(empty_df) 