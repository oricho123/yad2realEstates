/**
 * Enhanced Storage Manager - Simplified override + seen index for new property detection
 *
 * Provides localStorage operations with simplified approach:
 * 1. Main property data (override on each search - unchanged behavior)
 * 2. Lightweight seen index (permanent tracking for new property detection)
 */

// Configuration constants
const NEW_PROPERTY_MAX_AGE_HOURS = 12; // 12 hours - easily configurable

// Storage keys
const PROPERTY_DATA_KEY = "real_estate_data"; // Main storage (unchanged behavior)
const PROPERTY_SEEN_KEY = "real_estate_seen_index"; // Just IDs + dates, permanent

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
          PROPERTY_DATA_KEY,
          JSON.stringify(dataWithTimestamp)
        );

        // Get property count from payload
        const propertyCount =
          dataWithTimestamp.property_count ||
          (dataWithTimestamp.data ? dataWithTimestamp.data.length : 0) ||
          0;
        console.log(`Saved ${propertyCount} properties to localStorage`);
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
        const data = localStorage.getItem(PROPERTY_DATA_KEY);

        if (!data) {
          console.log("No stored data found");
          return null;
        }

        const parsed = JSON.parse(data);
        console.log(`Loaded ${parsed.data?.length || 0} properties`);
        return parsed;
      } catch (e) {
        console.error("Failed to load data from localStorage:", e);
        return null;
      }
    },

    has_data: function () {
      try {
        const data = localStorage.getItem(PROPERTY_DATA_KEY);
        return data !== null;
      } catch (e) {
        console.error("Failed to check data existence:", e);
        return false;
      }
    },

    clear_data: function () {
      try {
        localStorage.removeItem(PROPERTY_DATA_KEY);
        // NOTE: Do NOT clear PROPERTY_SEEN_KEY - it should be permanent for new property detection
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
        const data = localStorage.getItem(PROPERTY_DATA_KEY);

        if (!data) {
          return null;
        }

        const parsed = JSON.parse(data);
        return parsed.search_filters || null;
      } catch (e) {
        console.error("Failed to get search filters from localStorage:", e);
        return null;
      }
    },

    // NEW: Simplified new property detection using seen index
    detect_new_properties: function (
      newData,
      maxAgeHours = NEW_PROPERTY_MAX_AGE_HOURS
    ) {
      try {
        // Load lightweight seen index (permanent tracking)
        const seenIndex = JSON.parse(
          localStorage.getItem(PROPERTY_SEEN_KEY) || "{}"
        );

        let newCount = 0;
        const now = new Date();

        // Process each property against the seen index (just track, don't modify data)
        newData.data.forEach((prop) => {
          const propId = prop.id || prop.token;

          if (!propId) return; // Skip properties without ID

          // Check if we've EVER seen this property before
          const everSeen = seenIndex[propId];

          if (!everSeen) {
            // Truly new property - never seen before
            seenIndex[propId] = {
              first_seen: now.toISOString(),
              neighborhood: prop.neighborhood || "",
              price_range: prop.price
                ? Math.round(prop.price / 100000) * 100000
                : 0,
            };
            newCount++;
          }
          // Note: We don't modify the property data itself anymore
        });

        // Save updated seen index (lightweight, permanent)
        localStorage.setItem(PROPERTY_SEEN_KEY, JSON.stringify(seenIndex));

        return {
          newCount,
          processedData: newData, // Return original data unchanged
          seenIndexSize: Object.keys(seenIndex).length,
        };
      } catch (e) {
        console.error("Error detecting new properties:", e);
        return { newCount: 0, processedData: newData };
      }
    },

    // Calculate is_new status on-the-fly when loading data
    add_new_status_to_data: function (
      data,
      maxAgeHours = NEW_PROPERTY_MAX_AGE_HOURS
    ) {
      try {
        const seenIndex = JSON.parse(
          localStorage.getItem(PROPERTY_SEEN_KEY) || "{}"
        );
        const now = new Date();

        return data.map((prop) => {
          const propId = prop.id || prop.token;

          if (!propId) {
            return { ...prop, is_new: false };
          }

          const everSeen = seenIndex[propId];

          if (!everSeen) {
            return { ...prop, is_new: false }; // Not in index = not new anymore
          }

          // Check if still within "new" window
          const firstSeen = new Date(everSeen.first_seen);
          const ageHours =
            (now.getTime() - firstSeen.getTime()) / (1000 * 60 * 60);

          return {
            ...prop,
            is_new: ageHours <= maxAgeHours,
            first_seen_at: everSeen.first_seen,
          };
        });
      } catch (e) {
        console.error("Error adding new status:", e);
        return data.map((prop) => ({ ...prop, is_new: false }));
      }
    },
  },
});

console.log(
  `Enhanced Storage Manager loaded - NEW properties tracked for ${NEW_PROPERTY_MAX_AGE_HOURS} hours`
);
