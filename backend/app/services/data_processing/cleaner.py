# backend/app/services/data_processing/cleaner.py
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass

@dataclass
class DataQualityMetrics:
    """Simple metrics for data quality assessment"""
    missing_count: int
    duplicate_count: int
    outlier_count: int
    total_records: int
    clean_records: int

class DataCleaner:
    """
    Simplified data cleaner that handles basic data quality issues:
    - Missing values
    - Duplicates
    - Outliers
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Simplified configuration
        self.config = {
            'outlier_threshold': 1.5,  # IQR multiplier for outlier detection
            'max_missing_pct': 0.3,    # Maximum allowed missing percentage
            'min_records': 3           # Minimum required records
        }

    def clean_pairs(
        self,
        pair_dataframes: Dict[str, pd.DataFrame]
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, DataQualityMetrics]]:
        """Clean multiple category-value pair dataframes"""
        cleaned_pairs = {}
        quality_metrics = {}
        
        for pair_key, df in pair_dataframes.items():
            try:
                self.logger.info(f"Cleaning pair: {pair_key}")
                cleaned_df, metrics = self.clean_pair(df)
                
                if not cleaned_df.empty:
                    cleaned_pairs[pair_key] = cleaned_df
                    quality_metrics[pair_key] = metrics
                    
            except Exception as e:
                self.logger.error(f"Error cleaning pair {pair_key}: {str(e)}")
                continue
                
        return cleaned_pairs, quality_metrics

    def clean_pair(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, DataQualityMetrics]:
        """
        Clean a single category-value pair dataframe.
        Handles missing values, duplicates, and outliers.
        """
        try:
            df = df.copy()
            initial_records = len(df)
            
            if len(df) < self.config['min_records']:
                raise ValueError(f"Insufficient records: {len(df)}")

            # 1. Handle missing values
            missing_count = df['value'].isnull().sum()
            if missing_count / len(df) > self.config['max_missing_pct']:
                raise ValueError(f"Too many missing values: {missing_count}")
            
            df = self._handle_missing_values(df)

            # 2. Remove duplicates
            duplicate_count = df.index.duplicated().sum()
            df = df[~df.index.duplicated(keep='first')]

            # 3. Handle outliers
            df, outlier_count = self._handle_outliers(df)

            # Calculate metrics
            metrics = DataQualityMetrics(
                missing_count=missing_count,
                duplicate_count=duplicate_count,
                outlier_count=outlier_count,
                total_records=initial_records,
                clean_records=len(df)
            )

            return df, metrics
            
        except Exception as e:
            raise ValueError(f"Error in clean_pair: {str(e)}")

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values using forward fill and interpolation"""
        if 'value' not in df.columns:
            raise ValueError("DataFrame must contain 'value' column")

        # Forward fill using recommended method
        df['value'] = df['value'].ffill()
        
        # Interpolate any remaining missing values
        df['value'] = df['value'].interpolate(method='linear')
        
        # Back fill any remaining NaNs (at the start) using recommended method
        df['value'] = df['value'].bfill()
        
        return df

    def _handle_outliers(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, int]:
        """
        Handle outliers using IQR method.
        Returns cleaned DataFrame and count of outliers handled.
        """
        if 'value' not in df.columns:
            raise ValueError("DataFrame must contain 'value' column")

        # Ensure value column is float type
        df['value'] = df['value'].astype(float)

        # Calculate IQR
        Q1 = df['value'].quantile(0.25)
        Q3 = df['value'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Calculate bounds
        lower_bound = Q1 - (self.config['outlier_threshold'] * IQR)
        upper_bound = Q3 + (self.config['outlier_threshold'] * IQR)
        
        # Identify outliers
        outliers = (df['value'] < lower_bound) | (df['value'] > upper_bound)
        outlier_count = outliers.sum()
        
        # Replace outliers with bounds (using float values)
        df.loc[df['value'] < lower_bound, 'value'] = float(lower_bound)
        df.loc[df['value'] > upper_bound, 'value'] = float(upper_bound)
        
        return df, outlier_count

    def get_cleaning_summary(
        self,
        metrics: DataQualityMetrics
    ) -> Dict[str, Any]:
        """Generate a summary of cleaning results"""
        return {
            'records': {
                'initial': metrics.total_records,
                'cleaned': metrics.clean_records,
                'removed': metrics.total_records - metrics.clean_records
            },
            'issues_handled': {
                'missing_values': metrics.missing_count,
                'duplicates': metrics.duplicate_count,
                'outliers': metrics.outlier_count
            },
            'quality_score': round(metrics.clean_records / metrics.total_records * 100, 2)
        }