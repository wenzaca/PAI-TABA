# Ireland Environmental Data Analysis

## Project Overview

This project analyzes the relationship between air pollution, water quality, and population demographics in Ireland. The analysis integrates multiple datasets from the Central Statistics Office (CSO) Ireland to identify patterns and correlations between environmental indicators and demographic changes across Irish counties.

## Team Members
- Wendler Zacariotto - 19110260
- Felipe Signorini - 24235750 
- Oisin Carroll - 25113089

## Research Questions

**Primary Question:** What is the relationship between air pollution, water quality, and population growth in Ireland?

**Secondary Questions:**
- How do pollution levels correlate with water quality across Irish counties?
- What is the impact of population growth on environmental indicators?
- Which counties show the best/worst environmental performance?
- How have pollution and water quality trends evolved over time?

## Datasets Used

1. **Air Emissions Data (EAA20)** - 735 records
   - Source: CSO Ireland StatBank API
   - Content: National air emissions by pollutant type (CO2, NOx, PM2.5, etc.)
   - Coverage: 2009-2023 (15-year time series)
   - Scope: National-level aggregates

2. **Water Quality Data (EPA02)** - 249 records
   - Source: CSO Ireland StatBank API
   - Content: Bathing water quality classifications by county
   - Coverage: 2021-2024 (4-year observation window)
   - Scale: County-level with quality ratings (Excellent, Good, Sufficient, Poor)

3. **Population Data (G0420)** - 54 records
   - Source: CSO Ireland Census data
   - Content: County population counts from census years
   - Coverage: 2011, 2016, 2022 census periods
   - Granularity: County-level demographics

## Project Structure

```
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── test_setup.py          # Setup verification script
├── show_results.py        # Results display utility
├── README.md              # This file
├── src/                   # Source code modules
│   ├── __init__.py
│   ├── constants.py       # Centralized constants and column names
│   ├── data_collector.py  # Data collection from CSO StatBank API
│   ├── database_manager.py # SQLite database operations
│   ├── data_processor.py  # Data cleaning, normalization, and integration
│   ├── analyzer.py        # Statistical analysis and correlation detection
│   ├── analysis_results.py # Data structures for analysis results
│   └── dashboard_visualizer.py # Interactive dashboard generation
├── templates/             # HTML templates for dashboard
│   ├── dashboard.html     # Main dashboard template with styling
│   └── README.md          # Template documentation
├── data/                  # Database and raw data files
├── output/                # Generated visualizations and reports
└── logs/                  # Application logs
```

## Installation and Setup

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis:**
   ```bash
   python main.py
   ```

## Key Features

### Data Collection
- Automated data collection from CSO Ireland StatBank API
- Fallback mechanisms for API failures
- Data validation and quality checks
- Structured storage in SQLite database

### Data Processing
- County name normalization for consistent merging
- National-to-county emission allocation based on population proportion
- Three integrated datasets:
  1. **Pollution vs Population** (census years: 2011, 2016, 2022)
  2. **Pollution vs Water Quality** (water quality years: 2021-2024)
  3. **Water Quality vs Population** (water quality years with 2022 census forward-filled)
- Derived metrics: pollution index, emissions per capita, estimated county emissions

### Analysis Capabilities
- Correlation analysis between pollution, water quality, and population
- Statistical significance testing (Pearson correlation, p-values)
- Temporal trend analysis (linear regression, Mann-Kendall tests)
- County-level performance rankings
- ANOVA tests for county differences
- Population impact assessment on environmental indicators

### Visualizations
- Comprehensive interactive dashboard with 18 analytical components:
  - Water quality trends (national and county-level)
  - Pollution temporal analysis (2009-2023)
  - Population growth patterns (year-over-year and census periods)
  - Correlation heatmaps (pollution-water, overall metrics)
  - Scatter plots (pollution vs water quality, population vs emissions)
  - County rankings and comparisons
  - Data quality and coverage metrics
- All visualizations are interactive with hover tooltips and legend filtering

## Key Findings

### Data Integration Results
- **Counties Analyzed:** 17 counties with complete water quality and population data
- **Temporal Coverage:** Water quality (2021-2024), Pollution (2009-2023), Census (2011, 2016, 2022)
- **Integrated Records:** 57 county-year observations combining all three datasets

### Pollution-Water Quality Relationship
- Correlation analysis between estimated county emissions and water quality scores
- National pollution trends show temporal patterns from 2009-2023
- County-level water quality varies significantly across Ireland

### Population-Environment Correlations
- Population growth patterns analyzed across three census periods
- Emissions per capita calculated using national population totals
- Estimated county emissions allocated based on population proportion

### County Performance
- Water quality rankings identify best and worst performing counties
- Population density shows varying relationships with environmental indicators
- Year-over-year population growth rates differ significantly by county

### Temporal Trends
- National pollution index tracked over 15-year period (2009-2023)
- Water quality trends analyzed over 4-year observation window (2021-2024)
- Census period comparisons show demographic changes (2011→2016→2022)

## Technical Implementation

### Database Design
- SQLite database (`data/ireland_analysis.db`)
- Tables: raw_pollution, raw_water_quality, raw_population, analysis_results
- Efficient storage and retrieval of multi-year datasets

### Analysis Methods
- **Correlation Analysis:** Pearson correlation with significance testing
- **Trend Analysis:** Linear regression, Kendall's tau for temporal trends
- **Statistical Tests:** ANOVA for county comparisons, significance testing (α=0.05)
- **Derived Metrics:** Pollution index, emissions per capita, estimated county emissions

### Visualization Tools
- **Plotly:** Interactive dashboard with 18 components
- **Subplots:** Multi-panel layout organized by analytical theme
- **Interactive Features:** Hover tooltips, legend filtering, pan/zoom capabilities
- **Template-Based Design:** Separates HTML/CSS from Python logic for easier customization

## Usage Examples

### Running Individual Components

```python
from src.data_collector import DataCollector
from src.database_manager import DatabaseManager
from src.data_processor import DataProcessor

# Collect data from CSO StatBank API
collector = DataCollector()
datasets = collector.collect_all_datasets()

# Store in database
db_manager = DatabaseManager()
db_manager.store_datasets(datasets)

# Process and integrate datasets
processor = DataProcessor()
processed_data = processor.process_all_data(db_manager)
```

### Custom Analysis

```python
from src.analyzer import IrelandDataAnalyzer

# Perform statistical analysis
analyzer = IrelandDataAnalyzer()
results = analyzer.analyze_patterns(processed_data)

# Access specific results
correlations = results['correlations']
trends = results['trends']
county_analysis = results['county_analysis']
```

## Configuration

Key settings can be modified in `config.py`:
- Database paths
- API endpoints
- Analysis parameters
- Visualization settings

## Output Files

The analysis generates the following output:
- `output/comprehensive_dashboard.html` - Interactive dashboard with 18 visualizations
- `data/ireland_analysis.db` - SQLite database with all datasets and results
- `logs/app.log` - Application execution logs

## Dependencies

Key Python packages:
- **pandas, numpy** - Data manipulation and numerical operations
- **plotly** - Interactive visualizations and dashboard
- **scipy** - Statistical analysis (correlation, regression, significance tests)
- **scikit-learn** - Data preprocessing (StandardScaler)
- **requests** - CSO StatBank API calls
- **sqlite3** - Database operations

## Troubleshooting

### Common Issues

1. **API connection failures:**
   - The system automatically falls back to cached data if API calls fail
   - Check internet connection for fresh data collection
   - Verify CSO StatBank API availability

2. **Missing data directories:**
   - Run `python main.py` - directories are created automatically
   - Ensure write permissions for `data/`, `output/`, and `logs/` folders

3. **County name mismatches:**
   - County names are automatically normalized during processing
   - Check `src/data_processor.py` for normalization rules

### Logging

Check `logs/app.log` for detailed error messages and execution information.

## Future Enhancements

- Expand to additional CSO datasets (energy consumption, transport emissions)
- Add predictive modeling for future pollution/water quality trends
- Include more granular geographic data (electoral divisions, towns)
- Implement automated report generation with key insights
- Add time-series forecasting for population and emissions

## Academic Integrity

This project follows NCI academic integrity guidelines:
- All external sources are properly cited
- Code sources are documented with comments
- Original analysis and interpretation

## License

This project is for academic purposes as part of the Programming for AI module at National College of Ireland.

---

**Course:** Programming for AI - PGDAI  
**Institution:** National College of Ireland  
**Due Date:** Monday 17th December 2025