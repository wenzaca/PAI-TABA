"""
Unit tests for DashboardVisualizer class
"""

import unittest
import os
import tempfile
import shutil
import pandas as pd
from src.dashboard_visualizer import DashboardVisualizer
from src.analysis_results import AnalysisResults
from tests.test_fixtures import TestDataGenerator


class TestDashboardVisualizer(unittest.TestCase):
    """Test cases for DashboardVisualizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = DashboardVisualizer(output_dir=self.temp_dir)
        
        # Create sample analysis results using test fixtures
        self.sample_integrated = TestDataGenerator.create_integrated_dataset()
        self.sample_pollution = TestDataGenerator.create_pollution_time_series()
        
        self.sample_results = {
            'processed_data': {
                'integrated': self.sample_integrated,
                'pollution': self.sample_pollution,
                'pollution_vs_population': pd.DataFrame(),
                'pollution_vs_water': pd.DataFrame()
            },
            'correlations': {
                'overall': TestDataGenerator.create_correlation_matrix(),
                'pollution_water': pd.DataFrame()
            },
            'trends': {
                'annual_means': pd.DataFrame(),
                'trend_strength': {}
            },
            'county_analysis': {},
            'pollution_vs_population_analysis': {},
            'pollution_vs_water_analysis': {}
        }
        
    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_create_dashboard_with_dict(self):
        """Test dashboard creation with dictionary input"""
        # Should not raise an error
        self.visualizer.create(self.sample_results)
        
        # Check output file is created
        output_file = os.path.join(self.temp_dir, 'comprehensive_dashboard.html')
        self.assertTrue(os.path.exists(output_file))
        
    def test_create_dashboard_with_dataclass(self):
        """Test dashboard creation with AnalysisResults dataclass"""
        # Import dataclass components
        from src.analysis_results import ProcessedData, CorrelationData, CountyAnalysis
        from src.analysis_results import PollutionVsPopulationAnalysis, PollutionVsWaterAnalysis
        
        # Convert to dataclass
        results = AnalysisResults(
            processed_data=ProcessedData(
                integrated=self.sample_results['processed_data']['integrated'],
                pollution=self.sample_results['processed_data']['pollution']
            ),
            correlations=CorrelationData(
                overall=self.sample_results['correlations']['overall']
            ),
            trends=self.sample_results['trends'],
            county_analysis=CountyAnalysis(),
            pollution_vs_population_analysis=PollutionVsPopulationAnalysis(),
            pollution_vs_water_analysis=PollutionVsWaterAnalysis()
        )
        
        # Should not raise an error
        self.visualizer.create(results)
        
        # Check output file is created
        output_file = os.path.join(self.temp_dir, 'comprehensive_dashboard.html')
        self.assertTrue(os.path.exists(output_file))
        
    def test_dashboard_html_structure(self):
        """Test dashboard HTML contains expected elements"""
        self.visualizer.create(self.sample_results)
        
        output_file = os.path.join(self.temp_dir, 'comprehensive_dashboard.html')
        
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Check for key elements
        self.assertIn('Ireland Environmental Data Analysis Dashboard', html_content)
        self.assertIn('Water Quality', html_content)
        self.assertIn('Pollution', html_content)
        self.assertIn('Population', html_content)
        
    def test_create_analysis_insights_section(self):
        """Test creation of analysis insights section"""
        pvp_analysis = {
            'census_years': [2011, 2016, 2022],
            'overall_changes': {
                'pollution_change_pct': 5.0,
                'population_change_pct': 10.0,
                'years_span': '2011-2022'
            }
        }
        
        pvw_analysis = {
            'years_covered': [2021, 2022, 2023],
            'pollution_water_correlation': {
                'coefficient': -0.5,
                'significant': True,
                'interpretation': 'negative'
            }
        }
        
        # Should not raise an error
        html = self.visualizer._create_analysis_insights_section(pvp_analysis, pvw_analysis, self.sample_results)
        
        # Check HTML contains expected content
        self.assertIn('Multi-Dataset Integration Results', html)
        self.assertIn('Census', html)
        
    def test_empty_data_handling(self):
        """Test handling of minimal datasets"""
        # Create minimal data with required columns
        minimal_integrated = TestDataGenerator.create_minimal_integrated_dataset()
        minimal_pollution = TestDataGenerator.create_minimal_pollution_dataset()
        
        minimal_results = {
            'processed_data': {
                'integrated': minimal_integrated,
                'pollution': minimal_pollution,
                'pollution_vs_population': pd.DataFrame(),
                'pollution_vs_water': pd.DataFrame()
            },
            'correlations': {
                'overall': pd.DataFrame(),
                'pollution_water': pd.DataFrame()
            },
            'trends': {},
            'county_analysis': {},
            'pollution_vs_population_analysis': {},
            'pollution_vs_water_analysis': {}
        }
        
        # Should handle gracefully without crashing
        try:
            self.visualizer.create(minimal_results)
            output_file = os.path.join(self.temp_dir, 'comprehensive_dashboard.html')
            self.assertTrue(os.path.exists(output_file))
        except Exception as e:
            self.fail(f"Dashboard creation failed with minimal data: {str(e)}")
    
    def test_population_widgets_with_pvp_data(self):
        """Test that widgets 6, 7, and 15 use pollution_vs_population data when available"""
        # Create pollution_vs_population data with census years
        pvp_data = pd.DataFrame({
            'county': ['Cork', 'Dublin', 'Galway', 'Cork', 'Dublin', 'Galway'],
            'year': [2011, 2011, 2011, 2022, 2022, 2022],
            'census_year': [2011, 2011, 2011, 2022, 2022, 2022],
            'population': [500000, 1200000, 250000, 550000, 1300000, 260000],
            'total_national_population': [4500000, 4500000, 4500000, 5100000, 5100000, 5100000],
            'total_emissions': [50000, 50000, 50000, 52000, 52000, 52000],
            'pollution_index': [80, 90, 70, 82, 92, 68]
        })
        
        results_with_pvp = {
            'processed_data': {
                'integrated': self.sample_integrated,
                'pollution': self.sample_pollution,
                'pollution_vs_population': pvp_data,
                'pollution_vs_water': pd.DataFrame()
            },
            'correlations': {
                'overall': TestDataGenerator.create_correlation_matrix(),
                'pollution_water': pd.DataFrame()
            },
            'trends': {
                'annual_means': pd.DataFrame(),
                'trend_strength': {}
            },
            'county_analysis': {},
            'pollution_vs_population_analysis': {},
            'pollution_vs_water_analysis': {}
        }
        
        # Should create dashboard successfully with pvp data
        try:
            self.visualizer.create(results_with_pvp)
            output_file = os.path.join(self.temp_dir, 'comprehensive_dashboard.html')
            self.assertTrue(os.path.exists(output_file))
            
            # Verify the HTML contains population-related content
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check that population widgets are present
            self.assertIn('Population Growth per County', html_content)
            self.assertIn('National Population Growth', html_content)
            self.assertIn('Population-Pollution Correlation', html_content)
            
        except Exception as e:
            self.fail(f"Dashboard creation failed with pollution_vs_population data: {str(e)}")


if __name__ == '__main__':
    unittest.main()
    def test_calculate_national_period_growth_correlation(self):
        """Test national period growth correlation calculation"""
        # Create sample data with pollution_vs_population dataset
        sample_pvp_data = pd.DataFrame({
            'year': [2011, 2016, 2022],
            'total_national_population': [4500000, 4750000, 5000000],
            'total_emissions': [45000, 47500, 50000]
        })
        
        analysis_dict = {
            'processed_data': {
                'pollution_vs_population': sample_pvp_data,
                'integrated': pd.DataFrame()
            }
        }
        
        result = self.visualizer._calculate_national_period_growth_correlation(analysis_dict)
        
        # Check result structure
        self.assertIn('baseline_year', result)
        self.assertIn('final_year', result)
        self.assertIn('population_growth_pct', result)
        self.assertIn('emission_growth_pct', result)
        self.assertIn('correlation_coefficient', result)
        
        # Check calculations
        self.assertEqual(result['baseline_year'], 2011)
        self.assertEqual(result['final_year'], 2022)
        
        # Population growth: (5M - 4.5M) / 4.5M * 100 = 11.11%
        self.assertAlmostEqual(result['population_growth_pct'], 11.11, delta=0.1)
        
        # Emission growth: (50K - 45K) / 45K * 100 = 11.11%
        self.assertAlmostEqual(result['emission_growth_pct'], 11.11, delta=0.1)