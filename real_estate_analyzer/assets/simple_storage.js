/**
 * Simple Storage Manager - Client-side storage for single dataset
 *
 * Provides basic localStorage operations for auto-save/auto-load functionality
 * with a fixed storage key for seamless user experience.
 */

// Simple storage operations
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  storage: {
    save_data: function (data) {
      try {
        if (!data) {
          console.warn("No data provided for saving");
          return false;
        }

        // Add timestamp to track when data was saved
        const dataWithTimestamp = {
          ...data,
          saved_at: new Date().toISOString(),
          version: "1.0",
        };

        localStorage.setItem(
          "real_estate_data",
          JSON.stringify(dataWithTimestamp)
        );

        // Get property count from payload
        const propertyCount =
          dataWithTimestamp.property_count ||
          (dataWithTimestamp.data ? dataWithTimestamp.data.length : 0) ||
          0;
        console.log(
          `Saved ${propertyCount} properties to localStorage at ${dataWithTimestamp.saved_at}`
        );
        return true;
      } catch (e) {
        console.error("Failed to save data to localStorage:", e);

        if (e.name === "QuotaExceededError" || e.code === 22) {
          console.error("Storage quota exceeded");
          // Could show user notification here
        }

        return false;
      }
    },

    load_data: function () {
      try {
        const data = localStorage.getItem("real_estate_data");

        if (!data) {
          console.log("No stored data found");
          return null;
        }

        const parsed = JSON.parse(data);
        console.log(
          `Loaded ${parsed.data?.length || 0} properties from localStorage`
        );
        return parsed;
      } catch (e) {
        console.error("Failed to load data from localStorage:", e);
        return null;
      }
    },

    has_data: function () {
      try {
        const data = localStorage.getItem("real_estate_data");
        const hasData = data !== null;
        console.log(`Storage has data: ${hasData}`);
        return hasData;
      } catch (e) {
        console.error("Failed to check data existence:", e);
        return false;
      }
    },

    clear_data: function () {
      try {
        localStorage.removeItem("real_estate_data");
        console.log("Cleared stored data");
        return true;
      } catch (e) {
        console.error("Failed to clear data:", e);
        return false;
      }
    },

    get_storage_info: function () {
      try {
        const data = localStorage.getItem("real_estate_data");

        if (!data) {
          return {
            has_data: false,
            size_bytes: 0,
            property_count: 0,
            saved_at: null,
          };
        }

        const parsed = JSON.parse(data);
        const sizeBytes = new Blob([data]).size;

        return {
          has_data: true,
          size_bytes: sizeBytes,
          property_count: parsed.property_count || parsed.data?.length || 0,
          saved_at: parsed.saved_at || null,
          version: parsed.version || "unknown",
          has_search_filters: !!parsed.search_filters,
        };
      } catch (e) {
        console.error("Failed to get storage info:", e);
        return {
          has_data: false,
          size_bytes: 0,
          property_count: 0,
          saved_at: null,
          error: e.message,
        };
      }
    },

    get_search_filters: function () {
      try {
        const data = localStorage.getItem("real_estate_data");

        if (!data) {
          console.log("No stored data found for search filters");
          return null;
        }

        const parsed = JSON.parse(data);
        if (parsed.search_filters) {
          console.log("Found saved search filters:", parsed.search_filters);
          return parsed.search_filters;
        } else {
          console.log("No search filters found in stored data");
          return null;
        }
      } catch (e) {
        console.error("Failed to get search filters from localStorage:", e);
        return null;
      }
    },
  },
});

console.log(
  "Simple Storage Manager loaded - ready for auto-save/load operations"
);
