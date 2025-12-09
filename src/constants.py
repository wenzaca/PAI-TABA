class TableNames:
    RAW_POLLUTION = 'raw_pollution'
    RAW_WATER_QUALITY = 'raw_water_quality'
    RAW_POPULATION = 'raw_population'

class WaterQualityColumns:
    SITE_CODE = 'site_code'
    COUNTY = 'county'
    CLASSIFICATION = 'classification'
    YEAR = 'year'
    QUALITY_SCORE = 'quality_score'
    IS_EXCELLENT = 'is_excellent'
    IS_GOOD_OR_BETTER = 'is_good_or_better'
    SITES_PER_COUNTY = 'sites_per_county'
    AVG_QUALITY_SCORE = 'avg_quality_score'

class PollutionColumns:
    COUNTY = 'county'
    YEAR = 'year'
    POLLUTANT = 'pollutant'
    VALUE = 'value'
    TOTAL_EMISSIONS = 'total_emissions'
    CO2_EMISSIONS = 'co2_emissions'
    NOX_EMISSIONS = 'nox_emissions'
    PM25_EMISSIONS = 'pm25_emissions'
    POLLUTION_INDEX = 'pollution_index'

class PopulationColumns:
    COUNTY = 'county'
    YEAR = 'year'
    POPULATION = 'population'
    POPULATION_DENSITY = 'population_density'
    POPULATION_GROWTH = 'population_growth'
    POPULATION_GROWTH_TOTAL = 'population_growth_total'

class IntegratedColumns:
    COUNTY = 'county'
    YEAR = 'year'
    TOTAL_EMISSIONS = PollutionColumns.TOTAL_EMISSIONS
    POLLUTION_INDEX = PollutionColumns.POLLUTION_INDEX
    CO2_EMISSIONS = PollutionColumns.CO2_EMISSIONS
    AVG_QUALITY_SCORE = WaterQualityColumns.AVG_QUALITY_SCORE
    SITES_PER_COUNTY = WaterQualityColumns.SITES_PER_COUNTY
    PERCENT_EXCELLENT = 'percent_excellent'
    PERCENT_GOOD_OR_BETTER = 'percent_good_or_better'
    POPULATION = PopulationColumns.POPULATION
    POPULATION_GROWTH = PopulationColumns.POPULATION_GROWTH
    POPULATION_DENSITY = PopulationColumns.POPULATION_DENSITY
    EMISSIONS_PER_CAPITA = 'emissions_per_capita'

class IrishCounties:
    COUNTY_AREAS = {
        'Clare': 3450,
        'Cork': 7500,
        'Donegal': 4861,
        'Dublin': 922,
        'Fingal': 455,
        'Galway': 6149,
        'Kerry': 4807,
        'Leitrim': 1590,
        'Louth': 826,
        'Mayo': 5586,
        'Meath': 2342,
        'Sligo': 1838,
        'Tipperary': 4303,
        'Waterford': 1857,
        'Westmeath': 1840,
        'Wexford': 2365,
        'Wicklow': 2025
    }

class AnalysisConstants:
    EXCELLENT_THRESHOLD = 4
    GOOD_THRESHOLD = 3
    CORRELATION_THRESHOLD = 0.5
    SIGNIFICANCE_LEVEL = 0.05
