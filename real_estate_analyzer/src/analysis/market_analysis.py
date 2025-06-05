"""Market analysis utilities for real estate data."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import logging

from src.config.constants import ValueAnalysisConstants

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Handles market analysis and insights generation."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize with property DataFrame."""
        self.data = data.copy()
        
    def generate_market_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive market insights and recommendations.
        
        Returns:
            Dictionary containing market insights data
        """
        if len(self.data) == 0:
            return self._get_empty_insights()
        
        # Calculate basic market statistics
        basic_stats = self._calculate_basic_statistics()
        
        # Analyze neighborhoods
        neighborhood_analysis = self._analyze_neighborhoods()
        
        # Value opportunity analysis
        value_analysis = self._analyze_value_opportunities()
        
        # Price distribution analysis
        price_analysis = self._analyze_price_distribution()
        
        return {
            'basic_stats': basic_stats,
            'neighborhood_analysis': neighborhood_analysis,
            'value_analysis': value_analysis,
            'price_analysis': price_analysis,
            'recommendations': self._generate_recommendations(
                basic_stats, neighborhood_analysis, value_analysis
            )
        }
    
    def _calculate_basic_statistics(self) -> Dict[str, Any]:
        """Calculate basic market statistics."""
        return {
            'total_properties': len(self.data),
            'avg_price': self.data['price'].mean(),
            'median_price': self.data['price'].median(),
            'avg_price_per_sqm': self.data['price_per_sqm'].mean(),
            'median_price_per_sqm': self.data['price_per_sqm'].median(),
            'avg_size': self.data['square_meters'].mean(),
            'avg_rooms': self.data['rooms'].mean() if 'rooms' in self.data.columns else None
        }
    
    def _analyze_neighborhoods(self) -> Dict[str, Any]:
        """Analyze neighborhood affordability and value."""
        if 'neighborhood' not in self.data.columns or len(self.data) <= 5:
            return {
                'has_data': False,
                'most_affordable': 'N/A',
                'most_expensive': 'N/A',
                'best_value': 'N/A',
                'most_affordable_price': 0,
                'most_expensive_price': 0
            }
        
        # Group by neighborhood
        neighborhood_stats = self.data.groupby('neighborhood').agg({
            'price': 'mean',
            'price_per_sqm': 'mean',
            'square_meters': 'mean'
        }).reset_index()
        
        # Find most and least affordable by total price
        most_affordable_idx = neighborhood_stats['price'].idxmin()
        most_expensive_idx = neighborhood_stats['price'].idxmax()
        
        most_affordable_area = neighborhood_stats.loc[most_affordable_idx, 'neighborhood']
        most_expensive_area = neighborhood_stats.loc[most_expensive_idx, 'neighborhood']
        most_affordable_price = neighborhood_stats.loc[most_affordable_idx, 'price']
        most_expensive_price = neighborhood_stats.loc[most_expensive_idx, 'price']
        
        # Calculate size-adjusted value
        overall_avg_size = self.data['square_meters'].mean()
        neighborhood_stats['size_adjusted_price_per_sqm'] = (
            neighborhood_stats['price_per_sqm'] * 
            (neighborhood_stats['square_meters'] / overall_avg_size)
        )
        
        best_value_idx = neighborhood_stats['size_adjusted_price_per_sqm'].idxmin()
        best_value_area = neighborhood_stats.loc[best_value_idx, 'neighborhood']
        
        return {
            'has_data': True,
            'most_affordable': most_affordable_area,
            'most_expensive': most_expensive_area,
            'best_value': best_value_area,
            'most_affordable_price': most_affordable_price,
            'most_expensive_price': most_expensive_price,
            'neighborhood_count': len(neighborhood_stats)
        }
    
    def _analyze_value_opportunities(self) -> Dict[str, Any]:
        """Analyze value opportunities in the market."""
        try:
            x = self.data['square_meters'].values
            y = self.data['price'].values
            
            # Calculate trend line
            z = np.polyfit(x, y, ValueAnalysisConstants.POLYNOMIAL_DEGREE)
            trend_line_y = np.poly1d(z)(x)
            value_scores = ((y - trend_line_y) / trend_line_y * 100)
            
            # Count properties by value category
            excellent_deals = len([s for s in value_scores if s <= ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD])
            good_deals = len([s for s in value_scores if ValueAnalysisConstants.EXCELLENT_DEAL_THRESHOLD < s <= ValueAnalysisConstants.GOOD_DEAL_THRESHOLD])
            undervalued = excellent_deals + good_deals
            overvalued = len([s for s in value_scores if s > ValueAnalysisConstants.ABOVE_MARKET_THRESHOLD])
            
            return {
                'has_trend_data': True,
                'excellent_deals': excellent_deals,
                'good_deals': good_deals,
                'undervalued_total': undervalued,
                'overvalued_total': overvalued,
                'trend_slope': z[0] if len(z) > 0 else 0,
                'trend_intercept': z[1] if len(z) > 1 else 0
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate value opportunities: {e}")
            return {
                'has_trend_data': False,
                'excellent_deals': 0,
                'good_deals': 0,
                'undervalued_total': 0,
                'overvalued_total': 0,
                'trend_slope': 0,
                'trend_intercept': 0
            }
    
    def _analyze_price_distribution(self) -> Dict[str, Any]:
        """Analyze price distribution and quartiles."""
        price_quartiles = self.data['price'].quantile([0.25, 0.5, 0.75])
        
        return {
            'q1': price_quartiles[0.25],
            'median': price_quartiles[0.5],
            'q3': price_quartiles[0.75],
            'iqr': price_quartiles[0.75] - price_quartiles[0.25],
            'budget_range_lower': price_quartiles[0.25],
            'budget_range_upper': price_quartiles[0.75]
        }
    
    def _generate_recommendations(self, basic_stats: Dict, neighborhood_analysis: Dict, value_analysis: Dict) -> List[str]:
        """Generate market recommendations based on analysis."""
        recommendations = []
        
        # Budget recommendations
        if basic_stats['total_properties'] >= 10:
            recommendations.append(
                f"Based on {basic_stats['total_properties']} properties, "
                f"consider a budget range of ₪{basic_stats.get('price_analysis', {}).get('budget_range_lower', 0):,.0f} - "
                f"₪{basic_stats.get('price_analysis', {}).get('budget_range_upper', 0):,.0f} for the middle 50% of the market."
            )
        
        # Value opportunity recommendations
        if value_analysis.get('has_trend_data') and value_analysis['undervalued_total'] > 0:
            recommendations.append(
                f"Found {value_analysis['undervalued_total']} undervalued properties "
                f"({value_analysis['excellent_deals']} excellent deals, {value_analysis['good_deals']} good deals)."
            )
        
        # Neighborhood recommendations
        if neighborhood_analysis.get('has_data'):
            recommendations.append(
                f"Most affordable area: {neighborhood_analysis['most_affordable']} "
                f"(avg ₪{neighborhood_analysis['most_affordable_price']:,.0f})"
            )
            
            if neighborhood_analysis['best_value'] != neighborhood_analysis['most_affordable']:
                recommendations.append(
                    f"Best value considering size efficiency: {neighborhood_analysis['best_value']}"
                )
        
        return recommendations
    
    def _get_empty_insights(self) -> Dict[str, Any]:
        """Return empty insights when no data is available."""
        return {
            'basic_stats': {
                'total_properties': 0,
                'avg_price': 0,
                'median_price': 0,
                'avg_price_per_sqm': 0,
                'median_price_per_sqm': 0,
                'avg_size': 0,
                'avg_rooms': 0
            },
            'neighborhood_analysis': {
                'has_data': False,
                'most_affordable': 'N/A',
                'most_expensive': 'N/A',
                'best_value': 'N/A',
                'most_affordable_price': 0,
                'most_expensive_price': 0
            },
            'value_analysis': {
                'has_trend_data': False,
                'excellent_deals': 0,
                'good_deals': 0,
                'undervalued_total': 0,
                'overvalued_total': 0,
                'trend_slope': 0,
                'trend_intercept': 0
            },
            'price_analysis': {
                'q1': 0,
                'median': 0,
                'q3': 0,
                'iqr': 0,
                'budget_range_lower': 0,
                'budget_range_upper': 0
            },
            'recommendations': []
        }
    
    def get_neighborhood_ranking(self) -> pd.DataFrame:
        """
        Generate neighborhood ranking based on affordability and value.
        
        Returns:
            DataFrame with neighborhood rankings
        """
        if len(self.data) == 0 or 'neighborhood' not in self.data.columns:
            return pd.DataFrame()
        
        # Calculate neighborhood statistics
        neighborhood_stats = self.data.groupby('neighborhood').agg({
            'price': ['mean', 'median', 'count'],
            'price_per_sqm': ['mean', 'median'],
            'square_meters': 'mean',
            'rooms': 'mean'
        }).round(0)
        
        # Flatten column names
        neighborhood_stats.columns = [
            'avg_price', 'median_price', 'count', 
            'avg_price_per_sqm', 'median_price_per_sqm', 
            'avg_size', 'avg_rooms'
        ]
        neighborhood_stats = neighborhood_stats.reset_index()
        
        # Filter neighborhoods with sufficient data
        min_properties = ValueAnalysisConstants.MIN_PROPERTIES_FOR_RANKING
        neighborhood_stats = neighborhood_stats[neighborhood_stats['count'] >= min_properties]
        
        if len(neighborhood_stats) == 0:
            return pd.DataFrame()
        
        # Calculate affordability scores
        max_avg_price = neighborhood_stats['avg_price'].max()
        min_avg_price = neighborhood_stats['avg_price'].min()
        
        if max_avg_price > min_avg_price:
            neighborhood_stats['affordability_score'] = (
                (max_avg_price - neighborhood_stats['avg_price']) / 
                (max_avg_price - min_avg_price) * 100
            )
        else:
            neighborhood_stats['affordability_score'] = 50  # All equal
        
        # Calculate efficiency scores
        overall_avg_size = self.data['square_meters'].mean()
        neighborhood_stats['size_adjusted_price_per_sqm'] = (
            neighborhood_stats['avg_price_per_sqm'] * 
            (neighborhood_stats['avg_size'] / overall_avg_size)
        )
        
        max_adjusted_price = neighborhood_stats['size_adjusted_price_per_sqm'].max()
        min_adjusted_price = neighborhood_stats['size_adjusted_price_per_sqm'].min()
        
        if max_adjusted_price > min_adjusted_price:
            efficiency_score = (
                (max_adjusted_price - neighborhood_stats['size_adjusted_price_per_sqm']) / 
                (max_adjusted_price - min_adjusted_price) * 100
            )
        else:
            efficiency_score = 50  # All equal
        
        # Combined affordability score
        neighborhood_stats['real_affordability_score'] = (
            neighborhood_stats['affordability_score'] * ValueAnalysisConstants.AFFORDABILITY_WEIGHT + 
            efficiency_score * ValueAnalysisConstants.EFFICIENCY_WEIGHT
        )
        
        # Sort by real affordability score
        return neighborhood_stats.sort_values('real_affordability_score', ascending=False) 