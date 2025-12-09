"""
Data classes for modeling analysis results structure
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List
import pandas as pd


@dataclass
class ProcessedData:
    """Container for processed dataframes"""
    integrated: pd.DataFrame
    pollution: pd.DataFrame
    pollution_vs_population: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    def to_dict(self) -> Dict[str, pd.DataFrame]:
        """Convert to dictionary format expected by dashboard"""
        return {
            'integrated': self.integrated,
            'pollution': self.pollution,
            'pollution_vs_population': self.pollution_vs_population
        }


@dataclass
class CorrelationData:
    """Container for correlation matrices"""
    overall: pd.DataFrame = field(default_factory=pd.DataFrame)
    pollution_water: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    def to_dict(self) -> Dict[str, pd.DataFrame]:
        """Convert to dictionary format expected by dashboard"""
        return {
            'overall': self.overall,
            'pollution_water': self.pollution_water
        }


@dataclass
class TrendData:
    """Container for trend analysis results"""
    direction: str = ''
    r_squared: float = 0.0
    slope: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'direction': self.direction,
            'r_squared': self.r_squared,
            'slope': self.slope
        }


@dataclass
class CorrelationResult:
    """Container for correlation coefficient results"""
    coefficient: float = 0.0
    p_value: float = 1.0
    significant: bool = False
    interpretation: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'coefficient': self.coefficient,
            'p_value': self.p_value,
            'significant': self.significant,
            'interpretation': self.interpretation
        }


@dataclass
class CountyGrowth:
    """Container for county growth data"""
    county: str
    population_change_pct: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'county': self.county,
            'population_change_pct': self.population_change_pct
        }


@dataclass
class OverallChanges:
    """Container for overall temporal changes"""
    years_span: str = ''
    pollution_change_pct: float = 0.0
    population_change_pct: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'years_span': self.years_span,
            'pollution_change_pct': self.pollution_change_pct,
            'population_change_pct': self.population_change_pct
        }


@dataclass
class PollutionVsPopulationAnalysis:
    """Container for pollution vs population analysis results"""
    census_years: List[int] = field(default_factory=list)
    overall_changes: OverallChanges = field(default_factory=OverallChanges)
    population_emissions_correlation: CorrelationResult = field(default_factory=CorrelationResult)
    top_growing_counties: List[CountyGrowth] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by dashboard"""
        return {
            'census_years': self.census_years,
            'overall_changes': self.overall_changes.to_dict(),
            'population_emissions_correlation': self.population_emissions_correlation.to_dict(),
            'top_growing_counties': [c.to_dict() for c in self.top_growing_counties]
        }


@dataclass
class PollutionVsWaterAnalysis:
    """Container for pollution vs water quality analysis results"""
    years_covered: List[int] = field(default_factory=list)
    pollution_water_correlation: CorrelationResult = field(default_factory=CorrelationResult)
    pollution_trend: TrendData = field(default_factory=TrendData)
    water_quality_trend: TrendData = field(default_factory=TrendData)
    best_water_county: str = ''
    worst_water_county: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by dashboard"""
        return {
            'years_covered': self.years_covered,
            'pollution_water_correlation': self.pollution_water_correlation.to_dict(),
            'pollution_trend': self.pollution_trend.to_dict(),
            'water_quality_trend': self.water_quality_trend.to_dict(),
            'best_water_county': self.best_water_county,
            'worst_water_county': self.worst_water_county
        }


@dataclass
class CountyAnalysis:
    """Container for county-level analysis results"""
    # Add specific county analysis fields as needed
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return self.data


@dataclass
class AnalysisResults:
    """
    Main container for all analysis results passed to DashboardVisualizer.create()
    
    This dataclass models the dictionary structure expected by the dashboard visualizer,
    providing type safety and better IDE support.
    """
    processed_data: ProcessedData
    correlations: CorrelationData = field(default_factory=CorrelationData)
    trends: Dict[str, Any] = field(default_factory=dict)
    county_analysis: CountyAnalysis = field(default_factory=CountyAnalysis)
    pollution_vs_population_analysis: PollutionVsPopulationAnalysis = field(default_factory=PollutionVsPopulationAnalysis)
    pollution_vs_water_analysis: PollutionVsWaterAnalysis = field(default_factory=PollutionVsWaterAnalysis)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format expected by DashboardVisualizer.create()
        
        Returns:
            Dictionary with all analysis results in the expected structure
        """
        return {
            'processed_data': self.processed_data.to_dict(),
            'correlations': self.correlations.to_dict(),
            'trends': self.trends,
            'county_analysis': self.county_analysis.to_dict(),
            'pollution_vs_population_analysis': self.pollution_vs_population_analysis.to_dict(),
            'pollution_vs_water_analysis': self.pollution_vs_water_analysis.to_dict()
        }
