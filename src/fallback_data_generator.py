"""
Fallback Data Generator Module
Generates synthetic fallback data when API calls fail
"""

import pandas as pd
from typing import List


class FallbackDataGenerator:
    """Generates realistic fallback data for pollution, water quality, and population datasets"""
    
    FALLBACK_ANALYSIS_YEARS = list(range(2015, 2025))
    
    COUNTIES = [
        'Clare', 'Cork', 'Donegal', 'Dublin', 'Fingal', 'Galway', 'Kerry',
        'Leitrim', 'Louth', 'Mayo', 'Meath', 'Sligo', 'Tipperary',
        'Waterford', 'Westmeath', 'Wexford', 'Wicklow'
    ]
    
    # Census 2011 baseline populations (CORRECTED with official CSO figures)
    COUNTY_POPULATIONS_2011 = {
        'Clare': 117196,
        'Cork': 399802,  # Cork County only (excluding Cork City) - CORRECT per user
        'Cork City': 119230,  # Cork City separate
        'Donegal': 161137,
        'Dublin': 1273069,  # Combined Dublin area
        'Dublin City': 527612,  # Dublin City separate
        'South Dublin': 265205,  # South Dublin separate
        'Fingal': 273991,
        'Dún Laoghaire Rathdown': 206261,
        'Galway': 250541,  # CORRECTED: Official Galway County + City 2011 per user
        'Galway City': 75529,  # Galway City separate
        'Kerry': 145502,
        'Leitrim': 31798,
        'Louth': 122516,
        'Mayo': 130507,
        'Meath': 184135,
        'Sligo': 65393,
        'Tipperary': 158754,
        'Waterford': 113795,
        'Westmeath': 86164,
        'Wexford': 145273,
        'Wicklow': 136640,
        'Limerick': 191809,
        'Carlow': 54612,
        'Cavan': 73183,
        'Kilkenny': 95419,
        'Laois': 80559,
        'Longford': 39000,
        'Monaghan': 60483,
        'Offaly': 76687,
        'Roscommon': 64065
    }
    
    # Census 2022 populations (CORRECTED with official CSO figures)
    COUNTY_POPULATIONS_2022 = {
        'Clare': 127938,
        'Cork': 584156,  # Cork County + City combined in 2022
        'Donegal': 167084,
        'Dublin': 1458154,  # Dublin combined
        'Fingal': 273991,  # No 2022 data available
        'Galway': 276451,  # CORRECTED: Official Galway 2022 (County + City)
        'Kerry': 156458,
        'Leitrim': 35199,
        'Louth': 139703,
        'Mayo': 137970,
        'Meath': 220826,
        'Sligo': 70198,
        'Tipperary': 167895,
        'Waterford': 127363,
        'Westmeath': 96221,
        'Wexford': 163919,
        'Wicklow': 155851,
        'Limerick': 209536,
        'Carlow': 61968,
        'Cavan': 81704,
        'Kilkenny': 104160,
        'Laois': 91877,
        'Longford': 46751,
        'Monaghan': 65288,
        'Offaly': 83150,
        'Roscommon': 70259
    }
    
    def generate_pollution_data(self, years: List[int] = None) -> pd.DataFrame:
        """
        Generate fallback pollution data for all analysis years
        
        Args:
            years: List of years to generate data for (defaults to FALLBACK_ANALYSIS_YEARS)
            
        Returns:
            DataFrame with columns: county, year, pollutant, value
        """
        if years is None:
            years = self.FALLBACK_ANALYSIS_YEARS
            
        pollutants = ['CO2', 'NOx', 'SO2', 'PM2.5', 'PM10']
        
        data = []
        for county in self.COUNTIES:
            for year in years:
                for pollutant in pollutants:
                    base_value = hash(f"{county}{pollutant}") % 1000 + 500
                    # Realistic trend: slight decrease in pollution over time
                    year_factor = 1 - (year - 2011) * 0.015
                    value = base_value * year_factor
                    
                    data.append({
                        'county': county,
                        'year': year,
                        'pollutant': pollutant,
                        'value': value
                    })
        
        return pd.DataFrame(data)
    
    def generate_water_quality_data(self, years: List[int] = None) -> pd.DataFrame:
        """
        Generate fallback water quality data with realistic trends
        
        Args:
            years: List of years to generate data for (defaults to FALLBACK_ANALYSIS_YEARS)
            
        Returns:
            DataFrame with columns: site_code, site_name, county, water_type, 
                                   classification, year, quality_score
        """
        if years is None:
            years = self.FALLBACK_ANALYSIS_YEARS
            
        classifications = ['Excellent', 'Good', 'Sufficient', 'Poor']
        
        data = []
        for i, county in enumerate(self.COUNTIES):
            num_sites = 2 + (i % 3)
            
            for j in range(num_sites):
                site_base_quality = (i + j) % 4
                
                for year in years:
                    year_improvement = (year - 2015) * 0.05
                    quality_score = min(4, site_base_quality + year_improvement)
                    
                    if quality_score >= 3.5:
                        classification = 'Excellent'
                    elif quality_score >= 2.5:
                        classification = 'Good'
                    elif quality_score >= 1.5:
                        classification = 'Sufficient'
                    else:
                        classification = 'Poor'
                    
                    data.append({
                        'site_code': f'IE_{county[:3].upper()}_{j:03d}',
                        'site_name': f'{county} Beach {j+1}',
                        'county': county,
                        'water_type': 'Coastal',
                        'classification': classification,
                        'year': year,
                        'quality_score': quality_score
                    })
        
        return pd.DataFrame(data)
    
    def generate_population_data(self, years: List[int] = None) -> pd.DataFrame:
        """
        Generate fallback population data with interpolation between census years
        
        Args:
            years: List of years to generate data for (defaults to FALLBACK_ANALYSIS_YEARS)
            
        Returns:
            DataFrame with columns: county, year, population
        """
        if years is None:
            years = self.FALLBACK_ANALYSIS_YEARS
            
        # Census growth factors
        census_data = {
            2011: 1.0,
            2016: 1.035,
            2022: 1.08
        }
        
        data = []
        for county, base_pop_2011 in self.COUNTY_POPULATIONS_2011.items():
            for year in years:
                if year <= 2011:
                    growth_factor = 1.0
                elif year <= 2016:
                    progress = (year - 2011) / (2016 - 2011)
                    growth_factor = 1.0 + progress * (1.035 - 1.0)
                elif year <= 2022:
                    progress = (year - 2016) / (2022 - 2016)
                    growth_factor = 1.035 + progress * (1.08 - 1.035)
                else:
                    years_beyond = year - 2022
                    annual_growth = (1.08 - 1.035) / (2022 - 2016)
                    growth_factor = 1.08 + (years_beyond * annual_growth)
                
                population = int(base_pop_2011 * growth_factor)
                
                data.append({
                    'county': county,
                    'year': year,
                    'population': population
                })
        
        return pd.DataFrame(data)
