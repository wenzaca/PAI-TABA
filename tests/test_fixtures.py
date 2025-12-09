"""
Test fixtures and sample data generators for unit tests
"""

import pandas as pd
from src.constants import WaterQualityColumns, PollutionColumns, PopulationColumns


class TestDataGenerator:
    """Generates sample test data for unit tests"""
    
    @staticmethod
    def create_sample_pollution_data():
        """Create sample pollution data for testing"""
        return pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'pollutant': ['CO2', 'CO2'],
            'value': [1000, 1500]
        })
    
    @staticmethod
    def create_sample_water_quality_data():
        """Create sample water quality data for testing"""
        return pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'classification': ['Excellent', 'Good'],
            'quality_score': [4, 3]
        })
    
    @staticmethod
    def create_sample_population_data():
        """Create sample population data for testing"""
        return pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'population': [500000, 1200000]
        })
    
    @staticmethod
    def create_national_pollution_data():
        """Create sample national-level pollution data for testing"""
        return pd.DataFrame({
            PollutionColumns.COUNTY: ['Ireland', 'Ireland', 'Ireland'],
            PollutionColumns.YEAR: [2020, 2020, 2021],
            PollutionColumns.POLLUTANT: ['CO2', 'NOx', 'CO2'],
            PollutionColumns.VALUE: [1000, 50, 1100],
            'geographic_level': ['National', 'National', 'National']
        })
    
    @staticmethod
    def create_detailed_water_quality_data():
        """Create detailed water quality data with site codes for testing"""
        return pd.DataFrame({
            WaterQualityColumns.COUNTY: ['Cork County Council', 'Dublin City Council', 'Cork County Council'],
            WaterQualityColumns.YEAR: [2022, 2022, 2023],
            WaterQualityColumns.CLASSIFICATION: ['Excellent', 'Good', 'Excellent'],
            WaterQualityColumns.QUALITY_SCORE: [4, 3, 4],
            WaterQualityColumns.SITE_CODE: ['SITE1', 'SITE2', 'SITE3']
        })
    
    @staticmethod
    def create_detailed_population_data():
        """Create detailed population data with census years for testing"""
        return pd.DataFrame({
            PopulationColumns.COUNTY: ['Cork', 'Dublin', 'Cork'],
            PopulationColumns.YEAR: [2011, 2011, 2022],
            PopulationColumns.POPULATION: [500000, 1200000, 550000],
            'census_year': [2011, 2011, 2022],
            'statistic': ['Population per County', 'Population per County', 'Population per County']
        })
    
    @staticmethod
    def create_integrated_dataset():
        """Create sample integrated dataset for dashboard testing"""
        return pd.DataFrame({
            'county': ['Cork', 'Dublin', 'Galway'] * 2,
            'year': [2021, 2021, 2021, 2022, 2022, 2022],
            'pollution_index': [80, 90, 70, 82, 92, 68],
            'avg_quality_score': [3.5, 3.0, 3.8, 3.6, 2.9, 3.9],
            'population': [500000, 1200000, 250000, 510000, 1250000, 255000],
            'total_emissions': [50000, 50000, 50000, 51000, 51000, 51000],
            'total_national_population': [5000000, 5000000, 5000000, 5100000, 5100000, 5100000],
            'estimated_county_emissions': [5000, 12000, 2500, 5100, 12500, 2550],
            'percent_good_or_better': [85, 75, 90, 87, 73, 92],
            'percent_excellent': [60, 50, 70, 62, 48, 72]
        })
    
    @staticmethod
    def create_pollution_time_series():
        """Create sample pollution time series for trend analysis"""
        return pd.DataFrame({
            'county': ['Ireland'] * 4,
            'year': [2021, 2022, 2023, 2024],
            'pollution_index': [80, 82, 81, 79],
            'total_emissions': [50000, 51000, 50500, 49000]
        })
    
    @staticmethod
    def create_correlation_matrix():
        """Create sample correlation matrix for testing"""
        return pd.DataFrame({
            'pollution_index': [1.0, -0.5],
            'avg_quality_score': [-0.5, 1.0]
        }, index=['pollution_index', 'avg_quality_score'])
    
    @staticmethod
    def create_population_with_emissions():
        """Create population data with estimated emissions for testing"""
        return pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'census_year': [2022, 2022],
            'population': [500000, 1200000]
        })
    
    @staticmethod
    def create_minimal_integrated_dataset():
        """Create minimal integrated dataset for edge case testing"""
        return pd.DataFrame({
            'county': ['Cork'],
            'year': [2022],
            'pollution_index': [80],
            'avg_quality_score': [3.5],
            'population': [500000]
        })
    
    @staticmethod
    def create_minimal_pollution_dataset():
        """Create minimal pollution dataset for edge case testing"""
        return pd.DataFrame({
            'county': ['Ireland'],
            'year': [2022],
            'pollution_index': [80],
            'total_emissions': [50000]
        })
    
    @staticmethod
    def create_empty_dataframe_with_column():
        """Create empty dataframe with at least one column to avoid SQL errors"""
        return pd.DataFrame({'dummy': []})
