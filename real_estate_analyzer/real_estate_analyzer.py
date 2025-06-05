import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime

# Import the scraper module
from real_estate_scraper import RealEstateScraper

# For web visualization
import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dash.exceptions import PreventUpdate
import time

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Real Estate Price Analyzer')
    parser.add_argument('--output-dir', type=str, default='scraped_real_estate',
                        help='Directory to save scraped data')
    parser.add_argument('--port', type=int, default=8051,
                        help='Port to run the web server on')
    return parser.parse_args()

def load_data(csv_path):
    """Load and prepare the CSV data for visualization with strict data quality checks"""
    try:
        df = pd.read_csv(csv_path)
        initial_count = len(df)
        print(f"📁 Loaded {initial_count} raw records from CSV")
        
        # Data quality checks with detailed reporting
        original_df = df.copy()
        
        # Filter out properties with no price or invalid price
        before_price = len(df)
        df = df[df['price'].notna() & (df['price'] > 0)]
        removed_price = before_price - len(df)
        if removed_price > 0:
            print(f"🗑️  Removed {removed_price} properties with missing/invalid price")
        
        # Filter out properties with missing/invalid square meters data
        before_sqm = len(df)
        df = df[df['square_meters'].notna() & (df['square_meters'] > 0)]
        removed_sqm = before_sqm - len(df)
        if removed_sqm > 0:
            print(f"🗑️  Removed {removed_sqm} properties with missing/invalid square meters")
        
        # Ensure price_per_sqm is calculated correctly
        df['price_per_sqm'] = df['price'] / df['square_meters']
        
        # Remove any properties with unrealistic price per sqm (data quality check)
        before_realistic = len(df)
        df = df[(df['price_per_sqm'] >= 1000) & (df['price_per_sqm'] <= 100000)]  # Reasonable range for Israel
        removed_unrealistic = before_realistic - len(df)
        if removed_unrealistic > 0:
            print(f"🗑️  Removed {removed_unrealistic} properties with unrealistic price/sqm values")
        
        # Convert coordinates to numeric (but don't remove - some properties might not have coordinates)
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
        
        # Final data quality summary
        final_count = len(df)
        total_removed = initial_count - final_count
        quality_percentage = (final_count / initial_count) * 100
        
        print(f"✅ Data Quality Summary:")
        print(f"   • Started with: {initial_count} properties")
        print(f"   • Removed: {total_removed} incomplete/invalid properties")
        print(f"   • Final dataset: {final_count} high-quality properties ({quality_percentage:.1f}%)")
        
        return df
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame instead of exiting

def create_empty_dataframe():
    """Create an empty DataFrame with the expected structure"""
    return pd.DataFrame(columns=[
        'price', 'square_meters', 'price_per_sqm', 'lat', 'lng',
        'neighborhood', 'rooms', 'condition_text', 'ad_type', 
        'property_type', 'street', 'floor', 'full_url'
    ])

def create_map_figure(df):
    """Create an interactive map visualization of properties"""
    if len(df) == 0:
        # Return empty map
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No data available for map",
            geo=dict(projection_type='natural earth'),
            height=600
        )
        return empty_fig
    
    # Filter out properties without coordinates
    map_df = df.dropna(subset=['lat', 'lng'])
    
    if len(map_df) == 0:
        # Return empty map with message
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No properties with location data",
            geo=dict(projection_type='natural earth'),
            height=600
        )
        return empty_fig
    
    # Create the map using Plotly's scatter_mapbox
    fig = px.scatter_mapbox(
        map_df,
        lat='lat',
        lon='lng',
        color='price_per_sqm',
        size='rooms',
        size_max=20,
        hover_data=['neighborhood', 'price', 'square_meters', 'rooms', 'condition_text'],
        color_continuous_scale='viridis',
        zoom=11,
        height=600,
        labels={'price_per_sqm': 'Price/sqm (₪)', 'lat': 'Latitude', 'lng': 'Longitude'}
    )
    
    # Calculate center point for map
    center_lat = map_df['lat'].mean()
    center_lon = map_df['lng'].mean()
    
    # Update layout for better appearance
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=11
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        coloraxis_colorbar=dict(
            title="₪/sqm",
            title_font=dict(size=13),
            tickfont=dict(size=11)
        )
    )
    
    # Prepare custom data for click functionality
    street_display = map_df.apply(lambda row: 
        f"{row['street']}" if pd.notna(row['street']) and row['street'].strip() != '' 
        else f"{row['neighborhood']}", axis=1)
    
    custom_data = np.column_stack((
        map_df['neighborhood'].fillna('Unknown'),           # 0
        map_df['price'].round(0),                           # 1 - Fixed: Add price
        map_df['rooms'],                                    # 2 - Fixed: Moved rooms to index 2
        map_df['condition_text'].fillna('Not specified'),  # 3
        map_df['ad_type'],                                  # 4
        street_display,                                     # 5
        map_df['floor'].fillna('Not specified'),           # 6
        map_df['full_url'].fillna('')                      # 7
    ))
    
    # Update traces with custom hover template
    fig.update_traces(
        customdata=custom_data,
        hovertemplate='<b>🏡 %{customdata[0]}</b><br>' +
                      '<i>📍 %{customdata[5]}</i><br>' +
                      '<br>' +
                      '<b>Price:</b> ₪%{customdata[1]:,.0f}<br>' +
                      '<b>Size:</b> %{text} sqm<br>' +
                      '<b>Price/sqm:</b> ₪%{marker.color:,.0f}<br>' +
                      '<b>Rooms:</b> %{customdata[2]}<br>' +
                      '<b>Condition:</b> %{customdata[3]}<br>' +
                      '<br>' +
                      '<b>👆 Click to view listing</b>' +
                      '<extra></extra>',
        text=map_df['square_meters']
    )
    
    return fig

def create_enhanced_scatter_plot(df):
    """Create an enhanced scatter plot with trend lines, median lines, and value analysis"""
    if len(df) == 0:
        return px.scatter(title="No data available")
    
    plot_df = df.copy()
    
    # Calculate trend line using numpy polyfit
    x = plot_df['square_meters'].values
    y = plot_df['price'].values
    
    # Fit polynomial trend line (degree 1 for linear)
    try:
        z = np.polyfit(x, y, 1)
        trend_line_y = np.poly1d(z)(x)
        
        # Calculate value score: how far above/below trend line each property is
        plot_df['value_score'] = ((y - trend_line_y) / trend_line_y * 100)  # Percentage above/below trend
        plot_df['value_category'] = plot_df['value_score'].apply(lambda x: 
            'Excellent Deal' if x < -15 else
            'Good Deal' if x < -5 else
            'Fair Price' if x < 5 else
            'Above Market' if x < 15 else
            'Overpriced'
        )
    except:
        plot_df['value_score'] = 0
        plot_df['value_category'] = 'Unknown'
        trend_line_y = y.copy()
    
    # Create the enhanced scatter plot
    fig = px.scatter(
        plot_df, 
        x='square_meters', 
        y='price',
        color='value_category',
        size='rooms',
        size_max=15,
        color_discrete_map={
            'Excellent Deal': '#28a745',  # Green
            'Good Deal': '#20c997',       # Teal
            'Fair Price': '#6c757d',      # Gray
            'Above Market': '#fd7e14',    # Orange
            'Overpriced': '#dc3545'       # Red
        },
        hover_data=['neighborhood', 'rooms', 'condition_text', 'price_per_sqm', 'value_score'],
        labels={'square_meters': 'Square Meters', 
               'price': 'Price (₪)', 
               'value_category': 'Market Value'},
    )
    
    # Add trend line
    fig.add_scatter(
        x=x, 
        y=trend_line_y,
        mode='lines',
        name='Market Trend',
        line=dict(color='rgba(102, 126, 234, 0.8)', width=3, dash='dash'),
        hoverinfo='skip'
    )
    
    # Add median lines
    median_price = plot_df['price'].median()
    median_sqm = plot_df['square_meters'].median()
    
    # Vertical line for median square meters
    fig.add_vline(
        x=median_sqm, 
        line_dash="dot", 
        line_color="rgba(102, 126, 234, 0.6)",
        annotation_text=f"Median Size: {median_sqm:.0f}sqm",
        annotation_position="top"
    )
    
    # Horizontal line for median price
    fig.add_hline(
        y=median_price, 
        line_dash="dot", 
        line_color="rgba(102, 126, 234, 0.6)",
        annotation_text=f"Median Price: ₪{median_price:,.0f}",
        annotation_position="right"
    )
    
    # Prepare custom data for hover and click functionality
    street_display = plot_df.apply(lambda row: 
        f"{row['street']}" if pd.notna(row['street']) and row['street'].strip() != '' 
        else f"{row['neighborhood']}", axis=1)
    
    custom_data = np.column_stack((
        plot_df['neighborhood'].fillna('Unknown'),           # 0
        plot_df['rooms'],                                     # 1
        plot_df['price_per_sqm'].round(0),                   # 2 - Fixed: Price per sqm
        plot_df['condition_text'].fillna('Not specified'),   # 3 - Fixed: Moved condition to index 3
        plot_df['ad_type'],                                   # 4
        street_display,                                       # 5
        plot_df['floor'].fillna('Not specified'),            # 6
        plot_df['full_url'].fillna(''),                      # 7
        plot_df['value_score'].round(1),                     # 8
        plot_df['value_category']                            # 9
    ))
    
    # Update traces with enhanced hover template
    fig.update_traces(
        marker=dict(
            opacity=0.8,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        customdata=custom_data,
        hovertemplate='<b>🏡 %{customdata[0]}</b><br>' +
                      '<i>📍 %{customdata[5]}</i><br>' +
                      '<br>' +
                      '<b>Price:</b> ₪%{y:,.0f}<br>' +
                      '<b>Size:</b> %{x} sqm<br>' +
                      '<b>Price/sqm:</b> ₪%{customdata[2]:,.0f}<br>' +
                      '<b>Rooms:</b> %{customdata[1]}<br>' +
                      '<b>Condition:</b> %{customdata[3]}<br>' +
                      '<br>' +
                      '<b>💡 Value Analysis:</b><br>' +
                      '<b>Market Position:</b> %{customdata[9]}<br>' +
                      '<b>Value Score:</b> %{customdata[8]}%<br>' +
                      '<br>' +
                      '<b>👆 Click to view listing</b>' +
                      '<extra></extra>',
        selector=dict(mode='markers')
    )
    
    # Update layout
    fig.update_layout(
        clickmode='event+select',
        hoverdistance=100,
        hovermode='closest',
        dragmode='zoom',
        plot_bgcolor='rgba(240,240,240,0.2)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif"),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#eee'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#eee'
        ),
        title=dict(font=dict(size=16)),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_neighborhood_ranking(df):
    """Create neighborhood ranking analysis with proper affordability calculation"""
    if len(df) == 0 or 'neighborhood' not in df.columns:
        return px.bar(title="No neighborhood data available")
    
    # Calculate neighborhood statistics
    neighborhood_stats = df.groupby('neighborhood').agg({
        'price': ['mean', 'median', 'count'],
        'price_per_sqm': ['mean', 'median'],
        'square_meters': 'mean',
        'rooms': 'mean'
    }).round(0)
    
    # Flatten column names
    neighborhood_stats.columns = ['avg_price', 'median_price', 'count', 'avg_price_per_sqm', 'median_price_per_sqm', 'avg_size', 'avg_rooms']
    neighborhood_stats = neighborhood_stats.reset_index()
    
    # Filter neighborhoods with at least 3 properties
    neighborhood_stats = neighborhood_stats[neighborhood_stats['count'] >= 3]
    
    if len(neighborhood_stats) == 0:
        return px.bar(title="Not enough data for neighborhood comparison")
    
    # Calculate REAL affordability score based on total price and opportunity
    # Lower average total price = more affordable
    max_avg_price = neighborhood_stats['avg_price'].max()
    min_avg_price = neighborhood_stats['avg_price'].min()
    
    # Affordability score: higher score = more affordable (inverse of price)
    neighborhood_stats['affordability_score'] = ((max_avg_price - neighborhood_stats['avg_price']) / (max_avg_price - min_avg_price) * 100)
    
    # Add value efficiency: price per sqm adjusted for size
    # Smaller properties naturally have higher price/sqm, so we normalize by size
    overall_avg_size = df['square_meters'].mean()
    neighborhood_stats['size_adjusted_price_per_sqm'] = neighborhood_stats['avg_price_per_sqm'] * (neighborhood_stats['avg_size'] / overall_avg_size)
    
    # Calculate value score: combination of affordability and efficiency
    max_adjusted_price_per_sqm = neighborhood_stats['size_adjusted_price_per_sqm'].max()
    min_adjusted_price_per_sqm = neighborhood_stats['size_adjusted_price_per_sqm'].min()
    
    efficiency_score = ((max_adjusted_price_per_sqm - neighborhood_stats['size_adjusted_price_per_sqm']) / (max_adjusted_price_per_sqm - min_adjusted_price_per_sqm) * 100)
    
    # Combined affordability: 70% total price affordability + 30% size-adjusted efficiency
    neighborhood_stats['real_affordability_score'] = (neighborhood_stats['affordability_score'] * 0.7 + efficiency_score * 0.3)
    
    # Sort by real affordability score
    neighborhood_stats = neighborhood_stats.sort_values('real_affordability_score', ascending=False)
    
    # Create ranking chart showing real affordability
    fig = px.bar(
        neighborhood_stats.head(10),
        x='neighborhood', 
        y='avg_price',
        color='real_affordability_score',
        title='Real Neighborhood Affordability Ranking',
        labels={
            'avg_price': 'Average Total Price (₪)',
            'neighborhood': 'Neighborhood',
            'real_affordability_score': 'Real Affordability Score'
        },
        color_continuous_scale='RdYlGn',
        text='count'
    )
    
    # Add property count as text
    fig.update_traces(texttemplate='%{text} properties', textposition="outside")
    
    # Add comprehensive hover data
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' +
                      '<b>Avg Total Price:</b> ₪%{y:,.0f}<br>' +
                      '<b>Avg Size:</b> %{customdata[0]:.0f} sqm<br>' +
                      '<b>Avg Price/sqm:</b> ₪%{customdata[1]:,.0f}<br>' +
                      '<b>Properties:</b> %{text}<br>' +
                      '<b>Real Affordability:</b> %{marker.color:.0f}/100<br>' +
                      '<br><i>Higher score = more affordable</i>' +
                      '<extra></extra>',
        customdata=neighborhood_stats.head(10)[['avg_size', 'avg_price_per_sqm']].values
    )
    
    fig.update_layout(
        xaxis={'tickangle': 45},
        height=400,
        title_x=0.5,
        showlegend=False
    )
    
    return fig

def create_best_deals_table(df):
    """Create a table showing the best deals based on value analysis"""
    if len(df) == 0:
        return html.Div("No data available for best deals analysis")
    
    # Calculate value scores (same logic as in scatter plot)
    plot_df = df.copy()
    x = plot_df['square_meters'].values
    y = plot_df['price'].values
    
    try:
        z = np.polyfit(x, y, 1)
        trend_line_y = np.poly1d(z)(x)
        plot_df['value_score'] = ((y - trend_line_y) / trend_line_y * 100)
    except:
        plot_df['value_score'] = 0
    
    # Filter for best deals (below market value)
    best_deals = plot_df[plot_df['value_score'] < -5].copy()
    best_deals = best_deals.sort_values('value_score').head(10)
    
    if len(best_deals) == 0:
        return html.Div([
            html.P("No properties found significantly below market value.", 
                  style={'text-align': 'center', 'color': '#6c757d', 'font-style': 'italic'})
        ])
    
    # Create table rows
    table_rows = []
    for _, prop in best_deals.iterrows():
        savings = abs(prop['value_score'])
        row_style = {
            'background': 'linear-gradient(90deg, rgba(40,167,69,0.1) 0%, rgba(255,255,255,0.1) 100%)' if savings > 15 else
                         'rgba(40,167,69,0.05)',
            'border-radius': '8px',
            'margin-bottom': '10px',
            'padding': '15px',
            'border-left': f'4px solid {"#28a745" if savings > 15 else "#20c997"}',
            'box-shadow': '0 2px 8px rgba(0,0,0,0.1)'
        }
        
        table_rows.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.H5(f"{prop['neighborhood']}", 
                               style={'margin': '0 0 5px 0', 'color': '#2c3e50', 'font-weight': '600'}),
                        html.P(f"{prop.get('street', 'Address not available')}", 
                               style={'margin': '0 0 10px 0', 'color': '#6c757d', 'font-size': '14px'})
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{savings:.1f}% below market", 
                                style={'background': '#28a745', 'color': 'white', 'padding': '4px 8px', 
                                      'border-radius': '12px', 'font-size': '12px', 'font-weight': '600'})
                    ], style={'display': 'flex', 'align-items': 'flex-start'})
                ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'flex-start'}),
                
                html.Div([
                    html.Div([
                        html.Strong("₪{:,.0f}".format(prop['price'])),
                        html.Span(" | ", style={'color': '#dee2e6', 'margin': '0 8px'}),
                        html.Span(f"{prop['square_meters']:.0f} sqm"),
                        html.Span(" | ", style={'color': '#dee2e6', 'margin': '0 8px'}),
                        html.Span(f"{prop['rooms']:.1f} rooms"),
                        html.Span(" | ", style={'color': '#dee2e6', 'margin': '0 8px'}),
                        html.Span(f"₪{prop['price_per_sqm']:,.0f}/sqm")
                    ], style={'color': '#495057', 'font-size': '14px'}),
                ], style={'margin-top': '8px'}),
                
                html.Div([
                    html.A("View Listing", 
                          href=prop.get('full_url', '#'), 
                          target="_blank",
                          style={'color': '#667eea', 'text-decoration': 'none', 'font-weight': '500',
                                'font-size': '13px', 'display': 'flex', 'align-items': 'center', 'gap': '5px'}),
                ], style={'margin-top': '10px'})
            ], style=row_style)
        )
    
    return html.Div([
        html.H5("🎯 Best Property Deals", 
               style={'color': '#28a745', 'margin-bottom': '20px', 'font-weight': '600'}),
        html.Div(table_rows)
    ])

def create_market_insights_summary(df):
    """Create market insights and recommendations"""
    if len(df) == 0:
        return html.Div("No data available for market insights")
    
    # Calculate market statistics
    avg_price = df['price'].mean()
    avg_price_per_sqm = df['price_per_sqm'].mean()
    total_properties = len(df)
    
    # Find price ranges
    price_quartiles = df['price'].quantile([0.25, 0.5, 0.75])
    
    # Real affordability analysis - based on total price, not price per sqm
    if 'neighborhood' in df.columns and len(df) > 5:
        neighborhood_analysis = df.groupby('neighborhood').agg({
            'price': 'mean',
            'price_per_sqm': 'mean',
            'square_meters': 'mean'
        }).reset_index()
        
        # Find most and least affordable by total price
        most_affordable_area = neighborhood_analysis.loc[neighborhood_analysis['price'].idxmin(), 'neighborhood']
        most_expensive_area = neighborhood_analysis.loc[neighborhood_analysis['price'].idxmax(), 'neighborhood']
        
        most_affordable_total_price = neighborhood_analysis['price'].min()
        most_expensive_total_price = neighborhood_analysis['price'].max()
        
        # Find best value (lowest price per sqm adjusted for size)
        overall_avg_size = df['square_meters'].mean()
        neighborhood_analysis['size_adjusted_price_per_sqm'] = neighborhood_analysis['price_per_sqm'] * (neighborhood_analysis['square_meters'] / overall_avg_size)
        best_value_area = neighborhood_analysis.loc[neighborhood_analysis['size_adjusted_price_per_sqm'].idxmin(), 'neighborhood']
    else:
        most_expensive_area = "N/A"
        most_affordable_area = "N/A"
        best_value_area = "N/A"
        most_affordable_total_price = 0
        most_expensive_total_price = 0
    
    # Best value analysis
    x = df['square_meters'].values
    y = df['price'].values
    try:
        z = np.polyfit(x, y, 1)
        trend_line_y = np.poly1d(z)(x)
        value_scores = ((y - trend_line_y) / trend_line_y * 100)
        undervalued_count = len([score for score in value_scores if score < -5])
        overvalued_count = len([score for score in value_scores if score > 5])
    except:
        undervalued_count = 0
        overvalued_count = 0
    
    insights_style = {
        'container': {
            'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            'border-radius': '15px',
            'padding': '25px',
            'margin': '20px 0'
        },
        'insight_card': {
            'background': 'white',
            'border-radius': '10px',
            'padding': '15px',
            'margin': '10px 0',
            'border-left': '4px solid #667eea',
            'box-shadow': '0 2px 10px rgba(0,0,0,0.05)'
        },
        'metric': {
            'font-size': '18px',
            'font-weight': '600',
            'color': '#667eea'
        },
        'label': {
            'font-size': '14px',
            'color': '#6c757d',
            'margin-bottom': '5px'
        }
    }
    
    return html.Div([
        html.H4("📊 Market Insights & Recommendations", 
               style={'color': '#2c3e50', 'margin-bottom': '20px', 'font-weight': '600'}),
        
        html.Div([
            # Market Overview
            html.Div([
                html.H6("Market Overview", style={'color': '#495057', 'margin-bottom': '10px'}),
                html.P(f"Analyzing {total_properties} properties with an average price of ₪{avg_price:,.0f}", 
                      style={'margin': '0', 'font-size': '14px'})
            ], style=insights_style['insight_card']),
            
            # Price Analysis
            html.Div([
                html.H6("Price Distribution", style={'color': '#495057', 'margin-bottom': '10px'}),
                html.P([
                    f"Budget Range: ₪{price_quartiles[0.25]:,.0f} - ₪{price_quartiles[0.75]:,.0f} ",
                    html.Span("(middle 50%)", style={'color': '#6c757d', 'font-style': 'italic'})
                ], style={'margin': '0', 'font-size': '14px'})
            ], style=insights_style['insight_card']),
            
            # Real Affordability Analysis
            html.Div([
                html.H6("Affordability Analysis (by total price)", style={'color': '#495057', 'margin-bottom': '10px'}),
                html.P([
                    f"Most Affordable: ", 
                    html.Strong(f"{most_affordable_area}", style={'color': '#28a745'}),
                    f" (Avg: ₪{most_affordable_total_price:,.0f})"
                ], style={'margin': '0 0 5px 0', 'font-size': '14px'}),
                html.P([
                    f"Most Expensive: ", 
                    html.Strong(f"{most_expensive_area}", style={'color': '#dc3545'}),
                    f" (Avg: ₪{most_expensive_total_price:,.0f})"
                ], style={'margin': '0 0 5px 0', 'font-size': '14px'}),
                html.P([
                    f"Best Value: ", 
                    html.Strong(f"{best_value_area}", style={'color': '#667eea'}),
                    f" (size-adjusted efficiency)"
                ], style={'margin': '0', 'font-size': '14px'})
            ], style=insights_style['insight_card']),
            
            # Value Opportunities
            html.Div([
                html.H6("Investment Opportunities", style={'color': '#495057', 'margin-bottom': '10px'}),
                html.P([
                    html.Span("🟢 ", style={'color': '#28a745'}),
                    f"{undervalued_count} properties below market value"
                ], style={'margin': '0 0 5px 0', 'font-size': '14px'}),
                html.P([
                    html.Span("🔴 ", style={'color': '#dc3545'}),
                    f"{overvalued_count} properties above market value"
                ], style={'margin': '0', 'font-size': '14px'})
            ], style=insights_style['insight_card']),
            
        ], style=insights_style['container'])
    ])

def create_analytics_dashboard(df):
    """Create advanced analytics charts for deeper insights"""
    if len(df) == 0:
        # Create proper empty figures instead of incorrectly calling px functions
        def create_empty_figure(title):
            fig = go.Figure()
            fig.update_layout(
                title=title,
                xaxis_title="",
                yaxis_title="",
                height=350,
                showlegend=False
            )
            return fig
        
        empty_charts = {
            'price_histogram': create_empty_figure("Price Distribution - No data available"),
            'price_boxplot': create_empty_figure("Price/SQM Distribution - No data available"),
            'neighborhood_comparison': create_empty_figure("Neighborhood Comparison - No data available"), 
            'room_efficiency': create_empty_figure("Room Efficiency - No data available"),
            'neighborhood_ranking': create_empty_figure("Neighborhood Ranking - No data available")
        }
        return empty_charts
    
    analytics_df = df.copy()
    
    # 1. Price Distribution Histogram
    price_histogram = px.histogram(
        analytics_df,
        x='price',
        nbins=20,
        title='Property Price Distribution',
        labels={'price': 'Price (₪)', 'count': 'Number of Properties'},
        color_discrete_sequence=['#667eea']
    )
    price_histogram.update_layout(
        xaxis_title='Price (₪)',
        yaxis_title='Number of Properties',
        bargap=0.1,
        title_x=0.5,
        height=350
    )
    
    # 2. Price per SQM Box Plot by Neighborhood
    if 'neighborhood' in analytics_df.columns and len(analytics_df['neighborhood'].unique()) > 1:
        # Limit to top 8 neighborhoods by count to avoid clutter
        top_neighborhoods = analytics_df['neighborhood'].value_counts().head(8).index
        boxplot_df = analytics_df[analytics_df['neighborhood'].isin(top_neighborhoods)]
        
        price_boxplot = px.box(
            boxplot_df,
            x='neighborhood',
            y='price_per_sqm',
            title='Price/SQM Distribution by Neighborhood',
            labels={'price_per_sqm': 'Price per SQM (₪)', 'neighborhood': 'Neighborhood'},
            color='neighborhood',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        price_boxplot.update_layout(
            xaxis_title='Neighborhood',
            yaxis_title='Price per SQM (₪)',
            xaxis={'tickangle': 45},
            title_x=0.5,
            height=350,
            showlegend=False
        )
    else:
        price_boxplot = px.box(
            analytics_df,
            y='price_per_sqm',
            title='Overall Price/SQM Distribution',
            labels={'price_per_sqm': 'Price per SQM (₪)'},
            color_discrete_sequence=['#667eea']
        )
        price_boxplot.update_layout(height=350, title_x=0.5)
    
    # 3. Neighborhood Comparison Bar Chart
    if 'neighborhood' in analytics_df.columns and len(analytics_df['neighborhood'].unique()) > 1:
        neighborhood_stats = analytics_df.groupby('neighborhood').agg({
            'price': 'mean',
            'price_per_sqm': 'mean',
            'square_meters': 'mean',
            'rooms': 'mean'
        }).round(0).reset_index()
        
        # Limit to top 10 neighborhoods by count
        top_neighborhoods = analytics_df['neighborhood'].value_counts().head(10).index
        neighborhood_stats = neighborhood_stats[neighborhood_stats['neighborhood'].isin(top_neighborhoods)]
        
        neighborhood_comparison = px.bar(
            neighborhood_stats,
            x='neighborhood',
            y='price_per_sqm',
            title='Average Price/SQM by Neighborhood',
            labels={'price_per_sqm': 'Avg Price per SQM (₪)', 'neighborhood': 'Neighborhood'},
            color='price_per_sqm',
            color_continuous_scale='viridis'
        )
        neighborhood_comparison.update_layout(
            xaxis_title='Neighborhood',
            yaxis_title='Average Price per SQM (₪)',
            xaxis={'tickangle': 45},
            title_x=0.5,
            height=350
        )
    else:
        neighborhood_comparison = px.bar(
            x=['Overall Average'],
            y=[analytics_df['price_per_sqm'].mean()],
            title='Overall Average Price/SQM',
            labels={'y': 'Price per SQM (₪)', 'x': 'Category'},
            color_discrete_sequence=['#667eea']
        )
        neighborhood_comparison.update_layout(height=350, title_x=0.5)
    
    # 4. Room Efficiency Analysis  
    room_efficiency = px.scatter(
        analytics_df,
        x='rooms',
        y='square_meters',
        size='price',
        color='price_per_sqm',
        title='Room Count vs Property Size',
        labels={
            'rooms': 'Number of Rooms',
            'square_meters': 'Square Meters',
            'price_per_sqm': 'Price/SQM (₪)'
        },
        color_continuous_scale='viridis',
        size_max=15
    )
    room_efficiency.update_layout(
        xaxis_title='Number of Rooms',
        yaxis_title='Square Meters',
        title_x=0.5,
        height=350
    )
    
    return {
        'price_histogram': price_histogram,
        'price_boxplot': price_boxplot,
        'neighborhood_comparison': neighborhood_comparison,
        'room_efficiency': room_efficiency,
        'neighborhood_ranking': create_neighborhood_ranking(analytics_df)
    }

def create_dashboard(df, port=8051):
    """Create and run an interactive Dash app for visualizing the data"""
    
    # Create a custom stylesheet with enhanced design
    external_stylesheets = [
        {
            'href': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
            'rel': 'stylesheet'
        },
        {
            'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            'rel': 'stylesheet'
        }
    ]
    
    # Create the app
    app = dash.Dash(
        __name__, 
        title="Real Estate Price Analyzer",
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True
    )
    
    # Get unique values for filters
    neighborhoods = [{'label': 'All Neighborhoods', 'value': 'all'}] + [
        {'label': n, 'value': n} for n in sorted(df['neighborhood'].dropna().unique())
    ]
    
    property_types = [{'label': 'All Types', 'value': 'all'}] + [
        {'label': pt, 'value': pt} for pt in sorted(df['property_type'].dropna().unique())
    ]
    
    ad_types = [{'label': 'All', 'value': 'all'}] + [
        {'label': at, 'value': at} for at in sorted(df['ad_type'].unique())
    ]
    
    conditions = [{'label': 'All Conditions', 'value': 'all'}] + [
        {'label': ct, 'value': ct} for ct in sorted(df['condition_text'].dropna().unique())
    ]
    
    # Search options for new scraping
    city_options = [
        {'label': 'קרית ביאליק (Current)', 'value': 9500},
        {'label': 'תל אביב-יפו', 'value': 5000},
        {'label': 'ירושלים', 'value': 3000},
        {'label': 'חיפה', 'value': 8600},
        {'label': 'פתח תקווה', 'value': 7900},
        {'label': 'אשדוד', 'value': 1300},
        {'label': 'נתניה', 'value': 6300},
        {'label': 'באר שבע', 'value': 900}
    ]
    
    # Enhanced CSS styles with modern design
    styles = {
        'container': {
            'font-family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            'max-width': '1400px',
            'margin': '0 auto',
            'padding': '20px',
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'min-height': '100vh'
        },
        'content_wrapper': {
            'background-color': 'rgba(255, 255, 255, 0.95)',
            'border-radius': '20px',
            'padding': '30px',
            'box-shadow': '0 20px 40px rgba(0,0,0,0.1)',
            'backdrop-filter': 'blur(10px)'
        },
        'header': {
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'padding': '25px',
            'margin': '-30px -30px 30px -30px',
            'border-radius': '20px 20px 0 0',
            'text-align': 'center',
            'position': 'relative',
            'overflow': 'hidden'
        },
        'header_overlay': {
            'position': 'absolute',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'background': 'rgba(255,255,255,0.1)',
            'z-index': '1'
        },
        'header_content': {
            'position': 'relative',
            'z-index': '2'
        },
        'filter_container': {
            'display': 'grid',
            'grid-template-columns': 'repeat(auto-fit, minmax(280px, 1fr))',
            'gap': '20px',
            'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'margin-bottom': '25px',
            'backdrop-filter': 'blur(10px)',
            'border': '1px solid rgba(255,255,255,0.2)'
        },
        'filter': {
            'background': 'rgba(255,255,255,0.9)',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0 4px 15px rgba(0,0,0,0.08)',
            'border': '1px solid rgba(255,255,255,0.3)',
            'transition': 'all 0.3s ease'
        },
        'label': {
            'font-weight': '600',
            'margin-bottom': '10px',
            'color': '#2c3e50',
            'font-size': '14px',
            'display': 'flex',
            'align-items': 'center',
            'gap': '8px'
        },
        'dual_view_container': {
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'gap': '25px',
            'margin-bottom': '25px'
        },
        'graph': {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'border': '1px solid rgba(255,255,255,0.2)'
        },
        'map_container': {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'border': '1px solid rgba(255,255,255,0.2)'
        },
        'summary': {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'border': '1px solid rgba(255,255,255,0.2)'
        },
        'summary_header': {
            'color': '#2c3e50',
            'border-bottom': '3px solid #667eea',
            'padding-bottom': '15px',
            'margin-bottom': '20px',
            'font-weight': '600'
        },
        'click_instruction': {
            'text-align': 'center',
            'font-style': 'italic',
            'color': '#667eea',
            'margin': '15px 0',
            'padding': '15px',
            'background': 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            'border-radius': '12px',
            'border-left': '4px solid #667eea',
            'font-weight': '500'
        },
        'search_container': {
            'background': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'margin-bottom': '25px',
            'border': '1px solid rgba(255,255,255,0.3)'
        },
        'search_header': {
            'color': '#155724',
            'font-weight': '700',
            'font-size': '20px',
            'margin-bottom': '20px',
            'text-align': 'center',
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'gap': '10px'
        },
        'search_controls': {
            'display': 'grid',
            'grid-template-columns': 'repeat(auto-fit, minmax(200px, 1fr))',
            'gap': '20px',
            'align-items': 'end'
        },
        'search_filter': {
            'background': 'rgba(255,255,255,0.9)',
            'padding': '15px',
            'border-radius': '10px',
            'box-shadow': '0 4px 15px rgba(0,0,0,0.08)'
        },
        'scrape_button': {
            'background': 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
            'color': 'white',
            'border': 'none',
            'padding': '15px 25px',
            'border-radius': '10px',
            'cursor': 'pointer',
            'font-weight': '600',
            'font-size': '14px',
            'min-width': '180px',
            'height': '50px',
            'transition': 'all 0.3s ease',
            'box-shadow': '0 4px 15px rgba(40, 167, 69, 0.3)',
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'gap': '8px'
        },
        'loading_overlay': {
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'background': 'rgba(0,0,0,0.7)',
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'z-index': '9999',
            'backdrop-filter': 'blur(5px)'
        },
        'loading_content': {
            'background': 'white',
            'padding': '40px',
            'border-radius': '20px',
            'text-align': 'center',
            'box-shadow': '0 20px 40px rgba(0,0,0,0.3)',
            'max-width': '400px',
            'margin': '20px'
        },
        'spinner': {
            'width': '60px',
            'height': '60px',
            'border': '6px solid #f3f3f3',
            'border-top': '6px solid #667eea',
            'border-radius': '50%',
            'animation': 'spin 1s linear infinite',
            'margin': '0 auto 20px auto'
        },
        'loading_text': {
            'color': '#667eea',
            'font-weight': '600',
            'font-size': '18px',
            'margin-bottom': '10px'
        },
        'loading_subtitle': {
            'color': '#6c757d',
            'font-size': '14px',
            'line-height': '1.5'
        }
    }
    
    # Add custom CSS for animations and enhanced styling (including responsive grid)
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .fade-in {
                    animation: fadeIn 0.6s ease-out;
                }
                
                .pulse {
                    animation: pulse 2s infinite;
                }
                
                .filter-hover:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
                }
                
                .button-hover:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4) !important;
                }
                
                body {
                    margin: 0;
                    padding: 0;
                }
                
                .loading-dots::after {
                    content: '';
                    animation: dots 1.5s steps(5, end) infinite;
                }
                
                @keyframes dots {
                    0%, 20% { content: ''; }
                    40% { content: '.'; }
                    60% { content: '..'; }
                    80%, 100% { content: '...'; }
                }
                
                /* Responsive design for dual view */
                @media (max-width: 1200px) {
                    .dual-view-responsive {
                        grid-template-columns: 1fr !important;
                    }
                }
                
                /* Responsive design for analytics */
                @media (max-width: 900px) {
                    .analytics-grid {
                        grid-template-columns: 1fr !important;
                    }
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Enhanced loading component
    def create_loading_component(component_id, children, loading_text="Loading"):
        return dcc.Loading(
            id=f"loading-{component_id}",
            type="default",
            children=children,
            style={'margin': '20px 0'},
            color='#667eea',
            overlay_style={
                "visibility": "visible",
                "filter": "blur(2px)",
                "opacity": 0.5
            },
            custom_spinner=html.Div([
                html.Div(className="spinner", style=styles['spinner']),
                html.Div(loading_text, style=styles['loading_text']),
                html.Div("Please wait while we process your request...", style=styles['loading_subtitle'])
            ], style={'text-align': 'center'})
        )
    
    # Create the enhanced app layout with map integration
    app.layout = html.Div([
        # Global loading overlay (initially hidden)
        html.Div(
            id='global-loading-overlay',
            children=[
        html.Div([
                    html.Div(style=styles['spinner']),
                    html.Div("Processing your request", style=styles['loading_text'], className="loading-dots"),
                    html.Div("This may take a few moments...", style=styles['loading_subtitle'])
                ], style=styles['loading_content'])
            ],
            style={**styles['loading_overlay'], 'display': 'none'},
            className="fade-in"
        ),
        
        # Main content wrapper
        html.Div([
            # Enhanced Header
            html.Div([
                html.Div(style=styles['header_overlay']),
                html.Div([
                    html.H1([
                        html.I(className="fas fa-home", style={'margin-right': '15px'}),
                        "Real Estate Price Analysis Dashboard"
                    ], style={'margin': '0', 'font-weight': '700', 'font-size': '28px'}),
                    html.P("Discover market insights with interactive data visualization & geographic mapping", 
                           style={'margin': '10px 0 0 0', 'opacity': '0.9', 'font-size': '16px'})
                ], style=styles['header_content'])
        ], style=styles['header']),
        
            # Enhanced Search Controls Section
        html.Div([
            html.Div([
                    html.I(className="fas fa-search", style={'margin-right': '10px'}),
                    "Search New Properties"
                ], style=styles['search_header']),
                html.Div([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-map-marker-alt", style={'margin-right': '5px'}),
                            "City:"
                        ], style=styles['label']),
                    dcc.Dropdown(
                        id='search-city-dropdown',
                        options=city_options,
                        value=9500,
                            clearable=False,
                            style={'border-radius': '8px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-map", style={'margin-right': '5px'}),
                            "Area ID:"
                        ], style=styles['label']),
                    dcc.Input(
                        id='search-area',
                        type='number',
                        value=6,
                        placeholder="Area ID",
                            style={'width': '100%', 'padding': '12px', 'border-radius': '8px', 
                                   'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-shekel-sign", style={'margin-right': '5px'}),
                            "Min Price:"
                        ], style=styles['label']),
                    dcc.Input(
                        id='search-min-price',
                        type='number',
                        value=1000000,
                        step=50000,
                            style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                                   'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-shekel-sign", style={'margin-right': '5px'}),
                            "Max Price:"
                        ], style=styles['label']),
                    dcc.Input(
                        id='search-max-price',
                        type='number',
                        value=2000000,
                        step=50000,
                            style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                                   'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-bed", style={'margin-right': '5px'}),
                            "Min Rooms:"
                        ], style=styles['label']),
                    dcc.Dropdown(
                        id='search-min-rooms',
                        options=[{'label': 'Any', 'value': 'any'}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6]
                        ],
                        value='any',
                        clearable=True,
                        placeholder="Min rooms"
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-bed", style={'margin-right': '5px'}),
                            "Max Rooms:"
                        ], style=styles['label']),
                    dcc.Dropdown(
                        id='search-max-rooms',
                        options=[{'label': 'Any', 'value': 'any'}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8]
                        ],
                        value='any',
                        clearable=True,
                        placeholder="Max rooms"
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-ruler-combined", style={'margin-right': '5px'}),
                            "Min sqm:"
                        ], style=styles['label']),
                    dcc.Input(
                        id='search-min-sqm',
                        type='number',
                        value=None,
                        placeholder="Min sqm",
                            style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                                   'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                        html.Label([
                            html.I(className="fas fa-ruler-combined", style={'margin-right': '5px'}),
                            "Max sqm:"
                        ], style=styles['label']),
                    dcc.Input(
                        id='search-max-sqm',
                        type='number',
                        value=None,
                        placeholder="Max sqm",
                            style={'width': '100%', 'padding': '12px', 'border-radius': '8px',
                                   'border': '2px solid #e9ecef', 'font-size': '14px'}
                    ),
                    ], style=styles['search_filter'], className="filter-hover"),
                
                html.Div([
                    html.Label("Action:", style=styles['label']),
                        html.Button([
                            html.I(id='scrape-button-icon', className="fas fa-search", style={'margin-right': '8px'}),
                            html.Span(id='scrape-button-text', children="Scrape New Data")
                        ], 
                        id='scrape-button', 
                        style=styles['scrape_button'],
                        className="button-hover",
                        n_clicks=0
                    ),
                ], style=styles['search_filter']),
            ], style=styles['search_controls']),
            
                # Enhanced Loading/Status message
                html.Div(id='scrape-status', style={'margin-top': '20px'}),
            ], style=styles['search_container'], className="fade-in"),
            
            # Enhanced Current Data Filter section
        html.Div([
            html.Div([
                    html.Label([
                        html.I(className="fas fa-shekel-sign", style={'margin-right': '5px'}),
                        "Price Range:"
                    ], style=styles['label']),
                    create_loading_component("price-filter", 
                dcc.RangeSlider(
                    id='price-range-slider',
                    min=0 if len(df) == 0 else df['price'].min(),
                    max=10000000 if len(df) == 0 else df['price'].max(),
                    value=[0, 10000000] if len(df) == 0 else [df['price'].min(), df['price'].max()],
                    marks={
                        0: "₪0", 10000000: "₪10,000,000"
                    } if len(df) == 0 else {
                        int(df['price'].min()): f"₪{df['price'].min():,.0f}",
                        int(df['price'].max()): f"₪{df['price'].max():,.0f}"
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                        ), "Updating price range"
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            html.Div([
                    html.Label([
                        html.I(className="fas fa-ruler-combined", style={'margin-right': '5px'}),
                        "Square Meters:"
                    ], style=styles['label']),
                    create_loading_component("sqm-filter",
                dcc.RangeSlider(
                    id='sqm-range-slider',
                    min=0 if len(df) == 0 else df['square_meters'].min(),
                    max=500 if len(df) == 0 else df['square_meters'].max(),
                    value=[0, 500] if len(df) == 0 else [df['square_meters'].min(), df['square_meters'].max()],
                    marks={
                        0: "0", 500: "500"
                    } if len(df) == 0 else {
                        int(df['square_meters'].min()): f"{df['square_meters'].min():.0f}",
                        int(df['square_meters'].max()): f"{df['square_meters'].max():.0f}"
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                        ), "Updating size range"
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marker-alt", style={'margin-right': '5px'}),
                        "Neighborhood:"
                    ], style=styles['label']),
                dcc.Dropdown(
                    id='neighborhood-filter',
                    options=neighborhoods,
                    value='all',
                    clearable=False
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            html.Div([
                    html.Label([
                        html.I(className="fas fa-ban", style={'margin-right': '5px'}),
                        "Exclude Neighborhoods:"
                    ], style=styles['label']),
                    dcc.Dropdown(
                        id='exclude-neighborhoods-filter',
                        options=[{'label': n, 'value': n} for n in sorted(df['neighborhood'].dropna().unique())] if len(df) > 0 else [],
                        value=[],
                        multi=True,
                        placeholder="Select neighborhoods to exclude",
                        style={'min-height': '38px'}
                    ),
                ], style=styles['filter'], className="filter-hover"),
                
                html.Div([
                    html.Label([
                        html.I(className="fas fa-bed", style={'margin-right': '5px'}),
                        "Room Count:"
                    ], style=styles['label']),
                dcc.RangeSlider(
                    id='rooms-range-slider',
                    min=1 if len(df) == 0 else df['rooms'].min(),
                    max=8 if len(df) == 0 else df['rooms'].max(),
                    value=[1, 8] if len(df) == 0 else [df['rooms'].min(), df['rooms'].max()],
                    marks={
                        1: "1", 8: "8+"
                    } if len(df) == 0 else {
                        int(df['rooms'].min()): f"{df['rooms'].min():.0f}",
                        int(df['rooms'].max()): f"{df['rooms'].max():.0f}"
                    },
                    step=0.5,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            html.Div([
                    html.Label([
                        html.I(className="fas fa-tools", style={'margin-right': '5px'}),
                        "Condition:"
                    ], style=styles['label']),
                dcc.Dropdown(
                    id='condition-filter',
                    options=conditions,
                    value='all',
                    clearable=False
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            html.Div([
                    html.Label([
                        html.I(className="fas fa-tag", style={'margin-right': '5px'}),
                        "Ad Type:"
                    ], style=styles['label']),
                dcc.Dropdown(
                    id='ad-type-filter',
                    options=ad_types,
                    value='all',
                    clearable=False
                ),
                ], style=styles['filter'], className="filter-hover"),
            
            ], style=styles['filter_container'], className="fade-in"),
        
            # Enhanced click instruction
        html.Div([
                html.I(className="fas fa-mouse-pointer", style={'margin-right': '8px'}),
                html.Span("Click on any point in the chart or map to open the property listing in a new tab")
            ], style=styles['click_instruction'], className="fade-in"),
        
            # NEW: Dual view section with scatter plot and map side by side
            html.Div([
                # Scatter Plot section
            html.Div([
                    html.H3([
                        html.I(className="fas fa-chart-scatter", style={'margin-right': '10px', 'color': '#667eea'}),
                        "Price vs Size Analysis"
                    ], style={'color': '#2c3e50', 'margin-bottom': '20px', 'font-weight': '600', 'font-size': '18px'}),
                    create_loading_component("main-graph", 
                        dcc.Graph(
                            id='price-sqm-scatter',
                            config={
                                'displayModeBar': True,
                                'displaylogo': False,
                                'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'real_estate_scatter_analysis',
                                    'height': 600,
                                    'width': 800,
                                    'scale': 2
                                }
                            }
                        ), "Analyzing data and creating visualization"
                    )
                ], style=styles['graph'], className="fade-in"),
                
                # Map section
                html.Div([
                    html.H3([
                        html.I(className="fas fa-map-marked-alt", style={'margin-right': '10px', 'color': '#667eea'}),
                        "Geographic Distribution"
                    ], style={'color': '#2c3e50', 'margin-bottom': '20px', 'font-weight': '600', 'font-size': '18px'}),
                    create_loading_component("map-view", 
                        dcc.Graph(
                            id='property-map',
                            config={
                                'displayModeBar': True,
                                'displaylogo': False,
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'real_estate_map_view',
                                    'height': 600,
                                    'width': 800,
                                    'scale': 2
                                }
                            }
                        ), "Loading geographic visualization"
                    )
                ], style=styles['map_container'], className="fade-in"),
                
            ], style={**styles['dual_view_container'], **{'class': 'dual-view-responsive'}}, className="fade-in"),
            
            # NEW: Advanced Analytics Section (Phase 7)
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-line", style={'margin-right': '10px', 'color': '#667eea'}),
                    "Advanced Analytics Dashboard"
                ], style={'color': '#2c3e50', 'margin-bottom': '30px', 'font-weight': '600', 'font-size': '22px', 'text-align': 'center'}),
                
                # Analytics charts in 2x2 grid
                html.Div([
                    # Row 1: Histogram and Box Plot
                    html.Div([
                        html.Div([
                            create_loading_component("price-histogram", 
                                dcc.Graph(id='price-histogram', config={'displayModeBar': False}),
                                "Generating price distribution analysis"
                            )
                        ], style={'background': 'rgba(255,255,255,0.95)', 'padding': '20px', 'border-radius': '12px', 
                                 'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 'border': '1px solid rgba(255,255,255,0.3)'}),
                        
                        html.Div([
                            create_loading_component("price-boxplot", 
                                dcc.Graph(id='price-boxplot', config={'displayModeBar': False}),
                                "Creating neighborhood comparison"
                            )
                        ], style={'background': 'rgba(255,255,255,0.95)', 'padding': '20px', 'border-radius': '12px', 
                                 'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 'border': '1px solid rgba(255,255,255,0.3)'}),
                    ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '20px', 'margin-bottom': '20px'}),
                    
                    # Row 2: Bar Chart and Efficiency Scatter
                    html.Div([
                        html.Div([
                            create_loading_component("neighborhood-comparison", 
                                dcc.Graph(id='neighborhood-comparison', config={'displayModeBar': False}),
                                "Analyzing neighborhood trends"
                            )
                        ], style={'background': 'rgba(255,255,255,0.95)', 'padding': '20px', 'border-radius': '12px', 
                                 'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 'border': '1px solid rgba(255,255,255,0.3)'}),
                        
                        html.Div([
                            create_loading_component("room-efficiency", 
                                dcc.Graph(id='room-efficiency', config={'displayModeBar': False}),
                                "Computing room efficiency metrics"
                            )
                        ], style={'background': 'rgba(255,255,255,0.95)', 'padding': '20px', 'border-radius': '12px', 
                                 'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 'border': '1px solid rgba(255,255,255,0.3)'}),
                    ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '20px', 'margin-bottom': '20px'}),
                    
                    # Row 3: Neighborhood ranking (full width)
                    html.Div([
                        html.Div([
                            create_loading_component("neighborhood-ranking", 
                                dcc.Graph(id='neighborhood-ranking', config={'displayModeBar': False}),
                                "Ranking neighborhoods by affordability"
                            )
                        ], style={'background': 'rgba(255,255,255,0.95)', 'padding': '20px', 'border-radius': '12px', 
                                 'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 'border': '1px solid rgba(255,255,255,0.3)'}),
                    ]),
                ], style={
                    'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                    'padding': '25px',
                    'border-radius': '15px',
                    'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
                    'margin-bottom': '25px',
                    'border': '1px solid rgba(255,255,255,0.3)'
                })
            ], className="fade-in"),
            
            # NEW: Decision Support Section (Phase 7.5)
            html.Div([
                html.H3([
                    html.I(className="fas fa-lightbulb", style={'margin-right': '10px', 'color': '#28a745'}),
                    "Investment Decision Support"
                ], style={'color': '#2c3e50', 'margin-bottom': '30px', 'font-weight': '600', 'font-size': '22px', 'text-align': 'center'}),
                
                # Two column layout: Best deals + Market insights
                html.Div([
                    # Best deals table
                    html.Div([
                        create_loading_component("best-deals", 
                            html.Div(id='best-deals-table'),
                            "Finding best property deals"
                        )
                    ], style={
                        'background': 'rgba(255,255,255,0.95)', 
                        'padding': '25px', 
                        'border-radius': '12px', 
                        'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 
                        'border': '1px solid rgba(255,255,255,0.3)',
                        'flex': '1'
                    }),
                    
                    # Market insights
                    html.Div([
                        create_loading_component("market-insights", 
                            html.Div(id='market-insights'),
                            "Analyzing market trends"
                        )
                    ], style={
                        'background': 'rgba(255,255,255,0.95)', 
                        'padding': '25px', 
                        'border-radius': '12px', 
                        'box-shadow': '0 4px 15px rgba(0,0,0,0.08)', 
                        'border': '1px solid rgba(255,255,255,0.3)',
                        'flex': '1'
                    }),
                ], style={'display': 'flex', 'gap': '25px', 'align-items': 'flex-start'})
            ], style={
                'background': 'linear-gradient(135deg, #e8f5e8 0%, #d4f1d4 100%)',
                'padding': '25px',
                'border-radius': '15px',
                'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
                'margin-bottom': '25px',
                'border': '1px solid rgba(255,255,255,0.3)'
            }, className="fade-in"),
            
            # Enhanced Summary section
        html.Div([
                html.H3([
                    html.I(className="fas fa-chart-bar", style={'margin-right': '10px'}),
                    "Data Summary"
                ], style=styles['summary_header']),
                create_loading_component("summary", 
                    html.Div(id='summary-stats'), "Calculating statistics"
                )
            ], style=styles['summary'], className="fade-in"),
        
        # Store for clicked links
        dcc.Store(id='clicked-link', storage_type='memory'),
        dcc.Store(id='clicked-map-link', storage_type='memory'),
        
        # Store for current dataset
        dcc.Store(id='current-dataset', data=df.to_dict('records'), storage_type='session'),
            
            # Store for loading states
            dcc.Store(id='loading-state', data={'scraping': False}, storage_type='memory'),
            
        ], style=styles['content_wrapper'])
    ], style=styles['container'])
    
    # Enhanced callback for scraping with comprehensive loading experience
    @app.callback(
        [Output('current-dataset', 'data'),
         Output('scrape-status', 'children'),
         Output('scrape-button', 'disabled'),
         Output('loading-state', 'data'),
         Output('global-loading-overlay', 'style')],
        [Input('scrape-button', 'n_clicks')],
        [State('search-city-dropdown', 'value'),
         State('search-area', 'value'),
         State('search-min-price', 'value'),
         State('search-max-price', 'value'),
         State('search-min-rooms', 'value'),
         State('search-max-rooms', 'value'),
         State('search-min-sqm', 'value'),
         State('search-max-sqm', 'value'),
         State('loading-state', 'data')],
        prevent_initial_call=True
    )
    def scrape_new_data(n_clicks, city, area, min_price, max_price, min_rooms, max_rooms, min_sqm, max_sqm, loading_state):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
        
        # Function to create progressive loading messages
        def create_progress_message(step, total_steps, current_action, search_desc):
            progress_percentage = (step / total_steps) * 100
            
            return html.Div([
                # Progress header
                html.Div([
                    html.Div([
                        html.Div(style={
                            'width': '24px',
                            'height': '24px',
                            'border': '3px solid #f3f3f3',
                            'border-top': '3px solid #667eea',
                            'border-radius': '50%',
                            'animation': 'spin 1s linear infinite',
                            'margin-right': '15px'
                        }),
                        html.Span("Processing Your Request", style={'font-weight': '700', 'font-size': '18px', 'color': '#2c3e50'})
                    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin-bottom': '20px'}),
                    
                    # Progress bar
                    html.Div([
                        html.Div([
                            html.Div(
                                style={
                                    'width': f'{progress_percentage}%',
                                    'height': '100%',
                                    'background': 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                                    'border-radius': '10px',
                                    'transition': 'width 0.5s ease'
                                }
                            )
                        ], style={
                            'width': '100%',
                            'height': '8px',
                            'background-color': '#e9ecef',
                            'border-radius': '10px',
                            'margin-bottom': '15px',
                            'overflow': 'hidden'
                        }),
                        html.Div(f"Step {step} of {total_steps} ({progress_percentage:.0f}%)", 
                                style={'text-align': 'center', 'font-size': '12px', 'color': '#6c757d', 'margin-bottom': '15px'})
                    ]),
                    
                    # Current action
                    html.Div([
                        html.I(className="fas fa-cog fa-spin", style={'color': '#667eea', 'margin-right': '10px'}),
                        html.Span(current_action, style={'font-weight': '600', 'color': '#495057', 'font-size': '16px'})
                    ], style={'margin-bottom': '20px', 'text-align': 'center'}),
                    
                    # Search parameters
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-search", style={'color': '#667eea', 'margin-right': '8px'}),
                            html.Span("Search Parameters:", style={'font-weight': '600', 'color': '#2c3e50', 'font-size': '14px'})
                        ], style={'margin-bottom': '8px'}),
                        html.Div(search_desc, style={'color': '#495057', 'font-size': '13px', 'line-height': '1.5', 'margin-bottom': '15px'}),
                    ]),
                    
                    # Steps indicator
                    html.Div([
                        html.Div("Steps:", style={'font-weight': '600', 'color': '#2c3e50', 'margin-bottom': '10px', 'font-size': '14px'}),
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-check" if i < step else "fas fa-circle", 
                                       style={'color': '#28a745' if i < step else '#667eea' if i == step else '#dee2e6', 
                                              'margin-right': '8px', 'font-size': '12px'}),
                                html.Span(action, style={'font-size': '12px', 
                                                        'color': '#28a745' if i < step else '#2c3e50' if i == step else '#6c757d',
                                                        'font-weight': '500' if i == step else '400'})
                            ], style={'margin-bottom': '5px', 'display': 'flex', 'align-items': 'center'})
                            for i, action in enumerate([
                                "Preparing search parameters",
                                "Clearing old data files", 
                                "Fetching property listings",
                                "Processing and filtering data",
                                "Updating dashboard"
                            ], 1)
                        ])
                    ])
                ])
            ], style={
                'background': 'linear-gradient(135deg, #fff9e6 0%, #ffeaa7 100%)',
                'border': '1px solid #ffeaa7',
                'border-left': '5px solid #ffc107',
                'border-radius': '15px',
                'padding': '25px',
                'box-shadow': '0 8px 25px rgba(255, 193, 7, 0.2)',
                'text-align': 'left',
                'max-width': '500px',
                'margin': '0 auto'
            }, className="fade-in")
            
        try:
            # Step 1: Show initial loading and prepare parameters
            loading_overlay_style = {**styles['loading_overlay'], 'display': 'flex'}
            loading_state['scraping'] = True
            
            # Build search parameters description
            search_desc = f"City: {city}"
            if area: search_desc += f", Area: {area}"
            search_desc += f", Price: ₪{min_price:,.0f} - ₪{max_price:,.0f}"
            if (min_rooms and min_rooms != 'any') or (max_rooms and max_rooms != 'any'):
                room_range = ""
                if min_rooms and min_rooms != 'any': room_range += f"{min_rooms}+"
                if max_rooms and max_rooms != 'any': 
                    if min_rooms and min_rooms != 'any': room_range = f"{min_rooms}-{max_rooms}"
                    else: room_range = f"≤{max_rooms}"
                search_desc += f", Rooms: {room_range}"
            if min_sqm or max_sqm:
                sqm_range = ""
                if min_sqm: sqm_range += f"{min_sqm}+"
                if max_sqm:
                    if min_sqm: sqm_range = f"{min_sqm}-{max_sqm}"
                    else: sqm_range = f"≤{max_sqm}"
                search_desc += f", Size: {sqm_range}sqm"
            
            # Progressive loading steps
            
            # Step 1: Preparing search parameters
            step1_msg = create_progress_message(1, 5, "Preparing search parameters", search_desc)
            # Note: In a real app, you'd return this via an interval callback for real-time updates
            # For now, we'll show this in the global overlay
            
            # Update global loading overlay with step 1
            loading_overlay_content = html.Div([
                html.Div([
                    step1_msg
                ], style=styles['loading_content'])
            ])
            
            # Step 2: Delete old data files
            output_dir = Path("scraped_real_estate")
            csv_files = list(output_dir.glob("real_estate_listings_*.csv"))
            json_files = list(output_dir.glob("real_estate_listings_*.json"))
            raw_api_files = list(output_dir.glob("raw_api_response_*.json"))
            
            for file in csv_files + json_files + raw_api_files:
                try:
                    file.unlink()
                    print(f"🗑️  Deleted old file: {file}")
                except Exception as e:
                    print(f"⚠️  Could not delete {file}: {e}")
            
            # Show comprehensive loading status with all steps
            loading_status = create_progress_message(2, 5, "Processing your request - this may take 30-60 seconds", search_desc)
            
            # Create scraper instance and build parameters
            scraper = RealEstateScraper("scraped_real_estate")
            
            # Build API parameters
            api_params = {
                'city': city,
                'min_price': min_price,
                'max_price': max_price
            }
            
            # Add optional parameters if provided
            if area: 
                api_params['area'] = area
            if min_rooms and min_rooms != 'any':
                api_params['min_rooms'] = min_rooms
            if max_rooms and max_rooms != 'any':
                api_params['max_rooms'] = max_rooms  
            if min_sqm:
                api_params['min_square_meters'] = min_sqm
            if max_sqm:
                api_params['max_square_meters'] = max_sqm
            
            # Status update for fetching data
            fetching_status = create_progress_message(3, 5, "Fetching property listings from Yad2", search_desc)
            
            # Scrape new data with user parameters
            csv_path, json_path = scraper.scrape_and_save(**api_params)
            
            # Hide loading overlay
            loading_overlay_style = {**styles['loading_overlay'], 'display': 'none'}
            loading_state['scraping'] = False
            
            if csv_path:
                # Load new data
                new_df = pd.read_csv(csv_path)
                
                # Filter and prepare data (same as load_data function)
                new_df = new_df[new_df['price'] > 0]
                new_df = new_df[new_df['square_meters'].notna() & (new_df['square_meters'] > 0)]
                new_df['price_per_sqm'] = new_df['price'] / new_df['square_meters']
                new_df['lat'] = pd.to_numeric(new_df['lat'], errors='coerce')
                new_df['lng'] = pd.to_numeric(new_df['lng'], errors='coerce')
                
                # Enhanced success message
                success_msg = html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={'color': '#28a745', 'font-size': '24px', 'margin-bottom': '10px'}),
                        html.H4("Success!", style={'color': '#28a745', 'margin': '10px 0', 'font-weight': '600'}),
                        html.P([
                            html.Span(f"Found {len(new_df)} new properties ", style={'font-weight': '600'}),
                            html.Span("and updated the dashboard!")
                        ], style={'color': '#155724', 'margin': '0 0 10px 0'}),
                        html.P("Previous data has been cleared automatically.", 
                               style={'color': '#6c757d', 'font-size': '13px', 'margin': '0', 'font-style': 'italic'})
                    ], style={'text-align': 'center'})
                ], style={
                    'background': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
                    'border': '1px solid #c3e6cb',
                    'border-left': '5px solid #28a745',
                    'border-radius': '12px',
                    'padding': '20px',
                    'box-shadow': '0 4px 15px rgba(40, 167, 69, 0.2)'
                }, className="fade-in")
                
                return new_df.to_dict('records'), success_msg, False, loading_state, loading_overlay_style
            else:
                # Enhanced error message
                error_msg = html.Div([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'color': '#dc3545', 'font-size': '24px', 'margin-bottom': '10px'}),
                        html.H4("Scraping Failed", style={'color': '#dc3545', 'margin': '10px 0', 'font-weight': '600'}),
                        html.P("Unable to retrieve data. Please check your parameters and try again.", 
                               style={'color': '#721c24', 'margin': '0'})
                    ], style={'text-align': 'center'})
                ], style={
                    'background': 'linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%)',
                    'border': '1px solid #f1aeb5',
                    'border-left': '5px solid #dc3545',
                    'border-radius': '12px',
                    'padding': '20px',
                    'box-shadow': '0 4px 15px rgba(220, 53, 69, 0.2)'
                }, className="fade-in")
                
                return dash.no_update, error_msg, False, loading_state, loading_overlay_style
                
        except Exception as e:
            # Hide loading overlay on error
            loading_overlay_style = {**styles['loading_overlay'], 'display': 'none'}
            loading_state['scraping'] = False
            
            # Enhanced error message
            error_msg = html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-circle", style={'color': '#dc3545', 'font-size': '24px', 'margin-bottom': '10px'}),
                    html.H4("Error Occurred", style={'color': '#dc3545', 'margin': '10px 0', 'font-weight': '600'}),
                    html.P(f"Scraping failed: {str(e)}", style={'color': '#721c24', 'margin': '0', 'font-size': '14px'})
                ], style={'text-align': 'center'})
            ], style={
                'background': 'linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%)',
                'border': '1px solid #f1aeb5',
                'border-left': '5px solid #dc3545',
                'border-radius': '12px',
                'padding': '20px',
                'box-shadow': '0 4px 15px rgba(220, 53, 69, 0.2)'
            }, className="fade-in")
            
            return dash.no_update, error_msg, False, loading_state, loading_overlay_style
    
    # Enhanced callback to update button state during loading
    @app.callback(
        [Output('scrape-button-icon', 'className'),
         Output('scrape-button-text', 'children'),
         Output('scrape-button', 'style')],
        [Input('loading-state', 'data')]
    )
    def update_button_loading_state(loading_state):
        if loading_state and loading_state.get('scraping', False):
            # Loading state
            return (
                "fas fa-spinner fa-spin",
                "Scraping Properties...",
                {**styles['scrape_button'], 'opacity': '0.8', 'cursor': 'not-allowed'}
            )
        else:
            # Normal state
            return (
                "fas fa-search",
                "Scrape New Data", 
                styles['scrape_button']
            )
    
    # Client-side callback to open links in new tab (scatter plot)
    app.clientside_callback(
        """
        function(clickData) {
            if(clickData && clickData.points && clickData.points.length > 0) {
                const link = clickData.points[0].customdata[7];
                if(link && link.length > 0) {
                    window.open(link, '_blank');
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('clicked-link', 'data'),
        Input('price-sqm-scatter', 'clickData'),
        prevent_initial_call=True
    )
    
    # Client-side callback to open links in new tab (map)
    app.clientside_callback(
        """
        function(clickData) {
            if(clickData && clickData.points && clickData.points.length > 0) {
                const link = clickData.points[0].customdata[7];
                if(link && link.length > 0) {
                    window.open(link, '_blank');
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('clicked-map-link', 'data'),
        Input('property-map', 'clickData'),
        prevent_initial_call=True
    )
    
    # Enhanced callback to update filter ranges when new data is loaded with loading indicators
    @app.callback(
        [Output('price-range-slider', 'min'),
         Output('price-range-slider', 'max'),
         Output('price-range-slider', 'value'),
         Output('price-range-slider', 'marks'),
         Output('sqm-range-slider', 'min'),
         Output('sqm-range-slider', 'max'),
         Output('sqm-range-slider', 'value'),
         Output('sqm-range-slider', 'marks'),
         Output('neighborhood-filter', 'options'),
         Output('neighborhood-filter', 'value'),
         Output('exclude-neighborhoods-filter', 'options'),
         Output('exclude-neighborhoods-filter', 'value'),
         Output('rooms-range-slider', 'min'),
         Output('rooms-range-slider', 'max'),
         Output('rooms-range-slider', 'value'),
         Output('rooms-range-slider', 'marks'),
         Output('condition-filter', 'options'),
         Output('condition-filter', 'value'),
         Output('ad-type-filter', 'options'),
         Output('ad-type-filter', 'value')],
        [Input('current-dataset', 'data')]
    )
    def update_filter_ranges(current_data):
        # Convert current data back to DataFrame
        current_df = pd.DataFrame(current_data)
        
        if len(current_df) == 0:
            # Return default values if no data (20 values total now)
            default_neighborhoods = [{'label': 'All Neighborhoods', 'value': 'all'}]
            default_exclude_neighborhoods = []
            default_conditions = [{'label': 'All Conditions', 'value': 'all'}]
            default_ad_types = [{'label': 'All', 'value': 'all'}]
            return (0, 1000000, [0, 1000000], {}, 0, 100, [0, 100], {}, 
                   default_neighborhoods, 'all', default_exclude_neighborhoods, [], 
                   1, 8, [1, 8], {}, default_conditions, 'all', default_ad_types, 'all')
        
        # Update price range
        price_min = current_df['price'].min()
        price_max = current_df['price'].max()
        price_marks = {
            int(price_min): f"₪{price_min:,.0f}",
            int(price_max): f"₪{price_max:,.0f}"
        }
        
        # Update sqm range
        sqm_min = current_df['square_meters'].min()
        sqm_max = current_df['square_meters'].max()
        sqm_marks = {
            int(sqm_min): f"{sqm_min:.0f}",
            int(sqm_max): f"{sqm_max:.0f}"
        }
        
        # Update rooms range
        rooms_min = current_df['rooms'].min()
        rooms_max = current_df['rooms'].max()
        rooms_marks = {
            int(rooms_min): f"{rooms_min:.0f}",
            int(rooms_max): f"{rooms_max:.0f}"
        }
        
        # Update neighborhood options
        neighborhoods = [{'label': 'All Neighborhoods', 'value': 'all'}] + [
            {'label': n, 'value': n} for n in sorted(current_df['neighborhood'].dropna().unique())
        ]
        
        # Update exclude neighborhood options (all available neighborhoods)
        exclude_neighborhoods_options = [
            {'label': n, 'value': n} for n in sorted(current_df['neighborhood'].dropna().unique())
        ]
        
        # Update condition options
        conditions = [{'label': 'All Conditions', 'value': 'all'}] + [
            {'label': ct, 'value': ct} for ct in sorted(current_df['condition_text'].dropna().unique())
        ]
        
        # Update ad_type options
        ad_types = [{'label': 'All', 'value': 'all'}] + [
            {'label': at, 'value': at} for at in sorted(current_df['ad_type'].unique())
        ]
        
        print(f"🔄 Updated filters - Price: ₪{price_min:,.0f}-₪{price_max:,.0f}, Size: {sqm_min:.0f}-{sqm_max:.0f}sqm, Rooms: {rooms_min:.0f}-{rooms_max:.0f}")
        print(f"🔄 Neighborhoods: {len(neighborhoods)-1}, Exclude Options: {len(exclude_neighborhoods_options)}, Conditions: {len(conditions)-1}, Ad Types: {len(ad_types)-1}")
        
        return (
            price_min, price_max, [price_min, price_max], price_marks,
            sqm_min, sqm_max, [sqm_min, sqm_max], sqm_marks,
            neighborhoods, 'all', exclude_neighborhoods_options, [],
            rooms_min, rooms_max, [rooms_min, rooms_max], rooms_marks,
            conditions, 'all', ad_types, 'all'
        )
    
    # Enhanced callback for updating graph, map, analytics, and summary with better loading experience
    @app.callback(
        [Output('price-sqm-scatter', 'figure'),
         Output('property-map', 'figure'),
         Output('price-histogram', 'figure'),
         Output('price-boxplot', 'figure'),
         Output('neighborhood-comparison', 'figure'),
         Output('room-efficiency', 'figure'),
         Output('neighborhood-ranking', 'figure'),
         Output('best-deals-table', 'children'),
         Output('market-insights', 'children'),
         Output('summary-stats', 'children')],
        [Input('price-range-slider', 'value'),
         Input('sqm-range-slider', 'value'),
         Input('neighborhood-filter', 'value'),
         Input('exclude-neighborhoods-filter', 'value'),
         Input('rooms-range-slider', 'value'),
         Input('condition-filter', 'value'),
         Input('ad-type-filter', 'value'),
         Input('current-dataset', 'data')]
    )
    def update_graph(price_range, sqm_range, neighborhood, exclude_neighborhoods, rooms, condition, ad_type, current_data):
        # Convert current data back to DataFrame
        current_df = pd.DataFrame(current_data)
        
        # Debug info
        print(f"📊 Raw data loaded: {len(current_df)} rows")
        print(f"🔍 Filter values:")
        print(f"   - Price range: {price_range}")
        print(f"   - Size range: {sqm_range}")
        print(f"   - Neighborhood: '{neighborhood}' (type: {type(neighborhood)})")
        print(f"   - Exclude neighborhoods: '{exclude_neighborhoods}' (type: {type(exclude_neighborhoods)})")
        print(f"   - Rooms: '{rooms}' (type: {type(rooms)})")
        print(f"   - Condition: '{condition}' (type: {type(condition)})")
        print(f"   - Ad Type: '{ad_type}' (type: {type(ad_type)})")
        
        if len(current_df) == 0:
            print("❌ No data available")
            empty_fig = px.scatter(title="No data available")
            empty_map = create_map_figure(pd.DataFrame())
            empty_analytics = create_analytics_dashboard(pd.DataFrame())
            empty_summary = html.Div("No data to display", style={'text-align': 'center', 'color': '#666'})
            empty_deals = html.Div("No data available", style={'text-align': 'center', 'color': '#666'})
            empty_insights = html.Div("No data available", style={'text-align': 'center', 'color': '#666'})
            return (empty_fig, empty_map, 
                   empty_analytics['price_histogram'], empty_analytics['price_boxplot'],
                   empty_analytics['neighborhood_comparison'], empty_analytics['room_efficiency'],
                   empty_analytics['neighborhood_ranking'], empty_deals, empty_insights,
                   empty_summary)
        
        # Ensure we have the required columns
        required_cols = ['price', 'square_meters', 'price_per_sqm']
        for col in required_cols:
            if col not in current_df.columns:
                print(f"❌ Missing column: {col}")
                empty_fig = px.scatter(title=f"Error: Missing {col} column")
                empty_map = create_map_figure(pd.DataFrame())
                empty_analytics = create_analytics_dashboard(pd.DataFrame())
                empty_summary = html.Div(f"Data error: Missing {col}", style={'text-align': 'center', 'color': '#e74c3c'})
                empty_deals = html.Div("Data error", style={'text-align': 'center', 'color': '#e74c3c'})
                empty_insights = html.Div("Data error", style={'text-align': 'center', 'color': '#e74c3c'})
                return (empty_fig, empty_map,
                       empty_analytics['price_histogram'], empty_analytics['price_boxplot'],
                       empty_analytics['neighborhood_comparison'], empty_analytics['room_efficiency'],
                       empty_analytics['neighborhood_ranking'], empty_deals, empty_insights,
                       empty_summary)
        
        # Start with all data
        filtered_df = current_df.copy()
        print(f"📈 Starting with: {len(filtered_df)} rows")
        
        # Apply price filter if price_range is provided and valid
        if price_range and len(price_range) == 2 and price_range[0] is not None and price_range[1] is not None:
            price_min, price_max = price_range
            before_count = len(filtered_df)
            filtered_df = filtered_df[
                (filtered_df['price'] >= price_min) & 
                (filtered_df['price'] <= price_max)
            ]
            print(f"📈 Price filter ({price_min:,.0f}-{price_max:,.0f}): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"⚠️  Skipping price filter (invalid range: {price_range})")
        
        # Apply sqm filter if sqm_range is provided and valid
        if sqm_range and len(sqm_range) == 2 and sqm_range[0] is not None and sqm_range[1] is not None:
            sqm_min, sqm_max = sqm_range
            before_count = len(filtered_df)
            filtered_df = filtered_df[
                (filtered_df['square_meters'] >= sqm_min) & 
                (filtered_df['square_meters'] <= sqm_max)
            ]
            print(f"📈 Size filter ({sqm_min:.0f}-{sqm_max:.0f}sqm): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"⚠️  Skipping size filter (invalid range: {sqm_range})")
        
        # Apply neighborhood filter
        if neighborhood is not None and neighborhood != 'all' and 'neighborhood' in filtered_df.columns:
            before_count = len(filtered_df)
            filtered_df = filtered_df[filtered_df['neighborhood'] == neighborhood]
            print(f"📈 Neighborhood filter ('{neighborhood}'): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"📈 Neighborhood filter: keeping all (value='{neighborhood}')")
            
        # Apply exclude neighborhoods filter
        if exclude_neighborhoods and len(exclude_neighborhoods) > 0 and 'neighborhood' in filtered_df.columns:
            before_count = len(filtered_df)
            filtered_df = filtered_df[~filtered_df['neighborhood'].isin(exclude_neighborhoods)]
            print(f"📈 Exclude neighborhoods filter: {before_count} → {len(filtered_df)} rows (excluded: {exclude_neighborhoods})")
        else:
            print(f"📈 Exclude neighborhoods filter: no exclusions (value='{exclude_neighborhoods}')")
            
        # Apply rooms filter
        if rooms is not None and len(rooms) == 2 and rooms[0] is not None and rooms[1] is not None and 'rooms' in filtered_df.columns:
            rooms_min, rooms_max = rooms
            before_count = len(filtered_df)
            filtered_df = filtered_df[
                (filtered_df['rooms'] >= rooms_min) & 
                (filtered_df['rooms'] <= rooms_max)
            ]
            print(f"📈 Rooms filter ({rooms_min:.1f}-{rooms_max:.1f}): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"📈 Rooms filter: keeping all (value='{rooms}')")
            
        # Apply condition filter
        if condition is not None and condition != 'all' and 'condition_text' in filtered_df.columns:
            before_count = len(filtered_df)
            filtered_df = filtered_df[filtered_df['condition_text'] == condition]
            print(f"📈 Condition filter ('{condition}'): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"📈 Condition filter: keeping all (value='{condition}')")
            
        # Apply ad_type filter
        if ad_type is not None and ad_type != 'all' and 'ad_type' in filtered_df.columns:
            before_count = len(filtered_df)
            filtered_df = filtered_df[filtered_df['ad_type'] == ad_type]
            print(f"📈 Ad type filter ('{ad_type}'): {before_count} → {len(filtered_df)} rows")
        else:
            print(f"📈 Ad type filter: keeping all (value='{ad_type}')")
        
        print(f"📈 Final filtered data: {len(filtered_df)} rows")
        print("="*50)
        
        # If no data after filtering, show message
        if len(filtered_df) == 0:
            print("❌ No data remains after filtering")
            empty_fig = px.scatter(title="No properties match current filters")
            empty_map = create_map_figure(pd.DataFrame())
            empty_analytics = create_analytics_dashboard(pd.DataFrame())
            empty_summary = html.Div("Try adjusting your filters to see more properties", 
                                   style={'text-align': 'center', 'color': '#e67e22'})
            empty_deals = html.Div("No properties match filters", style={'text-align': 'center', 'color': '#e67e22'})
            empty_insights = html.Div("No properties match filters", style={'text-align': 'center', 'color': '#e67e22'})
            return (empty_fig, empty_map,
                   empty_analytics['price_histogram'], empty_analytics['price_boxplot'],
                   empty_analytics['neighborhood_comparison'], empty_analytics['room_efficiency'],
                   empty_analytics['neighborhood_ranking'], empty_deals, empty_insights,
                   empty_summary)
        
        # Clean data for plotting - handle NaN values
        plot_df = filtered_df.copy()
        
        # Fill NaN values in rooms column with median or default value
        if plot_df['rooms'].isna().any():
            median_rooms = plot_df['rooms'].median()
            default_rooms = 3 if pd.isna(median_rooms) else median_rooms
            plot_df['rooms'] = plot_df['rooms'].fillna(default_rooms)
            print(f"⚠️  Filled {filtered_df['rooms'].isna().sum()} NaN room values with {default_rooms}")
        
        # Ensure rooms column has valid numeric values
        plot_df['rooms'] = pd.to_numeric(plot_df['rooms'], errors='coerce')
        plot_df['rooms'] = plot_df['rooms'].fillna(3)  # Final fallback
        
        # Clean data by removing invalid records instead of filling with fake data
        initial_count = len(plot_df)
        
        # Critical fields that must have valid data - never fill these with fake values
        critical_fields = ['square_meters', 'price', 'price_per_sqm']
        
        for col in critical_fields:
            if col in plot_df.columns:
                # Convert to numeric
                plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce')
                
                # Remove rows with missing critical data instead of filling
                before_count = len(plot_df)
                plot_df = plot_df[plot_df[col].notna()]
                removed_count = before_count - len(plot_df)
                
                if removed_count > 0:
                    print(f"🗑️  Removed {removed_count} properties with missing/invalid {col} data")
        
        # For non-critical fields, we can be more lenient (only rooms in this case)
        if 'rooms' in plot_df.columns:
            plot_df['rooms'] = pd.to_numeric(plot_df['rooms'], errors='coerce')
            # Only fill rooms if it's a small amount of missing data
            rooms_missing = plot_df['rooms'].isna().sum()
            if rooms_missing > 0:
                if rooms_missing / len(plot_df) < 0.05:  # Less than 5% missing
                    median_rooms = plot_df['rooms'].median()
                    plot_df['rooms'] = plot_df['rooms'].fillna(median_rooms)
                    print(f"🔧 Filled {rooms_missing} missing room values with median: {median_rooms}")
                else:
                    # Remove properties with missing room data if too many
                    plot_df = plot_df[plot_df['rooms'].notna()]
                    print(f"🗑️  Removed {rooms_missing} properties with missing room data")
        
        # Data quality summary
        final_count = len(plot_df)
        removed_total = initial_count - final_count
        if removed_total > 0:
            print(f"📊 Data Quality: Removed {removed_total} incomplete properties ({removed_total/initial_count*100:.1f}%)")
            print(f"✅ Final dataset: {final_count} complete, high-quality properties")
        
        # Add data quality warning if significant data was removed
        data_quality_warning = None
        if removed_total > 0:
            quality_percentage = (final_count / initial_count) * 100
            if quality_percentage < 90:
                data_quality_warning = html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={'color': '#f39c12', 'margin-right': '8px'}),
                    f"Data Quality Notice: {removed_total} properties removed due to missing/invalid data ({100-quality_percentage:.1f}% of original dataset)"
                ], style={
                    'background': '#fff3cd',
                    'border': '1px solid #ffeaa7',
                    'color': '#856404',
                    'padding': '12px',
                    'border-radius': '8px',
                    'margin-bottom': '20px',
                    'font-size': '14px'
                })
        

        
        # Create enhanced scatter plot with trend lines and value analysis
        fig = create_enhanced_scatter_plot(plot_df)
        
        # Create the map visualization
        map_fig = create_map_figure(plot_df)
        
        # Create analytics dashboard
        analytics_charts = create_analytics_dashboard(plot_df)
        
        # Enhanced summary statistics with modern design
        summary_style = {
            'container': {
                'display': 'grid',
                'grid-template-columns': 'repeat(auto-fit, minmax(220px, 1fr))',
                'gap': '20px'
            },
            'card': {
                'padding': '20px',
                'border-radius': '12px',
                'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                'box-shadow': '0 4px 15px rgba(0,0,0,0.08)',
                'text-align': 'center',
                'border': '1px solid rgba(255,255,255,0.3)',
                'transition': 'all 0.3s ease'
            },
            'value': {
                'font-size': '24px',
                'font-weight': '700',
                'color': '#667eea',
                'margin': '10px 0',
                'text-shadow': '0 1px 3px rgba(0,0,0,0.1)'
            },
            'label': {
                'font-size': '14px',
                'color': '#495057',
                'margin': '0',
                'font-weight': '500',
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                'gap': '6px'
            },
            'icon': {
                'color': '#667eea',
                'font-size': '16px'
            }
        }
        
        # Create enhanced summary stats with icons and better layout
        summary_cards = [
            html.Div([
                html.P([
                    html.I(className="fas fa-home", style=summary_style['icon']),
                    "Properties Found"
                ], style=summary_style['label']),
                html.P(f"{len(plot_df):,}", style=summary_style['value'])
            ], style=summary_style['card'], className="filter-hover"),
            
            html.Div([
                html.P([
                    html.I(className="fas fa-shekel-sign", style=summary_style['icon']),
                    "Average Price"
                ], style=summary_style['label']),
                html.P(f"₪{plot_df['price'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card'], className="filter-hover"),
            
            html.Div([
                html.P([
                    html.I(className="fas fa-calculator", style=summary_style['icon']),
                    "Avg Price/sqm"
                ], style=summary_style['label']),
                html.P(f"₪{plot_df['price_per_sqm'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card'], className="filter-hover"),
            
            html.Div([
                html.P([
                    html.I(className="fas fa-ruler-combined", style=summary_style['icon']),
                    "Average Size"
                ], style=summary_style['label']),
                html.P(f"{plot_df['square_meters'].mean():,.0f} sqm", style=summary_style['value'])
            ], style=summary_style['card'], className="filter-hover"),
            
            html.Div([
                html.P([
                    html.I(className="fas fa-bed", style=summary_style['icon']),
                    "Average Rooms"
                ], style=summary_style['label']),
                html.P(f"{plot_df['rooms'].mean():.1f}", style=summary_style['value'])
            ], style=summary_style['card'], className="filter-hover"),
            
            html.Div([
                html.P([
                    html.I(className="fas fa-chart-line", style=summary_style['icon']),
                    "Price Range"
                ], style=summary_style['label']),
                html.P(f"₪{plot_df['price'].min():,.0f} - ₪{plot_df['price'].max():,.0f}", 
                       style={**summary_style['value'], 'font-size': '18px'})
            ], style=summary_style['card'], className="filter-hover"),
        ]
        
        # Combine data quality warning (if any) with summary cards
        summary_components = []
        if data_quality_warning:
            summary_components.append(data_quality_warning)
        
        summary_components.append(html.Div(summary_cards, style=summary_style['container'], className="fade-in"))
        summary = html.Div(summary_components)
        
        # Create decision support components
        best_deals_table = create_best_deals_table(plot_df)
        market_insights = create_market_insights_summary(plot_df)
        
        return (fig, map_fig,
               analytics_charts['price_histogram'], analytics_charts['price_boxplot'],
               analytics_charts['neighborhood_comparison'], analytics_charts['room_efficiency'],
               analytics_charts['neighborhood_ranking'], best_deals_table, market_insights,
               summary)
    
    # Run the app
    print(f"Starting dashboard on http://127.0.0.1:{port}/")
    app.run(debug=True, port=port)

def main():
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load the most recent CSV file if it exists
    scraped_dir = output_dir / "scraped_real_estate"
    df = create_empty_dataframe()
    
    if scraped_dir.exists():
        # Look for the most recent CSV file
        csv_files = list(scraped_dir.glob("real_estate_listings_*.csv"))
        if csv_files:
            # Sort by modification time, get the most recent
            latest_csv = max(csv_files, key=lambda f: f.stat().st_mtime)
            print(f"📁 Found existing data file: {latest_csv.name}")
            print("🔄 Loading existing data...")
            df = load_data(str(latest_csv))
            print(f"✅ Loaded {len(df)} properties from existing data")
        else:
            print("📂 No existing data files found. Use the search controls to scrape new data.")
    else:
        print("📂 No scraped data directory found. Use the search controls to scrape new data.")
    
    if len(df) == 0:
        print("🚀 Starting with empty dataset. Use the search controls to scrape data.")
        df = create_empty_dataframe()
    
    # Create and run the dashboard
    create_dashboard(df, args.port)


if __name__ == "__main__":
    main() 