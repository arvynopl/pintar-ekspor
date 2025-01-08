# backend/app/services/data_processing/transformer.py
from typing import Dict, Tuple, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
import warnings

@dataclass
class TransformationMetrics:
    """Metrics for transformed data"""
    trend_direction: str  # 'increasing', 'decreasing', 'stable', or 'unknown'
    growth_rate: Optional[float]
    moving_average: Dict[str, Optional[float]]

class DataTransformer:
    """
    Data transformer with robust numeric handling and error checking.
    Handles data transformation operations with safety checks and comprehensive error handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.config = {
            'ma_windows': [7, 30],  # Moving average windows (7 days, 30 days)
            'min_periods': 3,       # Minimum periods for calculations
            'growth_threshold': 0.05, # 5% threshold for trend determination
            'numeric_limits': {
                'max_value': 1e308,  # Maximum safe JavaScript number
                'min_value': -1e308, # Minimum safe JavaScript number
                'replace_value': None # Value to use for invalid numbers
            }
        }

    def _safe_numeric(self, value: Any) -> Optional[float]:
        """
        Safely convert and validate numeric values.
        
        Args:
            value: Any value to be converted to a safe numeric value
            
        Returns:
            Optional[float]: Safe numeric value or None if invalid
        """
        try:
            if pd.isna(value) or value is None:
                return None
            
            # Convert to float
            value = float(value)
            
            # Check for special cases
            if np.isnan(value) or np.isinf(value):
                return None
                
            # Check value bounds
            if abs(value) > self.config['numeric_limits']['max_value']:
                self.logger.warning(f"Value {value} exceeds safe limits")
                return None
                
            return value
        except (TypeError, ValueError) as e:
            self.logger.warning(f"Error converting numeric value: {str(e)}")
            return None

    def _safe_division(self, numerator: float, denominator: float) -> Optional[float]:
        """
        Safely perform division with error handling.
        
        Args:
            numerator: Division numerator
            denominator: Division denominator
            
        Returns:
            Optional[float]: Result of division or None if invalid
        """
        try:
            if denominator == 0:
                return None
            result = numerator / denominator
            return self._safe_numeric(result)
        except Exception:
            return None

    def transform_pairs(
        self,
        pair_dataframes: Dict[str, pd.DataFrame]
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, TransformationMetrics]]:
        """
        Transform multiple category-value pair dataframes with error handling.
        
        Args:
            pair_dataframes: Dictionary of DataFrames to transform
            
        Returns:
            Tuple containing transformed DataFrames and their metrics
        """
        transformed_pairs = {}
        transformation_metrics = {}
        
        for pair_key, df in pair_dataframes.items():
            try:
                self.logger.info(f"Transforming pair: {pair_key}")
                if df is None or df.empty:
                    self.logger.warning(f"Empty dataframe for {pair_key}")
                    continue
                    
                transformed_df, metrics = self.transform_pair(df)
                
                if not transformed_df.empty:
                    transformed_pairs[pair_key] = transformed_df
                    transformation_metrics[pair_key] = metrics
                    
            except Exception as e:
                self.logger.error(f"Error transforming pair {pair_key}: {str(e)}")
                continue
                
        return transformed_pairs, transformation_metrics

    def transform_pair(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, TransformationMetrics]:
        """
        Transform a single category-value pair dataframe with numeric safety.
        
        Args:
            df: DataFrame to transform
            
        Returns:
            Tuple containing transformed DataFrame and its metrics
        """
        try:
            df = df.copy()
            
            # Validate input data
            if 'value' not in df.columns:
                raise ValueError("DataFrame must contain 'value' column")
            
            # Clean and validate numeric values
            df['value'] = df['value'].apply(self._safe_numeric)
            df = df.dropna(subset=['value'])
            
            if df.empty:
                raise ValueError("No valid numeric values after cleaning")
            
            # Add moving averages
            for window in self.config['ma_windows']:
                col_name = f'ma_{window}d'
                ma_values = df['value'].rolling(
                    window=window,
                    min_periods=self.config['min_periods']
                ).mean()
                df[col_name] = ma_values.apply(self._safe_numeric)
            
            # Calculate percentage change
            pct_change = df['value'].pct_change()
            df['pct_change'] = pct_change.apply(self._safe_numeric)
            
            # Calculate trend metrics
            metrics = self._calculate_trend_metrics(df)
            
            return df, metrics
            
        except Exception as e:
            raise ValueError(f"Error in transform_pair: {str(e)}")

    def _calculate_trend_metrics(self, df: pd.DataFrame) -> TransformationMetrics:
        """
        Calculate trend metrics with robust numeric handling.
        
        Args:
            df: DataFrame with validated numeric values
            
        Returns:
            TransformationMetrics containing trend analysis results
        """
        try:
            # Calculate growth rate
            first_value = self._safe_numeric(df['value'].iloc[0])
            last_value = self._safe_numeric(df['value'].iloc[-1])
            
            growth_rate = None
            if first_value is not None and last_value is not None:
                growth_rate = self._safe_division(
                    last_value - first_value,
                    first_value
                )
            
            # Calculate moving averages at the end
            moving_averages = {}
            for window in self.config['ma_windows']:
                col_name = f'ma_{window}d'
                ma_value = self._safe_numeric(df[col_name].iloc[-1])
                moving_averages[f'{window}d'] = ma_value
            
            # Calculate trend direction using linear regression
            values = df['value'].dropna().values
            X = np.arange(len(values)).reshape(-1, 1)
            
            model = LinearRegression()
            model.fit(X, values)
            slope = self._safe_numeric(float(model.coef_[0]))
            
            # Determine trend direction
            if slope is None:
                trend_direction = 'unknown'
            elif abs(growth_rate or 0) < self.config['growth_threshold']:
                trend_direction = 'stable'
            else:
                trend_direction = 'increasing' if slope > 0 else 'decreasing'
            
            return TransformationMetrics(
                trend_direction=trend_direction,
                growth_rate=growth_rate,
                moving_average=moving_averages
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating trend metrics: {str(e)}")
            return TransformationMetrics(
                trend_direction='unknown',
                growth_rate=None,
                moving_average={}
            )

    def get_transformation_summary(
        self,
        metrics: TransformationMetrics
    ) -> Dict[str, Any]:
        """
        Generate a summary of transformation results.
        
        Args:
            metrics: TransformationMetrics to summarize
            
        Returns:
            Dictionary containing summarized metrics
        """
        return {
            'trend': {
                'direction': metrics.trend_direction,
                'growth_rate': (
                    f"{metrics.growth_rate:.2%}"
                    if metrics.growth_rate is not None
                    else None
                )
            },
            'moving_averages': {
                window: (
                    f"{value:.2f}" if value is not None else None
                )
                for window, value in metrics.moving_average.items()
            }
        }