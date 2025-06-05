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
    """Load and prepare the CSV data for visualization"""
    try:
        df = pd.read_csv(csv_path)
        
        # Filter out properties with no price or price = 0
        df = df[df['price'] > 0]
        
        # Filter out properties with missing square meters data
        df = df[df['square_meters'].notna() & (df['square_meters'] > 0)]
        
        # Ensure price_per_sqm is calculated
        df['price_per_sqm'] = df['price'] / df['square_meters']
        
        # Convert coordinates to numeric
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame instead of exiting

def create_empty_dataframe():
    """Create an empty DataFrame with the expected structure"""
    return pd.DataFrame(columns=[
        'price', 'square_meters', 'price_per_sqm', 'lat', 'lng',
        'neighborhood', 'rooms', 'condition_text', 'ad_type', 
        'property_type', 'street', 'floor', 'full_url'
    ])

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
        'graph': {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '25px',
            'border-radius': '15px',
            'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
            'margin-bottom': '25px',
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
    
    # Add custom CSS for animations and enhanced styling
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
    
    # Create the enhanced app layout
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
                    html.P("Discover market insights with interactive data visualization", 
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
                html.Span("Click on any point in the graph to open the property listing in a new tab")
            ], style=styles['click_instruction'], className="fade-in"),
        
            # Enhanced Graph section with comprehensive loading
        html.Div([
                create_loading_component("main-graph", 
                    dcc.Graph(
                        id='price-sqm-scatter',
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'real_estate_analysis',
                                'height': 800,
                                'width': 1200,
                                'scale': 2
                            }
                        }
                    ), "Analyzing data and creating visualization"
                )
            ], style=styles['graph'], className="fade-in"),
            
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
    
    # Client-side callback to open links in new tab
    app.clientside_callback(
        """
        function(clickData) {
            if(clickData && clickData.points && clickData.points.length > 0) {
                const link = clickData.points[0].customdata[6];
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
    
    # Enhanced callback for updating graph and summary with better loading experience
    @app.callback(
        [Output('price-sqm-scatter', 'figure'),
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
            empty_summary = html.Div("No data to display", style={'text-align': 'center', 'color': '#666'})
            return empty_fig, empty_summary
        
        # Ensure we have the required columns
        required_cols = ['price', 'square_meters', 'price_per_sqm']
        for col in required_cols:
            if col not in current_df.columns:
                print(f"❌ Missing column: {col}")
                empty_fig = px.scatter(title=f"Error: Missing {col} column")
                empty_summary = html.Div(f"Data error: Missing {col}", style={'text-align': 'center', 'color': '#e74c3c'})
                return empty_fig, empty_summary
        
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
            empty_summary = html.Div("Try adjusting your filters to see more properties", 
                                   style={'text-align': 'center', 'color': '#e67e22'})
            return empty_fig, empty_summary
        
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
        
        # Ensure all plotting columns are valid
        required_plot_cols = ['square_meters', 'price', 'price_per_sqm', 'rooms']
        for col in required_plot_cols:
            plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce')
            if plot_df[col].isna().any():
                print(f"⚠️  Found NaN values in {col}, using median fill")
                plot_df[col] = plot_df[col].fillna(plot_df[col].median())
        
        # Create scatter plot
        fig = px.scatter(
            plot_df, 
            x='square_meters', 
            y='price',
            color='price_per_sqm',
            size='rooms',
            size_max=15,
            color_continuous_scale='viridis',
            hover_data=['neighborhood', 'rooms', 'condition_text', 'ad_type'],
            labels={'square_meters': 'Square Meters', 
                   'price': 'Price (₪)', 
                   'price_per_sqm': 'Price per sqm (₪)'},
            title=f'Real Estate Prices by Size ({len(plot_df)} properties)'
        )
        
        # Create custom data array for hover and click functionality
        # Prepare street display - combine street with neighborhood for better context
        street_display = plot_df.apply(lambda row: 
            f"{row['street']}" if pd.notna(row['street']) and row['street'].strip() != '' 
            else f"{row['neighborhood']}", axis=1)
        
        custom_data = np.column_stack((
            plot_df['neighborhood'].fillna('Unknown'),
            plot_df['rooms'],
            plot_df['condition_text'].fillna('Not specified'),
            plot_df['ad_type'],
            street_display,
            plot_df['floor'].fillna('Not specified'),
            plot_df['full_url'].fillna('')
        ))
        
        # Update traces for better interactivity
        fig.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            customdata=custom_data,
            hovertemplate='<b>🏡 %{customdata[0]}</b><br>' +
                          '<i>📍 %{customdata[4]}</i><br>' +
                          '<br>' +
                          '<b>Price:</b> ₪%{y:,.0f}<br>' +
                          '<b>Size:</b> %{x} sqm<br>' +
                          '<b>Price/sqm:</b> ₪%{marker.color:,.0f}<br>' +
                          '<b>Rooms:</b> %{customdata[1]}<br>' +
                          '<b>Condition:</b> %{customdata[2]}<br>' +
                          '<b>Floor:</b> %{customdata[5]}<br>' +
                          '<br>' +
                          '<b>👆 Click to view listing</b>' +
                          '<extra></extra>'
        )
        
        # Configure layout
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
            coloraxis_colorbar=dict(
                title="₪/sqm",
                title_font=dict(size=13),
                tickfont=dict(size=11)
            ),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
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
        summary = html.Div([
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
        ], style=summary_style['container'], className="fade-in")
        
        return fig, summary
    
    # Run the app
    print(f"Starting dashboard on http://127.0.0.1:{port}/")
    app.run(debug=True, port=port)

def main():
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Start with empty data - users must scrape from UI
    print("Starting with empty dataset. Use the search controls to scrape data.")
    df = create_empty_dataframe()
    
    print(f"Loaded {len(df)} valid properties for analysis")
    
    # Create and run the dashboard
    create_dashboard(df, args.port)


if __name__ == "__main__":
    main() 