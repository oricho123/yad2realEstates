"""Table and summary components for property data visualization."""

import pandas as pd
from dash import html
from typing import Dict, Any

from src.config.constants import ValueAnalysisConstants
from src.analysis.value_analysis import ValueAnalyzer


class PropertyTableComponents:
    """Components for creating property data tables and summaries."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property data."""
        self.data = data

    def create_best_deals_table(self, max_deals: int = 10) -> html.Div:
        """
        Create a table showing the best deals based on value analysis.

        Args:
            max_deals: Maximum number of deals to show

        Returns:
            html.Div: Dash HTML component with best deals table
        """
        if len(self.data) == 0:
            return html.Div("No data available for best deals analysis")

        # Use ValueAnalyzer to get best deals
        value_analyzer = ValueAnalyzer(self.data)
        best_deals = value_analyzer.get_best_deals(max_deals)

        if len(best_deals) == 0:
            return html.Div([
                html.P("No properties found significantly below market value.",
                       style={'textAlign': 'center', 'color': '#6c757d', 'fontStyle': 'italic'})
            ])

        # Create table rows
        table_rows = []
        for _, prop in best_deals.iterrows():
            savings = abs(prop.get('value_score', 0))
            row_style = {
                'background': 'linear-gradient(90deg, rgba(40,167,69,0.1) 0%, rgba(255,255,255,0.1) 100%)' if savings > 15 else
                'rgba(40,167,69,0.05)',
                'borderRadius': '8px',
                'marginBottom': '10px',
                'padding': '15px',
                'borderLeft': f'4px solid {"#28a745" if savings > 15 else "#20c997"}',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
            }

            # Create property details
            neighborhood = prop.get('neighborhood', 'Unknown')
            street = prop.get('street', '')
            location = f"{street}, {neighborhood}" if street and street.strip(
            ) else neighborhood
            full_url = prop.get('full_url', '')

            price_display = f"₪{prop.get('price', 0):,.0f}"
            savings_display = f"{savings:.1f}%"

            room_info = f"{prop.get('rooms', 0)} rooms, {prop.get('square_meters', 0)} sqm"
            condition = prop.get('condition_text', 'Not specified')

            # Create clickable title if URL is available
            if full_url and full_url.strip():
                title_element = html.A(
                    f"Property in {neighborhood}",
                    href=full_url,
                    target="_blank",
                    style={'color': '#2c3e50', 'textDecoration': 'none', 'fontWeight': '600',
                           'cursor': 'pointer', 'borderBottom': '1px dashed #667eea'}
                )
            else:
                title_element = html.H6(f"Property in {neighborhood}",
                                        style={'margin': '0 0 5px 0', 'color': '#2c3e50', 'fontWeight': '600'})

            row = html.Div([
                html.Div([
                    html.Div([
                        title_element,
                        html.P(f"Location: {location}",
                               style={'margin': '5px 0 10px 0', 'color': '#6c757d', 'fontSize': '14px'})
                    ], style={'flex': '1'}),

                    html.Div([
                        html.Span(f"{savings_display} below market",
                                  style={'background': '#28a745', 'color': 'white',
                                         'padding': '4px 8px', 'borderRadius': '12px',
                                         'fontSize': '12px', 'fontWeight': '600'})
                    ], style={'textAlign': 'right'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}),

                html.Div([
                    html.Span(f"Price: {price_display}",
                              style={'marginRight': '15px', 'fontWeight': '600', 'color': '#2c3e50'}),
                    html.Span(f"{room_info}",
                              style={'marginRight': '15px', 'color': '#495057'}),
                    html.Span(f"Condition: {condition}",
                              style={'color': '#6c757d'})
                ], style={'marginTop': '10px'}),

                # Add view listing button if URL is available
                html.Div([
                    html.A(
                        [html.I(className="fas fa-external-link-alt",
                                style={'marginRight': '5px'}), "View Listing"],
                        href=full_url,
                        target="_blank",
                        style={
                            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            'color': 'white',
                            'padding': '6px 12px',
                            'borderRadius': '15px',
                            'textDecoration': 'none',
                            'fontSize': '12px',
                            'fontWeight': '500',
                            'display': 'inline-flex',
                            'alignItems': 'center',
                            'transition': 'all 0.3s ease',
                            'boxShadow': '0 2px 8px rgba(102, 126, 234, 0.3)'
                        }
                    ) if full_url and full_url.strip() else html.Span(
                        "No listing URL available",
                        style={'color': '#6c757d', 'fontSize': '12px',
                               'fontStyle': 'italic'}
                    )
                ], style={'marginTop': '10px', 'textAlign': 'right'})
            ], style=row_style)

            table_rows.append(row)

        return html.Div([
            html.H6(f"Top {len(best_deals)} Best Deals",
                    style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
            html.Div(table_rows)
        ])

    def create_market_insights_summary(self) -> html.Div:
        """
        Create market insights and recommendations summary.

        Returns:
            html.Div: Dash HTML component with market insights
        """
        if len(self.data) == 0:
            return html.Div("No data available for market insights")

        # Calculate market statistics
        avg_price = self.data['price'].mean()
        avg_price_per_sqm = self.data['price_per_sqm'].mean()
        total_properties = len(self.data)

        # Find price ranges
        price_quartiles = self.data['price'].quantile([0.25, 0.5, 0.75])

        # Neighborhood analysis
        affordability_analysis = self._analyze_neighborhood_affordability()

        # Value opportunities analysis
        value_analysis = self._analyze_value_opportunities()

        # Create insights cards
        insights_style = self._get_insights_styling()

        return html.Div([
            html.H4("Market Insights & Recommendations",
                    style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': '600'}),

            html.Div([
                # Market Overview
                html.Div([
                    html.H6("Market Overview", style={
                            'color': '#495057', 'marginBottom': '10px'}),
                    html.P(f"Analyzing {total_properties} properties with an average price of ₪{avg_price:,.0f}",
                           style={'margin': '0', 'fontSize': '14px'})
                ], style=insights_style['insight_card']),

                # Price Analysis
                html.Div([
                    html.H6("Price Distribution", style={
                            'color': '#495057', 'marginBottom': '10px'}),
                    html.P([
                        f"Budget Range: ₪{price_quartiles[0.25]:,.0f} - ₪{price_quartiles[0.75]:,.0f} ",
                        html.Span("(middle 50%)", style={
                                  'color': '#6c757d', 'fontStyle': 'italic'})
                    ], style={'margin': '0', 'fontSize': '14px'})
                ], style=insights_style['insight_card']),

                # Affordability Analysis
                html.Div([
                    html.H6("Affordability Analysis", style={
                            'color': '#495057', 'marginBottom': '10px'}),
                    html.P([
                        "Most Affordable: ",
                        html.Strong(f"{affordability_analysis['most_affordable']}", style={
                                    'color': '#28a745'}),
                        f" (Avg: ₪{affordability_analysis['most_affordable_price']:,.0f})"
                    ], style={'margin': '0 0 5px 0', 'fontSize': '14px'}),
                    html.P([
                        "Most Expensive: ",
                        html.Strong(f"{affordability_analysis['most_expensive']}", style={
                                    'color': '#dc3545'}),
                        f" (Avg: ₪{affordability_analysis['most_expensive_price']:,.0f})"
                    ], style={'margin': '0 0 5px 0', 'fontSize': '14px'}),
                    html.P([
                        "Best Value: ",
                        html.Strong(f"{affordability_analysis['best_value']}", style={
                                    'color': '#667eea'}),
                        " (size-adjusted efficiency)"
                    ], style={'margin': '0', 'fontSize': '14px'})
                ], style=insights_style['insight_card']),

                # Value Opportunities
                html.Div([
                    html.H6("Investment Opportunities", style={
                            'color': '#495057', 'marginBottom': '10px'}),
                    html.P(f"{value_analysis['undervalued_count']} properties below market value",
                           style={'margin': '0 0 5px 0', 'fontSize': '14px', 'color': '#28a745'}),
                    html.P(f"{value_analysis['overvalued_count']} properties above market value",
                           style={'margin': '0', 'fontSize': '14px', 'color': '#dc3545'})
                ], style=insights_style['insight_card']),

            ], style=insights_style['container'])
        ])

    def _analyze_neighborhood_affordability(self) -> Dict[str, Any]:
        """Analyze neighborhood affordability."""
        if 'neighborhood' not in self.data.columns or len(self.data) <= 5:
            return {
                'most_affordable': 'N/A',
                'most_expensive': 'N/A',
                'best_value': 'N/A',
                'most_affordable_price': 0,
                'most_expensive_price': 0
            }

        neighborhood_analysis = self.data.groupby('neighborhood').agg({
            'price': 'mean',
            'price_per_sqm': 'mean',
            'square_meters': 'mean'
        }).reset_index()

        # Find most and least affordable by total price
        most_affordable_area = neighborhood_analysis.loc[neighborhood_analysis['price'].idxmin(
        ), 'neighborhood']
        most_expensive_area = neighborhood_analysis.loc[neighborhood_analysis['price'].idxmax(
        ), 'neighborhood']

        most_affordable_price = neighborhood_analysis['price'].min()
        most_expensive_price = neighborhood_analysis['price'].max()

        # Find best value (size-adjusted price per sqm)
        overall_avg_size = self.data['square_meters'].mean()
        neighborhood_analysis['size_adjusted_price_per_sqm'] = (
            neighborhood_analysis['price_per_sqm'] *
            (neighborhood_analysis['square_meters'] / overall_avg_size)
        )
        best_value_area = neighborhood_analysis.loc[neighborhood_analysis['size_adjusted_price_per_sqm'].idxmin(
        ), 'neighborhood']

        return {
            'most_affordable': most_affordable_area,
            'most_expensive': most_expensive_area,
            'best_value': best_value_area,
            'most_affordable_price': most_affordable_price,
            'most_expensive_price': most_expensive_price
        }

    def _analyze_value_opportunities(self) -> Dict[str, int]:
        """Analyze value opportunities in the market."""
        # Use ValueAnalyzer for consistent calculations
        value_analyzer = ValueAnalyzer(self.data)

        try:
            df_with_scores = value_analyzer.calculate_value_scores()
            undervalued_count = len(
                df_with_scores[df_with_scores['value_score'] < ValueAnalysisConstants.GOOD_DEAL_THRESHOLD])
            overvalued_count = len(
                df_with_scores[df_with_scores['value_score'] > ValueAnalysisConstants.FAIR_PRICE_THRESHOLD])
        except Exception:
            undervalued_count = 0
            overvalued_count = 0

        return {
            'undervalued_count': undervalued_count,
            'overvalued_count': overvalued_count
        }

    def _get_insights_styling(self) -> Dict[str, Dict[str, Any]]:
        """Get styling for insights components."""
        return {
            'container': {
                'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                'borderRadius': '15px',
                'padding': '25px',
                'margin': '20px 0'
            },
            'insight_card': {
                'background': 'white',
                'borderRadius': '10px',
                'padding': '15px',
                'margin': '10px 0',
                'borderLeft': '4px solid #667eea',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.05)'
            }
        }

    def create_summary_statistics_cards(self) -> html.Div:
        """Create summary statistics cards."""
        if len(self.data) == 0:
            return html.Div("No data available for summary statistics")

        # Calculate key statistics
        stats = {
            'total_properties': len(self.data),
            'avg_price': self.data['price'].mean(),
            'avg_price_per_sqm': self.data['price_per_sqm'].mean(),
            'avg_size': self.data['square_meters'].mean(),
            'avg_rooms': self.data['rooms'].mean()
        }

        # Create statistics cards
        cards = []

        card_configs = [
            {'value': f"{stats['total_properties']}",
                'label': 'Total Properties'},
            {'value': f"₪{stats['avg_price']:,.0f}", 'label': 'Avg Price'},
            {'value': f"₪{stats['avg_price_per_sqm']:,.0f}",
                'label': 'Avg Price/SQM'},
            {'value': f"{stats['avg_size']:.0f} sqm", 'label': 'Avg Size'},
            {'value': f"{stats['avg_rooms']:.1f}", 'label': 'Avg Rooms'}
        ]

        for config in card_configs:
            card = html.Div([
                html.P(config['label'], style={
                    'fontSize': '14px',
                    'color': '#495057',
                    'margin': '0',
                    'fontWeight': '500',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'gap': '6px'
                }),
                html.P(config['value'], style={
                    'fontSize': '24px',
                    'fontWeight': '700',
                    'color': '#667eea',
                    'margin': '10px 0',
                    'textShadow': '0 1px 3px rgba(0,0,0,0.1)'
                })
            ], style={
                'padding': '20px',
                'borderRadius': '12px',
                'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.08)',
                'textAlign': 'center',
                'border': '1px solid rgba(255,255,255,0.3)',
                'transition': 'all 0.3s ease'
            })

            cards.append(card)

        return html.Div([
            html.H6("Summary Statistics",
                    style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
            html.Div(cards, style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))',
                'gap': '20px'
            })
        ])
