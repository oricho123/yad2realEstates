# New Properties Emphasis Feature - Execution Plan

## Overview

This document outlines the plan to add a feature that emphasizes new property ads that haven't been seen before. The feature will highlight these properties in the UI to help users identify fresh listings quickly.

## Current System Analysis

### Data Flow

1. **Scraping**: `src/scraping/` handles data collection from Yad2
2. **Storage**: Browser localStorage with `SimpleStorageManager`
3. **Visualization**: Scatter plot and map views in `src/visualization/charts/`
4. **UI**: Dash-based dashboard with callbacks in `src/dashboard/callbacks/`

### Data Structure

- Properties stored as records in browser localStorage
- Key fields: `id`, `token`, `price`, `square_meters`, `lat`, `lng`, `scraped_at`, etc.
- Client-side JavaScript handles storage operations (`assets/simple_storage.js`)

### Current Visualization

- Scatter plot with value categories (colors): Excellent Deal, Good Deal, Fair Price, Above Market, Overpriced
- Map view with property markers
- Interactive filtering and hover data

## Feature Requirements

### Core Functionality

1. **Identify New Properties**: Detect properties that weren't in previous searches
2. **Visual Distinction**: Show new properties with different styling
3. **Minimal Storage**: Avoid storing excessive historical data
4. **Simple Implementation**: Keep complexity low

### User Experience Goals

- Immediately see which properties are new since last search
- Different visual treatment (shape, border, icon) in scatter plot
- Optional: separate "New Properties" section or filter
- Maintain existing functionality without disruption

## Technical Approach

### Strategy: Simplified Override + Seen Index

Use a lightweight approach that preserves current storage behavior while adding new property detection:

1. **Main Property Data** (`real_estate_data`): **Keep current override behavior** - completely replaced on each search
2. **Lightweight Seen Index** (`real_estate_seen_index`): Just property IDs + first seen dates, kept indefinitely
3. **Pre-Save Detection**: Before saving to main storage, check seen index to mark new properties
4. **Visual Indicators**: Use different scatter plot symbols and colors for new properties
5. **Time-Based Aging**: Properties lose "new" status after time, but are never marked as "new" again

### Implementation Plan

#### Phase 1: Data Enhancement

1. **Enhance Property Model** (`src/data/models.py`)

   - Add `is_new` boolean field to `PropertyListing`
   - Add `first_seen_at` timestamp field
   - Update `to_dict()` and `from_dict()` methods

2. **Keep Storage Logic Simple** (`src/storage/simple_storage.py`)

   - **No changes needed** - keep current override behavior
   - New property detection handled entirely client-side

3. **Enhance Client Storage** (`assets/simple_storage.js`)
   - Add `detect_new_properties()` function using seen index
   - Integrate detection into existing save flow
   - **No complex cleanup logic** - main storage still overrides completely

#### Phase 2: Visualization Updates

1. **Update Scatter Plot** (`src/visualization/charts/scatter_plot.py`)

   - Add new symbol shapes for new properties (star, diamond, etc.)
   - Enhance color scheme to include "new property" indicator
   - Update hover template to show "NEW" badge

2. **Update Map View** (`src/visualization/charts/map_view.py`)
   - Add special markers for new properties
   - Different icon or border styling

#### Phase 3: UI Enhancements

1. **Add Filter Toggle** (`src/dashboard/components/filters.py`)

   - Add "Show only new properties" toggle
   - Add "Hide new properties" option

2. **Update Dashboard Layout** (`src/dashboard/layout.py`)

   - Add new properties count display
   - Optional: Add "New Properties" info card

3. **Enhance Callbacks** (`src/dashboard/callbacks/`)
   - Update visualization callbacks to handle new property styling
   - Update filtering callbacks for new property filters

#### Phase 4: Configuration & Polish

1. **Add Configuration** (`src/config/constants.py`)

   - Define "new property" time window (default: 24 hours)
   - Configure visual styling constants

2. **Update Hover Data** (`src/visualization/hover_data.py`)
   - Add "NEW" indicator to property hover templates
   - Show "first seen" timestamp

## Detailed Implementation

### 1. Property Model Enhancement

```python
# In src/data/models.py
@dataclass
class PropertyListing:
    # ... existing fields ...

    # New fields for tracking
    is_new: bool = field(default=False, init=False)
    first_seen_at: Optional[datetime] = None

    def mark_as_new(self, first_seen: Optional[datetime] = None):
        """Mark property as new with timestamp."""
        self.is_new = True
        self.first_seen_at = first_seen or datetime.now()

    def age_new_status(self, max_age_hours: int = 12) -> bool:
        """Age the 'new' status based on time. Returns True if still new."""
        if not self.is_new or not self.first_seen_at:
            return False

        age_hours = (datetime.now() - self.first_seen_at).total_seconds() / 3600
        if age_hours > max_age_hours:
            self.is_new = False

        return self.is_new
```

### 2. Enhanced Flow (No Server-Side Storage Changes)

```javascript
// Simplified flow - new property detection happens before saving
function enhanced_save_with_new_detection(newSearchData) {
  // 1. Check what's new using the lightweight seen index
  const processed =
    window.dash_clientside.storage.detect_new_properties(newSearchData);

  // 2. Save to main storage (override as before - no changes needed)
  const success = window.dash_clientside.storage.save_data(
    processed.processedData
  );

  // 3. Seen index was already updated inside detect_new_properties()

  console.log(
    `Saved ${processed.processedData.data.length} properties, ${processed.newCount} are new`
  );
  return success;
}
```

**Key Benefits:**

- ✅ **No server-side changes** to storage logic
- ✅ **Preserves current override behavior**
- ✅ **All detection logic client-side** for simplicity

### 3. Visualization Enhancement

```python
# In src/visualization/charts/scatter_plot.py
def _create_base_scatter_plot(self, plot_df: pd.DataFrame) -> go.Figure:
    """Enhanced scatter plot with new property indicators."""

    # Create custom symbol mapping
    plot_df['symbol'] = plot_df.apply(
        lambda row: 'star' if row.get('is_new', False) else 'circle',
        axis=1
    )

    # Enhanced color mapping including new properties
    plot_df['display_category'] = plot_df.apply(
        lambda row: f"🆕 NEW {row['value_category']}" if row.get('is_new', False)
                   else row['value_category'],
        axis=1
    )

    fig = px.scatter(
        plot_df,
        x='square_meters',
        y='price',
        color='display_category',
        symbol='symbol',
        size='rooms',
        # ... rest of configuration
    )

    return fig

def _get_enhanced_color_mapping(self) -> Dict[str, str]:
    """Color mapping including new property variants."""
    base_colors = self._get_value_category_colors()

    # Add new property colors (brighter/different variants)
    new_colors = {}
    for category, color in base_colors.items():
        new_colors[f"🆕 NEW {category}"] = self._brighten_color(color)

    return {**base_colors, **new_colors}
```

### 4. Client-Side Enhancements

```javascript
// In assets/simple_storage.js
// Simplified approach: Main storage (override) + lightweight seen index
const PROPERTY_DATA_KEY = "real_estate_data"; // Main storage (unchanged behavior)
const PROPERTY_SEEN_KEY = "real_estate_seen_index"; // Just IDs + dates, permanent

// Configuration constants
const NEW_PROPERTY_MAX_AGE_HOURS = 12; // 12 hours - easily configurable

window.dash_clientside.storage.detect_new_properties = function (
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

    // Process each property against the seen index
    const processedData = newData.data.map((prop) => {
      const propId = prop.id || prop.token;

      if (!propId) return prop; // Skip properties without ID

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

        return {
          ...prop,
          is_new: true,
          first_seen_at: seenIndex[propId].first_seen,
        };
      } else {
        // Property seen before - check if still within "new" window
        const firstSeen = new Date(everSeen.first_seen);
        const ageHours =
          (now.getTime() - firstSeen.getTime()) / (1000 * 60 * 60);

        return {
          ...prop,
          is_new: ageHours <= maxAgeHours,
          first_seen_at: everSeen.first_seen,
        };
      }
    });

    // Save updated seen index (lightweight, permanent)
    localStorage.setItem(PROPERTY_SEEN_KEY, JSON.stringify(seenIndex));

    return {
      newCount,
      processedData: { ...newData, data: processedData },
      seenIndexSize: Object.keys(seenIndex).length,
    };
  } catch (e) {
    console.error("Error detecting new properties:", e);
    return { newCount: 0, processedData: newData };
  }
};

// Optional: Cleanup seen index (only if it gets too large)
window.dash_clientside.storage.cleanup_seen_index = function (
  maxAgeMonths = 12
) {
  try {
    const seenIndex = JSON.parse(
      localStorage.getItem(PROPERTY_SEEN_KEY) || "{}"
    );
    const cutoffDate = new Date(
      Date.now() - maxAgeMonths * 30 * 24 * 60 * 60 * 1000
    );
    const originalSize = Object.keys(seenIndex).length;

    // Remove very old entries (older than 12 months)
    Object.keys(seenIndex).forEach((id) => {
      const firstSeen = new Date(seenIndex[id].first_seen);
      if (firstSeen < cutoffDate) {
        delete seenIndex[id];
      }
    });

    const cleanedSize = Object.keys(seenIndex).length;
    const removedCount = originalSize - cleanedSize;

    if (removedCount > 0) {
      localStorage.setItem(PROPERTY_SEEN_KEY, JSON.stringify(seenIndex));
      console.log(`Cleaned ${removedCount} very old entries from seen index`);
    }

    return { cleaned: removedCount, remaining: cleanedSize };
  } catch (e) {
    console.error("Error cleaning seen index:", e);
    return { cleaned: 0, error: e.message };
  }
};
```

## Configuration Options

### Constants to Add

```python
# In src/config/constants.py
class NewPropertyConfig:
    """Configuration for new property detection and display."""

    # Time-based settings
    NEW_PROPERTY_MAX_AGE_HOURS = 12  # 12 hours - properties stay "new" for 12 hours
    AUTO_AGING_ENABLED = True

    # Visual settings
    NEW_PROPERTY_SYMBOL = 'star'
    NEW_PROPERTY_COLOR_BRIGHTNESS = 1.3
    NEW_PROPERTY_BORDER_WIDTH = 3

    # UI settings
    SHOW_NEW_COUNT_IN_TITLE = True
    NEW_PROPERTY_BADGE_TEXT = "🆕 NEW"
```

```javascript
// In assets/simple_storage.js - Configuration constants at the top
const NEW_PROPERTY_MAX_AGE_HOURS = 12; // 12 hours - easily configurable
const PROPERTY_DATA_KEY = "real_estate_data";
const PROPERTY_SEEN_KEY = "real_estate_seen_index";
```

## Testing Strategy

### Unit Tests

1. Test new property detection logic
2. Test aging mechanism
3. Test visualization updates

### Integration Tests

1. Test complete scraping -> storage -> visualization flow
2. Test new property persistence across sessions
3. Test performance with large datasets

### User Testing

1. Verify visual distinction is clear
2. Test usability of new property filters
3. Validate performance impact

## Migration & Rollout

### Backward Compatibility

- Existing stored data will work without modification
- Properties without `is_new` field default to `false`
- Graceful handling of missing `first_seen_at` timestamps

### Rollout Steps

1. Deploy enhanced data models (no visual changes yet)
2. Update storage logic to start tracking new properties
3. Deploy visualization enhancements
4. Add UI toggles and filters
5. Gather user feedback and iterate

## Success Metrics

### Technical Metrics

- No performance degradation in visualization rendering
- Storage size increase < 10%
- New property detection accuracy > 95%

### User Metrics

- User engagement with new property features
- Time to identify new properties reduced
- User feedback on visual clarity

## Future Enhancements

### Phase 2 Features

1. **Historical Tracking**: Optional deeper history for power users
2. **Custom Time Windows**: User-configurable "new" property age
3. **New Property Notifications**: Alert system for new properties in saved searches
4. **Comparison Mode**: Side-by-side view of new vs existing properties

### Advanced Features

1. **Property Change Detection**: Track price changes, not just new listings
2. **Trend Analysis**: Show if new properties are above/below market trends
3. **Smart Filtering**: ML-based recommendations for new properties matching user preferences

## Risk Mitigation

### Performance Risks

- **Mitigation**: Implement efficient comparison algorithms
- **Monitoring**: Track rendering performance with new features

### Storage Risks

- **Mitigation**: Implement automatic cleanup of old "new" markers
- **Fallback**: Graceful degradation if storage quota exceeded

### User Experience Risks

- **Mitigation**: Comprehensive testing with real users
- **Fallback**: Toggle to disable new property features

## Simplified Implementation Summary

### Storage Architecture

| Storage Key              | Purpose                    | Behavior                                | Size Impact              |
| ------------------------ | -------------------------- | --------------------------------------- | ------------------------ |
| `real_estate_data`       | **Current search results** | **Override on each search** (unchanged) | ~50KB per search         |
| `real_estate_seen_index` | **New property detection** | Grows incrementally                     | ~2KB per 1000 properties |

### Key Simplifications

✅ **No server-side storage changes** - Keep current override behavior  
✅ **No complex cleanup logic** - Main storage works exactly as before  
✅ **All detection client-side** - Simple integration with existing flow  
✅ **Minimal storage growth** - Only lightweight index grows slowly

### Implementation Flow

```
1. User searches → Scraper returns new data
2. Client-side: Check new data against seen index ✅ IMPLEMENTED
3. Client-side: Mark new properties with is_new=true ✅ IMPLEMENTED
4. Client-side: Save to main storage (override as usual) ✅ IMPLEMENTED
5. Client-side: Update seen index with new property IDs ✅ IMPLEMENTED
```

### Completed Phases ✅

| Phase                        | Status      | Key Achievements                                 |
| ---------------------------- | ----------- | ------------------------------------------------ |
| **Phase 1: Foundation**      | ✅ COMPLETE | Constants, data models, storage detection        |
| **Phase 2: Integration**     | ✅ COMPLETE | Scraping callbacks, visualization, summary stats |
| **Phase 3: UI Enhancements** | 🔄 READY    | Filters, toggles, advanced UI features           |

## Conclusion

This feature will provide significant value to users by highlighting fresh property listings while maintaining the application's simplicity and performance. The implementation is designed to be lightweight, backward-compatible, and easily extensible for future enhancements.

The simplified override + seen index approach minimizes complexity while providing robust new property identification. The visual enhancements will make new properties immediately apparent without overwhelming the existing interface.
