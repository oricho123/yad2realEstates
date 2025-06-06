/**
 * DatasetStorageManager - Client-side storage manager for real estate datasets
 *
 * Handles browser localStorage operations with compression, error handling,
 * and storage quota management for multi-user dataset isolation.
 */

class DatasetStorageManager {
  constructor() {
    this.storageKey = "real_estate_datasets";
    this.maxStorageSize = 50 * 1024 * 1024; // 50MB limit
    this.maxDatasets = 10;
    this.compressionEnabled = this.detectCompressionSupport();

    // Initialize storage if needed
    this.initializeStorage();

    console.log(
      `DatasetStorageManager initialized with compression: ${this.compressionEnabled}`
    );
  }

  /**
   * Detect if LZString compression is available
   */
  detectCompressionSupport() {
    // Compression disabled for Phase 1 - can be enabled later with LZString CDN
    return false;
  }

  /**
   * Initialize storage structure if it doesn't exist
   */
  initializeStorage() {
    try {
      const existing = localStorage.getItem(this.storageKey);
      if (!existing) {
        const initialData = {
          datasets: {},
          metadata: {
            version: "1.0",
            created_at: new Date().toISOString(),
            last_cleanup: new Date().toISOString(),
          },
        };
        localStorage.setItem(this.storageKey, JSON.stringify(initialData));
        console.log("Initialized empty storage structure");
      }
    } catch (e) {
      console.error("Failed to initialize storage:", e);
      throw new Error("localStorage not available or full");
    }
  }

  /**
   * Get storage data with error handling
   */
  getStorageData() {
    try {
      const data = localStorage.getItem(this.storageKey);
      if (!data) {
        this.initializeStorage();
        return this.getStorageData();
      }

      const parsed = JSON.parse(data);

      // Ensure structure exists
      if (!parsed.datasets) parsed.datasets = {};
      if (!parsed.metadata) parsed.metadata = { version: "1.0" };

      return parsed;
    } catch (e) {
      console.error("Failed to get storage data:", e);
      // Try to recover by reinitializing
      this.initializeStorage();
      return { datasets: {}, metadata: { version: "1.0" } };
    }
  }

  /**
   * Save storage data with error handling
   */
  setStorageData(data) {
    try {
      const jsonStr = JSON.stringify(data);
      localStorage.setItem(this.storageKey, jsonStr);
      return true;
    } catch (e) {
      console.error("Failed to save storage data:", e);

      if (e.name === "QuotaExceededError" || e.code === 22) {
        throw new Error("Storage quota exceeded. Please delete some datasets.");
      }

      throw new Error(`Storage save failed: ${e.message}`);
    }
  }

  /**
   * Compress data if compression is available
   */
  compressData(data) {
    if (!this.compressionEnabled) {
      return { data: data, compressed: false };
    }

    try {
      const jsonStr = typeof data === "string" ? data : JSON.stringify(data);
      // Compression disabled for Phase 1
      return { data: jsonStr, compressed: false };
    } catch (e) {
      console.warn("Compression failed, using uncompressed data:", e);
      return {
        data: typeof data === "string" ? data : JSON.stringify(data),
        compressed: false,
      };
    }
  }

  /**
   * Decompress data if it was compressed
   */
  decompressData(compressedData) {
    if (!compressedData.compressed || !this.compressionEnabled) {
      return compressedData.data;
    }

    try {
      // Decompression disabled for Phase 1
      return compressedData.data;
    } catch (e) {
      console.warn("Decompression failed, returning raw data:", e);
      return compressedData.data;
    }
  }

  /**
   * Save a dataset to browser storage
   */
  saveDataset(datasetId, dataset, metadata) {
    try {
      // Validate inputs
      if (!datasetId || !dataset) {
        throw new Error("Dataset ID and data are required");
      }

      const storageData = this.getStorageData();

      // Check constraints
      const currentDatasets = Object.keys(storageData.datasets).length;
      if (
        !storageData.datasets[datasetId] &&
        currentDatasets >= this.maxDatasets
      ) {
        throw new Error(
          `Maximum number of datasets (${this.maxDatasets}) reached. Please delete some datasets first.`
        );
      }

      // Prepare dataset payload
      const payload = {
        metadata: metadata || {},
        data: dataset,
        version: "1.0",
        stored_at: new Date().toISOString(),
        user_agent: navigator.userAgent,
      };

      // Compress the payload
      const compressed = this.compressData(payload);

      // Check size constraints
      const payloadSize = new Blob([compressed.data]).size;
      if (payloadSize > this.maxStorageSize) {
        throw new Error(
          `Dataset too large (${(payloadSize / 1024 / 1024).toFixed(
            1
          )}MB). Maximum size is ${(this.maxStorageSize / 1024 / 1024).toFixed(
            1
          )}MB.`
        );
      }

      // Save the dataset
      storageData.datasets[datasetId] = compressed;
      storageData.metadata.last_updated = new Date().toISOString();

      this.setStorageData(storageData);

      console.log(
        `Saved dataset ${datasetId} (${(payloadSize / 1024).toFixed(
          1
        )}KB, compressed: ${compressed.compressed})`
      );
      return true;
    } catch (e) {
      console.error("Failed to save dataset:", e);
      throw e;
    }
  }

  /**
   * Load a dataset from browser storage
   */
  loadDataset(datasetId) {
    try {
      if (!datasetId) {
        throw new Error("Dataset ID is required");
      }

      const storageData = this.getStorageData();
      const compressedDataset = storageData.datasets[datasetId];

      if (!compressedDataset) {
        return null;
      }

      // Decompress the dataset
      const datasetStr = this.decompressData(compressedDataset);
      const dataset = JSON.parse(datasetStr);

      console.log(`Loaded dataset ${datasetId}`);
      return dataset;
    } catch (e) {
      console.error("Failed to load dataset:", e);
      throw new Error(`Failed to load dataset: ${e.message}`);
    }
  }

  /**
   * List all available datasets with metadata
   */
  listDatasets() {
    try {
      const storageData = this.getStorageData();
      const datasets = [];

      for (const [datasetId, compressedDataset] of Object.entries(
        storageData.datasets
      )) {
        try {
          const datasetStr = this.decompressData(compressedDataset);
          const dataset = JSON.parse(datasetStr);

          // Extract metadata for listing
          const metadata = dataset.metadata || {};
          const dataSize = new Blob([datasetStr]).size;

          datasets.push({
            id: datasetId,
            name: metadata.name || `Dataset ${datasetId}`,
            created_at: metadata.created_at || dataset.stored_at,
            updated_at: metadata.updated_at || dataset.stored_at,
            property_count:
              metadata.property_count ||
              (dataset.data ? dataset.data.length : 0),
            size_bytes: dataSize,
            compressed: compressedDataset.compressed || false,
            description: metadata.description,
            tags: metadata.tags || [],
          });
        } catch (e) {
          console.warn(`Failed to parse dataset ${datasetId}:`, e);
          // Include corrupted dataset in list for cleanup
          datasets.push({
            id: datasetId,
            name: `Corrupted Dataset ${datasetId}`,
            created_at: null,
            updated_at: null,
            property_count: 0,
            size_bytes: 0,
            compressed: false,
            corrupted: true,
          });
        }
      }

      // Sort by creation date (newest first)
      datasets.sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA;
      });

      return datasets;
    } catch (e) {
      console.error("Failed to list datasets:", e);
      return [];
    }
  }

  /**
   * Delete a dataset from storage
   */
  deleteDataset(datasetId) {
    try {
      if (!datasetId) {
        throw new Error("Dataset ID is required");
      }

      const storageData = this.getStorageData();

      if (!storageData.datasets[datasetId]) {
        console.warn(`Dataset ${datasetId} not found`);
        return false;
      }

      delete storageData.datasets[datasetId];
      storageData.metadata.last_updated = new Date().toISOString();

      this.setStorageData(storageData);

      console.log(`Deleted dataset ${datasetId}`);
      return true;
    } catch (e) {
      console.error("Failed to delete dataset:", e);
      throw new Error(`Failed to delete dataset: ${e.message}`);
    }
  }

  /**
   * Get storage information and usage statistics
   */
  getStorageInfo() {
    try {
      const datasets = this.listDatasets();
      const totalSize = datasets.reduce(
        (sum, dataset) => sum + dataset.size_bytes,
        0
      );

      // Estimate quota (this is approximate)
      let estimatedQuota = 10 * 1024 * 1024; // Conservative 10MB default

      try {
        // Try to get actual quota if available
        if ("storage" in navigator && "estimate" in navigator.storage) {
          navigator.storage
            .estimate()
            .then((estimate) => {
              if (estimate.quota) {
                estimatedQuota = Math.min(
                  estimate.quota * 0.8,
                  50 * 1024 * 1024
                ); // 80% of quota, max 50MB
              }
            })
            .catch(() => {});
        }
      } catch (e) {
        // Fallback to conservative estimate
      }

      const dates = datasets
        .map((d) => d.created_at)
        .filter((d) => d)
        .map((d) => new Date(d));

      const oldestDate = dates.length > 0 ? new Date(Math.min(...dates)) : null;
      const newestDate = dates.length > 0 ? new Date(Math.max(...dates)) : null;

      return {
        total_datasets: datasets.length,
        total_size_bytes: totalSize,
        estimated_quota_bytes: estimatedQuota,
        max_datasets_limit: this.maxDatasets,
        max_size_limit_bytes: this.maxStorageSize,
        supports_local_storage: this.isLocalStorageAvailable(),
        supports_compression: this.compressionEnabled,
        oldest_dataset_date: oldestDate ? oldestDate.toISOString() : null,
        newest_dataset_date: newestDate ? newestDate.toISOString() : null,
        usage_percentage:
          estimatedQuota > 0 ? (totalSize / estimatedQuota) * 100 : 0,
        corrupted_datasets: datasets.filter((d) => d.corrupted).length,
      };
    } catch (e) {
      console.error("Failed to get storage info:", e);
      return {
        total_datasets: 0,
        total_size_bytes: 0,
        estimated_quota_bytes: 0,
        max_datasets_limit: this.maxDatasets,
        max_size_limit_bytes: this.maxStorageSize,
        supports_local_storage: false,
        supports_compression: false,
        error: e.message,
      };
    }
  }

  /**
   * Check if localStorage is available
   */
  isLocalStorageAvailable() {
    try {
      const test = "__storage_test__";
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * Clean up corrupted or old datasets
   */
  cleanupStorage(maxAgeDays = 30) {
    try {
      const datasets = this.listDatasets();
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - maxAgeDays);

      let cleanedCount = 0;

      for (const dataset of datasets) {
        // Remove corrupted datasets
        if (dataset.corrupted) {
          this.deleteDataset(dataset.id);
          cleanedCount++;
          continue;
        }

        // Remove old datasets if we're over the limit
        if (datasets.length > this.maxDatasets && dataset.created_at) {
          const createdDate = new Date(dataset.created_at);
          if (createdDate < cutoffDate) {
            this.deleteDataset(dataset.id);
            cleanedCount++;
          }
        }
      }

      if (cleanedCount > 0) {
        console.log(`Cleaned up ${cleanedCount} datasets`);
      }

      return cleanedCount;
    } catch (e) {
      console.error("Failed to cleanup storage:", e);
      return 0;
    }
  }

  /**
   * Export a dataset as JSON file
   */
  exportDataset(datasetId) {
    try {
      const dataset = this.loadDataset(datasetId);
      if (!dataset) {
        throw new Error("Dataset not found");
      }

      const jsonStr = JSON.stringify(dataset, null, 2);
      const blob = new Blob([jsonStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `real_estate_dataset_${datasetId}_${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log(`Exported dataset ${datasetId}`);
      return true;
    } catch (e) {
      console.error("Failed to export dataset:", e);
      throw new Error(`Export failed: ${e.message}`);
    }
  }

  /**
   * Clear all storage (use with caution)
   */
  clearAllStorage() {
    try {
      localStorage.removeItem(this.storageKey);
      this.initializeStorage();
      console.log("Cleared all storage");
      return true;
    } catch (e) {
      console.error("Failed to clear storage:", e);
      return false;
    }
  }
}

// Make DatasetStorageManager globally available
window.DatasetStorageManager = DatasetStorageManager;

// Create global instance
window.datasetStorage = new DatasetStorageManager();

console.log("DatasetStorageManager loaded and initialized");
