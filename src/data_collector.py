"""
Data Collection Module
Collects Irish government data for environmental-demographic analysis
"""

import requests
import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import io
from src.fallback_data_generator import FallbackDataGenerator


class DataCollector:
    """Collects pollution, water quality, and population data from Irish government sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_urls = {
            'cso': 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset',
            'epa_bathing': 'https://epawebapp.epa.ie/bathingwater/api',
            'data_gov': 'https://data.gov.ie/api/3/action'
        }
        self._fallback_generator: Optional[FallbackDataGenerator] = None
        
    def collect_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Collect all required datasets for pollution-water-population analysis"""
        try:
            datasets = {
                'raw_pollution': self._collect_pollution_data(),
                'raw_water_quality': self._collect_water_quality_data(),
                'raw_population': self._collect_population_data()
            }
            return datasets
            
        except Exception as e:
            self.logger.error(f"Collection error: {str(e)}")
            raise
    
    def _collect_pollution_data(self) -> pd.DataFrame:
        """
        Collect air pollution emissions data from CSO Ireland
        Dataset: EAA20 - Air Pollution Emissions (national-level only)
        """
        try:
            url = f"{self.base_urls['cso']}/EAA20/JSON-stat/2.0/en"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                records = self._parse_cso_jsonstat(data, 'pollution')
                
                if records and len(records) > 0:
                    df = pd.DataFrame(records)
                    
                    df['geographic_level'] = 'National'
                    df['county'] = 'Ireland'
                    
                    return self._normalize_pollution_columns(df)
            
            self.logger.warning("Could not parse CSO pollution data, using fallback")
            
        except Exception as e:
            self.logger.error(f"Error collecting pollution data: {str(e)}")
        
        self.logger.warning("Using FALLBACK pollution data")
        return self._get_fallback_generator().generate_pollution_data()
    
    def _collect_water_quality_data(self) -> pd.DataFrame:
        """
        Collect bathing water quality data from CSO EPA02 dataset
        """
        try:
            url = f"{self.base_urls['cso']}/EPA02/JSON-stat/2.0/en"
            
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'dimension' in data and 'value' in data:
                    records = self._parse_cso_jsonstat(data, 'water_quality')
                    
                    if records:
                        df = pd.DataFrame(records)
                        df = self._normalize_water_quality_columns(df)
                        return df
            
            csv_url = f"{self.base_urls['cso']}/EPA02/CSV/1.0/en"
            response = requests.get(csv_url, timeout=60)
            
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                df = self._normalize_water_quality_columns(df)
                return df
            
            self.logger.warning("No water quality data available from CSO, using fallback")
            return self._get_fallback_generator().generate_water_quality_data()
                
        except Exception as e:
            self.logger.error(f"Error collecting water quality data: {str(e)}")
            return self._get_fallback_generator().generate_water_quality_data()
    
    def _collect_population_data(self) -> pd.DataFrame:
        """
        Collect population by county data from CSO Ireland census datasets
        """
        all_population_data = []
        
        census_datasets = {
            2011: 'E2011',
            2022: 'G0420'
        }

        self._process_2016_data_from_2011_dataset(all_population_data)
        
        for year, dataset_code in census_datasets.items():
            try:
                url = f"{self.base_urls['cso']}/{dataset_code}/JSON-stat/2.0/en"
                
                response = requests.get(url, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'dimension' in data and 'value' in data:

                        county_records = self._extract_county_population_data(data, year)
                        
                        if county_records:
                            df = pd.DataFrame(county_records)
                            all_population_data.append(df)
                        else:
                            self.logger.warning(f"No county records found in {year} census")
                    else:
                        self.logger.warning(f"Invalid data format from {year} Census")
                else:
                    self.logger.warning(f"Failed to fetch {year} Census (status {response.status_code})")
                    
            except Exception as e:
                self.logger.error(f"Error collecting {year} Census data: {str(e)}")
        
        if all_population_data:
            combined_df = pd.concat(all_population_data, ignore_index=True)
            return combined_df
        else:
            self.logger.warning("No census data collected, using fallback")
            return self._get_fallback_generator().generate_population_data([2011, 2016, 2022])

    def _process_2016_data_from_2011_dataset(self, all_population_data):
        try:
            url = f"{self.base_urls['cso']}/E2011/JSON-stat/2.0/en"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if 'dimension' in data and 'value' in data:
                    # Extract 2016 national total only
                    ireland_2016_record = self._extract_national_total_2016(data, 'E2011')
                    if ireland_2016_record:
                        df_2016 = pd.DataFrame([ireland_2016_record])
                        all_population_data.append(df_2016)
                        self.logger.info(
                            f"Extracted 2016 Ireland national total: {ireland_2016_record['population']:,}")
        except Exception as e:
            self.logger.warning(f"Could not extract 2016 national total: {str(e)}")

    def _parse_cso_jsonstat(self, data: dict, dataset_type: str) -> List[Dict]:
        """Parse CSO JSON-stat 2.0 format data"""
        records = []
        
        try:
            dimensions = data.get('dimension', {})
            values = data.get('value', [])
            
            dim_info = {}
            dim_sizes = []
            dim_names = []
            
            for dim_id, dim_data in dimensions.items():
                if 'category' in dim_data:
                    labels = list(dim_data['category'].get('label', {}).values())
                    dim_info[dim_id] = labels
                    dim_sizes.append(len(labels))
                    dim_names.append(dim_id)
            
            if dim_sizes and values:
                import itertools
                
                dim_values = [dim_info[name] for name in dim_names]
                
                for idx, combination in enumerate(itertools.product(*dim_values)):
                    if idx < len(values) and values[idx] is not None:
                        record = {}
                        
                        for dim_name, dim_value in zip(dim_names, combination):
                            if 'tlist' in dim_name.lower() or 'year' in dim_name.lower():
                                record['year'] = dim_value
                            elif 'statistic' in dim_name.lower():
                                record['statistic'] = dim_value
                            else:
                                if dataset_type == 'pollution':
                                    record['pollutant'] = dim_value
                                elif dataset_type == 'water_quality':
                                    record['county'] = dim_value
                                elif dataset_type == 'population':
                                    record['county'] = dim_value
                                else:
                                    record['category'] = dim_value
                        
                        record['value'] = values[idx]
                        records.append(record)
        
        except Exception as e:
            self.logger.warning(f"Error parsing JSON-stat data: {str(e)}")
        
        return records
    
    def _normalize_pollution_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize pollution data column names"""
        if 'county' not in df.columns and 'County' in df.columns:
            df.rename(columns={'County': 'county'}, inplace=True)
        if 'year' not in df.columns and 'Year' in df.columns:
            df.rename(columns={'Year': 'year'}, inplace=True)
        if 'pollutant' not in df.columns and 'Pollutant' in df.columns:
            df.rename(columns={'Pollutant': 'pollutant'}, inplace=True)
        if 'value' not in df.columns and 'Value' in df.columns:
            df.rename(columns={'Value': 'value'}, inplace=True)
        
        return df
    
    def _normalize_water_quality_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize water quality data column names"""
        if 'county' not in df.columns and 'County' in df.columns:
            df.rename(columns={'County': 'county'}, inplace=True)
        if 'year' not in df.columns and 'Year' in df.columns:
            df.rename(columns={'Year': 'year'}, inplace=True)
        if 'classification' not in df.columns and 'Classification' in df.columns:
            df.rename(columns={'Classification': 'classification'}, inplace=True)
        
        return df
    
    def _normalize_population_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize population data column names"""
        if 'county' not in df.columns and 'County' in df.columns:
            df.rename(columns={'County': 'county'}, inplace=True)
        if 'year' not in df.columns and 'Year' in df.columns:
            df.rename(columns={'Year': 'year'}, inplace=True)
        
        if 'population' not in df.columns:
            if 'value' in df.columns:
                df.rename(columns={'value': 'population'}, inplace=True)
            elif 'Population' in df.columns:
                df.rename(columns={'Population': 'population'}, inplace=True)
        
        return df
    
    def _extract_county_population_data(self, data: dict, year: int) -> List[Dict]:
        """
        Extract county-level population data from CSO JSON-stat format
        Properly handles city/county aggregation for Cork, Galway, etc.
        Handles different dataset structures for 2011, 2016, 2022
        """
        records = []
        
        try:
            dimensions = data.get('dimension', {})
            values = data.get('value', [])
            
            # Find dimension info - different datasets have different structures
            county_dim = None
            sex_dim = None
            statistic_dim = None
            year_dim = None

            for dim_id, dim_data in dimensions.items():
                label = dim_data.get('label', '').lower()
                if 'county' in label or 'city' in label or 'area' in label or 'electoral' in label or 'towns' in label:
                    county_dim = dim_id
                elif 'sex' in label:
                    sex_dim = dim_id
                elif 'statistic' in label:
                    statistic_dim = dim_id
                elif 'year' in label or 'census' in label:
                    year_dim = dim_id
            
            if not county_dim:
                self.logger.warning(f"No county/area dimension found in {year} census data")
                return records
            
            # Get dimension categories
            counties = list(dimensions[county_dim]['category']['label'].values())
            sexes = list(dimensions[sex_dim]['category']['label'].values()) if sex_dim else ['Both sexes']
            statistics = list(dimensions[statistic_dim]['category']['label'].values()) if statistic_dim else ['Population']
            years = list(dimensions[year_dim]['category']['label'].values()) if year_dim else [str(year)]
            
            self.logger.info(f"{year} census: Found {len(counties)} counties, {len(statistics)} statistics")
            

            import itertools
            
            dim_names = list(dimensions.keys())
            dim_values_lists = [list(dimensions[dim_id]['category']['label'].values()) for dim_id in dim_names]
            
            for idx, combination in enumerate(itertools.product(*dim_values_lists)):
                if idx < len(values) and values[idx] is not None:
                    dim_values = dict(zip(dim_names, combination))
                    
                    county = dim_values.get(county_dim, '')
                    sex = dim_values.get(sex_dim, 'Both sexes')
                    statistic = dim_values.get(statistic_dim, 'Population')
                    census_year = dim_values.get(year_dim, str(year))

                    include_record = False
                    
                    if year == 2011:
                        include_record = (
                            county != 'State' and 
                            sex == 'Both sexes' and 
                            statistic == 'Population' and
                            str(year) in census_year
                        )

                    elif year == 2022:
                        include_record = (
                            county.startswith('Co. ') and
                            'Population per County' in statistic
                        )
                        county = county.replace('Co. ', '')

                    
                    if include_record:
                        records.append({
                            'county': county,
                            'year': year,
                            'census_year': year,
                            'population': values[idx],
                            'statistic': 'Population per County'
                        })
            
            self.logger.info(f"Extracted {len(records)} raw records from {year} census")
            
            aggregated_records = self._aggregate_city_county_pairs(records)
            
            return aggregated_records
            
        except Exception as e:
            self.logger.error(f"Error extracting county population data for {year}: {str(e)}")
            return records
    
    def _aggregate_city_county_pairs(self, records: List[Dict]) -> List[Dict]:
        """
        Aggregate city and county pairs (Cork City + Cork County = Cork, etc.)
        """
        from .constants import IrishCounties
        
        aggregated = {}
        
        for record in records:
            county = record['county']
            population = record['population']
            
            # Get the base county name (or use original if no mapping)
            base_county = IrishCounties.AGGREGATION_MAPPING.get(county, county)
            
            # Initialize aggregated record if not exists
            if base_county not in aggregated:
                aggregated[base_county] = record.copy()
                aggregated[base_county]['county'] = base_county
                aggregated[base_county]['population'] = 0
            
            # Add population to the aggregated record
            aggregated[base_county]['population'] += population
        
        return list(aggregated.values())
    
    def _extract_national_total_2016(self, data: dict, dataset_code: str) -> dict:
        """
        Extract 2016 Ireland national total from CSO census datasets
        Look for State/Ireland records with 2016 population data
        """
        try:
            dimensions = data.get('dimension', {})
            values = data.get('value', [])

            area_dim = None
            year_dim = None
            statistic_dim = None
            
            for dim_id, dim_data in dimensions.items():
                label = dim_data.get('label', '').lower()
                categories = list(dim_data.get('category', {}).get('label', {}).values())

                if any(cat in ['State', 'Ireland', 'National'] for cat in categories):
                    area_dim = dim_id
                elif any('2016' in str(cat) for cat in categories):
                    year_dim = dim_id
                elif 'statistic' in label:
                    statistic_dim = dim_id
            
            if not area_dim:
                return None

            import itertools
            dim_names = list(dimensions.keys())
            dim_values_lists = [list(dimensions[dim_id]['category']['label'].values()) for dim_id in dim_names]
            
            for idx, combination in enumerate(itertools.product(*dim_values_lists)):
                if idx < len(values) and values[idx] is not None:
                    dim_values = dict(zip(dim_names, combination))
                    
                    area = dim_values.get(area_dim, '')
                    year_val = dim_values.get(year_dim, '') if year_dim else ''
                    statistic = dim_values.get(statistic_dim, '') if statistic_dim else ''

                    is_ireland = area in ['State', 'Ireland', 'National']
                    is_2016 = '2016' in str(year_val) or '2016' in str(statistic)
                    is_population = 'population' in statistic.lower() or 'persons' in statistic.lower()
                    
                    if is_ireland and is_2016 and (is_population or not statistic_dim):
                        return {
                            'county': 'Ireland',
                            'year': 2016,
                            'census_year': 2016,
                            'population': values[idx],
                            'statistic': 'Population per County'
                        }
            
        except Exception as e:
            self.logger.debug(f"Error extracting 2016 national total from {dataset_code}: {str(e)}")
        
        return None
    
    def _get_fallback_generator(self) -> FallbackDataGenerator:
        """
        Lazy initialization of fallback data generator
        Only creates the generator when fallback data is actually needed
        """
        if self._fallback_generator is None:
            self.logger.info("Initializing fallback data generator")
            self._fallback_generator = FallbackDataGenerator()
        return self._fallback_generator

