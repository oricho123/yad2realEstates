"""Simple browser storage manager for single dataset auto-save/load."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd

from ..data.models import PropertyDataFrame

logger = logging.getLogger(__name__)


class SimpleStorageManager:
    """
    Simple browser storage manager for single dataset per user.

    Provides auto-save/auto-load functionality using browser localStorage
    with a fixed storage key for seamless user experience.
    """

    STORAGE_KEY = 'real_estate_data'

    def __init__(self):
        """Initialize the simple storage manager."""
        logger.info(
            f"Initialized SimpleStorageManager with key='{self.STORAGE_KEY}'")

    def prepare_data_for_storage(self, data) -> Dict[str, Any]:
        """
        Prepare data for browser storage.

        Args:
            data: PropertyDataFrame or pandas DataFrame to store

        Returns:
            Dictionary ready for JSON serialization and browser storage
        """
        try:
            # Handle both PropertyDataFrame and regular DataFrame
            if hasattr(data, 'data') and hasattr(data, 'is_empty'):
                # PropertyDataFrame
                records = data.data.to_dict(
                    'records') if not data.is_empty else []
                property_count = len(data)
            else:
                # Regular pandas DataFrame
                records = data.to_dict('records') if not data.empty else []
                property_count = len(data)

            # Prepare simple storage payload
            storage_payload = {
                'data': records,
                'property_count': property_count,
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }

            logger.info(f"Prepared {property_count} properties for storage")
            return storage_payload

        except Exception as e:
            logger.error(f"Failed to prepare data for storage: {str(e)}")
            raise

    def prepare_data_from_storage(self, storage_data: Dict[str, Any]) -> PropertyDataFrame:
        """
        Convert stored data back to PropertyDataFrame.

        Args:
            storage_data: Data retrieved from browser storage

        Returns:
            PropertyDataFrame instance
        """
        try:
            # Extract data records
            records = storage_data.get('data', [])

            if records:
                # Create DataFrame from records
                df = pd.DataFrame(records)

                # Ensure proper data types
                numeric_columns = ['price', 'square_meters',
                                   'price_per_sqm', 'lat', 'lng', 'rooms']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # Convert datetime columns
                datetime_columns = ['scraped_at']
                for col in datetime_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')

                property_data = PropertyDataFrame(df)
            else:
                # Empty dataset
                property_data = PropertyDataFrame(pd.DataFrame())

            property_count = storage_data.get(
                'property_count', len(property_data))
            logger.info(f"Restored {property_count} properties from storage")

            return property_data

        except Exception as e:
            logger.error(f"Failed to restore data from storage: {str(e)}")
            # Return empty DataFrame on error
            return PropertyDataFrame(pd.DataFrame())

    def save_data(self, data) -> bool:
        """
        Save data to browser storage.
        Note: This method prepares data for client-side saving.

        Args:
            data: PropertyDataFrame or pandas DataFrame to save

        Returns:
            True if preparation successful (actual saving happens client-side)
        """
        try:
            storage_payload = self.prepare_data_for_storage(data)
            logger.info("Data prepared for client-side storage")
            return True
        except Exception as e:
            logger.error(f"Failed to prepare data for saving: {str(e)}")
            return False

    def load_data(self) -> Optional[PropertyDataFrame]:
        """
        Load data from browser storage.
        Note: This is a placeholder - actual loading happens client-side.

        Returns:
            None (actual loading happens via client-side callbacks)
        """
        logger.info("Data loading should be handled client-side")
        return None

    def has_data(self) -> bool:
        """
        Check if data exists in storage.
        Note: This is a placeholder - actual check happens client-side.

        Returns:
            False (actual check happens via client-side callbacks)
        """
        logger.info("Data existence check should be handled client-side")
        return False

    def clear_data(self) -> bool:
        """
        Clear stored data.
        Note: This is a placeholder - actual clearing happens client-side.

        Returns:
            False (actual clearing happens via client-side callbacks)
        """
        logger.info("Data clearing should be handled client-side")
        return False

    def get_storage_key(self) -> str:
        """Get the localStorage key used for storage."""
        return self.STORAGE_KEY
