"""
Unit tests for DatabaseManager class
"""

import unittest
import os
import tempfile
import pandas as pd
from src.database_manager import DatabaseManager
from src.constants import TableNames


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager"""
    
    def setUp(self):
        """Set up test fixtures with temporary database"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize database manager with temp database
        self.db_manager = DatabaseManager(db_path=self.temp_db.name)
        
        # Create sample datasets
        self.sample_pollution = pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'pollutant': ['CO2', 'CO2'],
            'value': [1000, 1500]
        })
        
        self.sample_water = pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'classification': ['Excellent', 'Good'],
            'quality_score': [4, 3]
        })
        
        self.sample_population = pd.DataFrame({
            'county': ['Cork', 'Dublin'],
            'year': [2022, 2022],
            'population': [500000, 1200000]
        })
        
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_store_and_load_pollution_data(self):
        """Test storing and loading pollution data"""
        # Store data with correct table names
        datasets = {
            TableNames.RAW_POLLUTION: self.sample_pollution,
            TableNames.RAW_WATER_QUALITY: self.sample_water,
            TableNames.RAW_POPULATION: self.sample_population
        }
        self.db_manager.store_datasets(datasets)
        
        # Load data
        loaded = self.db_manager.load_dataset(TableNames.RAW_POLLUTION)
        
        # Check data is loaded correctly
        self.assertEqual(len(loaded), len(self.sample_pollution))
        self.assertIn('county', loaded.columns)
        self.assertIn('year', loaded.columns)
        
    def test_store_and_load_water_quality_data(self):
        """Test storing and loading water quality data"""
        datasets = {
            TableNames.RAW_POLLUTION: self.sample_pollution,
            TableNames.RAW_WATER_QUALITY: self.sample_water,
            TableNames.RAW_POPULATION: self.sample_population
        }
        self.db_manager.store_datasets(datasets)
        
        loaded = self.db_manager.load_dataset(TableNames.RAW_WATER_QUALITY)
        
        self.assertEqual(len(loaded), len(self.sample_water))
        self.assertIn('county', loaded.columns)
        
    def test_store_and_load_population_data(self):
        """Test storing and loading population data"""
        datasets = {
            TableNames.RAW_POLLUTION: self.sample_pollution,
            TableNames.RAW_WATER_QUALITY: self.sample_water,
            TableNames.RAW_POPULATION: self.sample_population
        }
        self.db_manager.store_datasets(datasets)
        
        loaded = self.db_manager.load_dataset(TableNames.RAW_POPULATION)
        
        self.assertEqual(len(loaded), len(self.sample_population))
        self.assertIn('population', loaded.columns)
        
    def test_store_analysis_results(self):
        """Test storing analysis results"""
        results = {
            'correlations': {'overall': pd.DataFrame({'A': [1, 2], 'B': [3, 4]})},
            'statistics': {'descriptive': pd.DataFrame({'mean': [1.5], 'std': [0.5]})},
            'trends': {'annual_means': pd.DataFrame({'year': [2022], 'value': [100]})},
            'processed_data': {
                'integrated': pd.DataFrame({'county': ['Cork'], 'year': [2022]})
            }
        }
        
        # Should not raise an error
        self.db_manager.store_analysis_results(results)
        
    def test_database_connection(self):
        """Test database connection is established"""
        # Connection should be created in __init__
        self.assertIsNotNone(self.db_manager.engine)
        
    def test_empty_dataset_handling(self):
        """Test handling of empty datasets"""
        # Create empty dataframes with at least one column to avoid SQL syntax error
        empty_df = pd.DataFrame({'dummy': []})
        datasets = {
            'pollution': empty_df,
            'water_quality': empty_df,
            'population': empty_df
        }
        
        # Should not raise an error
        self.db_manager.store_datasets(datasets)


if __name__ == '__main__':
    unittest.main()
