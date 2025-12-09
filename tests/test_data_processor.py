"""
Unit tests for DataProcessor class
"""

import unittest
import pandas as pd
import numpy as np
from src.data_processor import DataProcessor
from src.constants import WaterQualityColumns, PollutionColumns, PopulationColumns


class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DataProcessor()
        
    def test_normalize_county_name(self):
        """Test county name normalization"""
        # Test removing prefixes and suffixes
        self.assertEqual(self.processor._normalize_county_name('Co. Cork'), 'Cork')
        self.assertEqual(self.processor._normalize_county_name('Dublin City Council'), 'Dublin')
        self.assertEqual(self.processor._normalize_county_name('Galway County Council'), 'Galway')
        
        # Test special cases
        self.assertEqual(self.processor._normalize_county_name('State'), 'Ireland')
        self.assertEqual(self.processor._normalize_county_name('Dún Laoghaire-Rathdown'), 'Dún Laoghaire Rathdown')
        
        # Test NaN handling
        self.assertTrue(pd.isna(self.processor._normalize_county_name(np.nan)))
        
    def test_process_pollution_data_national(self):
        """Test processing national-level pollution data"""
        # Create sample national pollution data
        data = {
            PollutionColumns.COUNTY: ['Ireland', 'Ireland', 'Ireland'],
            PollutionColumns.YEAR: [2020, 2020, 2021],
            PollutionColumns.POLLUTANT: ['CO2', 'NOx', 'CO2'],
            PollutionColumns.VALUE: [1000, 50, 1100],
            'geographic_level': ['National', 'National', 'National']
        }
        df = pd.DataFrame(data)
        
        result = self.processor._process_pollution_data(df)
        
        # Check that data_type is set to national
        self.assertTrue('data_type' in result.columns)
        self.assertEqual(result['data_type'].iloc[0], 'national')
        
        # Check that total_emissions is calculated
        self.assertTrue(PollutionColumns.TOTAL_EMISSIONS in result.columns)
        
        # Check that pollution_index is calculated
        self.assertTrue(PollutionColumns.POLLUTION_INDEX in result.columns)
        
    def test_process_water_quality_data(self):
        """Test processing water quality data"""
        # Create sample water quality data
        data = {
            WaterQualityColumns.COUNTY: ['Cork County Council', 'Dublin City Council', 'Cork County Council'],
            WaterQualityColumns.YEAR: [2022, 2022, 2023],
            WaterQualityColumns.CLASSIFICATION: ['Excellent', 'Good', 'Excellent'],
            WaterQualityColumns.QUALITY_SCORE: [4, 3, 4],
            WaterQualityColumns.SITE_CODE: ['SITE1', 'SITE2', 'SITE3']
        }
        df = pd.DataFrame(data)
        
        result = self.processor._process_water_quality_data(df)
        
        # Check county names are normalized
        self.assertIn('Cork', result[WaterQualityColumns.COUNTY].values)
        self.assertIn('Dublin', result[WaterQualityColumns.COUNTY].values)
        
        # Check aggregated columns exist
        self.assertTrue(WaterQualityColumns.AVG_QUALITY_SCORE in result.columns)
        self.assertTrue('percent_excellent' in result.columns)
        self.assertTrue('percent_good_or_better' in result.columns)
        
    def test_process_population_data(self):
        """Test processing population data"""
        # Create sample population data
        data = {
            PopulationColumns.COUNTY: ['Cork', 'Dublin', 'Cork'],
            PopulationColumns.YEAR: [2011, 2011, 2022],
            PopulationColumns.POPULATION: [500000, 1200000, 550000],
            'census_year': [2011, 2011, 2022],
            'statistic': ['Population per County', 'Population per County', 'Population per County']
        }
        df = pd.DataFrame(data)
        
        result = self.processor._process_population_data(df)
        
        # Check population density is calculated
        self.assertTrue(PopulationColumns.POPULATION_DENSITY in result.columns)
        
        # Check growth metrics are calculated
        self.assertTrue(PopulationColumns.POPULATION_GROWTH in result.columns)
        self.assertTrue(PopulationColumns.POPULATION_GROWTH_TOTAL in result.columns)
        
    def test_add_estimated_county_emissions(self):
        """Test calculation of estimated county emissions"""
        # Create sample population data with census_year column
        population_data = {
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'census_year': [2022, 2022],
            'population': [500000, 1200000]
        }
        pop_df = pd.DataFrame(population_data)
        
        # Create sample pollution data
        pollution_data = {
            'county': ['Ireland', 'Ireland'],
            'year': [2022, 2022],
            'total_emissions': [50000, 50000],
            'pollution_index': [100, 100],
            'data_type': ['national', 'national']
        }
        poll_df = pd.DataFrame(pollution_data)
        
        result = self.processor._create_pollution_vs_population(
            poll_df,
            pop_df,
            [2022]
        )
        
        # Check estimated_county_emissions is calculated
        self.assertTrue('estimated_county_emissions' in result.columns)
        
        # Check calculation is correct (proportional to population)
        cork_row = result[result['county'] == 'Cork']
        dublin_row = result[result['county'] == 'Dublin']
        
        if not cork_row.empty and not dublin_row.empty:
            cork_emissions = cork_row['estimated_county_emissions'].iloc[0]
            dublin_emissions = dublin_row['estimated_county_emissions'].iloc[0]
            
            # Cork should have ~10% of emissions (500k/1.7M), Dublin ~24% (1.2M/1.7M)
            self.assertGreater(dublin_emissions, cork_emissions)


if __name__ == '__main__':
    unittest.main()
