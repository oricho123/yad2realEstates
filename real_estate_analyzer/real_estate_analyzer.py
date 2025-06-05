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
    parser.add_argument('--city', type=int, default=9500,
                        help='City ID to scrape')
    parser.add_argument('--area', type=int, default=6,
                        help='Area ID to scrape')
    parser.add_argument('--top-area', type=int, default=25,
                        help='Top area ID to scrape')
    parser.add_argument('--min-price', type=int, default=1350000,
                        help='Minimum price filter')
    parser.add_argument('--max-price', type=int, default=1420000,
                        help='Maximum price filter')
    parser.add_argument('--skip-scrape', action='store_true',
                        help='Skip scraping and use existing data')
    parser.add_argument('--port', type=int, default=8051,
                        help='Port to run the web server on')
    return parser.parse_args()

def scrape_data(output_dir, city, area, top_area, min_price, max_price):
    """Run the scraper to collect real estate data"""
    print(f"Scraping data for city={city}, area={area}, price range={min_price}-{max_price}...")
    scraper = RealEstateScraper(output_dir)
    csv_path, json_path = scraper.scrape_and_save(
        city=city, 
        area=area, 
        top_area=top_area,
        min_price=min_price, 
        max_price=max_price
    )
    return csv_path

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
        sys.exit(1)

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
                        options=[{'label': 'Any', 'value': None}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6]
                        ],
                        value=None,
                        clearable=True,
                        placeholder="Min rooms"
                    ),
                ], style=styles['search_filter']),
                
                html.Div([
                    html.Label("Max Rooms:", style=styles['label']),
                    dcc.Dropdown(
                        id='search-max-rooms',
                        options=[{'label': 'Any', 'value': None}] + [
                            {'label': f'{i}', 'value': i} for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8]
                        ],
                        value=None,
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
                    min=df['price'].min(),
                    max=df['price'].max(),
                    value=[df['price'].min(), df['price'].max()],
                    marks={
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
                    min=df['square_meters'].min(),
                    max=df['square_meters'].max(),
                    value=[df['square_meters'].min(), df['square_meters'].max()],
                    marks={
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
            if min_rooms or max_rooms:
                room_range = ""
                if min_rooms: room_range += f"{min_rooms}+"
                if max_rooms: 
                    if min_rooms: room_range = f"{min_rooms}-{max_rooms}"
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
            if min_rooms:
                api_params['min_rooms'] = min_rooms
            if max_rooms:
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
                    html.Span(f"Found {len(new_df)} new properties. Dashboard updated!")
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
         Output('rooms-filter', 'options')],
        [Input('current-dataset', 'data')]
    )
    def update_filter_ranges(current_data):
        # Convert current data back to DataFrame
        current_df = pd.DataFrame(current_data)
        
        if len(current_df) == 0:
            # Return default values if no data
            return 0, 1000000, [0, 1000000], {}, 0, 100, [0, 100], {}, [], []
        
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
        
        print(f"🔄 Updated filters - Price: ₪{price_min:,.0f}-₪{price_max:,.0f}, Size: {sqm_min:.0f}-{sqm_max:.0f}sqm")
        
        return (
            price_min, price_max, [price_min, price_max], price_marks,
            sqm_min, sqm_max, [sqm_min, sqm_max], sqm_marks,
            neighborhoods, rooms_options
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
        print(f"🔍 Filter ranges - Price: {price_range}, Size: {sqm_range}")
        
        if len(current_df) == 0:
            # Return empty plot if no data
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
        if price_range and len(price_range) == 2:
            price_min, price_max = price_range
            filtered_df = filtered_df[
                (filtered_df['price'] >= price_min) & 
                (filtered_df['price'] <= price_max)
            ]
            print(f"📈 After price filter ({price_min:,.0f}-{price_max:,.0f}): {len(filtered_df)} rows")
        
        # Apply sqm filter if sqm_range is provided and valid
        if sqm_range and len(sqm_range) == 2:
            sqm_min, sqm_max = sqm_range
            filtered_df = filtered_df[
                (filtered_df['square_meters'] >= sqm_min) & 
                (filtered_df['square_meters'] <= sqm_max)
            ]
            print(f"📈 After size filter ({sqm_min:.0f}-{sqm_max:.0f}sqm): {len(filtered_df)} rows")
        
        # Apply other filters only if the values exist in the data
        if neighborhood and neighborhood != 'all' and 'neighborhood' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['neighborhood'] == neighborhood]
            print(f"📈 After neighborhood filter ({neighborhood}): {len(filtered_df)} rows")
            
        if rooms and rooms != 'all' and 'rooms' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['rooms'] == rooms]
            print(f"📈 After rooms filter ({rooms}): {len(filtered_df)} rows")
            
        if condition and condition != 'all' and 'condition_text' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['condition_text'] == condition]
            print(f"📈 After condition filter ({condition}): {len(filtered_df)} rows")
            
        if ad_type and ad_type != 'all' and 'ad_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ad_type'] == ad_type]
            print(f"📈 After ad_type filter ({ad_type}): {len(filtered_df)} rows")
        
        print(f"📈 Final filtered data: {len(filtered_df)} rows")
        
        # If no data after filtering, show message
        if len(filtered_df) == 0:
            empty_fig = px.scatter(title="No properties match current filters")
            empty_summary = html.Div("Try adjusting your filters to see more properties", 
                                   style={'text-align': 'center', 'color': '#e67e22'})
            return empty_fig, empty_summary
        
        # Create scatter plot
        fig = px.scatter(
            filtered_df, 
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
            title=f'Real Estate Prices by Size ({len(filtered_df)} properties)'
        )
        
        # Create custom data array for hover and click functionality
        custom_data = np.column_stack((
            filtered_df['neighborhood'].fillna(''),
            filtered_df['rooms'],
            filtered_df['condition_text'].fillna(''),
            filtered_df['ad_type'],
            filtered_df['street'].fillna(''),
            filtered_df['floor'].fillna(''),
            filtered_df['full_url'].fillna('')
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
                html.P(f"{len(filtered_df)}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Price", style=summary_style['label']),
                html.P(f"₪{filtered_df['price'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Avg Price/sqm", style=summary_style['label']),
                html.P(f"₪{filtered_df['price_per_sqm'].mean():,.0f}", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Size", style=summary_style['label']),
                html.P(f"{filtered_df['square_meters'].mean():,.0f} sqm", style=summary_style['value'])
            ], style=summary_style['card']),
            
            html.Div([
                html.P("Average Rooms", style=summary_style['label']),
                html.P(f"{filtered_df['rooms'].mean():.1f}", style=summary_style['value'])
            ], style=summary_style['card']),
        ], style=summary_style['container'])
        
        return fig, summary
    
    # Run the app
    print(f"Starting dashboard on http://127.0.0.1:{port}/")
    app.run(debug=False, port=port)

def main():
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Scrape the data if not skipped
    if not args.skip_scrape:
        csv_path = scrape_data(args.output_dir, args.city, args.area, args.top_area, args.min_price, args.max_price)
    else:
        # Find the most recent CSV file
        csv_files = list(output_dir.glob("real_estate_listings_*.csv"))
        if not csv_files:
            print("No existing CSV files found. Please run without --skip-scrape first.")
            sys.exit(1)
        csv_path = str(sorted(csv_files)[-1])
        print(f"Using existing data: {csv_path}")
    
    # Step 2: Load the data
    df = load_data(csv_path)
    
    print(f"Loaded {len(df)} valid properties for analysis")
    
    # Step 3: Create and run the dashboard
    create_dashboard(df, args.port)


if __name__ == "__main__":
    main() 