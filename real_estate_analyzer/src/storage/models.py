"""Data models for browser storage management."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class DatasetMetadata:
    """Metadata for browser-stored datasets."""

    # Core identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Dataset"

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Search parameters used to generate this dataset
    scraped_params: Dict[str, Any] = field(default_factory=dict)

    # Dataset statistics
    property_count: int = 0
    size_bytes: int = 0

    # User-defined metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Data quality metrics
    valid_properties_count: int = 0
    properties_with_location_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scraped_params': self.scraped_params,
            'property_count': self.property_count,
            'size_bytes': self.size_bytes,
            'description': self.description,
            'tags': self.tags,
            'valid_properties_count': self.valid_properties_count,
            'properties_with_location_count': self.properties_with_location_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetMetadata':
        """Create DatasetMetadata from dictionary."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except (ValueError, TypeError):
                created_at = datetime.now()

        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except (ValueError, TypeError):
                updated_at = datetime.now()

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'Untitled Dataset'),
            created_at=created_at,
            updated_at=updated_at,
            scraped_params=data.get('scraped_params', {}),
            property_count=data.get('property_count', 0),
            size_bytes=data.get('size_bytes', 0),
            description=data.get('description'),
            tags=data.get('tags', []),
            valid_properties_count=data.get('valid_properties_count', 0),
            properties_with_location_count=data.get(
                'properties_with_location_count', 0)
        )

    def update_stats(self, property_count: int, valid_count: int, location_count: int, size_bytes: int) -> None:
        """Update dataset statistics."""
        self.property_count = property_count
        self.valid_properties_count = valid_count
        self.properties_with_location_count = location_count
        self.size_bytes = size_bytes
        self.updated_at = datetime.now()


@dataclass
class StorageInfo:
    """Information about browser storage usage and capabilities."""

    # Storage capacity and usage
    total_datasets: int = 0
    total_size_bytes: int = 0
    estimated_quota_bytes: int = 0

    # Storage limits
    max_datasets_limit: int = 10
    max_size_limit_bytes: int = 50 * 1024 * 1024  # 50MB default

    # Browser capabilities
    supports_local_storage: bool = True
    supports_compression: bool = True

    # Usage statistics
    oldest_dataset_date: Optional[datetime] = None
    newest_dataset_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert storage info to dictionary for JSON serialization."""
        return {
            'total_datasets': self.total_datasets,
            'total_size_bytes': self.total_size_bytes,
            'estimated_quota_bytes': self.estimated_quota_bytes,
            'max_datasets_limit': self.max_datasets_limit,
            'max_size_limit_bytes': self.max_size_limit_bytes,
            'supports_local_storage': self.supports_local_storage,
            'supports_compression': self.supports_compression,
            'oldest_dataset_date': self.oldest_dataset_date.isoformat() if self.oldest_dataset_date else None,
            'newest_dataset_date': self.newest_dataset_date.isoformat() if self.newest_dataset_date else None
        }

    @property
    def usage_percentage(self) -> float:
        """Calculate storage usage as percentage."""
        if self.estimated_quota_bytes > 0:
            return (self.total_size_bytes / self.estimated_quota_bytes) * 100
        return 0.0

    @property
    def is_near_limit(self) -> bool:
        """Check if storage usage is approaching limits."""
        return (
            self.usage_percentage > 80 or
            self.total_datasets >= self.max_datasets_limit or
            self.total_size_bytes >= self.max_size_limit_bytes * 0.8
        )

    @property
    def available_space_bytes(self) -> int:
        """Calculate available storage space."""
        if self.estimated_quota_bytes > 0:
            return max(0, self.estimated_quota_bytes - self.total_size_bytes)
        return self.max_size_limit_bytes - self.total_size_bytes


@dataclass
class DatasetSummary:
    """Summary information for a stored dataset."""

    metadata: DatasetMetadata
    data_preview: List[Dict[str, Any]] = field(
        default_factory=list)  # First few records

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for UI display."""
        return {
            'metadata': self.metadata.to_dict(),
            'data_preview': self.data_preview,
            'display_name': self.get_display_name(),
            'age_display': self.get_age_display(),
            'size_display': self.get_size_display()
        }

    def get_display_name(self) -> str:
        """Get user-friendly display name."""
        if self.metadata.name and self.metadata.name != "Untitled Dataset":
            return self.metadata.name

        # Generate name from scraped params
        params = self.metadata.scraped_params
        if params.get('city'):
            city_name = "Unknown City"
            # You could add city name mapping here
            parts = [f"Search in {city_name}"]

            if params.get('min_price') or params.get('max_price'):
                price_range = []
                if params.get('min_price'):
                    price_range.append(f"₪{params['min_price']:,}")
                if params.get('max_price'):
                    price_range.append(f"₪{params['max_price']:,}")
                parts.append(" - ".join(price_range))

            return " | ".join(parts)

        return f"Dataset ({self.metadata.property_count} properties)"

    def get_age_display(self) -> str:
        """Get human-readable age of dataset."""
        if not self.metadata.created_at:
            return "Unknown"

        now = datetime.now()
        diff = now - self.metadata.created_at

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

    def get_size_display(self) -> str:
        """Get human-readable size display."""
        size = self.metadata.size_bytes

        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
