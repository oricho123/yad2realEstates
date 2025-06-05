# Real Estate Price Analyzer

An interactive web dashboard for analyzing real estate prices from Yad2 listings.

## 🚀 Features

- **API Data Collection**: Direct access to Yad2's real estate API
- **Interactive Dashboard**: Filter properties by price, size, neighborhood, rooms, and condition
- **Price Analysis**: Visualize price per square meter trends
- **Clickable Listings**: Click on any property to open the original Yad2 listing
- **Summary Statistics**: Real-time stats based on filtered data

## 📊 Key Metrics

- **Price per Square Meter**: Primary comparison metric
- **Room Efficiency**: Square meters per room analysis
- **Neighborhood Comparison**: Price trends by area
- **Property Condition**: Impact on pricing

## 🛠️ Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Quick Start

1. **Run with default parameters** (Kiryat Bialik area, ₪1.35M-₪1.42M):

   ```bash
   python real_estate_analyzer.py
   ```

2. **Use existing data** (skip scraping):

   ```bash
   python real_estate_analyzer.py --skip-scrape
   ```

3. **Custom search parameters**:
   ```bash
   python real_estate_analyzer.py --city 9500 --area 6 --min-price 1000000 --max-price 2000000
   ```

## 📈 Dashboard Features

### Interactive Filters

- **Price Range**: Slider to filter by price range
- **Size Range**: Filter by square meters
- **Neighborhood**: Dropdown for specific areas
- **Room Count**: Filter by number of rooms
- **Property Condition**: Filter by renovation status
- **Ad Type**: Private vs commercial listings

### Visualization

- **Scatter Plot**: Price vs Size (colored by price/sqm, sized by rooms)
- **Hover Info**: Detailed property information
- **Clickable Points**: Open listings in new tab
- **Summary Cards**: Key statistics

## 🔧 Command Line Options

```bash
python real_estate_analyzer.py [OPTIONS]

Options:
  --output-dir DIR     Directory to save scraped data (default: scraped_real_estate)
  --city INT           City ID to scrape (default: 9500)
  --area INT           Area ID to scrape (default: 6)
  --top-area INT       Top area ID to scrape (default: 25)
  --min-price INT      Minimum price filter (default: 1350000)
  --max-price INT      Maximum price filter (default: 1420000)
  --skip-scrape        Skip scraping and use existing data
  --port INT           Port to run the web server on (default: 8051)
```

## 📁 File Structure

```
real_estate_analyzer/
├── real_estate_analyzer.py    # Main application
├── real_estate_scraper.py     # API data collection
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── scraped_real_estate/       # Data directory
    ├── raw_api_response_*.json
    └── real_estate_listings_*.csv
```

## 📊 Data Fields

The scraper collects these key fields:

- **Basic**: Price, rooms, square meters, property type
- **Location**: City, neighborhood, street, coordinates
- **Details**: Floor, condition, ad type
- **Calculated**: Price per sqm, sqm per room
- **Links**: Full URL to original listing

## 🌐 API Parameters

To find different areas/cities, check the Yad2 website URLs:

- `city`: City ID (visible in URL)
- `area`: Area ID (visible in URL)
- `topArea`: Top area ID (visible in URL)

Example URL: `https://www.yad2.co.il/realestate/forsale?city=9500&area=6&topArea=25`

## 🎯 Usage Examples

1. **Analyze specific neighborhood**:

   - Run the scraper
   - Use the neighborhood filter in the dashboard
   - Compare price/sqm across different conditions

2. **Find best value properties**:

   - Look for outliers below the trend line
   - Filter by condition and room count
   - Click on interesting points to view listings

3. **Market analysis**:
   - Compare average price/sqm by neighborhood
   - Analyze room efficiency (sqm per room)
   - Check price distribution by property condition

## 🚀 Next Steps

Phase 1 ✅ **COMPLETE**:

- ✅ API scraper working
- ✅ Data processing pipeline
- ✅ Interactive dashboard
- ✅ Clickable listings

Future enhancements:

- [ ] Map visualization
- [ ] Historical price tracking
- [ ] Price prediction models
- [ ] Multiple area comparison
- [ ] Export filtered results

## 🎉 Success!

Your real estate analyzer is now ready! Open http://127.0.0.1:8051/ to start exploring property data.
