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
    
    def test_aggregate_city_county_pairs(self):
        """Test county aggregation functionality"""
        # Test data with city/county pairs
        test_records = [
            {'county': 'Cork City', 'population': 125000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Cork County', 'population': 400000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Galway City', 'population': 80000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Galway County', 'population': 180000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Dublin City', 'population': 550000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'South Dublin', 'population': 280000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Fingal', 'population': 320000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Dún Laoghaire-Rathdown', 'population': 220000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Limerick City and County', 'population': 195000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Waterford City and County', 'population': 116000, 'year': 2022, 'statistic': 'Population per County'},
            {'county': 'Kerry', 'population': 147000, 'year': 2022, 'statistic': 'Population per County'}
        ]
        
        result = self.collector._aggregate_city_county_pairs(test_records)
        
        # Convert to dict for easier testing
        result_dict = {record['county']: record['population'] for record in result}
        
        # Test Cork aggregation
        self.assertIn('Cork', result_dict)
        self.assertEqual(result_dict['Cork'], 525000)  # 125000 + 400000
        self.assertNotIn('Cork City', result_dict)
        self.assertNotIn('Cork County', result_dict)
        
        # Test Galway aggregation
        self.assertIn('Galway', result_dict)
        self.assertEqual(result_dict['Galway'], 260000)  # 80000 + 180000
        self.assertNotIn('Galway City', result_dict)
        self.assertNotIn('Galway County', result_dict)
        
        # Test Dublin aggregation
        self.assertIn('Dublin', result_dict)
        self.assertEqual(result_dict['Dublin'], 1370000)  # 550000 + 280000 + 320000 + 220000
        self.assertNotIn('Dublin City', result_dict)
        self.assertNotIn('South Dublin', result_dict)
        self.assertNotIn('Fingal', result_dict)
        self.assertNotIn('Dún Laoghaire-Rathdown', result_dict)
        
        # Test direct mappings
        self.assertIn('Limerick', result_dict)
        self.assertEqual(result_dict['Limerick'], 195000)
        self.assertNotIn('Limerick City and County', result_dict)
        
        self.assertIn('Waterford', result_dict)
        self.assertEqual(result_dict['Waterford'], 116000)
        self.assertNotIn('Waterford City and County', result_dict)
        
        # Test unchanged county
        self.assertIn('Kerry', result_dict)
        self.assertEqual(result_dict['Kerry'], 147000)
        
        # Test total number of aggregated records
        self.assertEqual(len(result), 6)  # Cork, Galway, Dublin, Limerick, Waterford, Kerry
    
    def test_aggregate_city_county_pairs_empty_input(self):
        """Test aggregation with empty input"""
        result = self.collector._aggregate_city_county_pairs([])
        self.assertEqual(result, [])
    
    def test_aggregate_city_county_pairs_single_county(self):
        """Test aggregation with single county (no pairs)"""
        test_records = [
            {'county': 'Kerry', 'population': 147000, 'year': 2022, 'statistic': 'Population per County'}
        ]
        
        result = self.collector._aggregate_city_county_pairs(test_records)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['county'], 'Kerry')
        self.assertEqual(result[0]['population'], 147000)


if __name__ == '__main__':
    unittest.main()
