"""Browser storage callback handlers for multi-user dataset management."""

import dash
from dash import clientside_callback, Output, Input, State, html
import logging

# BrowserStorageManager no longer used - replaced with SimpleStorageManager


logger = logging.getLogger(__name__)


class StorageCallbackManager:
    """Manages client-side storage callbacks for browser-based dataset management."""

    def __init__(self, app: dash.Dash):
        """
        Initialize storage callback manager.

        Args:
            app: Dash application instance
        """
        self.app = app
        # Complex storage manager no longer needed with simple storage approach
        self.storage_manager = None

    def register_all_callbacks(self) -> None:
        """Register all storage-related callbacks."""
        # All storage functionality now handled by SimpleStorageManager
        # Complex dataset management has been replaced with simple auto-save/load
        pass

    def _register_save_dataset_callback(self) -> None:
        """Register client-side callback to save dataset to browser storage."""

        clientside_callback(
            """
            function(n_clicks, current_data, dataset_name, dataset_description) {
                if (!n_clicks || !current_data || current_data.length === 0) {
                    return [false, null, "No data to save"];
                }

                try {
                    // Generate dataset ID
                    const datasetId = 'dataset_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

                    // Create metadata
                    const metadata = {
                        id: datasetId,
                        name: dataset_name || "Untitled Dataset",
                        description: dataset_description || "",
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        property_count: current_data.length,
                        scraped_params: {},
                        tags: []
                    };

                    // Use global storage manager
                    if (window.datasetStorage) {
                        window.datasetStorage.saveDataset(
                            datasetId, current_data, metadata);
                        return [true, datasetId, "Dataset saved successfully"];
                    } else {
                        return [false, null, "Storage not available"];
                    }
                } catch (error) {
                    console.error("Failed to save dataset:", error);
                    return [false, null, "Failed to save: " + error.message];
                }
            }
            """,
            [Output('save-dataset-result', 'data'),
             Output('save-dataset-id', 'data'),
             Output('save-dataset-message', 'data')],
            [Input('save-dataset-btn', 'n_clicks')],
            [State('current-dataset', 'data'),
             State('dataset-name-input', 'value'),
             State('dataset-description-input', 'value')],
            prevent_initial_call=True
        )

    def _register_load_dataset_callback(self) -> None:
        """Register client-side callback to load dataset from browser storage."""

        clientside_callback(
            """
            function(selected_dataset_id) {
                if (!selected_dataset_id || !window.datasetStorage) {
                    return [[], null, "No dataset selected"];
                }

                try {
                    const dataset = window.datasetStorage.loadDataset(selected_dataset_id);
                    if (dataset && dataset.data) {
                        return [dataset.data, dataset.metadata, "Dataset loaded successfully"];
                    } else {
                        return [[], null, "Dataset not found"];
                    }
                } catch (error) {
                    console.error("Failed to load dataset:", error);
                    return [[], null, "Failed to load: " + error.message];
                }
            }
            """,
            [Output('current-dataset', 'data'),
             Output('loaded-dataset-metadata', 'data'),
             Output('load-dataset-message', 'data')],
            [Input('dataset-selector', 'value')],
            prevent_initial_call=True
        )

    def _register_list_datasets_callback(self) -> None:
        """Register client-side callback to list available datasets."""

        clientside_callback(
            """
            function(trigger) {
                if (!window.datasetStorage) {
                    return [[], "Storage not available"];
                }

                try {
                    const datasets = window.datasetStorage.listDatasets();
                    const options = datasets.map(dataset => ({
                        label: `${dataset.name} (${dataset.property_count} properties, ${dataset.age_display})`,
                        value: dataset.id
                    }));

                    return [options, "Datasets loaded"];
                } catch (error) {
                    console.error("Failed to list datasets:", error);
                    return [[], "Failed to load datasets: " + error.message];
                }
            }
            """,
            [Output('dataset-selector', 'options'),
             Output('list-datasets-message', 'data')],
            [Input('refresh-datasets-btn', 'n_clicks'),
             # Trigger refresh after save
             Input('save-dataset-result', 'data'),
             Input('delete-dataset-result', 'data')],  # Trigger refresh after delete
            prevent_initial_call=False  # Allow initial load
        )

    def _register_delete_dataset_callback(self) -> None:
        """Register client-side callback to delete dataset from browser storage."""

        clientside_callback(
            """
            function(n_clicks, selected_dataset_id) {
                if (!n_clicks || !selected_dataset_id || !window.datasetStorage) {
                    return [false, "No dataset selected"];
                }

                try {
                    const success = window.datasetStorage.deleteDataset(selected_dataset_id);
                    if (success) {
                        return [true, "Dataset deleted successfully"];
                    } else {
                        return [false, "Failed to delete dataset"];
                    }
                } catch (error) {
                    console.error("Failed to delete dataset:", error);
                    return [false, "Failed to delete: " + error.message];
                }
            }
            """,
            [Output('delete-dataset-result', 'data'),
             Output('delete-dataset-message', 'data')],
            [Input('delete-dataset-btn', 'n_clicks')],
            [State('dataset-selector', 'value')],
            prevent_initial_call=True
        )

    def _register_storage_info_callback(self) -> None:
        """Register client-side callback to get storage information."""

        clientside_callback(
            """
            function(trigger) {
                if (!window.datasetStorage) {
                    return {
                        total_datasets: 0,
                        total_size_bytes: 0,
                        estimated_quota_bytes: 0,
                        supports_local_storage: false,
                        error: "Storage not available"
                    };
                }

                try {
                    return window.datasetStorage.getStorageInfo();
                } catch (error) {
                    console.error("Failed to get storage info:", error);
                    return {
                        total_datasets: 0,
                        total_size_bytes: 0,
                        estimated_quota_bytes: 0,
                        supports_local_storage: false,
                        error: error.message
                    };
                }
            }
            """,
            [Output('storage-info', 'data')],
            [Input('refresh-storage-info-btn', 'n_clicks'),
             Input('save-dataset-result', 'data'),  # Update after save
             Input('delete-dataset-result', 'data')],  # Update after delete
            prevent_initial_call=False  # Allow initial load
        )

    def create_storage_ui_components(self) -> html.Div:
        """
        Create UI components for dataset management.

        Returns:
            Div containing all storage management components
        """
        return html.Div([
            # Hidden stores for communication
            html.Div([
                dash.dcc.Store(id='save-dataset-result',
                               storage_type='memory'),
                dash.dcc.Store(id='save-dataset-id', storage_type='memory'),
                dash.dcc.Store(id='save-dataset-message',
                               storage_type='memory'),
                dash.dcc.Store(id='load-dataset-message',
                               storage_type='memory'),
                dash.dcc.Store(id='loaded-dataset-metadata',
                               storage_type='memory'),
                dash.dcc.Store(id='delete-dataset-result',
                               storage_type='memory'),
                dash.dcc.Store(id='delete-dataset-message',
                               storage_type='memory'),
                dash.dcc.Store(id='list-datasets-message',
                               storage_type='memory'),
                dash.dcc.Store(id='storage-info', storage_type='memory'),
            ], style={'display': 'none'}),

            # Dataset Management Section
            html.Div([
                html.H4([
                    html.I(className="fas fa-database",
                           style={'margin-right': '10px'}),
                    "Dataset Management"
                ], style={'color': '#2c3e50', 'margin-bottom': '20px'}),

                # Save Dataset Section
                html.Div([
                    html.H6("💾 Save Current Dataset", style={
                            'margin-bottom': '15px'}),
                    html.Div([
                        dash.dcc.Input(
                            id='dataset-name-input',
                            type='text',
                            placeholder='Enter dataset name...',
                            style={'width': '100%',
                                   'margin-bottom': '10px', 'padding': '8px'}
                        ),
                        dash.dcc.Textarea(
                            id='dataset-description-input',
                            placeholder='Optional description...',
                            style={'width': '100%', 'height': '60px',
                                   'margin-bottom': '10px', 'padding': '8px'}
                        ),
                        html.Button(
                            "Save Dataset",
                            id='save-dataset-btn',
                            className="btn btn-success",
                            style={'width': '100%', 'padding': '10px'}
                        )
                    ])
                ], style={
                    'background': '#f8f9fa', 'padding': '15px', 'border-radius': '8px', 'margin-bottom': '20px'
                }),

                # Load Dataset Section
                html.Div([
                    html.H6("📂 Load Saved Dataset", style={
                            'margin-bottom': '15px'}),
                    html.Div([
                        dash.dcc.Dropdown(
                            id='dataset-selector',
                            placeholder='Select a dataset to load...',
                            style={'margin-bottom': '10px'}
                        ),
                        html.Div([
                            html.Button(
                                "🔄 Refresh List",
                                id='refresh-datasets-btn',
                                className="btn btn-outline-secondary",
                                style={'margin-right': '10px'}
                            ),
                            html.Button(
                                "🗑️ Delete Selected",
                                id='delete-dataset-btn',
                                className="btn btn-outline-danger"
                            )
                        ])
                    ])
                ], style={
                    'background': '#f8f9fa', 'padding': '15px', 'border-radius': '8px', 'margin-bottom': '20px'
                }),

                # Storage Info Section
                html.Div([
                    html.H6("📊 Storage Information", style={
                            'margin-bottom': '15px'}),
                    html.Div(id='storage-info-display'),
                    html.Button(
                        "🔄 Refresh Info",
                        id='refresh-storage-info-btn',
                        className="btn btn-outline-info btn-sm",
                        style={'margin-top': '10px'}
                    )
                ], style={
                    'background': '#f8f9fa', 'padding': '15px', 'border-radius': '8px'
                })

            ], style={
                'background': 'white',
                'padding': '25px',
                'border-radius': '12px',
                'box-shadow': '0 4px 15px rgba(0,0,0,0.08)',
                'margin-bottom': '25px'
            })
        ])

    def register_storage_display_callbacks(self) -> None:
        """Register callbacks for updating storage display components."""
        # Simple storage approach doesn't require display callbacks
        pass
