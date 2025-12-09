"""
Unit tests for IrelandDataAnalyzer class
"""

import unittest
import pandas as pd
import numpy as np
from src.analyzer import IrelandDataAnalyzer
from src.constants import IntegratedColumns


class TestIrelandDataAnalyzer(unittest.TestCase):
    """Test cases for IrelandDataAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = IrelandDataAnalyzer()
        
        # Create sample integrated data
        self.sample_data = pd.DataFrame({
            IntegratedColumns.COUNTY: ['Cork', 'Dublin', 'Galway', 'Cork', 'Dublin', 'Galway'],
            IntegratedColumns.YEAR: [2021, 2021, 2021, 2022, 2022, 2022],
            IntegratedColumns.POLLUTION_INDEX: [80, 90, 70, 82, 92, 68],
            IntegratedColumns.AVG_QUALITY_SCORE: [3.5, 3.0, 3.8, 3.6, 2.9, 3.9],
            IntegratedColumns.POPULATION: [500000, 1200000, 250000, 510000, 1250000, 255000],
            IntegratedColumns.TOTAL_EMISSIONS: [50000, 50000, 50000, 51000, 51000, 51000],
            'total_national_population': [5000000, 5000000, 5000000, 5100000, 5100000, 5100000],
            IntegratedColumns.POPULATION_DENSITY: [100, 300, 50, 102, 310, 51],
            IntegratedColumns.PERCENT_GOOD_OR_BETTER: [85, 75, 90, 87, 73, 92]
        })
        
    def test_add_estimated_county_emissions(self):
        """Test calculation of estimated county emissions"""
        result = self.analyzer._add_estimated_county_emissions(self.sample_data)
        
        # Check column is added
        self.assertTrue('estimated_county_emissions' in result.columns)
        
        # Check calculation is correct
        cork_2021 = result[(result['county'] == 'Cork') & (result['year'] == 2021)]
        expected = 50000 * (500000 / 5000000)
        self.assertAlmostEqual(cork_2021['estimated_county_emissions'].iloc[0], expected, delta=10)
        
    def test_analyze_correlations(self):
        """Test correlation analysis"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check correlations are calculated
        self.assertIn('correlations', results)
        self.assertIn('overall', results['correlations'])
        
        # Check correlation matrix is a DataFrame
        self.assertIsInstance(results['correlations']['overall'], pd.DataFrame)
        
    def test_analyze_trends(self):
        """Test trend analysis"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check trends are calculated
        self.assertIn('trends', results)
        self.assertIn('annual_means', results['trends'])
        self.assertIn('trend_strength', results['trends'])
        
    def test_analyze_county_patterns(self):
        """Test county pattern analysis"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check county analysis exists
        self.assertIn('county_analysis', results)
        self.assertIn('means', results['county_analysis'])
        self.assertIn('rankings', results['county_analysis'])
        
    def test_pollution_water_relationship(self):
        """Test pollution-water quality relationship analysis"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check relationship analysis exists
        self.assertIn('pollution_water_relationship', results)
        
        # If enough data, should have correlation
        if 'correlation' in results['pollution_water_relationship']:
            corr = results['pollution_water_relationship']['correlation']
            self.assertIn('coefficient', corr)
            self.assertIn('p_value', corr)
            self.assertIn('significant', corr)
            
    def test_generate_insights(self):
        """Test insight generation"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check insights are generated
        self.assertIn('insights', results)
        self.assertIsInstance(results['insights'], dict)
        
    def test_statistical_analysis(self):
        """Test statistical analysis methods"""
        processed_data = {'integrated': self.sample_data}
        results = self.analyzer.analyze_patterns(processed_data)
        
        # Check statistics are calculated
        self.assertIn('statistics', results)
        self.assertIn('descriptive', results['statistics'])
        
        # Check descriptive stats is a DataFrame
        self.assertIsInstance(results['statistics']['descriptive'], pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
