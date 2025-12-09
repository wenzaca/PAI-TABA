"""
Unit tests for DataCollector class
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_collector import DataCollector


class TestDataCollector(unittest.TestCase):
    """Test cases for DataCollector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.collector = DataCollector()
        
    @patch('src.data_collector.requests.get')
    def test_collect_pollution_data_success(self, mock_get):
        """Test successful pollution data fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'dimension': {},
            'value': []
        }
        mock_get.return_value = mock_response
        
        result = self.collector._collect_pollution_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        
    @patch('src.data_collector.requests.get')
    def test_collect_pollution_data_fallback(self, mock_get):
        """Test pollution data fallback on API failure"""
        mock_get.side_effect = Exception("API Error")
        
        result = self.collector._collect_pollution_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        
    @patch('src.data_collector.requests.get')
    def test_collect_water_quality_data_success(self, mock_get):
        """Test successful water quality data fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'dimension': {},
            'value': []
        }
        mock_get.return_value = mock_response
        
        result = self.collector._collect_water_quality_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        
    @patch('src.data_collector.requests.get')
    def test_collect_population_data_success(self, mock_get):
        """Test successful population data fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'dimension': {},
            'value': []
        }
        mock_get.return_value = mock_response
        
        result = self.collector._collect_population_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_collect_all_datasets(self):
        """Test collecting all datasets"""
        datasets = self.collector.collect_all_datasets()
        
        # Check all datasets are present with correct keys
        self.assertIn('raw_pollution', datasets)
        self.assertIn('raw_water_quality', datasets)
        self.assertIn('raw_population', datasets)
        
        # Check all are DataFrames
        self.assertIsInstance(datasets['raw_pollution'], pd.DataFrame)
        self.assertIsInstance(datasets['raw_water_quality'], pd.DataFrame)
        self.assertIsInstance(datasets['raw_population'], pd.DataFrame)
        
    def test_fallback_data_structure(self):
        """Test fallback data has correct structure"""
        with patch('src.data_collector.requests.get', side_effect=Exception("API Error")):
            datasets = self.collector.collect_all_datasets()
            
            # Check pollution data structure
            pollution = datasets['raw_pollution']
            self.assertIn('county', pollution.columns)
            self.assertIn('year', pollution.columns)
            self.assertIn('pollutant', pollution.columns)
            self.assertIn('value', pollution.columns)


if __name__ == '__main__':
    unittest.main()
