"""
Configuration settings for the Ireland Environmental-Economic Analysis project
"""

import os
from typing import Dict, Any

# Database configuration
DATABASE_CONFIG = {
    'sqlite_path': 'data/ireland_analysis.db'
}

# Data sources configuration
DATA_SOURCES = {
    'pollution': {
        'dataset_id': 'EAA20',
        'description': 'Air emissions accounts'
    },
    'water_quality': {
        'dataset_id': 'EPA02',
        'description': 'Bathing water quality'
    },
    'population': {
        'census_2011': 'E2011',
        'census_2016': 'E2016',
        'census_2022': 'G0420',
        'description': 'Population census data'
    }
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'correlation_threshold': 0.5,
    'significance_level': 0.05
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    'output_dir': 'output',
    'figure_size': (12, 8),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'husl',
    'save_formats': ['png', 'html']
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': {
        'filename': 'logs/app.log',
        'max_bytes': 10485760,  # 10MB
        'backup_count': 5
    }
}

# Regional mapping
REGION_MAPPING = {
    'Clare': 'Munster',
    'Cork': 'Munster',
    'Donegal': 'Ulster',
    'Dublin': 'Leinster',
    'Fingal': 'Leinster',
    'Galway': 'Connacht',
    'Kerry': 'Munster',
    'Leitrim': 'Connacht',
    'Louth': 'Leinster',
    'Mayo': 'Connacht',
    'Meath': 'Leinster',
    'Sligo': 'Connacht',
    'Tipperary': 'Munster',
    'Waterford': 'Munster',
    'Westmeath': 'Leinster',
    'Wexford': 'Leinster',
    'Wicklow': 'Leinster'
}



def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section"""
    config_map = _build_config_map()
    return config_map.get(section, {})

def _build_config_map() -> Dict[str, Dict[str, Any]]:
    """Build mapping of configuration sections"""
    return {
        'database': DATABASE_CONFIG,
        'data_sources': DATA_SOURCES,
        'analysis': ANALYSIS_CONFIG,
        'logging': LOGGING_CONFIG,
        'regions': REGION_MAPPING
    }

def create_directories():
    """Create necessary directories for the project"""
    directories = [
        'data',
        'output',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)