"""Dashboard styling configuration and CSS definitions."""
from typing import Dict, Any


class DashboardStyles:
    """Main dashboard styling classes."""
    
    # Color palette
    PRIMARY_COLOR = '#667eea'
    SECONDARY_COLOR = '#764ba2'
    SUCCESS_COLOR = '#28a745'
    WARNING_COLOR = '#ffc107'
    DANGER_COLOR = '#dc3545'
    INFO_COLOR = '#17a2b8'
    
    # Base container styles
    CONTAINER = {
        'font-family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        'max-width': '1400px',
        'margin': '0 auto',
        'padding': '20px',
        'background': f'linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%)',
        'min-height': '100vh'
    }
    
    CONTENT_WRAPPER = {
        'background-color': 'rgba(255, 255, 255, 0.95)',
        'border-radius': '20px',
        'padding': '30px',
        'box-shadow': '0 20px 40px rgba(0,0,0,0.1)',
        'backdrop-filter': 'blur(10px)'
    }
    
    # Header styles
    HEADER = {
        'background': f'linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%)',
        'color': 'white',
        'padding': '25px',
        'margin': '-30px -30px 30px -30px',
        'border-radius': '20px 20px 0 0',
        'text-align': 'center',
        'position': 'relative',
        'overflow': 'hidden'
    }
    
    HEADER_OVERLAY = {
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0',
        'background': 'rgba(255,255,255,0.1)',
        'z-index': '1'
    }
    
    HEADER_CONTENT = {
        'position': 'relative',
        'z-index': '2'
    }
    
    # Filter container styles
    FILTER_CONTAINER = {
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
    }
    
    FILTER = {
        'background': 'rgba(255,255,255,0.9)',
        'padding': '20px',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0,0,0,0.08)',
        'border': '1px solid rgba(255,255,255,0.3)',
        'transition': 'all 0.3s ease'
    }
    
    LABEL = {
        'font-weight': '600',
        'margin-bottom': '10px',
        'color': '#2c3e50',
        'font-size': '14px',
        'display': 'flex',
        'align-items': 'center',
        'gap': '8px'
    }
    
    # Visualization styles
    DUAL_VIEW_CONTAINER = {
        'display': 'grid',
        'grid-template-columns': '1fr 1fr',
        'gap': '25px',
        'margin-bottom': '25px'
    }
    
    GRAPH = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'border-radius': '15px',
        'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }
    
    MAP_CONTAINER = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'border-radius': '15px',
        'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }
    
    # Summary styles
    SUMMARY = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'border-radius': '15px',
        'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }
    
    SUMMARY_HEADER = {
        'color': '#2c3e50',
        'border-bottom': f'3px solid {PRIMARY_COLOR}',
        'padding-bottom': '15px',
        'margin-bottom': '20px',
        'font-weight': '600'
    }
    
    # Search container styles
    SEARCH_CONTAINER = {
        'background': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
        'padding': '25px',
        'border-radius': '15px',
        'box-shadow': '0 8px 32px rgba(0,0,0,0.1)',
        'margin-bottom': '25px',
        'border': '1px solid rgba(255,255,255,0.3)'
    }
    
    SEARCH_HEADER = {
        'color': '#155724',
        'font-weight': '700',
        'font-size': '20px',
        'margin-bottom': '20px',
        'text-align': 'center',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
        'gap': '10px'
    }
    
    SEARCH_CONTROLS = {
        'display': 'grid',
        'grid-template-columns': 'repeat(auto-fit, minmax(200px, 1fr))',
        'gap': '20px',
        'align-items': 'end'
    }
    
    SEARCH_FILTER = {
        'background': 'rgba(255,255,255,0.9)',
        'padding': '15px',
        'border-radius': '10px',
        'box-shadow': '0 4px 15px rgba(0,0,0,0.08)'
    }
    
    # Button styles
    SCRAPE_BUTTON = {
        'background': f'linear-gradient(135deg, {SUCCESS_COLOR} 0%, #20c997 100%)',
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
    }
    
    # Loading styles
    LOADING_OVERLAY = {
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
    }
    
    LOADING_CONTENT = {
        'background': 'white',
        'padding': '40px',
        'border-radius': '20px',
        'text-align': 'center',
        'box-shadow': '0 20px 40px rgba(0,0,0,0.3)',
        'max-width': '400px',
        'margin': '20px'
    }
    
    SPINNER = {
        'width': '60px',
        'height': '60px',
        'border': '6px solid #f3f3f3',
        'border-top': f'6px solid {PRIMARY_COLOR}',
        'border-radius': '50%',
        'animation': 'spin 1s linear infinite',
        'margin': '0 auto 20px auto'
    }
    
    LOADING_TEXT = {
        'color': PRIMARY_COLOR,
        'font-weight': '600',
        'font-size': '18px',
        'margin-bottom': '10px'
    }
    
    LOADING_SUBTITLE = {
        'color': '#6c757d',
        'font-size': '14px',
        'line-height': '1.5'
    }
    
    # Click instruction
    CLICK_INSTRUCTION = {
        'text-align': 'center',
        'font-style': 'italic',
        'color': PRIMARY_COLOR,
        'margin': '15px 0',
        'padding': '15px',
        'background': f'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
        'border-radius': '12px',
        'border-left': f'4px solid {PRIMARY_COLOR}',
        'font-weight': '500'
    }


class SummaryStyles:
    """Styles for summary statistics cards."""
    
    CONTAINER = {
        'display': 'grid',
        'grid-template-columns': 'repeat(auto-fit, minmax(220px, 1fr))',
        'gap': '20px'
    }
    
    CARD = {
        'padding': '20px',
        'border-radius': '12px',
        'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
        'box-shadow': '0 4px 15px rgba(0,0,0,0.08)',
        'text-align': 'center',
        'border': '1px solid rgba(255,255,255,0.3)',
        'transition': 'all 0.3s ease'
    }
    
    VALUE = {
        'font-size': '24px',
        'font-weight': '700',
        'color': DashboardStyles.PRIMARY_COLOR,
        'margin': '10px 0',
        'text-shadow': '0 1px 3px rgba(0,0,0,0.1)'
    }
    
    LABEL = {
        'font-size': '14px',
        'color': '#495057',
        'margin': '0',
        'font-weight': '500',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
        'gap': '6px'
    }
    
    ICON = {
        'color': DashboardStyles.PRIMARY_COLOR,
        'font-size': '16px'
    }


class CustomCSS:
    """Custom CSS for animations and responsive design."""
    
    CSS_STRING = """
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
    """
    
    @classmethod
    def get_dash_index_string(cls) -> str:
        """Get the complete HTML index string for Dash app."""
        return f'''
        <!DOCTYPE html>
        <html>
            <head>
                {{%metas%}}
                <title>{{%title%}}</title>
                {{%favicon%}}
                {{%css%}}
                <style>
                    {cls.CSS_STRING}
                </style>
            </head>
            <body>
                {{%app_entry%}}
                <footer>
                    {{%config%}}
                    {{%scripts%}}
                    {{%renderer%}}
                </footer>
            </body>
        </html>
        '''


class StyleUtils:
    """Utility functions for style management."""
    
    @staticmethod
    def get_all_styles() -> Dict[str, Any]:
        """Get all styles as a dictionary for easy access."""
        return {
            'container': DashboardStyles.CONTAINER,
            'content_wrapper': DashboardStyles.CONTENT_WRAPPER,
            'header': DashboardStyles.HEADER,
            'header_overlay': DashboardStyles.HEADER_OVERLAY,
            'header_content': DashboardStyles.HEADER_CONTENT,
            'filter_container': DashboardStyles.FILTER_CONTAINER,
            'filter': DashboardStyles.FILTER,
            'label': DashboardStyles.LABEL,
            'dual_view_container': DashboardStyles.DUAL_VIEW_CONTAINER,
            'graph': DashboardStyles.GRAPH,
            'map_container': DashboardStyles.MAP_CONTAINER,
            'summary': DashboardStyles.SUMMARY,
            'summary_header': DashboardStyles.SUMMARY_HEADER,
            'search_container': DashboardStyles.SEARCH_CONTAINER,
            'search_header': DashboardStyles.SEARCH_HEADER,
            'search_controls': DashboardStyles.SEARCH_CONTROLS,
            'search_filter': DashboardStyles.SEARCH_FILTER,
            'scrape_button': DashboardStyles.SCRAPE_BUTTON,
            'loading_overlay': DashboardStyles.LOADING_OVERLAY,
            'loading_content': DashboardStyles.LOADING_CONTENT,
            'spinner': DashboardStyles.SPINNER,
            'loading_text': DashboardStyles.LOADING_TEXT,
            'loading_subtitle': DashboardStyles.LOADING_SUBTITLE,
            'click_instruction': DashboardStyles.CLICK_INSTRUCTION
        }
    
    @staticmethod
    def merge_styles(base_style: Dict[str, Any], override_style: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two style dictionaries."""
        merged = base_style.copy()
        merged.update(override_style)
        return merged 