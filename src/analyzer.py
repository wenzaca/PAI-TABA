"""
Environmental Analysis Module
Performs statistical analysis on pollution, water quality, and population data
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
from .constants import (
    PopulationColumns, IntegratedColumns, AnalysisConstants
)

class IrelandDataAnalyzer:
    """Analyzes patterns in pollution, water quality, and population data for Ireland"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
    def analyze_patterns(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Perform comprehensive analysis on all three datasets"""
        results = {
            'correlations': {},
            'statistics': {},
            'trends': {},
            'insights': {},
            'processed_data': processed_data
        }
        
        try:
            integrated_data = processed_data['integrated']
            
            results['correlations'] = self._analyze_correlations(integrated_data)
            results['statistics'] = self._perform_statistical_analysis(integrated_data)
            results['trends'] = self._analyze_trends(integrated_data)
            results['county_analysis'] = self._analyze_county_patterns(integrated_data)
            results['pollution_water_relationship'] = self._analyze_pollution_water_relationship(integrated_data)
            results['population_impact'] = self._analyze_population_impact(integrated_data)
            
            if 'pollution_vs_population' in processed_data:
                results['pollution_vs_population_analysis'] = self._analyze_pollution_vs_population(
                    processed_data['pollution_vs_population']
                )
            
            if 'pollution_vs_water' in processed_data:
                results['pollution_vs_water_analysis'] = self._analyze_pollution_vs_water(
                    processed_data['pollution_vs_water']
                )
            
            results['insights'] = self._generate_insights(results)
            return results
            
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            raise
    
    def _analyze_pollution_vs_population(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze pollution trends vs population growth across census years (2011, 2016, 2022)"""
        analysis = {}
        
        census_years = sorted(df['census_year'].unique())
        analysis['census_years'] = census_years
        
        pollution_by_year = df.groupby('year').agg({
            'total_emissions': 'first',
            'pollution_index': 'first',
            'total_national_population': 'first'
        }).reset_index()
        
        analysis['national_trends'] = pollution_by_year
        
        if len(pollution_by_year) > 1:
            first_year = pollution_by_year.iloc[0]
            last_year = pollution_by_year.iloc[-1]
            
            pollution_change = ((last_year['total_emissions'] - first_year['total_emissions']) / 
                              first_year['total_emissions'] * 100)
            population_change = ((last_year['total_national_population'] - first_year['total_national_population']) / 
                               first_year['total_national_population'] * 100)
            
            analysis['overall_changes'] = {
                'pollution_change_pct': pollution_change,
                'population_change_pct': population_change,
                'years_span': f"{int(first_year['year'])}-{int(last_year['year'])}"
            }
        
        if 'estimated_county_emissions' in df.columns and 'population' in df.columns:
            county_census_counts = df.groupby('county')['census_year'].nunique()
            counties_with_multiple = county_census_counts[county_census_counts > 1].index
            
            if len(counties_with_multiple) > 0:
                county_changes = []
                
                for county in counties_with_multiple:
                    county_data = df[df['county'] == county].sort_values('year')
                    if len(county_data) >= 2:
                        first = county_data.iloc[0]
                        last = county_data.iloc[-1]
                        
                        pop_change = ((last['population'] - first['population']) / first['population'] * 100)
                        emissions_change = ((last['estimated_county_emissions'] - first['estimated_county_emissions']) / 
                                          first['estimated_county_emissions'] * 100)
                        
                        county_changes.append({
                            'county': county,
                            'population_change_pct': pop_change,
                            'emissions_change_pct': emissions_change,
                            'population_2011': first['population'] if first['year'] == 2011 else None,
                            'population_2022': last['population'] if last['year'] == 2022 else None
                        })
                
                analysis['county_changes'] = pd.DataFrame(county_changes)
        
        if 'population' in df.columns and 'estimated_county_emissions' in df.columns:
            clean_df = df[['population', 'estimated_county_emissions']].dropna()
            if len(clean_df) > 3:
                corr, p_value = pearsonr(clean_df['population'], clean_df['estimated_county_emissions'])
                analysis['population_emissions_correlation'] = {
                    'coefficient': corr,
                    'p_value': p_value,
                    'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL
                }
        
        if 'county_changes' in analysis and len(analysis['county_changes']) > 0:
            top_growth = analysis['county_changes'].nlargest(5, 'population_change_pct')
            analysis['top_growing_counties'] = top_growth[['county', 'population_change_pct']].to_dict('records')
        
        return analysis
    
    def _analyze_pollution_vs_water(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze pollution vs water quality relationships"""
        analysis = {}
        
        # Years covered
        years = sorted(df['year'].unique())
        analysis['years_covered'] = years
        
        annual_summary = df.groupby('year').agg({
            'pollution_index': 'first',
            'total_emissions': 'first',
            'avg_quality_score': 'mean',
            'percent_good_or_better': 'mean'
        }).reset_index()
        
        analysis['annual_summary'] = annual_summary
        
        if 'pollution_index' in df.columns and 'avg_quality_score' in df.columns:
            clean_df = df[['pollution_index', 'avg_quality_score']].dropna()
            if len(clean_df) > 3:
                corr, p_value = pearsonr(clean_df['pollution_index'], clean_df['avg_quality_score'])
                analysis['pollution_water_correlation'] = {
                    'coefficient': corr,
                    'p_value': p_value,
                    'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL,
                    'interpretation': 'negative' if corr < -0.3 else 'positive' if corr > 0.3 else 'weak'
                }
        
        county_water_quality = df.groupby('county')['avg_quality_score'].mean().sort_values(ascending=False)
        analysis['county_water_rankings'] = county_water_quality.head(10).to_dict()
        
        if len(annual_summary) > 2:
            years_arr = annual_summary['year'].values
            pollution_arr = annual_summary['pollution_index'].values
            
            mask = ~np.isnan(pollution_arr)
            if mask.sum() >= 2:
                slope_p, _, r_p, p_val_p, _ = stats.linregress(years_arr[mask], pollution_arr[mask])
                analysis['pollution_trend'] = {
                    'slope': slope_p,
                    'r_squared': r_p**2,
                    'p_value': p_val_p,
                    'direction': 'increasing' if slope_p > 0 else 'decreasing'
                }
            
            water_arr = annual_summary['avg_quality_score'].values
            mask = ~np.isnan(water_arr)
            if mask.sum() >= 2:
                slope_w, _, r_w, p_val_w, _ = stats.linregress(years_arr[mask], water_arr[mask])
                analysis['water_quality_trend'] = {
                    'slope': slope_w,
                    'r_squared': r_w**2,
                    'p_value': p_val_w,
                    'direction': 'improving' if slope_w > 0 else 'declining'
                }
        
        if len(county_water_quality) > 0:
            analysis['best_water_county'] = county_water_quality.idxmax()
            analysis['worst_water_county'] = county_water_quality.idxmin()
        
        return analysis
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze correlations between pollution, water quality, and population variables"""
        correlations = {}
        
        # Calculate estimated county emissions if possible
        df_with_estimates = self._add_estimated_county_emissions(df)
        
        # Add national growth rates
        df_with_growth = self._add_national_growth_rates(df_with_estimates)
        
        key_columns = [
            IntegratedColumns.POLLUTION_INDEX,
            IntegratedColumns.TOTAL_EMISSIONS,
            IntegratedColumns.AVG_QUALITY_SCORE,
            IntegratedColumns.PERCENT_GOOD_OR_BETTER,
            IntegratedColumns.POPULATION,
            IntegratedColumns.POPULATION_DENSITY,
            IntegratedColumns.POPULATION_GROWTH,
            IntegratedColumns.EMISSIONS_PER_CAPITA
        ]
        
        # Add estimated county emissions if available
        if 'estimated_county_emissions' in df_with_growth.columns:
            key_columns.append('estimated_county_emissions')
        
        # Add national growth rates if available
        if 'national_population_total_growth' in df_with_growth.columns:
            key_columns.append('national_population_total_growth')
        if 'national_emission_total_growth' in df_with_growth.columns:
            key_columns.append('national_emission_total_growth')
        
        available_columns = [col for col in key_columns if col in df_with_growth.columns]
        
        if len(available_columns) >= 2:
            corr_matrix = df_with_growth[available_columns].corr()
            correlations['overall'] = corr_matrix
            
            pollution_cols = [col for col in available_columns if 'pollution' in col.lower() or 'emission' in col.lower()]
            water_cols = [col for col in available_columns if 'quality' in col.lower() or 'percent' in col.lower()]
            
            # Pollution-water correlation with estimated emissions
            if pollution_cols and water_cols:
                pw_cols = [col for col in pollution_cols + water_cols if col in df_with_growth.columns]
                if pw_cols:
                    pollution_water_corr = df_with_growth[pw_cols].corr()
                    correlations['pollution_water'] = pollution_water_corr
            
            pop_cols = [col for col in available_columns if 'population' in col.lower()]
            env_cols = pollution_cols + water_cols
            
            if pop_cols and env_cols:
                pe_cols = [col for col in pop_cols + env_cols if col in df_with_growth.columns]
                if pe_cols:
                    pop_env_corr = df_with_growth[pe_cols].corr()
                    correlations['population_environment'] = pop_env_corr
        
        return correlations
    
    def _add_estimated_county_emissions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate estimated county emissions based on population proportion"""
        df_copy = df.copy()
        
        # Check if we have the necessary columns
        if ('population' in df_copy.columns and 
            'total_national_population' in df_copy.columns and 
            'total_emissions' in df_copy.columns):
            
            df_copy['estimated_county_emissions'] = (
                df_copy['total_emissions'] * 
                (df_copy['population'] / df_copy['total_national_population'])
            )
            self.logger.info("Calculated estimated county emissions based on population proportion")
        
        return df_copy
    
    def _add_national_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add national population and emission total period growth rates (2011-2022)"""
        df_copy = df.copy()
        
        if 'total_national_population' in df_copy.columns and 'total_emissions' in df_copy.columns:
            # Calculate national data by year
            national_data = df_copy.groupby('year').agg({
                'total_national_population': 'first',
                'total_emissions': 'first'
            }).reset_index().sort_values('year')
            
            if len(national_data) >= 2:
                # Get baseline (first year) and final year values
                baseline_year = national_data.iloc[0]
                final_year = national_data.iloc[-1]
                
                # Calculate total period growth rates (2011-2022)
                pop_total_growth = ((final_year['total_national_population'] - baseline_year['total_national_population']) / 
                                   baseline_year['total_national_population'] * 100)
                emission_total_growth = ((final_year['total_emissions'] - baseline_year['total_emissions']) / 
                                        baseline_year['total_emissions'] * 100)
                
                # Add these as constant values to all rows
                df_copy['national_population_total_growth'] = pop_total_growth
                df_copy['national_emission_total_growth'] = emission_total_growth
                
                self.logger.info(f"Added total period growth rates: Population {pop_total_growth:.1f}%, Emissions {emission_total_growth:.1f}%")
        
        return df_copy
    
    def _perform_statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical tests and analysis"""
        statistics = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        statistics['descriptive'] = df[numeric_cols].describe()
        
        if IntegratedColumns.COUNTY in df.columns:
            county_anova = {}
            key_vars = [
                IntegratedColumns.POLLUTION_INDEX,
                IntegratedColumns.AVG_QUALITY_SCORE,
                IntegratedColumns.POPULATION_DENSITY
            ]
            
            for var in key_vars:
                if var in df.columns:
                    groups = [group[var].dropna() for name, group in df.groupby(IntegratedColumns.COUNTY)]
                    if len(groups) > 1 and all(len(group) > 0 for group in groups):
                        f_stat, p_value = stats.f_oneway(*groups)
                        county_anova[var] = {
                            'f_statistic': f_stat,
                            'p_value': p_value,
                            'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL
                        }
            
            statistics['county_anova'] = county_anova
        
        if IntegratedColumns.YEAR in df.columns:
            trend_tests = {}
            key_vars = [
                IntegratedColumns.POLLUTION_INDEX,
                IntegratedColumns.AVG_QUALITY_SCORE,
                IntegratedColumns.POPULATION,
                IntegratedColumns.EMISSIONS_PER_CAPITA
            ]
            
            for var in key_vars:
                if var in df.columns:
                    annual_means = df.groupby(IntegratedColumns.YEAR)[var].mean().dropna()
                    if len(annual_means) > 2:
                        tau, p_value = stats.kendalltau(annual_means.index, annual_means.values)
                        trend_tests[var] = {
                            'tau': tau,
                            'p_value': p_value,
                            'has_trend': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL,
                            'direction': 'increasing' if tau > 0 else 'decreasing'
                        }
            
            statistics['trend_tests'] = trend_tests
        
        return statistics
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal trends in the data"""
        trends = {}
        
        if IntegratedColumns.YEAR not in df.columns:
            trends['warning'] = "No year column found for trend analysis"
            return trends
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != IntegratedColumns.YEAR]
        
        annual_trends = df.groupby(IntegratedColumns.YEAR)[numeric_cols].agg(['mean', 'std', 'count'])
        annual_means = annual_trends.xs('mean', level=1, axis=1)
        annual_stds = annual_trends.xs('std', level=1, axis=1)
        
        trends['annual_means'] = annual_means
        trends['annual_stds'] = annual_stds
        
        yoy_changes = annual_means.pct_change(fill_method=None) * 100
        trends['year_over_year_changes'] = yoy_changes
        
        trend_strength = {}
        significant_trends = []
        
        for col in annual_means.columns:
            if len(annual_means[col].dropna()) > 2:
                years = annual_means.index.values
                values = annual_means[col].values
                
                mask = ~np.isnan(values)
                if mask.sum() < 3:
                    continue
                
                years_clean = years[mask]
                values_clean = values[mask]
                
                if np.std(values_clean) < 0.01:
                    trend_strength[col] = {
                        'slope': 0,
                        'r_squared': 0,
                        'p_value': 1.0,
                        'significant': False,
                        'note': 'Insufficient variation'
                    }
                    continue
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(years_clean, values_clean)
                
                trend_strength[col] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL,
                    'direction': 'increasing' if slope > 0 else 'decreasing',
                    'strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                }
                
                if p_value < AnalysisConstants.SIGNIFICANCE_LEVEL and abs(slope) > 0.01:
                    direction = "increasing" if slope > 0 else "decreasing"
                    significant_trends.append(f"{col}: {direction} trend (R²={r_value**2:.3f})")
        
        trends['trend_strength'] = trend_strength
        trends['significant_trends_summary'] = significant_trends
        
        if IntegratedColumns.COUNTY in df.columns:
            county_trends = {}
            for county in df[IntegratedColumns.COUNTY].unique():
                county_data = df[df[IntegratedColumns.COUNTY] == county]
                if len(county_data) > 2:
                    county_annual = county_data.groupby(IntegratedColumns.YEAR)[numeric_cols].mean()
                    county_trends[county] = county_annual
            
            trends['county_trends'] = county_trends
        
        return trends
    
    def _analyze_county_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns by county"""
        county_analysis = {}
        
        if IntegratedColumns.COUNTY not in df.columns:
            return county_analysis
        
        county_means = df.groupby(IntegratedColumns.COUNTY).agg({
            col: 'mean' for col in df.select_dtypes(include=[np.number]).columns
        })
        county_analysis['means'] = county_means
        
        rankings = {}
        key_metrics = [
            IntegratedColumns.POLLUTION_INDEX,
            IntegratedColumns.AVG_QUALITY_SCORE,
            IntegratedColumns.POPULATION_DENSITY,
            IntegratedColumns.EMISSIONS_PER_CAPITA
        ]
        
        for metric in key_metrics:
            if metric in county_means.columns:
                # For pollution/emissions, lower is better (rank ascending)
                # For water quality, higher is better (rank descending)
                ascending = 'pollution' in metric.lower() or 'emission' in metric.lower()
                rankings[metric] = county_means[metric].rank(ascending=ascending).to_dict()
        
        county_analysis['rankings'] = rankings
        
        if IntegratedColumns.POLLUTION_INDEX in county_means.columns:
            county_analysis['lowest_pollution'] = county_means[IntegratedColumns.POLLUTION_INDEX].idxmin()
            county_analysis['highest_pollution'] = county_means[IntegratedColumns.POLLUTION_INDEX].idxmax()
        
        if IntegratedColumns.AVG_QUALITY_SCORE in county_means.columns:
            county_analysis['best_water_quality'] = county_means[IntegratedColumns.AVG_QUALITY_SCORE].idxmax()
            county_analysis['worst_water_quality'] = county_means[IntegratedColumns.AVG_QUALITY_SCORE].idxmin()
        
        return county_analysis
    
    def _analyze_pollution_water_relationship(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the relationship between pollution and water quality"""
        relationship = {}
        
        if IntegratedColumns.POLLUTION_INDEX not in df.columns or IntegratedColumns.AVG_QUALITY_SCORE not in df.columns:
            return relationship
        
        clean_df = df[[IntegratedColumns.POLLUTION_INDEX, IntegratedColumns.AVG_QUALITY_SCORE]].dropna()
        
        if len(clean_df) > 3:
            corr, p_value = pearsonr(clean_df[IntegratedColumns.POLLUTION_INDEX], 
                                     clean_df[IntegratedColumns.AVG_QUALITY_SCORE])
            
            relationship['correlation'] = {
                'coefficient': corr,
                'p_value': p_value,
                'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL,
                'interpretation': 'negative' if corr < -0.3 else 'positive' if corr > 0.3 else 'weak'
            }
            
            pollution_median = clean_df[IntegratedColumns.POLLUTION_INDEX].median()
            water_median = clean_df[IntegratedColumns.AVG_QUALITY_SCORE].median()
            
            categories = []
            for _, row in clean_df.iterrows():
                if row[IntegratedColumns.POLLUTION_INDEX] < pollution_median and row[IntegratedColumns.AVG_QUALITY_SCORE] >= water_median:
                    categories.append('Low Pollution - Good Water')
                elif row[IntegratedColumns.POLLUTION_INDEX] < pollution_median and row[IntegratedColumns.AVG_QUALITY_SCORE] < water_median:
                    categories.append('Low Pollution - Poor Water')
                elif row[IntegratedColumns.POLLUTION_INDEX] >= pollution_median and row[IntegratedColumns.AVG_QUALITY_SCORE] >= water_median:
                    categories.append('High Pollution - Good Water')
                else:
                    categories.append('High Pollution - Poor Water')
            
            category_dist = pd.Series(categories).value_counts()
            relationship['category_distribution'] = category_dist.to_dict()
        
        return relationship
    
    def _analyze_population_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how population growth relates to environmental indicators"""
        impact = {}
        
        if IntegratedColumns.POPULATION_DENSITY in df.columns and IntegratedColumns.POLLUTION_INDEX in df.columns:
            clean_df = df[[IntegratedColumns.POPULATION_DENSITY, IntegratedColumns.POLLUTION_INDEX]].dropna()
            if len(clean_df) > 3:
                corr, p_value = pearsonr(clean_df[IntegratedColumns.POPULATION_DENSITY], 
                                        clean_df[IntegratedColumns.POLLUTION_INDEX])
                impact['density_pollution_correlation'] = {
                    'coefficient': corr,
                    'p_value': p_value,
                    'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL
                }
        
        if IntegratedColumns.POPULATION_GROWTH in df.columns and IntegratedColumns.EMISSIONS_PER_CAPITA in df.columns:
            clean_df = df[[IntegratedColumns.POPULATION_GROWTH, IntegratedColumns.EMISSIONS_PER_CAPITA]].dropna()
            if len(clean_df) > 3:
                corr, p_value = pearsonr(clean_df[IntegratedColumns.POPULATION_GROWTH], 
                                        clean_df[IntegratedColumns.EMISSIONS_PER_CAPITA])
                impact['growth_emissions_correlation'] = {
                    'coefficient': corr,
                    'p_value': p_value,
                    'significant': p_value < AnalysisConstants.SIGNIFICANCE_LEVEL
                }
        
        if PopulationColumns.POPULATION_GROWTH_TOTAL in df.columns:
            high_growth_threshold = df[PopulationColumns.POPULATION_GROWTH_TOTAL].quantile(0.75)
            high_growth_counties = df[df[PopulationColumns.POPULATION_GROWTH_TOTAL] >= high_growth_threshold]
            
            if len(high_growth_counties) > 0:
                impact['high_growth_counties'] = {
                    'count': len(high_growth_counties[IntegratedColumns.COUNTY].unique()),
                    'avg_pollution': high_growth_counties[IntegratedColumns.POLLUTION_INDEX].mean() if IntegratedColumns.POLLUTION_INDEX in high_growth_counties.columns else None,
                    'avg_water_quality': high_growth_counties[IntegratedColumns.AVG_QUALITY_SCORE].mean() if IntegratedColumns.AVG_QUALITY_SCORE in high_growth_counties.columns else None
                }
        
        return impact
    
    def _generate_insights(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate key insights from the analysis"""
        insights = {}
        
        if 'correlations' in results and 'pollution_water' in results['correlations']:
            corr_matrix = results['correlations']['pollution_water']
            if not corr_matrix.empty:
                # Find strongest negative correlation (expected: pollution ↑ water quality ↓)
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > AnalysisConstants.CORRELATION_THRESHOLD:
                            var1, var2 = corr_matrix.columns[i], corr_matrix.columns[j]
                            relationship = "negative" if corr_val < 0 else "positive"
                            insights['pollution_water_correlation'] = f"Strong {relationship} correlation ({corr_val:.3f}) between {var1} and {var2}"
                            break
        
        if 'trends' in results and 'significant_trends_summary' in results['trends']:
            significant_trends = results['trends']['significant_trends_summary']
            if significant_trends:
                insights['significant_trends'] = f"Found {len(significant_trends)} significant trends: " + "; ".join(significant_trends[:2])
        
        if 'county_analysis' in results:
            county_data = results['county_analysis']
            if 'best_water_quality' in county_data:
                insights['best_county_water'] = f"{county_data['best_water_quality']} has the best water quality"
            if 'lowest_pollution' in county_data:
                insights['cleanest_county'] = f"{county_data['lowest_pollution']} has the lowest pollution levels"
        
        if 'population_impact' in results:
            pop_impact = results['population_impact']
            if 'density_pollution_correlation' in pop_impact:
                corr_data = pop_impact['density_pollution_correlation']
                if corr_data['significant']:
                    insights['population_density_impact'] = f"Population density shows significant correlation ({corr_data['coefficient']:.3f}) with pollution levels"
        
        return insights

