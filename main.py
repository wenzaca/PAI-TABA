#!/usr/bin/env python3
"""
Ireland Environmental-Population Resilience Analysis

Course: Programming for AI - TABA
"""

import logging
from src.data_collector import DataCollector
from src.database_manager import DatabaseManager
from src.data_processor import DataProcessor
from src.analyzer import IrelandDataAnalyzer
from src.dashboard_visualizer import DashboardVisualizer
from config import get_config, create_directories

def setup_logging():
    """Configure logging for the application"""
    create_directories()
    log_config = get_config('logging')
    
    handlers = _create_log_handlers(log_config)
    _configure_logging(log_config, handlers)

def _create_log_handlers(log_config: dict) -> list:
    """Create logging handlers for file and console output"""
    return [
        logging.FileHandler(log_config['file_handler']['filename']),
        logging.StreamHandler()
    ]

def _configure_logging(log_config: dict, handlers: list) -> None:
    """Configure basic logging with specified handlers"""
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=handlers
    )

def main():
    """Main application workflow"""
    logger = logging.getLogger(__name__)
    logger.info("Starting analysis")
    
    try:
        db_manager = DatabaseManager()
        data_collector = DataCollector()
        processor = DataProcessor()
        analyzer = IrelandDataAnalyzer()
        dashboard = DashboardVisualizer()
        
        datasets = data_collector.collect_all_datasets()
        db_manager.store_datasets(datasets)
        
        processed_data = processor.process_all_data(db_manager)
        analysis_results = analyzer.analyze_patterns(processed_data)
        
        dashboard.create(analysis_results)
        db_manager.store_analysis_results(analysis_results)
        
        logger.info("Analysis complete")
        db_manager.close()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    setup_logging()
    main()