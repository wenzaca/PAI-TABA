"""
Unit tests for TestDataGenerator fixtures
"""

import unittest
import pandas as pd
from tests.test_fixtures import TestDataGenerator


class TestTestDataGenerator(unittest.TestCase):
    """Test cases for TestDataGenerator fixture methods"""
    
    def test_create_sample_pollution_data(self):
        """Test sample pollution data generation"""
        df = TestDataGenerator.create_sample_pollution_data()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('county', df.columns)
        self.assertIn('year', df.columns)
        self.assertIn('pollutant', df.columns)
        self.assertIn('value', df.columns)
    
    def test_create_sample_water_quality_data(self):
        """Test sample water quality data generation"""
        df = TestDataGenerator.create_sample_water_quality_data()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('county', df.columns)
        self.assertIn('classification', df.columns)
    
    def test_create_sample_population_data(self):
        """Test sample population data generation"""
        df = TestDataGenerator.create_sample_population_data()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('population', df.columns)
    
    def test_create_national_pollution_data(self):
        """Test national pollution data generation"""
        df = TestDataGenerator.create_national_pollution_data()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertTrue(all(df['county'] == 'Ireland'))
        self.assertIn('geographic_level', df.columns)
    
    def test_create_integrated_dataset(self):
        """Test integrated dataset generation"""
        df = TestDataGenerator.create_integrated_dataset()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 6)  # 3 counties * 2 years
        self.assertIn('pollution_index', df.columns)
        self.assertIn('avg_quality_score', df.columns)
        self.assertIn('estimated_county_emissions', df.columns)
    
    def test_create_correlation_matrix(self):
        """Test correlation matrix generation"""
        df = TestDataGenerator.create_correlation_matrix()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertEqual(df.loc['pollution_index', 'pollution_index'], 1.0)
    
    def test_create_empty_dataframe_with_column(self):
        """Test empty dataframe generation"""
        df = TestDataGenerator.create_empty_dataframe_with_column()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)
        self.assertIn('dummy', df.columns)


if __name__ == '__main__':
    unittest.main()
