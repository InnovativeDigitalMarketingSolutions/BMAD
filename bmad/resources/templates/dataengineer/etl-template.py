#!/usr/bin/env python3
"""
ETL Pipeline Template
This template provides a comprehensive ETL pipeline structure.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ETLPipeline(ABC):
    """Abstract base class for ETL pipelines."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        self.metrics = {}
        self.errors = []
        
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data from source."""
        pass
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the extracted data."""
        pass
    
    @abstractmethod
    def load(self, data: pd.DataFrame) -> bool:
        """Load the transformed data to target."""
        pass
    
    def run(self) -> Dict[str, Any]:
        """Run the complete ETL pipeline."""
        logger.info(f"Starting ETL pipeline: {self.name}")
        self.start_time = datetime.now()
        self.status = "running"
        
        try:
            # Extract
            logger.info("Starting extraction phase")
            data = self.extract()
            logger.info(f"Extraction completed: {len(data)} records")
            
            # Transform
            logger.info("Starting transformation phase")
            transformed_data = self.transform(data)
            logger.info(f"Transformation completed: {len(transformed_data)} records")
            
            # Load
            logger.info("Starting loading phase")
            load_success = self.load(transformed_data)
            logger.info("Loading completed")
            
            self.end_time = datetime.now()
            self.status = "completed" if load_success else "failed"
            
            # Calculate metrics
            execution_time = (self.end_time - self.start_time).total_seconds()
            self.metrics = {
                "execution_time": execution_time,
                "records_processed": len(transformed_data),
                "status": self.status,
                "errors": len(self.errors)
            }
            
            logger.info(f"ETL pipeline {self.name} completed successfully in {execution_time:.2f} seconds")
            return self.metrics
            
        except Exception as e:
            self.status = "failed"
            self.end_time = datetime.now()
            self.errors.append(str(e))
            logger.error(f"ETL pipeline {self.name} failed: {str(e)}")
            raise

class DatabaseETL(ETLPipeline):
    """Database-based ETL pipeline."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.source_connection = config.get("source_connection")
        self.target_connection = config.get("target_connection")
        self.extract_query = config.get("extract_query")
        self.target_table = config.get("target_table")
    
    def extract(self) -> pd.DataFrame:
        """Extract data from database."""
        logger.info(f"Extracting data using query: {self.extract_query}")
        # Implement database extraction logic
        # This is a placeholder - replace with actual database connection
        return pd.DataFrame({
            'id': range(100),
            'name': [f'Record {i}' for i in range(100)],
            'value': np.random.randn(100),
            'timestamp': [datetime.now() - timedelta(hours=i) for i in range(100)]
        })
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the extracted data."""
        logger.info("Transforming database data")
        
        # Data cleaning
        data = data.dropna()
        data = data.drop_duplicates()
        
        # Data validation
        data = data[data['value'].notna()]
        data = data[data['name'].str.len() > 0]
        
        # Data enrichment
        data['processed_at'] = datetime.now()
        data['pipeline_name'] = self.name
        
        return data
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to database."""
        logger.info(f"Loading {len(data)} records to table: {self.target_table}")
        # Implement database loading logic
        # This is a placeholder - replace with actual database connection
        return True

class APIETL(ETLPipeline):
    """API-based ETL pipeline."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.target_table = config.get("target_table")
    
    def extract(self) -> pd.DataFrame:
        """Extract data from API."""
        logger.info(f"Extracting data from API: {self.api_url}")
        # Implement API extraction logic
        # This is a placeholder - replace with actual API call
        return pd.DataFrame({
            'id': range(50),
            'api_data': [f'API Record {i}' for i in range(50)],
            'api_value': np.random.randn(50),
            'api_timestamp': [datetime.now() - timedelta(minutes=i) for i in range(50)]
        })
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the extracted API data."""
        logger.info("Transforming API data")
        
        # Data cleaning
        data = data.dropna()
        data = data.drop_duplicates()
        
        # Data validation
        data = data[data['api_value'].notna()]
        
        # Data enrichment
        data['processed_at'] = datetime.now()
        data['pipeline_name'] = self.name
        data['source'] = 'api'
        
        return data
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load API data to target."""
        logger.info(f"Loading {len(data)} API records to table: {self.target_table}")
        # Implement loading logic
        return True

class FileETL(ETLPipeline):
    """File-based ETL pipeline."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.source_file = config.get("source_file")
        self.target_file = config.get("target_file")
        self.file_type = config.get("file_type", "csv")
    
    def extract(self) -> pd.DataFrame:
        """Extract data from file."""
        logger.info(f"Extracting data from file: {self.source_file}")
        
        if self.file_type == "csv":
            return pd.read_csv(self.source_file)
        elif self.file_type == "excel":
            return pd.read_excel(self.source_file)
        elif self.file_type == "json":
            return pd.read_json(self.source_file)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the extracted file data."""
        logger.info("Transforming file data")
        
        # Data cleaning
        data = data.dropna()
        data = data.drop_duplicates()
        
        # Data validation
        # Add validation logic based on business rules
        
        # Data enrichment
        data['processed_at'] = datetime.now()
        data['pipeline_name'] = self.name
        data['source'] = 'file'
        
        return data
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load file data to target."""
        logger.info(f"Loading {len(data)} file records to: {self.target_file}")
        
        if self.file_type == "csv":
            data.to_csv(self.target_file, index=False)
        elif self.file_type == "excel":
            data.to_excel(self.target_file, index=False)
        elif self.file_type == "json":
            data.to_json(self.target_file, orient='records')
        
        return True

class DataValidator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_schema(data: pd.DataFrame, expected_schema: Dict[str, str]) -> bool:
        """Validate data schema."""
        logger.info("Validating data schema")
        
        for column, expected_type in expected_schema.items():
            if column not in data.columns:
                logger.error(f"Missing column: {column}")
                return False
            
            # Add type validation logic here
            logger.info(f"Column {column} validated")
        
        return True
    
    @staticmethod
    def validate_business_rules(data: pd.DataFrame, rules: List[Dict[str, Any]]) -> List[str]:
        """Validate business rules."""
        logger.info("Validating business rules")
        violations = []
        
        for rule in rules:
            rule_type = rule.get("type")
            column = rule.get("column")
            rule.get("condition")
            
            if rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                violations.extend(
                    data[~data[column].between(min_val, max_val)][column].tolist()
                )
            elif rule_type == "unique":
                duplicates = data[data.duplicated(subset=[column], keep=False)]
                if not duplicates.empty:
                    violations.extend(duplicates[column].tolist())
            elif rule_type == "not_null":
                null_values = data[data[column].isna()]
                if not null_values.empty:
                    violations.extend(null_values[column].tolist())
        
        return violations

class DataTransformer:
    """Data transformation utilities."""
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """Clean the data."""
        logger.info("Cleaning data")
        
        # Remove duplicates
        data = data.drop_duplicates()
        
        # Handle missing values
        data = data.fillna(method='ffill')
        
        # Remove outliers (example: remove values beyond 3 standard deviations)
        for column in data.select_dtypes(include=[np.number]).columns:
            mean = data[column].mean()
            std = data[column].std()
            data = data[abs(data[column] - mean) <= 3 * std]
        
        return data
    
    @staticmethod
    def normalize_data(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize numerical data."""
        logger.info("Normalizing data")
        
        for column in columns:
            if column in data.columns and data[column].dtype in ['int64', 'float64']:
                data[column] = (data[column] - data[column].mean()) / data[column].std()
        
        return data
    
    @staticmethod
    def encode_categorical(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Encode categorical variables."""
        logger.info("Encoding categorical variables")
        
        for column in columns:
            if column in data.columns:
                data[column] = pd.Categorical(data[column]).codes
        
        return data

# Example usage
if __name__ == "__main__":
    # Example configurations
    db_config = {
        "source_connection": "postgresql://user:pass@localhost/source_db",
        "target_connection": "postgresql://user:pass@localhost/target_db",
        "extract_query": "SELECT * FROM customers WHERE updated_at > '2024-01-01'",
        "target_table": "customer_dimension"
    }
    
    api_config = {
        "api_url": "https://api.example.com/data",
        "api_key": "your_api_key",
        "target_table": "api_data"
    }
    
    file_config = {
        "source_file": "data/input.csv",
        "target_file": "data/output.csv",
        "file_type": "csv"
    }
    
    # Create and run pipelines
    db_pipeline = DatabaseETL("Customer ETL", db_config)
    api_pipeline = APIETL("API ETL", api_config)
    file_pipeline = FileETL("File ETL", file_config)
    
    # Run pipelines
    db_results = db_pipeline.run()
    api_results = api_pipeline.run()
    file_results = file_pipeline.run()
    
    print(f"Database ETL results: {db_results}")
    print(f"API ETL results: {api_results}")
    print(f"File ETL results: {file_results}") 