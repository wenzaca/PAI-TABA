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


class TestDashboardVisualizer(unittest.TestCase):
    """Test cases for DashboardVisualizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = DashboardVisualizer(output_dir=self.temp_dir)
        
        # Create sample analysis results
        self.sample_integrated = pd.DataFrame({
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
        
        self.sample_pollution = pd.DataFrame({
            'county': ['Ireland'] * 4,
            'year': [2021, 2022, 2023, 2024],
            'pollution_index': [80, 82, 81, 79],
            'total_emissions': [50000, 51000, 50500, 49000]
        })
        
        self.sample_results = {
            'processed_data': {
                'integrated': self.sample_integrated,
                'pollution': self.sample_pollution,
                'pollution_vs_population': pd.DataFrame(),
                'pollution_vs_water': pd.DataFrame()
            },
            'correlations': {
                'overall': pd.DataFrame({
                    'pollution_index': [1.0, -0.5],
                    'avg_quality_score': [-0.5, 1.0]
                }, index=['pollution_index', 'avg_quality_score']),
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
        html = self.visualizer._create_analysis_insights_section(pvp_analysis, pvw_analysis)
        
        # Check HTML contains expected content
        self.assertIn('Multi-Dataset Integration Results', html)
        self.assertIn('Census', html)
        
    def test_empty_data_handling(self):
        """Test handling of minimal datasets"""
        # Create minimal data with required columns
        minimal_integrated = pd.DataFrame({
            'county': ['Cork'],
            'year': [2022],
            'pollution_index': [80],
            'avg_quality_score': [3.5],
            'population': [500000]
        })
        
        minimal_pollution = pd.DataFrame({
            'county': ['Ireland'],
            'year': [2022],
            'pollution_index': [80],
            'total_emissions': [50000]
        })
        
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


if __name__ == '__main__':
    unittest.main()
