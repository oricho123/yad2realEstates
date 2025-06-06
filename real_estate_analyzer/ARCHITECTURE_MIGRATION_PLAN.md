# 🏗️ Architecture Migration Plan: Simple Browser Storage

## 📋 Executive Summary

**Problem:** The current real estate analyzer uses local file storage (CSV/JSON) which creates conflicts when multiple users access the application simultaneously. When one user scrapes new data, it overwrites the data for all other users.

**Solution:** Migrate to simple browser-based storage (localStorage) where each user session maintains one dataset that auto-saves when scraping and auto-loads when opening the page.

**Benefits:**

- ✅ Multi-user support without data conflicts
- ✅ No server-side storage requirements
- ✅ Reduced server disk usage
- ✅ Simple auto-save/load behavior
- ✅ Each user maintains their own latest search

---

## 🎯 Current Architecture Analysis

### Data Flow Issues

```
User A scrapes data → Saves to data/scraped/real_estate_listings_DATE.csv
User B visits site → Loads same CSV file (User A's data)
User B scrapes data → Overwrites CSV file
User A refreshes → Now sees User B's data (conflict!)
```

### Current Components Affected

1. **Data Storage:** `src/data/loaders.py` - PropertyDataLoader
2. **Scraping:** `src/scraping/yad2_scraper.py` - Saves CSV/JSON files
3. **Dashboard State:** `src/dashboard/layout.py` - Uses dcc.Store('memory')
4. **Callbacks:** `src/dashboard/callbacks/scraping.py` - Loads from files
5. **Main App:** `main.py` - Initial data loading from latest file

---

## 📐 Target Architecture

### Simple Browser-Based Data Flow

```
User A → Scrapes data → Auto-saves to User A's localStorage → User A sees own data
User B → Scrapes data → Auto-saves to User B's localStorage → User B sees own data
Page load → Auto-loads user's latest data if exists
```

### Storage Strategy

- **Single Dataset:** One dataset per user in localStorage
- **Auto-Save:** Automatically save when new data is scraped
- **Auto-Load:** Automatically load when page opens
- **Data Format:** JSON
- **Key:** Simple fixed key `real_estate_data`

---

## 🚀 Implementation Plan

## **Phase 1: Simple Browser Storage (1 day)**

### 1.1 Create Simple Storage Utilities

**New File: `src/storage/simple_storage.py`**

```python
class SimpleStorageManager:
    """Simple browser storage for single dataset."""

    STORAGE_KEY = 'real_estate_data'

    def save_data(self, df: pd.DataFrame) -> bool:
        """Save DataFrame to browser storage."""

    def load_data(self) -> Optional[pd.DataFrame]:
        """Load DataFrame from browser storage."""

    def has_data(self) -> bool:
        """Check if data exists in storage."""

    def clear_data(self) -> bool:
        """Clear stored data."""
```

### 1.2 Client-Side Storage

**New File: `assets/simple_storage.js`**

```javascript
// Simple storage operations
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  storage: {
    save_data: function (data) {
      localStorage.setItem("real_estate_data", JSON.stringify(data));
      return true;
    },

    load_data: function () {
      const data = localStorage.getItem("real_estate_data");
      return data ? JSON.parse(data) : null;
    },

    has_data: function () {
      return localStorage.getItem("real_estate_data") !== null;
    },
  },
});
```

---

## **Phase 2: Update Scraping (1 day)**

### 2.1 Remove File Operations

**Update `src/scraping/yad2_scraper.py`:**

```python
class Yad2Scraper:
    def __init__(self):
        # Remove output_dir parameter
        # No file operations

    def scrape(self, params: ScrapingParams) -> ScrapingResult:
        # Return data directly, no file saving
        return ScrapingResult(
            success=True,
            data=scraped_df,  # Direct DataFrame
            listings_count=len(scraped_df)
        )
```

### 2.2 Update Scraping Callbacks

**Modify `src/dashboard/callbacks/scraping.py`:**

```python
# Add auto-save clientside callback
@app.clientside_callback(
    """
    function(data) {
        if (data && data.length > 0) {
            localStorage.setItem('real_estate_data', JSON.stringify(data));
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('storage-status', 'children'),
    Input('current-data', 'data')
)

def handle_scrape_request(...):
    result = scraper.scrape(scraping_params)

    if result.success:
        # Return data to be auto-saved
        return result.data.to_dict('records')
    else:
        return dash.no_update
```

---

## **Phase 3: Auto-Load on Startup (1 day)**

### 3.1 Update Main App

**Modify `main.py`:**

```python
def load_initial_data() -> PropertyDataFrame:
    """Return empty DataFrame - browser will load if exists."""
    return PropertyDataFrame(pd.DataFrame())

def main():
    # Remove all file loading logic
    initial_data = load_initial_data()  # Always empty
    app = create_real_estate_app(initial_data)
    app.run(debug=args.debug, port=args.port, host=args.host)
```

### 3.2 Add Auto-Load Callback

**Add to layout initialization:**

```python
# Auto-load callback
@app.clientside_callback(
    """
    function(_) {
        const stored_data = localStorage.getItem('real_estate_data');
        if (stored_data) {
            return JSON.parse(stored_data);
        }
        return [];
    }
    """,
    Output('current-data', 'data'),
    Input('app-load-trigger', 'children'),
    prevent_initial_call=False
)
```

---

## **Phase 4: Clean Up (1 day)**

### 4.1 Remove File Dependencies

**Remove/Update:**

- All file path references
- `PropertyDataLoader.find_latest_data_file()`
- Data directory setup
- File cleanup logic

### 4.2 Update Configuration

**Simplify `src/config/settings.py`:**

```python
class AppSettings:
    # Remove all file-related settings
    # Remove DATA_DIRECTORY

    # Simple storage key
    STORAGE_KEY = 'real_estate_data'
```

---

## 📋 Simple Implementation Checklist

### Phase 1: Simple Storage ✅

- [ ] Create `SimpleStorageManager`
- [ ] Add basic client-side storage JavaScript
- [ ] Test save/load functionality

### Phase 2: Scraping Updates ✅

- [ ] Remove file saving from scraper
- [ ] Add auto-save callback after scraping
- [ ] Test scraping → auto-save flow

### Phase 3: Auto-Load ✅

- [ ] Remove file loading from startup
- [ ] Add auto-load callback on page load
- [ ] Test page load → auto-load flow

### Phase 4: Cleanup ✅

- [ ] Remove all file references
- [ ] Clean up configuration
- [ ] Update tests
- [ ] Remove data directory requirements

---

## 🎯 Simple Data Flow

### Current (File-Based)

```
Page Load → Find latest CSV → Load data → Display
Scrape → Save CSV → Load CSV → Display
```

### New (Browser Storage)

```
Page Load → Check localStorage → Load if exists → Display
Scrape → Get data → Auto-save to localStorage → Display
```

---

## ✅ Expected Results

1. **Multi-User Support**: Each user has isolated data in their browser
2. **Zero Configuration**: No data directories or file management
3. **Seamless Experience**: Auto-save when scraping, auto-load when opening
4. **Simple Architecture**: One dataset, automatic persistence
5. **No Conflicts**: Users never see each other's data

---

## 🚀 Implementation Timeline

- **Day 1**: Simple storage utilities and client-side code
- **Day 2**: Update scraping to remove files and add auto-save
- **Day 3**: Add auto-load on page startup
- **Day 4**: Clean up file dependencies and test

**Total: 4 days** for complete migration to simple browser storage.

This approach eliminates all the complexity of dataset management while solving the core multi-user conflict issue. Each user gets a seamless experience with their own persistent data.
