"""Browser storage manager for multi-user dataset management."""
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd


from .models import DatasetMetadata, StorageInfo, DatasetSummary
from ..data.models import PropertyDataFrame
from ..config.settings import AppSettings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class StorageQuotaError(StorageError):
    """Raised when storage quota is exceeded."""
    pass


class BrowserStorageManager:
    """
    Manages browser-based data storage via Dash clientside callbacks.

    This class provides a Python interface for browser localStorage operations
    that are executed via JavaScript clientside callbacks.
    """

    def __init__(self):
        """Initialize the browser storage manager."""
        self.storage_key = self._get_storage_key()
        self.max_datasets = self._get_max_datasets()
        self.max_size_bytes = self._get_max_size_bytes()

        logger.info(
            f"Initialized BrowserStorageManager with key='{self.storage_key}', "
            f"max_datasets={self.max_datasets}, max_size={self.max_size_bytes / 1024 / 1024:.1f}MB"
        )

    def _get_storage_key(self) -> str:
        """Get the storage key for localStorage."""
        return getattr(AppSettings, 'BROWSER_STORAGE_KEY', 'real_estate_analyzer')

    def _get_max_datasets(self) -> int:
        """Get maximum number of datasets per user."""
        return getattr(AppSettings, 'MAX_DATASETS_PER_USER', 10)

    def _get_max_size_bytes(self) -> int:
        """Get maximum storage size in bytes."""
        return getattr(AppSettings, 'MAX_STORAGE_SIZE_MB', 50) * 1024 * 1024

    def prepare_dataset_for_storage(self, data, metadata: DatasetMetadata) -> Dict[str, Any]:
        """
        Prepare a dataset for browser storage.

        Args:
            data: PropertyDataFrame or pandas DataFrame to store
            metadata: Dataset metadata

        Returns:
            Dictionary ready for JSON serialization and browser storage

        Raises:
            StorageError: If data preparation fails
        """
        try:
            # Handle both PropertyDataFrame and regular DataFrame
            if hasattr(data, 'data') and hasattr(data, 'is_empty'):
                # PropertyDataFrame
                records = data.data.to_dict(
                    'records') if not data.is_empty else []
                valid_data = data.get_valid_properties()
                location_data = data.get_properties_with_location()
                property_count = len(data)
                valid_count = len(valid_data)
                location_count = len(location_data)
            else:
                # Regular pandas DataFrame
                records = data.to_dict('records') if not data.empty else []
                property_count = len(data)
                # For regular DataFrame, assume all data is valid
                valid_count = property_count
                location_count = len(data.dropna(
                    subset=['lat', 'lng'])) if 'lat' in data.columns and 'lng' in data.columns else 0

            # Update metadata with current statistics
            json_str = json.dumps(records)
            size_bytes = len(json_str.encode('utf-8'))

            metadata.update_stats(
                property_count=property_count,
                valid_count=valid_count,
                location_count=location_count,
                size_bytes=size_bytes
            )

            # Prepare storage payload
            storage_payload = {
                'metadata': metadata.to_dict(),
                'data': records,
                'version': '1.0',  # For future compatibility
                'stored_at': datetime.now().isoformat()
            }

            logger.info(
                f"Prepared dataset '{metadata.name}' for storage: "
                f"{metadata.property_count} properties, {size_bytes / 1024:.1f}KB"
            )

            return storage_payload

        except Exception as e:
            logger.error(f"Failed to prepare dataset for storage: {str(e)}")
            raise StorageError(f"Dataset preparation failed: {str(e)}")

    def prepare_dataset_from_storage(self, storage_data: Dict[str, Any]) -> Tuple[PropertyDataFrame, DatasetMetadata]:
        """
        Convert stored data back to PropertyDataFrame and metadata.

        Args:
            storage_data: Data retrieved from browser storage

        Returns:
            Tuple of (PropertyDataFrame, DatasetMetadata)

        Raises:
            StorageError: If data conversion fails
        """
        try:
            # Extract metadata
            metadata_dict = storage_data.get('metadata', {})
            metadata = DatasetMetadata.from_dict(metadata_dict)

            # Extract and convert data
            records = storage_data.get('data', [])

            if records:
                # Create DataFrame from records
                df = pd.DataFrame(records)

                # Ensure proper data types (similar to PropertyDataLoader)
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

            logger.info(
                f"Restored dataset '{metadata.name}': "
                f"{len(property_data)} properties from storage"
            )

            return property_data, metadata

        except Exception as e:
            logger.error(f"Failed to restore dataset from storage: {str(e)}")
            raise StorageError(f"Dataset restoration failed: {str(e)}")

    def validate_storage_constraints(self, new_dataset_size: int, current_datasets_count: int) -> None:
        """
        Validate storage constraints before saving.

        Args:
            new_dataset_size: Size of new dataset in bytes
            current_datasets_count: Current number of stored datasets

        Raises:
            StorageQuotaError: If storage constraints would be violated
        """
        # Check dataset count limit
        if current_datasets_count >= self.max_datasets:
            raise StorageQuotaError(
                f"Maximum number of datasets ({self.max_datasets}) reached. "
                f"Please delete some datasets before saving new ones."
            )

        # Check size limit
        if new_dataset_size > self.max_size_bytes:
            raise StorageQuotaError(
                f"Dataset size ({new_dataset_size / 1024 / 1024:.1f}MB) exceeds "
                f"maximum allowed size ({self.max_size_bytes / 1024 / 1024:.1f}MB)."
            )

        logger.debug(
            f"Storage constraints validation passed for {new_dataset_size} bytes")

    def create_dataset_summary(self, data: PropertyDataFrame, metadata: DatasetMetadata,
                               preview_size: int = 3) -> DatasetSummary:
        """
        Create a dataset summary for UI display.

        Args:
            data: PropertyDataFrame
            metadata: Dataset metadata
            preview_size: Number of records to include in preview

        Returns:
            DatasetSummary with preview data
        """
        try:
            # Get preview data (first few records)
            preview_records = []
            if not data.is_empty and len(data) > 0:
                preview_df = data.data.head(preview_size)

                # Select key columns for preview
                preview_columns = [
                    'neighborhood', 'price', 'rooms', 'square_meters',
                    'price_per_sqm', 'condition_text'
                ]

                available_columns = [
                    col for col in preview_columns if col in preview_df.columns]
                if available_columns:
                    preview_records = preview_df[available_columns].to_dict(
                        'records')

            return DatasetSummary(
                metadata=metadata,
                data_preview=preview_records
            )

        except Exception as e:
            logger.warning(f"Failed to create dataset summary: {str(e)}")
            return DatasetSummary(metadata=metadata, data_preview=[])

    def calculate_storage_info(self, datasets_metadata: List[DatasetMetadata]) -> StorageInfo:
        """
        Calculate storage information from dataset metadata.

        Args:
            datasets_metadata: List of dataset metadata

        Returns:
            StorageInfo with usage statistics
        """
        try:
            # Calculate totals
            total_datasets = len(datasets_metadata)
            total_size = sum(meta.size_bytes for meta in datasets_metadata)

            # Find date range
            dates = [
                meta.created_at for meta in datasets_metadata if meta.created_at]
            oldest_date = min(dates) if dates else None
            newest_date = max(dates) if dates else None

            # Estimate browser quota (this will be updated by clientside callback)
            estimated_quota = 10 * 1024 * 1024  # Conservative 10MB estimate

            storage_info = StorageInfo(
                total_datasets=total_datasets,
                total_size_bytes=total_size,
                estimated_quota_bytes=estimated_quota,
                max_datasets_limit=self.max_datasets,
                max_size_limit_bytes=self.max_size_bytes,
                supports_local_storage=True,  # Will be verified by clientside
                supports_compression=True,
                oldest_dataset_date=oldest_date,
                newest_dataset_date=newest_date
            )

            logger.debug(
                f"Calculated storage info: {total_datasets} datasets, "
                f"{total_size / 1024:.1f}KB total, {storage_info.usage_percentage:.1f}% used"
            )

            return storage_info

        except Exception as e:
            logger.error(f"Failed to calculate storage info: {str(e)}")
            # Return default storage info
            return StorageInfo()

    def generate_dataset_name(self, scraped_params: Dict[str, Any]) -> str:
        """
        Generate a descriptive name for a dataset based on scraping parameters.

        Args:
            scraped_params: Parameters used for scraping

        Returns:
            Generated dataset name
        """
        try:
            parts = []

            # Add location info
            if scraped_params.get('city'):
                # You could map city IDs to names here
                parts.append(f"City {scraped_params['city']}")

            # Add price range
            min_price = scraped_params.get('min_price')
            max_price = scraped_params.get('max_price')
            if min_price or max_price:
                price_parts = []
                if min_price:
                    price_parts.append(f"₪{min_price:,}")
                if max_price:
                    price_parts.append(f"₪{max_price:,}")
                parts.append(" - ".join(price_parts))

            # Add room range
            min_rooms = scraped_params.get('min_rooms')
            max_rooms = scraped_params.get('max_rooms')
            if min_rooms or max_rooms:
                if min_rooms == max_rooms:
                    parts.append(f"{min_rooms} rooms")
                else:
                    room_parts = []
                    if min_rooms:
                        room_parts.append(f"{min_rooms}")
                    if max_rooms:
                        room_parts.append(f"{max_rooms}")
                    parts.append(f"{'-'.join(room_parts)} rooms")

            # Combine parts
            if parts:
                name = " | ".join(parts)
            else:
                name = f"Search {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Limit length
            if len(name) > 50:
                name = name[:47] + "..."

            return name

        except Exception as e:
            logger.warning(f"Failed to generate dataset name: {str(e)}")
            return f"Dataset {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    def cleanup_old_datasets(self, datasets_metadata: List[DatasetMetadata],
                             max_age_days: int = 30) -> List[str]:
        """
        Identify old datasets that should be cleaned up.

        Args:
            datasets_metadata: List of dataset metadata
            max_age_days: Maximum age in days before suggesting cleanup

        Returns:
            List of dataset IDs suggested for deletion
        """
        try:
            cleanup_ids = []
            cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

            for metadata in datasets_metadata:
                if metadata.created_at and metadata.created_at.timestamp() < cutoff_date:
                    cleanup_ids.append(metadata.id)

            if cleanup_ids:
                logger.info(
                    f"Identified {len(cleanup_ids)} datasets for cleanup (older than {max_age_days} days)")

            return cleanup_ids

        except Exception as e:
            logger.warning(f"Failed to identify cleanup candidates: {str(e)}")
            return []

    def get_storage_recommendations(self, storage_info: StorageInfo) -> List[str]:
        """
        Get storage management recommendations.

        Args:
            storage_info: Current storage information

        Returns:
            List of recommendation messages
        """
        recommendations = []

        try:
            # Usage-based recommendations
            if storage_info.usage_percentage > 90:
                recommendations.append(
                    "⚠️ Storage is nearly full. Consider deleting old datasets."
                )
            elif storage_info.usage_percentage > 75:
                recommendations.append(
                    "💡 Storage usage is high. You may want to clean up old datasets."
                )

            # Dataset count recommendations
            if storage_info.total_datasets >= storage_info.max_datasets_limit:
                recommendations.append(
                    f"📊 You have reached the maximum number of datasets ({storage_info.max_datasets_limit}). "
                    f"Delete some datasets to save new ones."
                )
            elif storage_info.total_datasets >= storage_info.max_datasets_limit * 0.8:
                recommendations.append(
                    f"📈 You have {storage_info.total_datasets} of {storage_info.max_datasets_limit} datasets. "
                    f"Consider organizing or cleaning up old ones."
                )

            # Age-based recommendations
            if storage_info.oldest_dataset_date:
                age_days = (datetime.now() -
                            storage_info.oldest_dataset_date).days
                if age_days > 30:
                    recommendations.append(
                        f"🗓️ Your oldest dataset is {age_days} days old. "
                        f"Consider reviewing and cleaning up old datasets."
                    )

            # Positive feedback
            if not recommendations and storage_info.total_datasets > 0:
                recommendations.append(
                    f"✅ Storage looks good! You have {storage_info.total_datasets} datasets "
                    f"using {storage_info.usage_percentage:.1f}% of available space."
                )

        except Exception as e:
            logger.warning(
                f"Failed to generate storage recommendations: {str(e)}")
            recommendations.append(
                "ℹ️ Unable to analyze storage usage at this time.")

        return recommendations
