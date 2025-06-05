"""Interaction callback handlers for the dashboard."""

import dash
from dash import clientside_callback, Output, Input
from src.visualization.charts.scatter_plot import HoverDataFields, MapHoverDataFields


class InteractionCallbackManager:
    """Manages all user interaction callbacks like clicks and navigation."""

    def __init__(self, app: dash.Dash):
        """
        Initialize the interaction callback manager.

        Args:
            app: Dash application instance
        """
        self.app = app

    def register_all_callbacks(self) -> None:
        """Register all interaction callbacks."""
        self._register_click_callbacks()

    def _register_click_callbacks(self) -> None:
        """Register client-side callbacks to handle clicks on charts."""

        # Scatter plot click handler
        clientside_callback(
            f"""
            function(clickData) {{
                if(clickData && clickData.points && clickData.points.length > 0) {{
                    const link = clickData.points[0].customdata[{HoverDataFields.FULL_URL}];
                    if(link && link.length > 0 && link !== '') {{
                        window.open(link, '_blank');
                    }}
                }}
                return window.dash_clientside.no_update;
            }}
            """,
            Output('clicked-link', 'data'),
            Input('price-sqm-scatter', 'clickData'),
            prevent_initial_call=True
        )

        # Map click handler
        clientside_callback(
            f"""
            function(clickData) {{
                if(clickData && clickData.points && clickData.points.length > 0) {{
                    const link = clickData.points[0].customdata[{MapHoverDataFields.FULL_URL}];
                    if(link && link.length > 0 && link !== '') {{
                        window.open(link, '_blank');
                    }}
                }}
                return window.dash_clientside.no_update;
            }}
            """,
            Output('clicked-map-link', 'data'),
            Input('property-map', 'clickData'),
            prevent_initial_call=True
        )
