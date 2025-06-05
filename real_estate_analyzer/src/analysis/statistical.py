"""Statistical analysis utilities for property data."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class StatisticalCalculator:
    """Handles statistical calculations and analysis for property data."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize with property DataFrame."""
        self.data = data.copy()
        
    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive summary statistics.
        
        Returns:
            Dictionary containing summary statistics
        """
        if len(self.data) == 0:
            return self._get_empty_summary()
        
        # Basic count and availability
        total_properties = len(self.data)
        
        # Price statistics
        price_stats = self._calculate_price_statistics()
        
        # Size statistics
        size_stats = self._calculate_size_statistics()
        
        # Efficiency statistics
        efficiency_stats = self._calculate_efficiency_statistics()
        
        # Location statistics
        location_stats = self._calculate_location_statistics()
        
        return {
            'total_properties': total_properties,
            'price_stats': price_stats,
            'size_stats': size_stats,
            'efficiency_stats': efficiency_stats,
            'location_stats': location_stats,
            'data_quality': self._calculate_data_quality()
        }
    
    def _calculate_price_statistics(self) -> Dict[str, Any]:
        """Calculate price-related statistics."""
        if 'price' not in self.data.columns or self.data['price'].isna().all():
            return {
                'avg_price': 0,
                'median_price': 0,
                'min_price': 0,
                'max_price': 0,
                'std_price': 0,
                'avg_price_per_sqm': 0,
                'median_price_per_sqm': 0,
                'price_range': 0
            }
        
        price_data = self.data['price'].dropna()
        price_per_sqm_data = self.data['price_per_sqm'].dropna() if 'price_per_sqm' in self.data.columns else pd.Series([])
        
        return {
            'avg_price': float(price_data.mean()),
            'median_price': float(price_data.median()),
            'min_price': float(price_data.min()),
            'max_price': float(price_data.max()),
            'std_price': float(price_data.std()),
            'avg_price_per_sqm': float(price_per_sqm_data.mean()) if len(price_per_sqm_data) > 0 else 0,
            'median_price_per_sqm': float(price_per_sqm_data.median()) if len(price_per_sqm_data) > 0 else 0,
            'price_range': float(price_data.max() - price_data.min())
        }
    
    def _calculate_size_statistics(self) -> Dict[str, Any]:
        """Calculate size-related statistics."""
        if 'square_meters' not in self.data.columns or self.data['square_meters'].isna().all():
            return {
                'avg_size': 0,
                'median_size': 0,
                'min_size': 0,
                'max_size': 0,
                'avg_rooms': 0,
                'median_rooms': 0
            }
        
        size_data = self.data['square_meters'].dropna()
        rooms_data = self.data['rooms'].dropna() if 'rooms' in self.data.columns else pd.Series([])
        
        return {
            'avg_size': float(size_data.mean()),
            'median_size': float(size_data.median()),
            'min_size': float(size_data.min()),
            'max_size': float(size_data.max()),
            'avg_rooms': float(rooms_data.mean()) if len(rooms_data) > 0 else 0,
            'median_rooms': float(rooms_data.median()) if len(rooms_data) > 0 else 0
        }
    
    def _calculate_efficiency_statistics(self) -> Dict[str, Any]:
        """Calculate efficiency-related statistics."""
        if 'rooms' not in self.data.columns or 'square_meters' not in self.data.columns:
            return {
                'avg_sqm_per_room': 0,
                'median_sqm_per_room': 0,
                'efficiency_distribution': {}
            }
        
        # Calculate sqm per room
        valid_data = self.data[(self.data['rooms'] > 0) & (self.data['square_meters'] > 0)].copy()
        
        if len(valid_data) == 0:
            return {
                'avg_sqm_per_room': 0,
                'median_sqm_per_room': 0,
                'efficiency_distribution': {}
            }
        
        valid_data['sqm_per_room'] = valid_data['square_meters'] / valid_data['rooms']
        
        # Calculate efficiency distribution
        efficiency_bins = [0, 15, 20, 25, 30, float('inf')]
        efficiency_labels = ['Very Compact', 'Compact', 'Standard', 'Spacious', 'Very Spacious']
        
        try:
            efficiency_categories = pd.cut(
                valid_data['sqm_per_room'], 
                bins=efficiency_bins, 
                labels=efficiency_labels, 
                include_lowest=True
            )
            efficiency_distribution = efficiency_categories.value_counts().to_dict()
            
            # Convert to string keys for JSON serialization
            efficiency_distribution = {str(k): int(v) for k, v in efficiency_distribution.items()}
            
        except Exception as e:
            logger.warning(f"Error calculating efficiency distribution: {e}")
            efficiency_distribution = {}
        
        return {
            'avg_sqm_per_room': float(valid_data['sqm_per_room'].mean()),
            'median_sqm_per_room': float(valid_data['sqm_per_room'].median()),
            'efficiency_distribution': efficiency_distribution
        }
    
    def _calculate_location_statistics(self) -> Dict[str, Any]:
        """Calculate location-related statistics."""
        location_stats = {
            'neighborhoods_count': 0,
            'properties_with_coordinates': 0,
            'coordinate_coverage': 0.0
        }
        
        # Neighborhood count
        if 'neighborhood' in self.data.columns:
            location_stats['neighborhoods_count'] = self.data['neighborhood'].nunique()
        
        # Coordinate coverage
        if 'lat' in self.data.columns and 'lng' in self.data.columns:
            has_coordinates = (
                self.data['lat'].notna() & 
                self.data['lng'].notna() & 
                (self.data['lat'] != 0) & 
                (self.data['lng'] != 0)
            )
            location_stats['properties_with_coordinates'] = int(has_coordinates.sum())
            location_stats['coordinate_coverage'] = float(has_coordinates.mean() * 100)
        
        return location_stats
    
    def _calculate_data_quality(self) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        if len(self.data) == 0:
            return {
                'completeness_score': 0,
                'missing_data_percentage': 100,
                'critical_fields_complete': 0
            }
        
        total_cells = len(self.data) * len(self.data.columns)
        missing_cells = self.data.isna().sum().sum()
        completeness_score = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
        
        # Critical fields
        critical_fields = ['price', 'square_meters', 'price_per_sqm']
        available_critical_fields = [field for field in critical_fields if field in self.data.columns]
        
        if available_critical_fields:
            critical_complete = self.data[available_critical_fields].notna().all(axis=1).sum()
            critical_percentage = (critical_complete / len(self.data) * 100)
        else:
            critical_percentage = 0
        
        return {
            'completeness_score': float(completeness_score),
            'missing_data_percentage': float(missing_cells / total_cells * 100) if total_cells > 0 else 100,
            'critical_fields_complete': float(critical_percentage)
        }
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix for numerical columns.
        
        Returns:
            Correlation matrix DataFrame
        """
        numerical_columns = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numerical_columns) < 2:
            return pd.DataFrame()
        
        try:
            correlation_matrix = self.data[numerical_columns].corr()
            return correlation_matrix.round(3)
        except Exception as e:
            logger.warning(f"Error calculating correlation matrix: {e}")
            return pd.DataFrame()
    
    def identify_statistical_outliers(self, column: str, method: str = 'iqr') -> pd.Series:
        """
        Identify outliers in a specific column using statistical methods.
        
        Args:
            column: Column name to analyze
            method: Method to use ('iqr', 'zscore', or 'modified_zscore')
            
        Returns:
            Boolean Series indicating outliers
        """
        if column not in self.data.columns or len(self.data) < 4:
            return pd.Series([False] * len(self.data), index=self.data.index)
        
        data = self.data[column].dropna()
        
        if len(data) < 4:
            return pd.Series([False] * len(self.data), index=self.data.index)
        
        outliers = pd.Series([False] * len(self.data), index=self.data.index)
        
        try:
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (self.data[column] < lower_bound) | (self.data[column] > upper_bound)
                outliers[outlier_mask] = True
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(data))
                outlier_indices = data.index[z_scores > 2]
                outliers[outlier_indices] = True
                
            elif method == 'modified_zscore':
                median = data.median()
                mad = np.median(np.abs(data - median))
                modified_z_scores = 0.6745 * (data - median) / mad
                outlier_indices = data.index[np.abs(modified_z_scores) > 3.5]
                outliers[outlier_indices] = True
                
        except Exception as e:
            logger.warning(f"Error identifying outliers in {column}: {e}")
        
        return outliers
    
    def calculate_price_distribution_stats(self) -> Dict[str, Any]:
        """
        Calculate detailed price distribution statistics.
        
        Returns:
            Dictionary with distribution statistics
        """
        if 'price' not in self.data.columns or len(self.data) == 0:
            return self._get_empty_distribution_stats()
        
        price_data = self.data['price'].dropna()
        
        if len(price_data) == 0:
            return self._get_empty_distribution_stats()
        
        try:
            # Calculate percentiles
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            percentile_values = {f'p{p}': float(price_data.quantile(p/100)) for p in percentiles}
            
            # Calculate distribution shape
            skewness = float(stats.skew(price_data))
            kurtosis = float(stats.kurtosis(price_data))
            
            # Calculate normality test
            try:
                shapiro_stat, shapiro_p = stats.shapiro(price_data[:5000])  # Limit to 5000 for performance
                is_normal = shapiro_p > 0.05
            except Exception:
                shapiro_stat, shapiro_p, is_normal = 0, 0, False
            
            return {
                'percentiles': percentile_values,
                'skewness': skewness,
                'kurtosis': kurtosis,
                'is_normal_distribution': is_normal,
                'shapiro_statistic': float(shapiro_stat),
                'shapiro_p_value': float(shapiro_p),
                'coefficient_of_variation': float(price_data.std() / price_data.mean()) if price_data.mean() != 0 else 0
            }
            
        except Exception as e:
            logger.warning(f"Error calculating price distribution stats: {e}")
            return self._get_empty_distribution_stats()
    
    def _get_empty_summary(self) -> Dict[str, Any]:
        """Return empty summary statistics."""
        return {
            'total_properties': 0,
            'price_stats': {
                'avg_price': 0,
                'median_price': 0,
                'min_price': 0,
                'max_price': 0,
                'std_price': 0,
                'avg_price_per_sqm': 0,
                'median_price_per_sqm': 0,
                'price_range': 0
            },
            'size_stats': {
                'avg_size': 0,
                'median_size': 0,
                'min_size': 0,
                'max_size': 0,
                'avg_rooms': 0,
                'median_rooms': 0
            },
            'efficiency_stats': {
                'avg_sqm_per_room': 0,
                'median_sqm_per_room': 0,
                'efficiency_distribution': {}
            },
            'location_stats': {
                'neighborhoods_count': 0,
                'properties_with_coordinates': 0,
                'coordinate_coverage': 0.0
            },
            'data_quality': {
                'completeness_score': 0,
                'missing_data_percentage': 100,
                'critical_fields_complete': 0
            }
        }
    
    def _get_empty_distribution_stats(self) -> Dict[str, Any]:
        """Return empty distribution statistics."""
        return {
            'percentiles': {f'p{p}': 0 for p in [10, 25, 50, 75, 90, 95, 99]},
            'skewness': 0,
            'kurtosis': 0,
            'is_normal_distribution': False,
            'shapiro_statistic': 0,
            'shapiro_p_value': 0,
            'coefficient_of_variation': 0
        } 