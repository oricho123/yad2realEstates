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
        'fontFamily': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '20px',
        'background': f'linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%)',
        'minHeight': '100vh'
    }

    CONTENT_WRAPPER = {
        'backgroundColor': 'rgba(255, 255, 255, 0.95)',
        'borderRadius': '20px',
        'padding': '30px',
        'boxShadow': '0 20px 40px rgba(0,0,0,0.1)',
        'backdropFilter': 'blur(10px)'
    }

    # Header styles
    HEADER = {
        'background': f'linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%)',
        'color': 'white',
        'padding': '25px',
        'margin': '-30px -30px 30px -30px',
        'borderRadius': '20px 20px 0 0',
        'textAlign': 'center',
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
        'zIndex': '1'
    }

    HEADER_CONTENT = {
        'position': 'relative',
        'zIndex': '2'
    }

    # Filter container styles
    FILTER_CONTAINER = {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
        'gap': '20px',
        'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
        'marginBottom': '25px',
        'backdropFilter': 'blur(10px)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }

    FILTER = {
        'background': 'rgba(255,255,255,0.9)',
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.08)',
        'border': '1px solid rgba(255,255,255,0.3)',
        'transition': 'all 0.3s ease'
    }

    LABEL = {
        'fontWeight': '600',
        'marginBottom': '10px',
        'color': '#2c3e50',
        'fontSize': '14px',
        'display': 'flex',
        'alignItems': 'center',
        'gap': '8px'
    }

    # Visualization styles
    DUAL_VIEW_CONTAINER = {
        'display': 'grid',
        'gridTemplateColumns': '1fr 1fr',
        'gap': '25px',
        'marginBottom': '25px'
    }

    GRAPH = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }

    MAP_CONTAINER = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }

    # Summary styles
    SUMMARY = {
        'background': 'rgba(255,255,255,0.95)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
        'border': '1px solid rgba(255,255,255,0.2)'
    }

    SUMMARY_HEADER = {
        'color': '#2c3e50',
        'borderBottom': f'3px solid {PRIMARY_COLOR}',
        'paddingBottom': '15px',
        'marginBottom': '20px',
        'fontWeight': '600'
    }

    # Search container styles
    SEARCH_CONTAINER = {
        'background': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
        'marginBottom': '25px',
        'border': '1px solid rgba(255,255,255,0.3)'
    }

    SEARCH_HEADER = {
        'color': '#155724',
        'fontWeight': '700',
        'fontSize': '20px',
        'marginBottom': '20px',
        'textAlign': 'center',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'gap': '10px'
    }

    SEARCH_CONTROLS = {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
        'gap': '20px',
        'alignItems': 'end'
    }

    SEARCH_FILTER = {
        'background': 'rgba(255,255,255,0.9)',
        'padding': '15px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.08)'
    }

    # Button styles
    SCRAPE_BUTTON = {
        'background': f'linear-gradient(135deg, {SUCCESS_COLOR} 0%, #20c997 100%)',
        'color': 'white',
        'border': 'none',
        'padding': '15px 25px',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'fontWeight': '600',
        'fontSize': '14px',
        'minWidth': '180px',
        'height': '50px',
        'transition': 'all 0.3s ease',
        'boxShadow': '0 4px 15px rgba(40, 167, 69, 0.3)',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
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
        'alignItems': 'center',
        'justifyContent': 'center',
        'zIndex': '9999',
        'backdropFilter': 'blur(5px)'
    }

    LOADING_CONTENT = {
        'background': 'white',
        'padding': '40px',
        'borderRadius': '20px',
        'textAlign': 'center',
        'boxShadow': '0 20px 40px rgba(0,0,0,0.3)',
        'maxWidth': '400px',
        'margin': '20px'
    }

    SPINNER = {
        'width': '60px',
        'height': '60px',
        'border': '6px solid #f3f3f3',
        'borderTop': f'6px solid {PRIMARY_COLOR}',
        'borderRadius': '50%',
        'animation': 'spin 1s linear infinite',
        'margin': '0 auto 20px auto'
    }

    LOADING_TEXT = {
        'color': PRIMARY_COLOR,
        'fontWeight': '600',
        'fontSize': '18px',
        'marginBottom': '10px'
    }

    LOADING_SUBTITLE = {
        'color': '#6c757d',
        'fontSize': '14px',
        'lineHeight': '1.5'
    }

    # Click instruction
    CLICK_INSTRUCTION = {
        'textAlign': 'center',
        'fontStyle': 'italic',
        'color': PRIMARY_COLOR,
        'margin': '15px 0',
        'padding': '15px',
        'background': 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
        'borderRadius': '12px',
        'borderLeft': f'4px solid {PRIMARY_COLOR}',
        'fontWeight': '500'
    }


class SummaryStyles:
    """Styles for summary statistics cards."""

    CONTAINER = {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))',
        'gap': '20px'
    }

    CARD = {
        'padding': '20px',
        'borderRadius': '12px',
        'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.08)',
        'textAlign': 'center',
        'border': '1px solid rgba(255,255,255,0.3)',
        'transition': 'all 0.3s ease'
    }

    VALUE = {
        'fontSize': '24px',
        'fontWeight': '700',
        'color': DashboardStyles.PRIMARY_COLOR,
        'margin': '10px 0',
        'textShadow': '0 1px 3px rgba(0,0,0,0.1)'
    }

    LABEL = {
        'fontSize': '14px',
        'color': '#495057',
        'margin': '0',
        'fontWeight': '500',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'gap': '6px'
    }

    ICON = {
        'color': DashboardStyles.PRIMARY_COLOR,
        'fontSize': '16px'
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
    

    
    .button-hover:hover {
        transform: translateY(-2px);
        boxShadow: 0 8px 25px rgba(40, 167, 69, 0.4) !important;
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
    @media (maxWidth: 1200px) {
        .dual-view-responsive {
            gridTemplateColumns: 1fr !important;
        }
    }
    
    /* Responsive design for analytics */
    @media (maxWidth: 900px) {
        .analytics-grid {
            gridTemplateColumns: 1fr !important;
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
