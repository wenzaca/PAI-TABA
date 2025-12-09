#!/usr/bin/env python3
"""
Ireland Environmental-Population Resilience Analysis

Course: Programming for AI - TABA
"""

import os
import logging
from src.data_collector import DataCollector
from src.database_manager import DatabaseManager
from src.data_processor import DataProcessor
from src.analyzer import IrelandDataAnalyzer
from src.dashboard_visualizer import DashboardVisualizer

def setup_logging():
    """Configure logging for the application"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
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