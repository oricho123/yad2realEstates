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
    
    # Create a custom stylesheet
    external_stylesheets = [
        {
            'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap',
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
    
    # Define CSS styles (similar to vehicle analyzer)
    styles = {
        'container': {
            'font-family': 'Roboto, sans-serif',
            'max-width': '1200px',
            'margin': '0 auto',
            'padding': '20px',
            'background-color': '#f9f9f9',
            'border-radius': '8px',
            'box-shadow': '0 4px 8px rgba(0,0,0,0.1)'
        },
        'header': {
            'background-color': '#2c3e50',
            'color': 'white',
            'padding': '15px 20px',
            'margin-bottom': '20px',
            'border-radius': '5px',
            'text-align': 'center'
        },
        'filter_container': {
            'display': 'flex',
            'flex-wrap': 'wrap',
            'gap': '15px',
            'background-color': 'white',
            'padding': '15px',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'margin-bottom': '20px'
        },
        'filter': {
            'width': '23%',
            'min-width': '200px',
            'padding': '10px'
        },
        'label': {
            'font-weight': 'bold',
            'margin-bottom': '5px',
            'color': '#2c3e50'
        },
        'graph': {
            'background-color': 'white',
            'padding': '15px',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'margin-bottom': '20px'
        },
        'summary': {
            'background-color': 'white',
            'padding': '15px',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)'
        },
        'summary_header': {
            'color': '#2c3e50',
            'border-bottom': '2px solid #3498db',
            'padding-bottom': '10px',
            'margin-bottom': '15px'
        },
        'click_instruction': {
            'text-align': 'center',
            'font-style': 'italic',
            'color': '#3498db',
            'margin': '10px 0',
            'padding': '8px',
            'background-color': '#f0f7ff',
            'border-radius': '5px',
            'border-left': '3px solid #3498db'
        },
        'search_container': {
            'background-color': '#e8f5e8',
            'padding': '20px',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'margin-bottom': '20px',
            'border-left': '4px solid #27ae60'
        },
        'search_header': {
            'color': '#27ae60',
            'font-weight': 'bold',
            'font-size': '18px',
            'margin-bottom': '15px',
            'text-align': 'center'
        },
        'search_controls': {
            'display': 'flex',
            'flex-wrap': 'wrap',
            'gap': '15px',
            'align-items': 'end'
        },
        'search_filter': {
            'width': '20%',
            'min-width': '150px',
            'padding': '5px'
        },
        'scrape_button': {
            'background-color': '#27ae60',
            'color': 'white',
            'border': 'none',
            'padding': '12px 24px',
            'border-radius': '5px',
            'cursor': 'pointer',
            'font-weight': 'bold',
            'font-size': '14px',
            'min-width': '150px',
            'height': '40px'
        },
        'loading_text': {
            'color': '#e67e22',
            'font-weight': 'bold',
            'text-align': 'center',
            'padding': '10px',
            'background-color': '#fef9e7',
            'border-radius': '5px',
            'border-left': '3px solid #e67e22'
        }
    }
    
    # Create the app layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("🏠 Real Estate Price Analysis Dashboard", style={'margin': '0'})
        ], style=styles['header']),
        
        # Search Controls Section
        html.Div([
            html.Div("🔍 Search New Properties", style=styles['search_header']),
            html.Div([
                html.Div([
                    html.Label("City:", style=styles['label']),
                    dcc.Dropdown(
                        id='search-city-dropdown',
                        options=city_options,
                        value=9500,
                        clearable=False
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Area ID (Optional):", style=styles['label']),
                    dcc.Input(
                        id='search-area',
                        type='number',
                        value=6,
                        placeholder="Area ID",
                        style={'width': '100%', 'padding': '8px', 'border-radius': '4px', 'border': '1px solid #ddd'}
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Min Price (₪):", style=styles['label']),
                    dcc.Input(
                        id='search-min-price',
                        type='number',
                        value=1000000,
                        step=50000,
                        style={'width': '100%', 'padding': '8px', 'border-radius': '4px', 'border': '1px solid #ddd'}
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Max Price (₪):", style=styles['label']),
                    dcc.Input(
                        id='search-max-price',
                        type='number',
                        value=2000000,
                        step=50000,
                        style={'width': '100%', 'padding': '8px', 'border-radius': '4px', 'border': '1px solid #ddd'}
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Min Rooms:", style=styles['label']),
                    dcc.Dropdown(
                        id='search-min-rooms',
                        options=[{'label': 'Any', 'value': 'any'}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6]
                        ],
                        value='any',
                        clearable=True,
                        placeholder="Min rooms"
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Max Rooms:", style=styles['label']),
                    dcc.Dropdown(
                        id='search-max-rooms',
                        options=[{'label': 'Any', 'value': 'any'}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8]
                        ],
                        value='any',
                        clearable=True,
                        placeholder="Max rooms"
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Min sqm:", style=styles['label']),
                    dcc.Input(
                        id='search-min-sqm',
                        type='number',
                        value=None,
                        placeholder="Min sqm",
                        style={'width': '100%', 'padding': '8px', 'border-radius': '4px', 'border': '1px solid #ddd'}
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Max sqm:", style=styles['label']),
                    dcc.Input(
                        id='search-max-sqm',
                        type='number',
                        value=None,
                        placeholder="Max sqm",
                        style={'width': '100%', 'padding': '8px', 'border-radius': '4px', 'border': '1px solid #ddd'}
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Action:", style=styles['label']),
                    html.Button(
                        "🔍 Scrape New Data", 
                        id='scrape-button', 
                        style=styles['scrape_button'],
                        n_clicks=0
                    ),
                ], style=styles['search_filter']),
            ], style=styles['search_controls']),
            
            # Loading/Status message
            html.Div(id='scrape-status', style={'margin-top': '10px'}),
        ], style=styles['search_container']),
        
        # Current Data Filter section
        html.Div([
            html.Div([
                html.Label("Price Range (₪):", style=styles['label']),
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
                ),
            ], style=styles['filter']),
            
            html.Div([
                html.Label("Square Meters:", style=styles['label']),
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
                ),
            ], style=styles['filter']),
            
            html.Div([
                html.Label("Neighborhood:", style=styles['label']),
                dcc.Dropdown(
                    id='neighborhood-filter',
                    options=neighborhoods,
                    value='all',
                    clearable=False
                ),
            ], style=styles['filter']),
            
            html.Div([
                html.Label("Room Count:", style=styles['label']),
                dcc.Dropdown(
                    id='rooms-filter',
                    options=[{'label': 'All', 'value': 'all'}] + [
                        {'label': f"{r} rooms", 'value': r} 
                        for r in sorted(df['rooms'].dropna().unique())
                    ],
                    value='all',
                    clearable=False
                ),
            ], style=styles['filter']),
            
            html.Div([
                html.Label("Property Condition:", style=styles['label']),
                dcc.Dropdown(
                    id='condition-filter',
                    options=conditions,
                    value='all',
                    clearable=False
                ),
            ], style=styles['filter']),
            
            html.Div([
                html.Label("Ad Type:", style=styles['label']),
                dcc.Dropdown(
                    id='ad-type-filter',
                    options=ad_types,
                    value='all',
                    clearable=False
                ),
            ], style=styles['filter']),
            
        ], style=styles['filter_container']),
        
        # Click instruction
        html.Div([
            html.P("👆 Click on any point in the graph to open the property listing in a new tab")
        ], style=styles['click_instruction']),
        
        # Graph section
        html.Div([
            dcc.Graph(id='price-sqm-scatter')
        ], style=styles['graph']),
        
        # Summary section
        html.Div([
            html.H3("Data Summary", style=styles['summary_header']),
            html.Div(id='summary-stats')
        ], style=styles['summary']),
        
        # Store for clicked links
        dcc.Store(id='clicked-link', storage_type='memory'),
        
        # Store for current dataset
        dcc.Store(id='current-dataset', data=df.to_dict('records'), storage_type='session'),
    ], style=styles['container'])
    
    # Callback for scraping new data
    @app.callback(
        [Output('current-dataset', 'data'),
         Output('scrape-status', 'children'),
         Output('scrape-button', 'disabled')],
        [Input('scrape-button', 'n_clicks')],
        [State('search-city-dropdown', 'value'),
         State('search-area', 'value'),
         State('search-min-price', 'value'),
         State('search-max-price', 'value'),
         State('search-min-rooms', 'value'),
         State('search-max-rooms', 'value'),
         State('search-min-sqm', 'value'),
         State('search-max-sqm', 'value')],
        prevent_initial_call=True
    )
    def scrape_new_data(n_clicks, city, area, min_price, max_price, min_rooms, max_rooms, min_sqm, max_sqm):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
            
        try:
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
            
            # Show loading status
            loading_msg = html.Div([
                html.Span("🔄 Scraping new data... "),
                html.Span(search_desc)
            ], style=styles['loading_text'])
            
            # Delete old data files first
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
            
            # Create scraper instance
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
            
            # Scrape new data with user parameters
            csv_path, json_path = scraper.scrape_and_save(**api_params)
            
            if csv_path:
                # Load new data
                new_df = pd.read_csv(csv_path)
                
                # Filter and prepare data (same as load_data function)
                new_df = new_df[new_df['price'] > 0]
                new_df = new_df[new_df['square_meters'].notna() & (new_df['square_meters'] > 0)]
                new_df['price_per_sqm'] = new_df['price'] / new_df['square_meters']
                new_df['lat'] = pd.to_numeric(new_df['lat'], errors='coerce')
                new_df['lng'] = pd.to_numeric(new_df['lng'], errors='coerce')
                
                # Success message
                success_msg = html.Div([
                    html.Span("✅ Success! "),
                    html.Span(f"Found {len(new_df)} new properties. Dashboard updated! Old data cleared.")
                ], style={'color': '#27ae60', 'font-weight': 'bold', 'text-align': 'center', 
                         'padding': '10px', 'background-color': '#d5f4e6', 'border-radius': '5px'})
                
                return new_df.to_dict('records'), success_msg, False
            else:
                # Error message
                error_msg = html.Div([
                    html.Span("❌ Error: "),
                    html.Span("Failed to scrape data. Please try again.")
                ], style={'color': '#e74c3c', 'font-weight': 'bold', 'text-align': 'center',
                         'padding': '10px', 'background-color': '#fdf2f2', 'border-radius': '5px'})
                
                raise PreventUpdate
                
        except Exception as e:
            # Error message
            error_msg = html.Div([
                html.Span("❌ Error: "),
                html.Span(f"Scraping failed: {str(e)}")
            ], style={'color': '#e74c3c', 'font-weight': 'bold', 'text-align': 'center',
                     'padding': '10px', 'background-color': '#fdf2f2', 'border-radius': '5px'})
            
            return dash.no_update, error_msg, False
    
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
    
    # Callback to update filter ranges when new data is loaded
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
         Output('rooms-filter', 'options'),
         Output('rooms-filter', 'value'),
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
            # Return default values if no data
            return (0, 1000000, [0, 1000000], {}, 0, 100, [0, 100], {}, 
                   [], 'all', [], 'all', [], 'all', [], 'all')
        
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
        
        # Update neighborhood options
        neighborhoods = [{'label': 'All Neighborhoods', 'value': 'all'}] + [
            {'label': n, 'value': n} for n in sorted(current_df['neighborhood'].dropna().unique())
        ]
        
        # Update rooms options
        rooms_options = [{'label': 'All', 'value': 'all'}] + [
            {'label': f"{r} rooms", 'value': r} 
            for r in sorted(current_df['rooms'].dropna().unique())
        ]
        
        # Update condition options
        conditions = [{'label': 'All Conditions', 'value': 'all'}] + [
            {'label': ct, 'value': ct} for ct in sorted(current_df['condition_text'].dropna().unique())
        ]
        
        # Update ad_type options
        ad_types = [{'label': 'All', 'value': 'all'}] + [
            {'label': at, 'value': at} for at in sorted(current_df['ad_type'].unique())
        ]
        
        print(f"🔄 Updated filters - Price: ₪{price_min:,.0f}-₪{price_max:,.0f}, Size: {sqm_min:.0f}-{sqm_max:.0f}sqm")
        print(f"🔄 Neighborhoods: {len(neighborhoods)-1}, Rooms: {len(rooms_options)-1}, Conditions: {len(conditions)-1}, Ad Types: {len(ad_types)-1}")
        
        return (
            price_min, price_max, [price_min, price_max], price_marks,
            sqm_min, sqm_max, [sqm_min, sqm_max], sqm_marks,
            neighborhoods, 'all', rooms_options, 'all', conditions, 'all', ad_types, 'all'
        )
    
    @app.callback(
        [Output('price-sqm-scatter', 'figure'),
         Output('summary-stats', 'children')],
        [Input('price-range-slider', 'value'),
         Input('sqm-range-slider', 'value'),
         Input('neighborhood-filter', 'value'),
         Input('rooms-filter', 'value'),
         Input('condition-filter', 'value'),
         Input('ad-type-filter', 'value'),
         Input('current-dataset', 'data')]
    )
    def update_graph(price_range, sqm_range, neighborhood, rooms, condition, ad_type, current_data):
        # Convert current data back to DataFrame
        current_df = pd.DataFrame(current_data)
        
        # Debug info
        print(f"📊 Raw data loaded: {len(current_df)} rows")
        print(f"🔍 Filter values:")
        print(f"   - Price range: {price_range}")
        print(f"   - Size range: {sqm_range}")
        print(f"   - Neighborhood: '{neighborhood}' (type: {type(neighborhood)})")
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
            
        # Apply rooms filter
        if rooms is not None and rooms != 'all' and 'rooms' in filtered_df.columns:
            before_count = len(filtered_df)
            filtered_df = filtered_df[filtered_df['rooms'] == rooms]
            print(f"📈 Rooms filter ('{rooms}'): {before_count} → {len(filtered_df)} rows")
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
        custom_data = np.column_stack((
            plot_df['neighborhood'].fillna(''),
            plot_df['rooms'],
            plot_df['condition_text'].fillna(''),
            plot_df['ad_type'],
            plot_df['street'].fillna(''),
            plot_df['floor'].fillna(''),
            plot_df['full_url'].fillna('')
        ))
        
        # Update traces for better interactivity
        fig.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            customdata=custom_data,
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                          'Price: ₪%{y:,.0f}<br>' +
                          'Size: %{x} sqm<br>' +
                          'Price/sqm: ₪%{marker.color:,.0f}<br>' +
                          'Rooms: %{customdata[1]}<br>' +
                          'Condition: %{customdata[2]}<br>' +
                          'Floor: %{customdata[5]}<br>' +
                          '<b>👆 Click to view listing</b>'
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
        
        # Enhanced summary statistics
        summary_style = {
            'container': {
                'display': 'flex',
                'flex-wrap': 'wrap',
                'gap': '20px'
            },
            'card': {
                'flex': '1',
                'min-width': '180px',
                'padding': '15px',
                'border-radius': '5px',
                'background-color': '#f5f9ff',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
                'text-align': 'center'
            },
            'value': {
                'font-size': '20px',
                'font-weight': 'bold',
                'color': '#2c3e50',
                'margin': '10px 0'
            },
            'label': {
                'font-size': '14px',
                'color': '#7f8c8d',
                'margin': '0'
            }
        }
        
        # Create summary stats
        summary = html.Div([
            html.Div([
                html.P("Number of Properties", style=summary_style['label']),
                html.P(f"{len(plot_df)}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Price", style=summary_style['label']),
                html.P(f"₪{plot_df['price'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Avg Price/sqm", style=summary_style['label']),
                html.P(f"₪{plot_df['price_per_sqm'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Size", style=summary_style['label']),
                html.P(f"{plot_df['square_meters'].mean():,.0f} sqm", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Rooms", style=summary_style['label']),
                html.P(f"{plot_df['rooms'].mean():.1f}", style=summary_style['value'])
            ], style=summary_style['card']),
        ], style=summary_style['container'])
        
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