"""
Database Management Module
"""

import sqlite3
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any
import os

class DatabaseManager:
    
    def __init__(self, db_path: str = "data/ireland_analysis.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.logger.info(f"Database initialized at {db_path}")
        
    def store_datasets(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Store all collected datasets in the database"""
        try:
            for dataset_name, df in datasets.items():
                self._store_dataframe(df, dataset_name)
                self.logger.info(f"Stored {len(df)} records for {dataset_name}")
                
        except Exception as e:
            self.logger.error(f"Error storing datasets: {str(e)}")
            raise
    
    def _store_dataframe(self, df: pd.DataFrame, table_name: str) -> None:
        """Store a pandas DataFrame in the database"""
        try:
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            self.logger.debug(f"Stored DataFrame in table: {table_name}")
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error storing {table_name}: {str(e)}")
            raise
    
    def load_dataset(self, table_name: str) -> pd.DataFrame:
        """Load a dataset from the database"""
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, self.engine)
            self.logger.debug(f"Loaded {len(df)} records from {table_name}")
            return df
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error loading {table_name}: {str(e)}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = [row[1] for row in result.fetchall()]
                
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.fetchone()[0]
                
                return {
                    'columns': columns,
                    'row_count': row_count,
                    'table_name': table_name
                }
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting table info for {table_name}: {str(e)}")
            raise
    
    def list_tables(self) -> list:
        """List all tables in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                return tables
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a custom SQL query and return results as DataFrame"""
        try:
            df = pd.read_sql(query, self.engine)
            self.logger.debug(f"Query executed, returned {len(df)} rows")
            return df
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise
    
    def store_analysis_results(self, results: Dict[str, Any]) -> None:
        """Store analysis results in the database"""
        try:
            if 'correlations' in results:
                for analysis_type, corr_data in results['correlations'].items():
                    if isinstance(corr_data, pd.DataFrame):
                        table_name = f"analysis_correlation_{analysis_type}"
                        self._store_dataframe(corr_data, table_name)
            
            if 'statistics' in results:
                for stat_type, stat_data in results['statistics'].items():
                    if isinstance(stat_data, pd.DataFrame):
                        table_name = f"analysis_stats_{stat_type}"
                        self._store_dataframe(stat_data, table_name)
            
            if 'processed_data' in results:
                for dataset_name, df in results['processed_data'].items():
                    if isinstance(df, pd.DataFrame):
                        table_name = f"processed_{dataset_name}"
                        self._store_dataframe(df, table_name)
            
            self.logger.info("Analysis results stored")
            
        except Exception as e:
            self.logger.error(f"Error storing analysis results: {str(e)}")
            raise
    
    def create_indexes(self) -> None:
        """Create database indexes"""
        try:
            with self.engine.connect() as conn:
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_pollution_county ON raw_pollution(county)",
                    "CREATE INDEX IF NOT EXISTS idx_pollution_year ON raw_pollution(year)",
                    "CREATE INDEX IF NOT EXISTS idx_water_county ON raw_water_quality(county)",
                    "CREATE INDEX IF NOT EXISTS idx_water_year ON raw_water_quality(year)",
                    "CREATE INDEX IF NOT EXISTS idx_population_county ON raw_population(county)",
                    "CREATE INDEX IF NOT EXISTS idx_population_year ON raw_population(year)"
                ]
                
                for index_sql in indexes:
                    conn.execute(text(index_sql))
                    
                conn.commit()
                self.logger.info("Database indexes created")
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close database connection"""
        try:
            self.engine.dispose()
            self.logger.info("Database connection closed")
            
        except Exception as e:
            self.logger.error(f"Error closing database: {str(e)}")
            raise