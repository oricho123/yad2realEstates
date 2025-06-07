"""Dashboard layout management for the Real Estate Analyzer."""

import pandas as pd
from dash import html, dcc
from typing import Dict, List, Any

from ..config.styles import DashboardStyles
from .components.filters import FilterComponentManager
from .components.search import SearchComponentManager
from .components.loading import LoadingComponentManager


class DashboardLayoutManager:
    """Manages the main dashboard layout and component structure."""

    def __init__(self, initial_data: pd.DataFrame):
        """
        Initialize layout manager with data.

        Args:
            initial_data: Initial property data to configure layout
        """
        self.data = initial_data
        self.filter_manager = FilterComponentManager(initial_data)
        self.search_manager = SearchComponentManager()
        self.loading_manager = LoadingComponentManager()
        # Note: storage_manager will be initialized in the app setup

    def create_main_layout(self) -> html.Div:
        """
        Create the complete dashboard layout.

        Returns:
            Main dashboard layout component
        """
        return html.Div([
            # Global loading overlay
            self._create_global_loading_overlay(),

            # Simple storage is handled via clientside callbacks - no initialization script needed

            # Main content wrapper
            html.Div([
                # Header section
                self._create_header(),

                # Search controls section
                self._create_search_section(),

                # Filter controls section
                self._create_filter_section(),

                # Main visualization section
                self._create_dual_view_section(),

                # Advanced analytics section
                self._create_analytics_section(),

                # Decision support section
                self._create_decision_support_section(),

                # Summary section
                self._create_summary_section(),

            ] + self._create_data_stores(), style=DashboardStyles.CONTENT_WRAPPER, className="container-responsive")

        ], style=DashboardStyles.CONTAINER, className="container-responsive")

    def _create_global_loading_overlay(self) -> html.Div:
        """Create the global loading overlay component."""
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

    def _create_header(self) -> html.Div:
        """Create the dashboard header section."""
        return html.Div([
            html.Div(style=DashboardStyles.HEADER_OVERLAY),
            html.Div([
                html.H1([
                    html.I(className="fas fa-home",
                           style={'marginRight': '15px'}),
                    "Real Estate Price Analysis Dashboard"
                ], style={'margin': '0', 'fontWeight': '700', 'fontSize': '28px'}),
                html.P("Discover market insights with interactive data visualization & geographic mapping",
                       style={'margin': '10px 0 0 0', 'opacity': '0.9', 'fontSize': '16px'})
            ], style=DashboardStyles.HEADER_CONTENT)
        ], style=DashboardStyles.HEADER, className="header-responsive")

    def _create_search_section(self) -> html.Div:
        """Create the search controls section."""
        return self.search_manager.create_search_section()

    def _create_filter_section(self) -> html.Div:
        """Create the filter controls section."""
        return self.filter_manager.create_filter_section()

    def _create_dual_view_section(self) -> html.Div:
        """Create the main dual-view visualization section."""
        return html.Div([
            # Scatter plot section
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-scatter",
                           style={'marginRight': '10px', 'color': '#667eea'}),
                    "Price vs Size Analysis"
                ], style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': '600', 'fontSize': '18px'}),

                # Value score explanation
                html.Div([
                    html.H6([
                        html.I(className="fas fa-info-circle",
                               style={'marginRight': '8px', 'color': '#17a2b8'}),
                        "Value Score Explanation"
                    ], style={'color': '#2c3e50', 'marginBottom': '10px', 'fontWeight': '600'}),
                    html.P([
                        "The ", html.Strong(
                            "Value Score"), " shows how a property's price compares to market expectations based on its size:"
                    ], style={'margin': '0 0 8px 0', 'fontSize': '13px'}),
                    html.Ul([
                        html.Li([html.Strong("Negative score", style={'color': '#28a745'}), " = Below expected price (Good deal)"],
                                style={'fontSize': '12px', 'marginBottom': '4px'}),
                        html.Li([html.Strong("Positive score", style={'color': '#dc3545'}), " = Above expected price (Expensive)"],
                                style={'fontSize': '12px', 'marginBottom': '4px'}),
                        html.Li("Example: -15% means property costs 15% less than similar-sized properties",
                                style={'fontSize': '12px', 'color': '#6c757d', 'fontStyle': 'italic'})
                    ], style={'margin': '0', 'paddingLeft': '16px'}),
                ], style={
                    'background': 'linear-gradient(135deg, #e3f2fd 0%, #f1f8ff 100%)',
                    'border': '1px solid #b3d9ff',
                    'borderRadius': '8px',
                    'padding': '15px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
                }),

                # Scatter plot
                self.loading_manager.create_loading_component("main-graph",
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
            ], style=DashboardStyles.GRAPH, className="fade-in graph-responsive"),

            # Map section
            html.Div([
                html.H3([
                    html.I(className="fas fa-map-marked-alt",
                           style={'marginRight': '10px', 'color': '#667eea'}),
                    "Property Locations by Market Value Analysis"
                ], style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': '600', 'fontSize': '18px'}),
                self.loading_manager.create_loading_component("map-view",
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
            ], style=DashboardStyles.MAP_CONTAINER, className="fade-in graph-responsive"),

        ], style=DashboardStyles.DUAL_VIEW_CONTAINER, className="fade-in dual-view-responsive")

    def _create_analytics_section(self) -> html.Div:
        """Create the advanced analytics dashboard section."""
        return html.Div([
            html.H3([
                html.I(className="fas fa-chart-line",
                       style={'marginRight': '10px', 'color': '#667eea'}),
                "Advanced Analytics Dashboard"
            ], style={'color': '#2c3e50', 'marginBottom': '30px', 'fontWeight': '600', 'fontSize': '22px', 'textAlign': 'center'}),

            # Analytics charts in 2x2 grid
            html.Div([
                # Row 1: Histogram and Box Plot
                html.Div([
                    html.Div([
                        self.loading_manager.create_loading_component("price-histogram",
                                                                      dcc.Graph(
                                                                          id='price-histogram', config={'displayModeBar': False}),
                                                                      "Generating price distribution analysis"
                                                                      )
                    ], style=self._get_analytics_chart_style()),

                    html.Div([
                        self.loading_manager.create_loading_component("price-boxplot",
                                                                      dcc.Graph(
                                                                          id='price-boxplot', config={'displayModeBar': False}),
                                                                      "Creating neighborhood comparison"
                                                                      )
                    ], style=self._get_analytics_chart_style()),
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '20px'}, className="analytics-row"),

                # Row 2: Bar Chart and Efficiency Scatter
                html.Div([
                    html.Div([
                        self.loading_manager.create_loading_component("neighborhood-comparison",
                                                                      dcc.Graph(
                                                                          id='neighborhood-comparison', config={'displayModeBar': False}),
                                                                      "Analyzing neighborhood trends"
                                                                      )
                    ], style=self._get_analytics_chart_style()),

                    html.Div([
                        self.loading_manager.create_loading_component("room-efficiency",
                                                                      dcc.Graph(
                                                                          id='room-efficiency', config={'displayModeBar': False}),
                                                                      "Computing room efficiency metrics"
                                                                      )
                    ], style=self._get_analytics_chart_style()),
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '20px'}, className="analytics-row"),

                # Row 3: Neighborhood ranking (full width)
                html.Div([
                    html.Div([
                        self.loading_manager.create_loading_component("neighborhood-ranking",
                                                                      dcc.Graph(
                                                                          id='neighborhood-ranking', config={'displayModeBar': False}),
                                                                      "Ranking neighborhoods by affordability"
                                                                      )
                    ], style=self._get_analytics_chart_style()),
                ]),
            ], style={
                'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                'padding': '25px',
                'borderRadius': '15px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
                'marginBottom': '25px',
                'border': '1px solid rgba(255,255,255,0.3)'
            }, className="analytics-grid")
        ], className="fade-in")

    def _create_decision_support_section(self) -> html.Div:
        """Create the investment decision support section."""
        return html.Div([
            html.H3([
                html.I(className="fas fa-lightbulb",
                       style={'marginRight': '10px', 'color': '#28a745'}),
                "Investment Decision Support"
            ], style={'color': '#2c3e50', 'marginBottom': '30px', 'fontWeight': '600', 'fontSize': '22px', 'textAlign': 'center'}),

            # Two column layout: Best deals + Market insights
            html.Div([
                # Best deals table
                html.Div([
                    self.loading_manager.create_loading_component("best-deals",
                                                                  html.Div(
                                                                      id='best-deals-table'),
                                                                  "Finding best property deals"
                                                                  )
                ], style=self._get_decision_support_style()),

                # Market insights
                html.Div([
                    self.loading_manager.create_loading_component("market-insights",
                                                                  html.Div(
                                                                      id='market-insights'),
                                                                  "Analyzing market trends"
                                                                  )
                ], style=self._get_decision_support_style()),
            ], style={'display': 'flex', 'gap': '25px', 'alignItems': 'flex-start'}, className="decision-support-layout")
        ], style={
            'background': 'linear-gradient(135deg, #e8f5e8 0%, #d4f1d4 100%)',
            'padding': '25px',
            'borderRadius': '15px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.1)',
            'marginBottom': '25px',
            'border': '1px solid rgba(255,255,255,0.3)'
        }, className="fade-in")

    def _create_summary_section(self) -> html.Div:
        """Create the summary statistics section."""
        return html.Div([
            html.H3([
                html.I(className="fas fa-chart-bar",
                       style={'marginRight': '10px'}),
                "Data Summary"
            ], style=DashboardStyles.SUMMARY_HEADER),
            self.loading_manager.create_loading_component("summary",
                                                          html.Div(
                                                              id='summary-stats'), "Calculating statistics"
                                                          )
        ], style=DashboardStyles.SUMMARY, className="fade-in")

    def _create_data_stores(self) -> List[dcc.Store]:
        """Create data stores for state management."""
        return [
            # Store for clicked links
            dcc.Store(id='clicked-link', storage_type='memory'),
            dcc.Store(id='clicked-map-link', storage_type='memory'),

            # Store for current dataset
            dcc.Store(id='current-dataset', storage_type='memory',
                      data=self.data.data.to_dict('records') if hasattr(self.data, 'data') and not self.data.is_empty else []),

            # Store for scraped data (browser storage integration)
            dcc.Store(id='scraped-data-store', storage_type='memory'),

            # Store for loading state
            dcc.Store(id='loading-state', storage_type='memory',
                      data={'loading': False}),

            # Auto-load trigger (fires once on page load)
            dcc.Interval(id='auto-load-trigger', interval=1000,
                         n_intervals=0, max_intervals=1, disabled=False)
        ]

    def _get_analytics_chart_style(self) -> Dict[str, Any]:
        """Get consistent styling for analytics charts."""
        return {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.08)',
            'border': '1px solid rgba(255,255,255,0.3)'
        }

    def _get_decision_support_style(self) -> Dict[str, Any]:
        """Get consistent styling for decision support components."""
        return {
            'background': 'rgba(255,255,255,0.95)',
            'padding': '25px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.08)',
            'border': '1px solid rgba(255,255,255,0.3)',
            'flex': '1'
        }
