"""
Data Processing Module
Handles data cleaning, transformation, and preparation for pollution-water-population analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Any
from .constants import (
    TableNames, WaterQualityColumns, PollutionColumns, 
    PopulationColumns, IntegratedColumns, IrishCounties, AnalysisConstants
)

class DataProcessor:
    """Processes and transforms pollution, water quality, and population datasets"""
    
    # Counties to include in analysis (only those with both water quality and population data)
    ANALYSIS_COUNTIES = [
        'Clare', 'Cork', 'Donegal', 'Dublin', 'Fingal', 'Galway', 'Kerry', 
        'Leitrim', 'Louth', 'Mayo', 'Meath', 'Sligo', 'Tipperary', 
        'Waterford', 'Westmeath', 'Wexford', 'Wicklow'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def process_all_data(self, db_manager) -> Dict[str, pd.DataFrame]:
        """Process all datasets and return cleaned, transformed data"""
        processed_data = {}
        
        try:
            pollution_data = db_manager.load_dataset(TableNames.RAW_POLLUTION)
            water_quality_data = db_manager.load_dataset(TableNames.RAW_WATER_QUALITY)
            population_data = db_manager.load_dataset(TableNames.RAW_POPULATION)
            
            processed_data['pollution'] = self._process_pollution_data(pollution_data)
            processed_data['water_quality'] = self._process_water_quality_data(water_quality_data)
            processed_data['population'] = self._process_population_data(population_data)
            
            # Create integrated datasets (3 types)
            integrated_datasets = self._create_all_integrated_datasets(processed_data)
            processed_data.update(integrated_datasets)
            
            # Keep 'integrated' as the main dataset (water quality years with all data)
            processed_data['integrated'] = integrated_datasets['integrated_water_quality']
            
            self.logger.info("Data processing complete")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise
    
    def _process_pollution_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process air pollution emissions data"""
        processed_df = df.copy()
        
        # Check if this is national-level data
        is_national = 'geographic_level' in processed_df.columns and \
                     (processed_df['geographic_level'] == 'National').any()
        
        if is_national:
            processed_df['data_type'] = 'national'
        else:
            processed_df['data_type'] = 'county'
        
        processed_df[PollutionColumns.YEAR] = processed_df[PollutionColumns.YEAR].astype(int)
        
        # Normalize county names (if county-level data) but DO NOT filter
        if not is_national and PollutionColumns.COUNTY in processed_df.columns:
            processed_df[PollutionColumns.COUNTY] = processed_df[PollutionColumns.COUNTY].apply(self._normalize_county_name)
        
        # Pivot to get pollutants as columns
        pollution_pivot = processed_df.pivot_table(
            index=[PollutionColumns.COUNTY, PollutionColumns.YEAR],
            columns=PollutionColumns.POLLUTANT,
            values=PollutionColumns.VALUE,
            aggfunc='sum'
        ).reset_index()
        
        pollution_pivot.columns.name = None
        
        pollutant_cols = [col for col in pollution_pivot.columns if col not in [PollutionColumns.COUNTY, PollutionColumns.YEAR]]
        if pollutant_cols:
            pollution_pivot[PollutionColumns.TOTAL_EMISSIONS] = pollution_pivot[pollutant_cols].sum(axis=1)
        
        if 'CO2' in pollution_pivot.columns:
            pollution_pivot[PollutionColumns.CO2_EMISSIONS] = pollution_pivot['CO2']
        if 'NOx' in pollution_pivot.columns:
            pollution_pivot[PollutionColumns.NOX_EMISSIONS] = pollution_pivot['NOx']
        if 'PM2.5' in pollution_pivot.columns:
            pollution_pivot[PollutionColumns.PM25_EMISSIONS] = pollution_pivot['PM2.5']
        
        if is_national:
            pollution_pivot['data_type'] = 'national'
        
        # Calculate pollution index (normalized 0-100, higher = more pollution)
        if PollutionColumns.TOTAL_EMISSIONS in pollution_pivot.columns:
            max_emissions = pollution_pivot[PollutionColumns.TOTAL_EMISSIONS].max()
            if max_emissions > 0:
                pollution_pivot[PollutionColumns.POLLUTION_INDEX] = (
                    pollution_pivot[PollutionColumns.TOTAL_EMISSIONS] / max_emissions * 100
                )
            else:
                pollution_pivot[PollutionColumns.POLLUTION_INDEX] = 0
        
        return pollution_pivot
    
    def _process_water_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process water quality classification data"""
        processed_df = df.copy()
        
        processed_df[WaterQualityColumns.YEAR] = processed_df[WaterQualityColumns.YEAR].astype(int)
        
        # Handle different column names from real API vs fallback
        if 'statistic' in processed_df.columns and WaterQualityColumns.CLASSIFICATION not in processed_df.columns:
            processed_df[WaterQualityColumns.CLASSIFICATION] = processed_df['statistic']
        
        # Clean county names (remove "County Council" suffix)
        if WaterQualityColumns.COUNTY in processed_df.columns:
            processed_df[WaterQualityColumns.COUNTY] = processed_df[WaterQualityColumns.COUNTY].str.replace(' County Council', '', regex=False)
            processed_df[WaterQualityColumns.COUNTY] = processed_df[WaterQualityColumns.COUNTY].str.replace('Co. ', '', regex=False)
            processed_df[WaterQualityColumns.COUNTY] = processed_df[WaterQualityColumns.COUNTY].str.strip()
        
        # Ensure quality_score exists (convert classification to numeric if needed)
        if WaterQualityColumns.QUALITY_SCORE not in processed_df.columns:
            classification_map = {
                'Excellent': 4,
                'Good': 3,
                'Sufficient': 2,
                'Poor': 1
            }
            processed_df[WaterQualityColumns.QUALITY_SCORE] = processed_df[WaterQualityColumns.CLASSIFICATION].map(classification_map)
        
        processed_df[WaterQualityColumns.IS_EXCELLENT] = (
            processed_df[WaterQualityColumns.QUALITY_SCORE] >= AnalysisConstants.EXCELLENT_THRESHOLD
        ).astype(int)
        
        processed_df[WaterQualityColumns.IS_GOOD_OR_BETTER] = (
            processed_df[WaterQualityColumns.QUALITY_SCORE] >= AnalysisConstants.GOOD_THRESHOLD
        ).astype(int)
        
        agg_dict = {
            WaterQualityColumns.QUALITY_SCORE: 'mean',
            WaterQualityColumns.IS_EXCELLENT: 'mean',
            WaterQualityColumns.IS_GOOD_OR_BETTER: 'mean'
        }
        
        # Add site count if site_code column exists
        if WaterQualityColumns.SITE_CODE in processed_df.columns:
            agg_dict[WaterQualityColumns.SITE_CODE] = 'count'
        else:
            # Use any column for counting records
            agg_dict[WaterQualityColumns.CLASSIFICATION] = 'count'
        
        # Normalize county names BEFORE groupby
        processed_df[WaterQualityColumns.COUNTY] = processed_df[WaterQualityColumns.COUNTY].apply(self._normalize_county_name)
        
        # Filter to only include analysis counties
        processed_df = processed_df[processed_df[WaterQualityColumns.COUNTY].isin(self.ANALYSIS_COUNTIES)]
        
        county_year_agg = processed_df.groupby([WaterQualityColumns.COUNTY, WaterQualityColumns.YEAR]).agg(agg_dict).reset_index()
        
        # Rename aggregated columns
        rename_dict = {
            WaterQualityColumns.QUALITY_SCORE: WaterQualityColumns.AVG_QUALITY_SCORE,
            WaterQualityColumns.IS_EXCELLENT: IntegratedColumns.PERCENT_EXCELLENT,
            WaterQualityColumns.IS_GOOD_OR_BETTER: IntegratedColumns.PERCENT_GOOD_OR_BETTER
        }
        
        if WaterQualityColumns.SITE_CODE in county_year_agg.columns:
            rename_dict[WaterQualityColumns.SITE_CODE] = WaterQualityColumns.SITES_PER_COUNTY
        elif WaterQualityColumns.CLASSIFICATION in county_year_agg.columns:
            rename_dict[WaterQualityColumns.CLASSIFICATION] = WaterQualityColumns.SITES_PER_COUNTY
        
        county_year_agg.rename(columns=rename_dict, inplace=True)
        
        county_year_agg[IntegratedColumns.PERCENT_EXCELLENT] *= 100
        county_year_agg[IntegratedColumns.PERCENT_GOOD_OR_BETTER] *= 100
        
        return county_year_agg
    
    def _process_population_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process population data from multiple census years"""
        processed_df = df.copy()
        
        processed_df[PopulationColumns.YEAR] = processed_df[PopulationColumns.YEAR].astype(int)
        
        # Normalize county names BEFORE filtering
        processed_df[PopulationColumns.COUNTY] = processed_df[PopulationColumns.COUNTY].apply(self._normalize_county_name)
        
        # Filter to county-level data only (exclude town/electoral division level)
        # For 2011: Keep "State" level (will be renamed to Ireland)
        # For 2016: Filter to county-level aggregates (need to aggregate from electoral divisions)
        # For 2022: Keep "Population per County" statistic
        
        # Identify county-level records
        county_level_records = []
        
        # 2022 Census: Direct county-level data (exclude "Ireland" national aggregate)
        census_2022 = processed_df[
            (processed_df['census_year'] == 2022) &
            (processed_df['statistic'] == 'Population per County') &
            (processed_df[PopulationColumns.COUNTY] != 'Ireland')
        ].copy()
        if len(census_2022) > 0:
            self.logger.info(f"Found {len(census_2022)} county records from 2022 Census (excluding Ireland aggregate)")
            county_level_records.append(census_2022)
        
        # 2016 Census: Use the official census total from the dataset
        # NOTE: The 2016 census total (4,761,865) is stored in the dataset with census_year=2011
        # as one of the "Ireland" population records (after "State" is normalized to "Ireland")
        # This represents the official 2016 census (3.8% growth from 2011's 4,588,252)
        
        # Get the 2016 total from Ireland records in census_year 2011
        ireland_2016_candidates = processed_df[
            (processed_df['census_year'] == 2011) &
            (processed_df[PopulationColumns.COUNTY] == 'Ireland') &
            (processed_df['statistic'] == 'Population') &
            (processed_df[PopulationColumns.POPULATION] > 4700000) &  # Filter for 2016 census value
            (processed_df[PopulationColumns.POPULATION] < 4800000)
        ].copy()
        
        if len(ireland_2016_candidates) > 0:
            # Found the 2016 census total - use it as a single Ireland record
            ireland_2016 = ireland_2016_candidates.iloc[0:1].copy()
            ireland_2016[PopulationColumns.YEAR] = 2016
            ireland_2016['census_year'] = 2016
            ireland_2016['statistic'] = 'Population per County'
            county_level_records.append(ireland_2016)
        
        # 2011 Census: County-level data
        # NOTE: 2011 census has 6 "Population" records per county (different time periods/estimates)
        # We take the SECOND-HIGHEST value which represents the official 2011 census count
        census_2011 = processed_df[processed_df['census_year'] == 2011].copy()
        if len(census_2011) > 0:
            # Filter to "Population" statistic and exclude "State" (Ireland national)
            census_2011_pop = census_2011[
                (census_2011['statistic'] == 'Population') &
                (census_2011[PopulationColumns.COUNTY] != 'Ireland')
            ].copy()
            
            if len(census_2011_pop) > 0:
                # For each county, take the second-highest population value (official 2011 census)
                census_2011_corrected = []
                for county in census_2011_pop[PopulationColumns.COUNTY].unique():
                    county_data = census_2011_pop[census_2011_pop[PopulationColumns.COUNTY] == county].copy()
                    # Sort by population descending and take the second record
                    county_data = county_data.sort_values(PopulationColumns.POPULATION, ascending=False)
                    if len(county_data) >= 2:
                        # Take second-highest (official census count)
                        official_record = county_data.iloc[1:2].copy()
                    else:
                        # Fallback to highest if only one record
                        official_record = county_data.iloc[0:1].copy()
                    census_2011_corrected.append(official_record)
                
                census_2011_pop = pd.concat(census_2011_corrected, ignore_index=True)
                census_2011_pop['statistic'] = 'Population per County'
                self.logger.info(f"Found {len(census_2011_pop)} county records from 2011 Census (using second-highest value = official census)")
                county_level_records.append(census_2011_pop)
        
        # Combine all county-level records
        if county_level_records:
            processed_df = pd.concat(county_level_records, ignore_index=True)
        else:
            self.logger.warning("No county-level population data found")
            return pd.DataFrame()
        
        # Sort by county and year for growth calculations
        processed_df = processed_df.sort_values([PopulationColumns.COUNTY, PopulationColumns.YEAR])
        
        # Calculate population density (population per km²)
        processed_df[PopulationColumns.POPULATION_DENSITY] = processed_df.apply(
            lambda row: row[PopulationColumns.POPULATION] / IrishCounties.COUNTY_AREAS.get(row[PopulationColumns.COUNTY], 1000),
            axis=1
        )
        
        # Calculate year-over-year population growth
        processed_df[PopulationColumns.POPULATION_GROWTH] = processed_df.groupby(PopulationColumns.COUNTY)[PopulationColumns.POPULATION].pct_change() * 100
        
        # Calculate total growth since first year
        first_year_pop = processed_df.groupby(PopulationColumns.COUNTY)[PopulationColumns.POPULATION].transform('first')
        processed_df[PopulationColumns.POPULATION_GROWTH_TOTAL] = (
            (processed_df[PopulationColumns.POPULATION] - first_year_pop) / first_year_pop * 100
        )
        
        return processed_df
    
    def _normalize_county_name(self, county: str) -> str:
        """Normalize county names for consistent merging"""
        if pd.isna(county):
            return county
        # Remove various prefixes and suffixes
        county = str(county).strip()
        county = county.replace('Co. ', '')
        county = county.replace(' County Council', '')
        county = county.replace(' City Council', '')
        county = county.replace(' City', '')
        # Handle special cases
        if county == 'Dún Laoghaire-Rathdown':
            county = 'Dún Laoghaire Rathdown'
        if county == 'State':
            county = 'Ireland'
        return county
    
    def _create_all_integrated_datasets(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Create three types of integrated datasets:
        1. pollution_vs_population: Pollution vs Population (census years: 2011, 2016, 2022)
        2. pollution_vs_water: Pollution vs Water Quality (water quality years)
        3. integrated_water_quality: Water Quality vs Population (water quality years with 2022 census forward-filled)
        """
        pollution_df = processed_data['pollution'].copy()
        water_quality_df = processed_data['water_quality'].copy()
        population_df = processed_data['population'].copy()
        
        # Check if pollution is national-level
        is_national_pollution = 'data_type' in pollution_df.columns and \
                               (pollution_df['data_type'] == 'national').any()
        
        if not is_national_pollution:
            return {'integrated_water_quality': self._create_integrated_dataset(processed_data)}
        
        # Get national pollution data
        national_pollution = pollution_df[pollution_df['data_type'] == 'national'].copy()
        
        # Filter population data to only include actual county population (not other statistics)
        county_pop = population_df[
            (population_df['statistic'] == 'Population per County') |
            (population_df['statistic'] == 'Population per  County')  # Handle potential double space
        ].copy()
        
        # Get census years available
        census_years = sorted(county_pop['census_year'].unique())
        self.logger.info(f"Census years available: {census_years}")
        
        # Create three integrated datasets
        pollution_vs_pop = self._create_pollution_vs_population(national_pollution, county_pop, census_years)
        pollution_vs_water = self._create_pollution_vs_water(national_pollution, water_quality_df)
        integrated_water_quality = self._create_water_vs_population(water_quality_df, county_pop, national_pollution)
        
        return {
            'pollution_vs_population': pollution_vs_pop,
            'pollution_vs_water': pollution_vs_water,
            'integrated_water_quality': integrated_water_quality
        }
    
    def _create_pollution_vs_population(self, national_pollution: pd.DataFrame, 
                                       county_pop: pd.DataFrame, 
                                       census_years: list) -> pd.DataFrame:
        """Create Pollution vs Population dataset for census years only"""
        # Filter pollution data to census years
        pollution_census = national_pollution[national_pollution['year'].isin(census_years)].copy()
        
        # Filter population to census years
        pop_census = county_pop[county_pop['census_year'].isin(census_years)].copy()
        
        # Get unique counties
        counties = pop_census['county'].unique()
        
        # Create dataset: for each county-census year, add national pollution
        records = []
        for _, pop_row in pop_census.iterrows():
            county = pop_row['county']
            year = pop_row['year']
            
            # Get pollution for this year
            poll_year = pollution_census[pollution_census['year'] == year]
            
            if len(poll_year) > 0:
                poll_data = poll_year.iloc[0].to_dict()
                record = {
                    'county': county,
                    'year': year,
                    'census_year': pop_row['census_year'],
                    'population': pop_row['population'],
                    'total_emissions': poll_data.get('total_emissions', None),
                    'pollution_index': poll_data.get('pollution_index', None),
                    'data_type': 'pollution_vs_population'
                }
                
                # Add all pollution columns
                for col in poll_data:
                    if col not in record and col not in ['county', 'year', 'data_type']:
                        record[col] = poll_data[col]
                
                records.append(record)
        
        df = pd.DataFrame(records)
        
        # Calculate total national population by year
        total_pop_by_year = county_pop.groupby('year').agg({
            'population': 'sum'
        }).reset_index()
        total_pop_by_year.rename(columns={'population': 'total_national_population'}, inplace=True)
        
        df = df.merge(total_pop_by_year, on='year', how='left')
        
        # Calculate emissions per capita using national population
        if 'total_emissions' in df.columns and 'total_national_population' in df.columns:
            df['emissions_per_capita'] = (df['total_emissions'] / df['total_national_population'] * 1000)
        
        # Calculate estimated county emissions based on population proportion
        if 'total_emissions' in df.columns and 'population' in df.columns and 'total_national_population' in df.columns:
            df['estimated_county_emissions'] = df['total_emissions'] * (df['population'] / df['total_national_population'])
        
        return df
    
    def _create_pollution_vs_water(self, national_pollution: pd.DataFrame, 
                                   water_quality_df: pd.DataFrame) -> pd.DataFrame:
        """Create Pollution vs Water Quality dataset"""
        # Get water quality years
        water_years = water_quality_df['year'].unique()
        
        # Filter pollution to water quality years
        pollution_water_years = national_pollution[national_pollution['year'].isin(water_years)].copy()
        
        # Merge water quality with pollution (by year only, broadcast national pollution to all counties)
        df = water_quality_df.merge(
            pollution_water_years.drop(columns=['county']),
            on='year',
            how='left'
        )
        
        df['data_type'] = 'pollution_vs_water'
        
        return df
    
    def _create_water_vs_population(self, water_quality_df: pd.DataFrame,
                                   county_pop: pd.DataFrame,
                                   national_pollution: pd.DataFrame) -> pd.DataFrame:
        """Create Water Quality vs Population dataset (current methodology with 2022 forward-filled)"""
        # Get water quality years and counties
        water_years = water_quality_df['year'].unique()
        water_counties = water_quality_df['county'].unique()
        
        # Filter to counties that have population data
        pop_counties = county_pop['county'].unique()
        valid_counties = [c for c in water_counties if c in pop_counties and c != 'Ireland']
        
        # Filter water quality to valid counties
        water_filtered = water_quality_df[water_quality_df['county'].isin(valid_counties)].copy()
        
        # Create county-year grid for population forward-filling
        county_year_grid = pd.DataFrame([
            {'county': county, 'year': year}
            for county in valid_counties
            for year in water_years
        ])
        
        # Merge with available population data (2022 census)
        county_pop_2022 = county_pop[county_pop['census_year'] == 2022][['county', 'year', 'population']].copy()
        
        county_pop_expanded = county_year_grid.merge(
            county_pop_2022,
            on=['county', 'year'],
            how='left'
        )
        
        # Forward and backward fill population
        county_pop_expanded = county_pop_expanded.sort_values(['county', 'year'])
        county_pop_expanded['population'] = county_pop_expanded.groupby('county')['population'].ffill()
        county_pop_expanded['population'] = county_pop_expanded.groupby('county')['population'].bfill()
        
        # Merge water quality with population
        df = water_filtered.merge(
            county_pop_expanded,
            on=['county', 'year'],
            how='left'
        )
        
        # Add national pollution data
        pollution_water_years = national_pollution[national_pollution['year'].isin(water_years)].copy()
        df = df.merge(
            pollution_water_years.drop(columns=['county']),
            on='year',
            how='left'
        )
        
        # Calculate total national population by year
        total_pop_by_year = county_pop.groupby('year').agg({
            'population': 'sum'
        }).reset_index()
        total_pop_by_year.rename(columns={'population': 'total_national_population'}, inplace=True)
        
        df = df.merge(total_pop_by_year, on='year', how='left')
        
        # Calculate emissions per capita
        if 'total_emissions' in df.columns and 'total_national_population' in df.columns:
            df['emissions_per_capita'] = (df['total_emissions'] / df['total_national_population'] * 1000)
        
        # Calculate estimated county emissions based on population proportion
        if 'total_emissions' in df.columns and 'population' in df.columns and 'total_national_population' in df.columns:
            df['estimated_county_emissions'] = df['total_emissions'] * (df['population'] / df['total_national_population'])
        
        df['data_type'] = 'water_vs_population'
        
        return df
    
    def _create_integrated_dataset(self, processed_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create integrated dataset combining pollution, water quality, and population
        
        Creates three types of integrated data:
        1. Pollution vs Population (census years: 2011, 2016, 2022)
        2. Pollution vs Water Quality (water quality years)
        3. Water Quality vs Population (water quality years with 2022 census forward-filled)
        """
        # Get datasets (county names already normalized during processing)
        water_quality_df = processed_data['water_quality'].copy()
        population_df = processed_data['population'].copy()
        
        # Check if pollution data is national-level
        pollution_df = processed_data['pollution'].copy()
        is_national_pollution = 'data_type' in pollution_df.columns and \
                               (pollution_df['data_type'] == 'national').any()
        
        if is_national_pollution:
            # Get list of counties that have population data
            # Try both possible statistic names
            pop_filter = (population_df['statistic'] == 'Population per County') | (population_df['statistic'].str.contains('Population', na=False))
            counties_with_population = population_df[pop_filter][PopulationColumns.COUNTY].unique()
            
            # Start with water quality data (county-level), but only for counties with population data
            # Exclude 'Ireland' national summary as it's not comparable to county-level data
            integrated = water_quality_df[
                (water_quality_df[WaterQualityColumns.COUNTY].isin(counties_with_population)) &
                (water_quality_df[WaterQualityColumns.COUNTY] != 'Ireland')
            ].copy()
            
            # Add national pollution data to each county row
            national_pollution = pollution_df[pollution_df['data_type'] == 'national'].copy()
            
            # Merge pollution by year only (broadcast national data to all counties)
            integrated = integrated.merge(
                national_pollution.drop(columns=[PollutionColumns.COUNTY]),
                on=WaterQualityColumns.YEAR,
                how='left',
                suffixes=('', '_pollution')
            )
            
            # Calculate total national population by year
            total_pop_by_year = population_df.groupby(PopulationColumns.YEAR).agg({
                PopulationColumns.POPULATION: 'sum'
            }).reset_index()
            total_pop_by_year.rename(columns={PopulationColumns.POPULATION: 'total_national_population'}, inplace=True)
            
            # Add total national population
            integrated = integrated.merge(
                total_pop_by_year,
                on=WaterQualityColumns.YEAR,
                how='left'
            )
            
            # Add county-specific population
            county_pop = population_df[population_df['statistic'] == 'Population per County'][[
                PopulationColumns.COUNTY,
                PopulationColumns.YEAR,
                PopulationColumns.POPULATION
            ]].copy()
            
            # Since population data is only available for 2022, we need to forward-fill for other years
            # Get all unique counties and years from integrated dataset
            self.logger.info(f"Integrated columns: {integrated.columns.tolist()}")
            all_counties = integrated[WaterQualityColumns.COUNTY].unique()
            all_years = integrated[WaterQualityColumns.YEAR].unique()
            self.logger.info(f"Found {len(all_counties)} counties and {len(all_years)} years in water quality data")
            
            # Create a complete county-year grid
            county_year_grid = pd.DataFrame([
                {PopulationColumns.COUNTY: county, PopulationColumns.YEAR: year}
                for county in all_counties
                for year in all_years
            ])
            
            # Merge with available population data
            county_pop_expanded = county_year_grid.merge(
                county_pop,
                on=[PopulationColumns.COUNTY, PopulationColumns.YEAR],
                how='left'
            )
            
            # Fill missing years with nearest census data
            # For each county, use the most recent census data available
            county_pop_expanded = county_pop_expanded.sort_values([PopulationColumns.COUNTY, PopulationColumns.YEAR])
            
            # Forward fill (2022 -> 2023, 2024) and backward fill (2022 -> 2021)
            county_pop_expanded[PopulationColumns.POPULATION] = county_pop_expanded.groupby(PopulationColumns.COUNTY)[PopulationColumns.POPULATION].ffill()
            county_pop_expanded[PopulationColumns.POPULATION] = county_pop_expanded.groupby(PopulationColumns.COUNTY)[PopulationColumns.POPULATION].bfill()
            
            self.logger.info(f"Expanded population data from {len(county_pop)} to {len(county_pop_expanded)} records (forward-filled for missing years)")
            
            integrated = integrated.merge(
                county_pop_expanded,
                on=[WaterQualityColumns.COUNTY, WaterQualityColumns.YEAR],
                how='left',
                suffixes=('', '_county')
            )
            
            self.logger.info(f"Created county-level dataset with national pollution data for {integrated[WaterQualityColumns.COUNTY].nunique()} counties")
            
        else:
            # Original county-level logic
            integrated = pollution_df.copy()
            
            # Merge population data
            population = population_df[[
                PopulationColumns.COUNTY,
                PopulationColumns.YEAR,
                PopulationColumns.POPULATION,
                PopulationColumns.POPULATION_DENSITY,
                PopulationColumns.POPULATION_GROWTH,
                PopulationColumns.POPULATION_GROWTH_TOTAL
            ]]
            
            integrated = integrated.merge(
                population,
                left_on=[PollutionColumns.COUNTY, PollutionColumns.YEAR],
                right_on=[PopulationColumns.COUNTY, PopulationColumns.YEAR],
                how='outer'
            )
            
            # Merge water quality
            integrated = integrated.merge(
                water_quality_df,
                on=[PollutionColumns.COUNTY, PollutionColumns.YEAR],
                how='outer'
            )
        
        # Ensure county and year columns are properly named
        if IntegratedColumns.COUNTY not in integrated.columns:
            if WaterQualityColumns.COUNTY in integrated.columns:
                integrated.rename(columns={WaterQualityColumns.COUNTY: IntegratedColumns.COUNTY}, inplace=True)
        
        if IntegratedColumns.YEAR not in integrated.columns:
            if WaterQualityColumns.YEAR in integrated.columns:
                integrated.rename(columns={WaterQualityColumns.YEAR: IntegratedColumns.YEAR}, inplace=True)
        
        # Calculate derived metrics
        # Emissions per capita (use total national population for national emissions)
        if IntegratedColumns.TOTAL_EMISSIONS in integrated.columns:
            if 'total_national_population' in integrated.columns and is_national_pollution:
                self.logger.info("Calculating emissions per capita using TOTAL NATIONAL POPULATION (national emissions)")
                integrated[IntegratedColumns.EMISSIONS_PER_CAPITA] = (
                    integrated[IntegratedColumns.TOTAL_EMISSIONS] / integrated['total_national_population'] * 1000
                )
            elif IntegratedColumns.POPULATION in integrated.columns:
                self.logger.info("Calculating emissions per capita using county population")
                integrated[IntegratedColumns.EMISSIONS_PER_CAPITA] = (
                    integrated[IntegratedColumns.TOTAL_EMISSIONS] / integrated[IntegratedColumns.POPULATION] * 1000
                )
        
        # Water quality vs pollution relationship (negative correlation expected)
        if IntegratedColumns.AVG_QUALITY_SCORE in integrated.columns and IntegratedColumns.POLLUTION_INDEX in integrated.columns:
            # Normalize both to 0-100 scale
            water_normalized = integrated[IntegratedColumns.AVG_QUALITY_SCORE] / 4 * 100  # Quality score is 1-4
            pollution_normalized = integrated[IntegratedColumns.POLLUTION_INDEX]
            
            # Create relationship metric (higher = better water quality relative to pollution)
            integrated[IntegratedColumns.WATER_QUALITY_VS_POLLUTION] = water_normalized - pollution_normalized
        
        # Fill NaN values for numeric columns (but NOT population - keep it as NaN if truly missing)
        numeric_columns = integrated.select_dtypes(include=[np.number]).columns
        # Exclude population from median filling
        columns_to_fill = [col for col in numeric_columns if col not in [IntegratedColumns.POPULATION, 'total_national_population']]
        if columns_to_fill:
            integrated[columns_to_fill] = integrated[columns_to_fill].fillna(integrated[columns_to_fill].median())
        
        # Sort by county and year
        integrated = integrated.sort_values([IntegratedColumns.COUNTY, IntegratedColumns.YEAR])
        
        self.logger.info(f"Created integrated dataset with {len(integrated)} records")
        return integrated
