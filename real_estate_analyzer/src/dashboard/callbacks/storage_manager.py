"""Enhanced storage callback manager for comprehensive dataset management."""

import pandas as pd
from typing import Dict, Any, List, Optional
from dash import Input, Output, State, ctx, no_update, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from src.storage.browser_storage import BrowserStorageManager
from src.data.models import PropertyDataFrame
from src.dashboard.components.dataset_manager import DatasetManagerComponent


class EnhancedStorageCallbackManager:
    """Enhanced callback manager for comprehensive dataset management."""

    def __init__(self, app, storage_manager: BrowserStorageManager):
        """
        Initialize the enhanced storage callback manager.

        Args:
            app: Dash application instance
            storage_manager: Browser storage manager instance
        """
        self.app = app
        self.storage_manager = storage_manager
        self.dataset_component = DatasetManagerComponent()
        self._register_callbacks()

    def _register_callbacks(self):
        """Register all storage-related callbacks."""
        self._register_dataset_list_callbacks()
        self._register_dataset_operations_callbacks()
        self._register_storage_info_callbacks()
        self._register_ui_state_callbacks()
        self._register_integration_callbacks()

    def _register_dataset_list_callbacks(self):
        """Register callbacks for dataset list management."""

        @self.app.callback(
            [Output('dataset-manager-dataset-table', 'data'),
             Output('dataset-manager-dataset-count', 'children'),
             Output('available-datasets', 'data'),
             Output('dataset-metadata', 'data')],
            [Input('storage-operations', 'data'),
             Input('scraped-data-store', 'data')]
        )
        def update_dataset_list(storage_ops_data, scraped_data):
            """Update the dataset list when storage operations occur."""
            try:
                # Get available datasets
                available_datasets = self.storage_manager.list_datasets()

                # Format for table display
                table_data = self.dataset_component.format_dataset_for_table(
                    available_datasets)

                # Update count
                dataset_count = len(available_datasets)

                # Prepare metadata dict for easy access
                metadata_dict = {
                    dataset['name']: dataset for dataset in available_datasets
                }

                return table_data, str(dataset_count), available_datasets, metadata_dict

            except Exception as e:
                print(f"Error updating dataset list: {e}")
                return [], "0", [], {}

    def _register_dataset_operations_callbacks(self):
        """Register callbacks for dataset operations (save, load, delete)."""

        # Save dataset modal control
        @self.app.callback(
            Output('dataset-manager-save-modal', 'is_open'),
            [Input('dataset-manager-save-btn', 'n_clicks'),
             Input('dataset-manager-save-cancel-btn', 'n_clicks'),
             Input('dataset-manager-save-confirm-btn', 'n_clicks')],
            [State('dataset-manager-save-modal', 'is_open')]
        )
        def toggle_save_modal(save_clicks, cancel_clicks, confirm_clicks, is_open):
            """Toggle the save dataset modal."""
            if ctx.triggered_id == 'dataset-manager-save-btn':
                return True
            elif ctx.triggered_id in ['dataset-manager-save-cancel-btn', 'dataset-manager-save-confirm-btn']:
                return False
            return is_open

        # Save dataset operation
        @self.app.callback(
            [Output('storage-operations', 'data', allow_duplicate=True),
             Output('dataset-manager-status-message',
                    'children', allow_duplicate=True),
             Output('dataset-manager-save-name-input', 'value')],
            [Input('dataset-manager-save-confirm-btn', 'n_clicks')],
            [State('dataset-manager-save-name-input', 'value'),
             State('current-dataset', 'data'),
             State('scraped-data-store', 'data')],
            prevent_initial_call=True
        )
        def save_dataset(n_clicks, dataset_name, current_data, scraped_data):
            """Save the current dataset with a custom name."""
            if not n_clicks or not dataset_name:
                raise PreventUpdate

            try:
                # Use current dataset data if available, otherwise use scraped data
                if current_data and len(current_data) > 0:
                    df_data = PropertyDataFrame.from_dict_records(current_data)
                elif scraped_data:
                    # Handle scraped data format
                    if isinstance(scraped_data, dict) and 'data' in scraped_data:
                        df_data = PropertyDataFrame.from_dict_records(
                            scraped_data['data'])
                    else:
                        df_data = PropertyDataFrame.from_dict_records(
                            scraped_data)
                else:
                    return no_update, dbc.Alert("No data available to save", color="warning"), ""

                # Save to storage
                dataset_id = self.storage_manager.save_dataset(
                    df_data, dataset_name)

                success_msg = dbc.Alert(
                    f"Dataset '{dataset_name}' saved successfully!",
                    color="success",
                    duration=4000
                )

                # Trigger list refresh
                storage_ops = {'operation': 'save', 'dataset_id': dataset_id,
                               'timestamp': pd.Timestamp.now().isoformat()}

                return storage_ops, success_msg, ""

            except Exception as e:
                error_msg = dbc.Alert(
                    f"Error saving dataset: {str(e)}", color="danger", duration=4000)
                return no_update, error_msg, dataset_name

        # Load dataset operation
        @self.app.callback(
            [Output('current-dataset', 'data', allow_duplicate=True),
             Output('selected-dataset', 'data'),
             Output('dataset-manager-status-message', 'children', allow_duplicate=True)],
            [Input('dataset-manager-load-btn', 'n_clicks')],
            [State('dataset-manager-table', 'selected_rows'),
             State('dataset-manager-table', 'data')],
            prevent_initial_call=True
        )
        def load_dataset(n_clicks, selected_rows, table_data):
            """Load the selected dataset."""
            if not n_clicks or not selected_rows or not table_data:
                raise PreventUpdate

            try:
                selected_row = table_data[selected_rows[0]]
                dataset_name = selected_row['name']

                # Load dataset from storage
                dataset = self.storage_manager.load_dataset(dataset_name)

                success_msg = dbc.Alert(
                    f"Dataset '{dataset_name}' loaded successfully!",
                    color="success",
                    duration=4000
                )

                return dataset.to_dict('records'), dataset_name, success_msg

            except Exception as e:
                error_msg = dbc.Alert(
                    f"Error loading dataset: {str(e)}", color="danger", duration=4000)
                return no_update, no_update, error_msg

        # Delete dataset operation
        @self.app.callback(
            [Output('storage-operations', 'data', allow_duplicate=True),
             Output('dataset-manager-status-message', 'children', allow_duplicate=True)],
            [Input('dataset-manager-delete-btn', 'n_clicks')],
            [State('dataset-manager-table', 'selected_rows'),
             State('dataset-manager-table', 'data')],
            prevent_initial_call=True
        )
        def delete_dataset(n_clicks, selected_rows, table_data):
            """Delete the selected dataset."""
            if not n_clicks or not selected_rows or not table_data:
                raise PreventUpdate

            try:
                selected_row = table_data[selected_rows[0]]
                dataset_name = selected_row['name']

                # Delete from storage
                self.storage_manager.delete_dataset(dataset_name)

                success_msg = dbc.Alert(
                    f"Dataset '{dataset_name}' deleted successfully!",
                    color="success",
                    duration=4000
                )

                # Trigger list refresh
                storage_ops = {'operation': 'delete', 'dataset_name': dataset_name,
                               'timestamp': pd.Timestamp.now().isoformat()}

                return storage_ops, success_msg

            except Exception as e:
                error_msg = dbc.Alert(
                    f"Error deleting dataset: {str(e)}", color="danger", duration=4000)
                return no_update, error_msg

        # Enable/disable buttons based on selection
        @self.app.callback(
            [Output('dataset-manager-load-btn', 'disabled'),
             Output('dataset-manager-rename-btn', 'disabled'),
             Output('dataset-manager-export-btn', 'disabled'),
             Output('dataset-manager-delete-btn', 'disabled')],
            [Input('dataset-manager-table', 'selected_rows')]
        )
        def update_button_states(selected_rows):
            """Enable/disable buttons based on dataset selection."""
            has_selection = selected_rows and len(selected_rows) > 0
            return not has_selection, not has_selection, not has_selection, not has_selection

    def _register_storage_info_callbacks(self):
        """Register callbacks for storage information display."""

        @self.app.callback(
            [Output('dataset-manager-storage-used', 'children'),
             Output('dataset-manager-usage-bar', 'children'),
             Output('dataset-manager-usage-text', 'children'),
             Output('storage-info', 'data')],
            [Input('available-datasets', 'data')]
        )
        def update_storage_info(available_datasets):
            """Update storage usage information."""
            try:
                storage_info = self.storage_manager.get_storage_info()

                # Format storage used
                used_mb = storage_info.used_bytes / (1024 * 1024)
                total_mb = storage_info.quota_bytes / (1024 * 1024)

                storage_used_display = f"{used_mb:.1f} MB"

                # Create usage bar
                usage_bar = self.dataset_component._create_usage_bar(
                    used_mb, total_mb)

                # Usage text
                usage_text = f"{used_mb:.1f} MB of {total_mb:.1f} MB used"

                storage_info_dict = {
                    'used_bytes': storage_info.used_bytes,
                    'quota_bytes': storage_info.quota_bytes,
                    'available_bytes': storage_info.available_bytes,
                    'dataset_count': len(available_datasets)
                }

                return storage_used_display, usage_bar, usage_text, storage_info_dict

            except Exception as e:
                print(f"Error updating storage info: {e}")
                return "Error", html.Div(), "Error calculating usage", {}

    def _register_ui_state_callbacks(self):
        """Register callbacks for UI state management."""

        # Dataset management section toggle
        @self.app.callback(
            Output('dataset-management-collapse', 'is_open'),
            [Input('dataset-management-toggle', 'n_clicks')],
            [State('dataset-management-collapse', 'is_open')]
        )
        def toggle_dataset_management(n_clicks, is_open):
            """Toggle the dataset management section."""
            if n_clicks:
                return not is_open
            return is_open

        # Dataset details panel
        @self.app.callback(
            Output('dataset-manager-dataset-details', 'children'),
            [Input('dataset-manager-table', 'selected_rows'),
             Input('dataset-manager-table', 'data')]
        )
        def update_dataset_details(selected_rows, table_data):
            """Update the dataset details panel when selection changes."""
            if not selected_rows or not table_data:
                return self.dataset_component._create_empty_details_panel()

            try:
                selected_row = table_data[selected_rows[0]]
                metadata = selected_row.get('raw_metadata', {})

                return self._create_dataset_details_content(metadata)

            except Exception as e:
                return html.Div(f"Error displaying details: {e}", style={'color': 'red'})

    def _register_integration_callbacks(self):
        """Register callbacks for integration with main application."""

        # Auto-save after scraping
        @self.app.callback(
            Output('storage-operations', 'data', allow_duplicate=True),
            [Input('scraped-data-store', 'data')],
            prevent_initial_call=True
        )
        def auto_save_scraped_data(scraped_data):
            """Automatically save scraped data to storage."""
            if not scraped_data:
                raise PreventUpdate

            try:
                # Generate auto-save name
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                auto_name = f"Auto_Save_{timestamp}"

                # Prepare data for saving
                if isinstance(scraped_data, dict) and 'data' in scraped_data:
                    df_data = PropertyDataFrame.from_dict_records(
                        scraped_data['data'])
                else:
                    df_data = PropertyDataFrame.from_dict_records(scraped_data)

                # Save to storage
                dataset_id = self.storage_manager.save_dataset(
                    df_data, auto_name)

                # Return operation info
                return {
                    'operation': 'auto_save',
                    'dataset_id': dataset_id,
                    'timestamp': pd.Timestamp.now().isoformat()
                }

            except Exception as e:
                print(f"Error in auto-save: {e}")
                raise PreventUpdate

    def _create_dataset_details_content(self, metadata: Dict[str, Any]) -> html.Div:
        """
        Create detailed view of dataset metadata.

        Args:
            metadata: Dataset metadata dictionary

        Returns:
            html.Div: Formatted dataset details panel
        """
        return html.Div([
            html.H6(metadata.get('name', 'Unknown Dataset'),
                    style={'color': '#2c3e50', 'margin-bottom': '15px', 'font-weight': '600'}),

            html.Hr(),

            # Basic info
            html.Div([
                html.Strong("Properties: "),
                html.Span(f"{metadata.get('property_count', 0):,}")
            ], style={'margin-bottom': '10px'}),

            html.Div([
                html.Strong("Size: "),
                html.Span(self._format_size(metadata.get('size_bytes', 0)))
            ], style={'margin-bottom': '10px'}),

            html.Div([
                html.Strong("Created: "),
                html.Span(self._format_date(metadata.get('created_at')))
            ], style={'margin-bottom': '15px'}),

            # Search parameters
            html.H6("Search Parameters", style={
                    'color': '#495057', 'margin-bottom': '10px'}),
            html.Div(
                self._format_search_params(metadata.get('scraped_params', {})),
                style={'background': '#f8f9fa', 'padding': '10px',
                       'border-radius': '5px', 'font-size': '0.9em'}
            )
        ], className="card", style={'padding': '20px'})

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string for display."""
        if not date_str:
            return "Unknown"

        try:
            from datetime import datetime
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = date_str
            return dt.strftime("%B %d, %Y at %H:%M")
        except:
            return "Unknown"

    def _format_search_params(self, params: Dict[str, Any]) -> List[html.Div]:
        """Format search parameters for display."""
        if not params:
            return [html.Div("No search parameters saved", style={'color': '#6c757d', 'font-style': 'italic'})]

        param_items = []

        for key, value in params.items():
            if value is not None and value != "":
                formatted_key = key.replace('_', ' ').title()
                param_items.append(
                    html.Div([
                        html.Strong(f"{formatted_key}: "),
                        html.Span(str(value))
                    ], style={'margin-bottom': '5px'})
                )

        if not param_items:
            return [html.Div("No search parameters saved", style={'color': '#6c757d', 'font-style': 'italic'})]

        return param_items
