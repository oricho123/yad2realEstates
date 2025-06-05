# Real Estate Price Analyzer

An interactive web dashboard for analyzing real estate prices from Yad2 listings.

## 🚀 Features

- **API Data Collection**: Direct access to Yad2's real estate API
- **Interactive Dashboard**: Filter properties by price, size, neighborhood, rooms, and condition
- **Dual Visualization**: Side-by-side scatter plot and interactive map views
- **Geographic Mapping**: Interactive map showing property locations with price-based color coding
- **Enhanced Value Analysis**: Trend lines, median lines, and value-based property scoring
- **Best Deals Identification**: Automatic detection of properties below market value
- **Neighborhood Ranking**: Affordability-based area comparison and ranking
- **Investment Decision Support**: Market insights and purchase recommendations
- **Advanced Analytics**: 5 comprehensive chart types with statistical insights
- **Clickable Listings**: Click on any property in chart or map to open the original Yad2 listing
- **Summary Statistics**: Real-time stats based on filtered data
- **Cross-Platform Filtering**: Changes in filters update all visualizations simultaneously

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
- **Neighborhood**: Dropdown for specific areas with exclusion options
- **Room Count**: Filter by number of rooms
- **Property Condition**: Filter by renovation status
- **Ad Type**: Private vs commercial listings

### Advanced Visualizations

- **Enhanced Scatter Plot**: Price vs Size with trend lines, median lines, and value-based color coding
- **Interactive Map**: Geographic distribution with price-based markers and clickable listings
- **Value Analysis**: Properties categorized as Excellent Deal, Good Deal, Fair Price, Above Market, or Overpriced
- **Analytics Dashboard**: 5 comprehensive charts including price histograms, box plots, and efficiency analysis
- **Neighborhood Ranking**: Affordability-based area comparison with property counts
- **Best Deals Table**: Top undervalued properties with savings percentages
- **Market Insights**: Investment recommendations and market overview

### Decision Support Tools

- **Trend Analysis**: Market trend line showing price-to-size correlation
- **Value Scoring**: Each property receives a market position score (% above/below trend)
- **Investment Opportunities**: Automatic identification of undervalued and overvalued properties
- **Budget Recommendations**: Price range suggestions based on market quartiles
- **Area Analysis**: Most affordable vs premium neighborhoods comparison

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

   - Run the scraper using the search controls
   - Use the neighborhood filter in the dashboard
   - Compare price/sqm across different conditions
   - View geographic distribution on the map

2. **Find best value properties**:

   - Look for outliers below the trend line in the scatter plot
   - Use the map to identify properties in desired areas
   - Filter by condition and room count
   - Click on interesting points in either view to open listings

3. **Geographic market analysis**:

   - Use the map to identify price clusters by area
   - Compare densely populated vs sparse areas
   - Analyze proximity to landmarks or transportation
   - Cross-reference map patterns with scatter plot trends

4. **Investment decision-making**:
   - Use the enhanced scatter plot to identify properties below the market trend line
   - Check the "Best Deals" table for properties with highest savings percentages
   - Review market insights for budget recommendations and area analysis
   - Compare neighborhoods using the affordability ranking chart
   - Look for green-colored properties (Excellent Deal/Good Deal) in the value analysis
5. **Comprehensive market analysis**:
   - Compare average price/sqm by neighborhood using filters and ranking charts
   - Analyze room efficiency (sqm per room) in the scatter plot
   - Check price distribution by property condition
   - Use dual-view to correlate location with price patterns
   - Review median lines and trend analysis for market positioning

## 🚀 Implementation Status

**Phase 1-5** ✅ **COMPLETE**:

- ✅ API scraper working
- ✅ Data processing pipeline
- ✅ Interactive dashboard
- ✅ Advanced filtering system
- ✅ Enhanced user experience

**Phase 6** ✅ **COMPLETE**:

- ✅ Interactive map visualization
- ✅ Side-by-side dual view layout
- ✅ Geographic property distribution
- ✅ Clickable map markers
- ✅ Responsive design

**Phase 7** ✅ **COMPLETE**:

- ✅ Advanced Analytics Dashboard (multiple chart types, box plots, trends)
- ✅ Price distribution histograms
- ✅ Neighborhood comparison charts
- ✅ Room efficiency analysis
- ✅ Statistical insights and visualizations

**Phase 7.5** ✅ **COMPLETE**:

- ✅ Enhanced Decision Support Analytics (trend lines, value analysis, best deals identification)
- ✅ Market trend line and median reference lines
- ✅ Value-based property categorization and scoring
- ✅ Best deals table with savings percentages
- ✅ Neighborhood affordability ranking
- ✅ Investment insights and market recommendations

**Next Phases** (Planned):

- [ ] **Phase 8**: Data Export & Persistence (CSV/Excel export, saved searches)
- [ ] **Phase 9**: ML & Price Prediction (price estimation models, market trends)
- [ ] **Phase 10**: Multi-Area Comparison (compare multiple cities simultaneously)

## 🎉 Success!

Your real estate analyzer is now ready! Open http://127.0.0.1:8051/ to start exploring property data.
