"""Dataset management UI component for browser storage integration."""

from typing import List, Dict, Any
from dash import html, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime


class DatasetManagerComponent:
    """UI component for managing stored datasets with enhanced features."""

    def __init__(self):
        """Initialize the dataset manager component."""
        self.component_id_prefix = "dataset-manager"

    def create_dataset_management_section(self) -> html.Div:
        """
        Create the main dataset management section with all controls.

        Returns:
            html.Div: Complete dataset management interface
        """
        return html.Div([
            # Header with storage info
            self._create_header_section(),

            # Action buttons
            self._create_action_buttons(),

            # Dataset list and details
            html.Div([
                # Left side: Dataset list
                html.Div([
                    self._create_dataset_list()
                ], className="col-md-8"),

                # Right side: Selected dataset details
                html.Div([
                    self._create_dataset_details()
                ], className="col-md-4")
            ], className="row", style={'margin-top': '20px'}),

            # Storage information display
            self._create_storage_info_display(),

        ], id=f"{self.component_id_prefix}-main-container", className="dataset-management-section")

    def _create_header_section(self) -> html.Div:
        """Create the header section with title and quick stats."""
        return html.Div([
            html.Div([
                html.H4([
                    html.I(className="fas fa-database",
                           style={'margin-right': '10px', 'color': '#6f42c1'}),
                    "My Datasets"
                ], style={'color': '#2c3e50', 'margin-bottom': '10px', 'font-weight': '600'}),

                html.P([
                    "Manage your saved property searches and analysis datasets. ",
                    html.Small("Data is stored locally in your browser.",
                               style={'color': '#6c757d', 'font-style': 'italic'})
                ], style={'color': '#495057', 'margin-bottom': '0'})
            ], className="col-md-8"),

            html.Div([
                html.Div(id=f"{self.component_id_prefix}-quick-stats",
                         children=self._create_quick_stats())
            ], className="col-md-4")
        ], className="row", style={'margin-bottom': '20px'})

    def _create_action_buttons(self) -> html.Div:
        """Create action buttons for dataset operations."""
        return html.Div([
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="fas fa-save",
                           style={'margin-right': '8px'}),
                    "Save Current"
                ], id=f"{self.component_id_prefix}-save-btn",
                    color="primary", size="sm"),

                dbc.Button([
                    html.I(className="fas fa-folder-open",
                           style={'margin-right': '8px'}),
                    "Load Selected"
                ], id=f"{self.component_id_prefix}-load-btn",
                    color="success", size="sm", disabled=True),

                dbc.Button([
                    html.I(className="fas fa-edit",
                           style={'margin-right': '8px'}),
                    "Rename"
                ], id=f"{self.component_id_prefix}-rename-btn",
                    color="info", size="sm", disabled=True),

                dbc.Button([
                    html.I(className="fas fa-download",
                           style={'margin-right': '8px'}),
                    "Export"
                ], id=f"{self.component_id_prefix}-export-btn",
                    color="secondary", size="sm", disabled=True),

                dbc.Button([
                    html.I(className="fas fa-trash",
                           style={'margin-right': '8px'}),
                    "Delete"
                ], id=f"{self.component_id_prefix}-delete-btn",
                    color="danger", size="sm", disabled=True)
            ], style={'margin-bottom': '15px'}),

            # Status message area
            html.Div(id=f"{self.component_id_prefix}-status-message",
                     style={'margin-top': '10px'})
        ])

    def _create_dataset_list(self) -> html.Div:
        """Create the dataset list table."""
        return html.Div([
            html.H6([
                html.I(className="fas fa-list", style={'margin-right': '8px'}),
                "Available Datasets"
            ], style={'color': '#495057', 'margin-bottom': '15px'}),

            html.Div(id=f"{self.component_id_prefix}-dataset-table",
                     children=self._create_empty_dataset_table())
        ])

    def _create_dataset_details(self) -> html.Div:
        """Create the dataset details panel."""
        return html.Div([
            html.H6([
                html.I(className="fas fa-info-circle",
                       style={'margin-right': '8px'}),
                "Dataset Details"
            ], style={'color': '#495057', 'margin-bottom': '15px'}),

            html.Div(id=f"{self.component_id_prefix}-dataset-details",
                     children=self._create_empty_details_panel())
        ])

    def _create_storage_info_display(self) -> html.Div:
        """Create the storage information display."""
        return html.Div([
            html.Hr(style={'margin': '30px 0 20px 0'}),

            html.H6([
                html.I(className="fas fa-hdd", style={'margin-right': '8px'}),
                "Storage Information"
            ], style={'color': '#495057', 'margin-bottom': '15px'}),

            html.Div(id=f"{self.component_id_prefix}-storage-info",
                     children=self._create_storage_info_cards())
        ])

    def _create_quick_stats(self) -> List[html.Div]:
        """Create quick statistics cards."""
        return [
            html.Div([
                html.Div([
                    html.H6("0", id=f"{self.component_id_prefix}-dataset-count",
                            style={'margin': '0', 'color': '#6f42c1', 'font-weight': 'bold'}),
                    html.Small("Datasets", style={'color': '#6c757d'})
                ], style={'text-align': 'center', 'padding': '15px'})
            ], className="card", style={'margin-bottom': '10px'}),

            html.Div([
                html.Div([
                    html.H6("0 MB", id=f"{self.component_id_prefix}-storage-used",
                            style={'margin': '0', 'color': '#28a745', 'font-weight': 'bold'}),
                    html.Small("Storage Used", style={'color': '#6c757d'})
                ], style={'text-align': 'center', 'padding': '15px'})
            ], className="card")
        ]

    def _create_empty_dataset_table(self) -> dash_table.DataTable:
        """Create an empty dataset table."""
        return dash_table.DataTable(
            id=f"{self.component_id_prefix}-table",
            columns=[
                {'name': 'Name', 'id': 'name', 'presentation': 'markdown'},
                {'name': 'Properties', 'id': 'property_count', 'type': 'numeric'},
                {'name': 'Size', 'id': 'size_display'},
                {'name': 'Created', 'id': 'created_display'},
                {'name': 'Search Params', 'id': 'search_summary'}
            ],
            data=[],
            row_selectable='single',
            selected_rows=[],
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'fontSize': '14px'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': '600',
                'color': '#495057',
                'border': '1px solid #dee2e6'
            },
            style_data={
                'backgroundColor': 'white',
                'border': '1px solid #dee2e6'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'state': 'selected'},
                    'backgroundColor': '#e3f2fd',
                    'border': '1px solid #2196f3'
                }
            ],
            page_size=10,
            sort_action='native',
            filter_action='native'
        )

    def _create_empty_details_panel(self) -> html.Div:
        """Create an empty details panel."""
        return html.Div([
            html.Div([
                html.I(className="fas fa-hand-pointer",
                       style={'font-size': '48px', 'color': '#dee2e6', 'margin-bottom': '15px'}),
                html.P("Select a dataset to view details",
                       style={'color': '#6c757d', 'margin': '0'})
            ], style={'text-align': 'center', 'padding': '40px'})
        ], className="card", style={'height': '100%', 'min-height': '300px'})

    def _create_storage_info_cards(self) -> html.Div:
        """Create storage information cards."""
        return html.Div([
            html.Div([
                html.Div([
                    html.H6("Storage Usage", style={
                            'color': '#495057', 'margin-bottom': '15px'}),
                    html.Div(id=f"{self.component_id_prefix}-usage-bar",
                             children=self._create_usage_bar(0, 100)),
                    html.Small(id=f"{self.component_id_prefix}-usage-text",
                               children="0 MB of 50 MB used",
                               style={'color': '#6c757d'})
                ], style={'padding': '20px'})
            ], className="card col-md-6"),

            html.Div([
                html.Div([
                    html.H6("Browser Storage", style={
                            'color': '#495057', 'margin-bottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-check-circle",
                                   style={'color': '#28a745', 'margin-right': '8px'}),
                            "localStorage Available"
                        ], id=f"{self.component_id_prefix}-storage-status"),
                        html.Div([
                            html.I(className="fas fa-info-circle",
                                   style={'color': '#17a2b8', 'margin-right': '8px'}),
                            "Data persists until manually cleared"
                        ], style={'margin-top': '10px', 'font-size': '0.9em', 'color': '#6c757d'})
                    ])
                ], style={'padding': '20px'})
            ], className="card col-md-6")
        ], className="row")

    def _create_usage_bar(self, used: float, total: float) -> html.Div:
        """Create a usage progress bar."""
        percentage = (used / total * 100) if total > 0 else 0

        color = '#28a745'  # Green
        if percentage > 80:
            color = '#dc3545'  # Red
        elif percentage > 60:
            color = '#ffc107'  # Yellow

        return dbc.Progress(
            value=percentage,
            color=color.replace('#', ''),
            style={'height': '10px', 'margin-bottom': '10px'}
        )

    def create_save_dataset_modal(self) -> dbc.Modal:
        """Create modal for saving datasets with custom names."""
        return dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Save Dataset")),
            dbc.ModalBody([
                html.P("Enter a name for your dataset:",
                       style={'margin-bottom': '15px'}),
                dbc.Input(
                    id=f"{self.component_id_prefix}-save-name-input",
                    placeholder="e.g., Tel Aviv 3BR Under 2M",
                    type="text",
                    style={'margin-bottom': '15px'}
                ),
                html.Small("This will save your current search results and filters.",
                           style={'color': '#6c757d'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id=f"{self.component_id_prefix}-save-cancel-btn",
                           className="ms-auto", n_clicks=0, color="secondary"),
                dbc.Button("Save", id=f"{self.component_id_prefix}-save-confirm-btn",
                           className="ms-1", n_clicks=0, color="primary")
            ])
        ], id=f"{self.component_id_prefix}-save-modal", is_open=False)

    def create_rename_dataset_modal(self) -> dbc.Modal:
        """Create modal for renaming datasets."""
        return dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Rename Dataset")),
            dbc.ModalBody([
                html.P("Enter a new name for the dataset:",
                       style={'margin-bottom': '15px'}),
                dbc.Input(
                    id=f"{self.component_id_prefix}-rename-input",
                    placeholder="New dataset name",
                    type="text",
                    style={'margin-bottom': '15px'}
                )
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id=f"{self.component_id_prefix}-rename-cancel-btn",
                           className="ms-auto", n_clicks=0, color="secondary"),
                dbc.Button("Rename", id=f"{self.component_id_prefix}-rename-confirm-btn",
                           className="ms-1", n_clicks=0, color="primary")
            ])
        ], id=f"{self.component_id_prefix}-rename-modal", is_open=False)

    def format_dataset_for_table(self, datasets_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format dataset metadata for display in the table.

        Args:
            datasets_metadata: List of dataset metadata dictionaries

        Returns:
            List of formatted dictionaries for the DataTable
        """
        formatted_data = []

        for i, dataset in enumerate(datasets_metadata):
            # Format size
            size_bytes = dataset.get('size_bytes', 0)
            if size_bytes < 1024:
                size_display = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_display = f"{size_bytes / 1024:.1f} KB"
            else:
                size_display = f"{size_bytes / (1024 * 1024):.1f} MB"

            # Format creation date
            created_at = dataset.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_dt = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00'))
                    else:
                        created_dt = created_at
                    created_display = created_dt.strftime("%m/%d %H:%M")
                except:
                    created_display = "Unknown"
            else:
                created_display = "Unknown"

            # Format search parameters summary
            scraped_params = dataset.get('scraped_params', {})
            search_parts = []
            if scraped_params.get('city'):
                search_parts.append(f"City: {scraped_params['city']}")
            if scraped_params.get('area'):
                search_parts.append(f"Area: {scraped_params['area']}")
            if scraped_params.get('min_price') or scraped_params.get('max_price'):
                min_p = scraped_params.get('min_price', 0)
                max_p = scraped_params.get('max_price', '∞')
                search_parts.append(f"₪{min_p:,}-{max_p}")

            search_summary = ", ".join(
                search_parts) if search_parts else "No filters"

            formatted_data.append({
                'id': i,
                'name': dataset.get('name', f'Dataset {i+1}'),
                'property_count': dataset.get('property_count', 0),
                'size_display': size_display,
                'created_display': created_display,
                'search_summary': search_summary,
                'raw_metadata': dataset  # Keep original for reference
            })

        return formatted_data
