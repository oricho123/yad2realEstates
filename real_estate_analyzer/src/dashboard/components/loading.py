"""Loading components and states management for the dashboard."""

from dash import html, dcc
from typing import Any

from src.config.styles import DashboardStyles


class LoadingComponentManager:
    """Manages loading components and states throughout the dashboard."""
    
    def __init__(self):
        """Initialize the loading component manager."""
        pass
        
    def create_loading_component(self, component_id: str, children: Any, loading_text: str = "Loading") -> dcc.Loading:
        """
        Create a loading component with consistent styling.
        
        Args:
            component_id: Unique identifier for the component
            children: The component(s) to wrap with loading
            loading_text: Text to display while loading
            
        Returns:
            Configured loading component
        """
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
                html.Div(className="spinner", style=DashboardStyles.SPINNER),
                html.Div(loading_text, style=DashboardStyles.LOADING_TEXT),
                html.Div("Please wait while we process your request...", style=DashboardStyles.LOADING_SUBTITLE)
            ], style={'text-align': 'center'})
        )
        
    def create_global_loading_overlay(self) -> html.Div:
        """
        Create a global loading overlay for full-screen loading states.
        
        Returns:
            Global loading overlay component
        """
        return html.Div(
            id='global-loading-overlay',
            children=[
                html.Div([
                    html.Div(style=DashboardStyles.SPINNER),
                    html.Div("Processing your request", 
                            style=DashboardStyles.LOADING_TEXT, 
                            className="loading-dots"),
                    html.Div("This may take a few moments...", 
                            style=DashboardStyles.LOADING_SUBTITLE)
                ], style=DashboardStyles.LOADING_CONTENT)
            ],
            style={**DashboardStyles.LOADING_OVERLAY, 'display': 'none'},
            className="fade-in"
        ) 