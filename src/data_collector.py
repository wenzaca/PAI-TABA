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
            2016: 'E2016',
            2022: 'G0420'
        }
        
        for year, dataset_code in census_datasets.items():
            try:
                url = f"{self.base_urls['cso']}/{dataset_code}/JSON-stat/2.0/en"
                
                response = requests.get(url, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'dimension' in data and 'value' in data:
                        records = self._parse_cso_jsonstat(data, 'population')
                        
                        if records:
                            df = pd.DataFrame(records)
                            df = self._normalize_population_columns(df)
                            
                            df['year'] = year
                            df['census_year'] = year
                            
                            all_population_data.append(df)
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
            return self._get_fallback_generator().generate_population_data()
    
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
    
    def _get_fallback_generator(self) -> FallbackDataGenerator:
        """
        Lazy initialization of fallback data generator
        Only creates the generator when fallback data is actually needed
        """
        if self._fallback_generator is None:
            self.logger.info("Initializing fallback data generator")
            self._fallback_generator = FallbackDataGenerator()
        return self._fallback_generator

