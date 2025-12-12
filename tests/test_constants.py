import unittest
from src.constants import (
    TableNames,
    WaterQualityColumns,
    PollutionColumns,
    PopulationColumns,
    IntegratedColumns,
    IrishCounties,
    AnalysisConstants
)


class TestTableNames(unittest.TestCase):
    """Test TableNames constants"""
    
    def test_table_names_exist(self):
        """Test that all table names are defined"""
        self.assertEqual(TableNames.RAW_POLLUTION, 'raw_pollution')
        self.assertEqual(TableNames.RAW_WATER_QUALITY, 'raw_water_quality')
        self.assertEqual(TableNames.RAW_POPULATION, 'raw_population')
    
    def test_table_names_are_strings(self):
        """Test that all table names are strings"""
        self.assertIsInstance(TableNames.RAW_POLLUTION, str)
        self.assertIsInstance(TableNames.RAW_WATER_QUALITY, str)
        self.assertIsInstance(TableNames.RAW_POPULATION, str)


class TestWaterQualityColumns(unittest.TestCase):
    """Test WaterQualityColumns constants"""
    
    def test_column_names_exist(self):
        """Test that all water quality column names are defined"""
        self.assertEqual(WaterQualityColumns.SITE_CODE, 'site_code')
        self.assertEqual(WaterQualityColumns.COUNTY, 'county')
        self.assertEqual(WaterQualityColumns.CLASSIFICATION, 'classification')
        self.assertEqual(WaterQualityColumns.YEAR, 'year')
        self.assertEqual(WaterQualityColumns.QUALITY_SCORE, 'quality_score')
        self.assertEqual(WaterQualityColumns.IS_EXCELLENT, 'is_excellent')
        self.assertEqual(WaterQualityColumns.IS_GOOD_OR_BETTER, 'is_good_or_better')
        self.assertEqual(WaterQualityColumns.SITES_PER_COUNTY, 'sites_per_county')
        self.assertEqual(WaterQualityColumns.AVG_QUALITY_SCORE, 'avg_quality_score')


class TestPollutionColumns(unittest.TestCase):
    """Test PollutionColumns constants"""
    
    def test_column_names_exist(self):
        """Test that all pollution column names are defined"""
        self.assertEqual(PollutionColumns.COUNTY, 'county')
        self.assertEqual(PollutionColumns.YEAR, 'year')
        self.assertEqual(PollutionColumns.POLLUTANT, 'pollutant')
        self.assertEqual(PollutionColumns.VALUE, 'value')
        self.assertEqual(PollutionColumns.TOTAL_EMISSIONS, 'total_emissions')
        self.assertEqual(PollutionColumns.CO2_EMISSIONS, 'co2_emissions')
        self.assertEqual(PollutionColumns.NOX_EMISSIONS, 'nox_emissions')
        self.assertEqual(PollutionColumns.PM25_EMISSIONS, 'pm25_emissions')
        self.assertEqual(PollutionColumns.POLLUTION_INDEX, 'pollution_index')


class TestPopulationColumns(unittest.TestCase):
    """Test PopulationColumns constants"""
    
    def test_column_names_exist(self):
        """Test that all population column names are defined"""
        self.assertEqual(PopulationColumns.COUNTY, 'county')
        self.assertEqual(PopulationColumns.YEAR, 'year')
        self.assertEqual(PopulationColumns.POPULATION, 'population')
        self.assertEqual(PopulationColumns.POPULATION_DENSITY, 'population_density')
        self.assertEqual(PopulationColumns.POPULATION_GROWTH, 'population_growth')
        self.assertEqual(PopulationColumns.POPULATION_GROWTH_TOTAL, 'population_growth_total')


class TestIntegratedColumns(unittest.TestCase):
    """Test IntegratedColumns constants"""
    
    def test_column_names_exist(self):
        """Test that all integrated column names are defined"""
        self.assertEqual(IntegratedColumns.COUNTY, 'county')
        self.assertEqual(IntegratedColumns.YEAR, 'year')
        self.assertEqual(IntegratedColumns.TOTAL_EMISSIONS, 'total_emissions')
        self.assertEqual(IntegratedColumns.POLLUTION_INDEX, 'pollution_index')
        self.assertEqual(IntegratedColumns.CO2_EMISSIONS, 'co2_emissions')
        self.assertEqual(IntegratedColumns.AVG_QUALITY_SCORE, 'avg_quality_score')
        self.assertEqual(IntegratedColumns.SITES_PER_COUNTY, 'sites_per_county')
        self.assertEqual(IntegratedColumns.PERCENT_EXCELLENT, 'percent_excellent')
        self.assertEqual(IntegratedColumns.PERCENT_GOOD_OR_BETTER, 'percent_good_or_better')
        self.assertEqual(IntegratedColumns.POPULATION, 'population')
        self.assertEqual(IntegratedColumns.POPULATION_GROWTH, 'population_growth')
        self.assertEqual(IntegratedColumns.POPULATION_DENSITY, 'population_density')
        self.assertEqual(IntegratedColumns.EMISSIONS_PER_CAPITA, 'emissions_per_capita')
    
    def test_inherited_columns_match(self):
        """Test that inherited columns match their source"""
        self.assertEqual(IntegratedColumns.TOTAL_EMISSIONS, PollutionColumns.TOTAL_EMISSIONS)
        self.assertEqual(IntegratedColumns.POLLUTION_INDEX, PollutionColumns.POLLUTION_INDEX)
        self.assertEqual(IntegratedColumns.CO2_EMISSIONS, PollutionColumns.CO2_EMISSIONS)
        self.assertEqual(IntegratedColumns.AVG_QUALITY_SCORE, WaterQualityColumns.AVG_QUALITY_SCORE)
        self.assertEqual(IntegratedColumns.SITES_PER_COUNTY, WaterQualityColumns.SITES_PER_COUNTY)
        self.assertEqual(IntegratedColumns.POPULATION, PopulationColumns.POPULATION)
        self.assertEqual(IntegratedColumns.POPULATION_GROWTH, PopulationColumns.POPULATION_GROWTH)
        self.assertEqual(IntegratedColumns.POPULATION_DENSITY, PopulationColumns.POPULATION_DENSITY)


class TestIrishCounties(unittest.TestCase):
    """Test IrishCounties constants"""
    
    def test_county_areas_exist(self):
        """Test that county areas dictionary exists"""
        self.assertIsInstance(IrishCounties.COUNTY_AREAS, dict)
        self.assertGreater(len(IrishCounties.COUNTY_AREAS), 0)
    
    def test_county_areas_are_numeric(self):
        """Test that all county areas are numeric"""
        for county, area in IrishCounties.COUNTY_AREAS.items():
            self.assertIsInstance(county, str)
            self.assertIsInstance(area, (int, float))
            self.assertGreater(area, 0)
    
    def test_specific_counties_exist(self):
        """Test that specific counties are in the dictionary"""
        expected_counties = ['Dublin', 'Cork', 'Galway', 'Kerry', 'Mayo']
        for county in expected_counties:
            self.assertIn(county, IrishCounties.COUNTY_AREAS)
    
    def test_county_count(self):
        """Test that we have the expected number of counties"""
        self.assertEqual(len(IrishCounties.COUNTY_AREAS), 17)
    
    def test_area_values_reasonable(self):
        """Test that area values are within reasonable ranges (in km²)"""
        for county, area in IrishCounties.COUNTY_AREAS.items():
            self.assertGreater(area, 0, f"{county} area should be positive")
            self.assertLess(area, 10000, f"{county} area seems too large")
    
    def test_aggregation_mapping_exists(self):
        """Test that aggregation mapping dictionary exists"""
        self.assertIsInstance(IrishCounties.AGGREGATION_MAPPING, dict)
        self.assertGreater(len(IrishCounties.AGGREGATION_MAPPING), 0)
    
    def test_aggregation_mapping_structure(self):
        """Test aggregation mapping has correct structure"""
        for source, target in IrishCounties.AGGREGATION_MAPPING.items():
            self.assertIsInstance(source, str)
            self.assertIsInstance(target, str)
            self.assertGreater(len(source), 0)
            self.assertGreater(len(target), 0)
    
    def test_aggregation_mapping_specific_cases(self):
        """Test specific aggregation mapping cases"""
        # Cork aggregation
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Cork City'], 'Cork')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Cork County'], 'Cork')
        
        # Galway aggregation
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Galway City'], 'Galway')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Galway County'], 'Galway')
        
        # Dublin aggregation
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Dublin City'], 'Dublin')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['South Dublin'], 'Dublin')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Fingal'], 'Dublin')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Dún Laoghaire-Rathdown'], 'Dublin')
        
        # Direct mappings
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Limerick City and County'], 'Limerick')
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Waterford City and County'], 'Waterford')
    
    def test_normalization_mapping_exists(self):
        """Test that normalization mapping dictionary exists"""
        self.assertIsInstance(IrishCounties.NORMALIZATION_MAPPING, dict)
        self.assertGreater(len(IrishCounties.NORMALIZATION_MAPPING), 0)
    
    def test_normalization_mapping_structure(self):
        """Test normalization mapping has correct structure"""
        for source, target in IrishCounties.NORMALIZATION_MAPPING.items():
            self.assertIsInstance(source, str)
            self.assertIsInstance(target, str)
            self.assertGreater(len(source), 0)
            self.assertGreater(len(target), 0)
    
    def test_normalization_mapping_specific_cases(self):
        """Test specific normalization mapping cases"""
        # Cork - keeps city separate
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Cork City'], 'Cork City')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Cork County'], 'Cork')
        
        # Dublin - keeps city separate
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Dublin City'], 'Dublin City')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Dublin County'], 'Dublin')
        
        # Galway - keeps city separate
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Galway City'], 'Galway City')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Galway County'], 'Galway')
        
        # Combined entities
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Limerick City and County'], 'Limerick')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Waterford City and County'], 'Waterford')
        
        # Special cases
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Dún Laoghaire-Rathdown'], 'Dún Laoghaire Rathdown')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['State'], 'Ireland')
    
    def test_mapping_differences(self):
        """Test that aggregation and normalization mappings serve different purposes"""
        # Cork City should aggregate to Cork but normalize to Cork City
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Cork City'], 'Cork')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Cork City'], 'Cork City')
        
        # Dublin City should aggregate to Dublin but normalize to Dublin City
        self.assertEqual(IrishCounties.AGGREGATION_MAPPING['Dublin City'], 'Dublin')
        self.assertEqual(IrishCounties.NORMALIZATION_MAPPING['Dublin City'], 'Dublin City')


class TestAnalysisConstants(unittest.TestCase):
    """Test AnalysisConstants"""
    
    def test_thresholds_exist(self):
        """Test that all analysis constants are defined"""
        self.assertEqual(AnalysisConstants.EXCELLENT_THRESHOLD, 4)
        self.assertEqual(AnalysisConstants.GOOD_THRESHOLD, 3)
        self.assertEqual(AnalysisConstants.CORRELATION_THRESHOLD, 0.5)
        self.assertEqual(AnalysisConstants.SIGNIFICANCE_LEVEL, 0.05)
    
    def test_thresholds_are_numeric(self):
        """Test that all thresholds are numeric"""
        self.assertIsInstance(AnalysisConstants.EXCELLENT_THRESHOLD, (int, float))
        self.assertIsInstance(AnalysisConstants.GOOD_THRESHOLD, (int, float))
        self.assertIsInstance(AnalysisConstants.CORRELATION_THRESHOLD, (int, float))
        self.assertIsInstance(AnalysisConstants.SIGNIFICANCE_LEVEL, (int, float))
    
    def test_threshold_relationships(self):
        """Test that thresholds have logical relationships"""
        self.assertGreater(AnalysisConstants.EXCELLENT_THRESHOLD, AnalysisConstants.GOOD_THRESHOLD)
        self.assertGreater(AnalysisConstants.CORRELATION_THRESHOLD, 0)
        self.assertLess(AnalysisConstants.CORRELATION_THRESHOLD, 1)
        self.assertGreater(AnalysisConstants.SIGNIFICANCE_LEVEL, 0)
        self.assertLess(AnalysisConstants.SIGNIFICANCE_LEVEL, 1)


if __name__ == '__main__':
    unittest.main()
