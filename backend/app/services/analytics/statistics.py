# backend/app/services/analytics/statistics.py
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

@dataclass
class AnalyticsResults:
    """Core analytics results for category-value pairs"""
    trend_analysis: Dict[str, Any]
    growth_metrics: Dict[str, float]
    basic_stats: Dict[str, float]
    forecast: Optional[Dict[str, Any]] = None

class DataAnalytics:
    """
    Analytics implementation with robust numeric handling and error checking
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration with numeric safety limits
        self.config = {
            'forecast_days': 30,
            'min_points': 10,
            'growth_windows': [7, 30],
            'significant_change': 0.01,
            'numeric_limits': {
                'max_value': 1e308,
                'min_value': -1e308,
                'replace_value': None
            }
        }

    def _safe_numeric(self, value: Any) -> Optional[float]:
        """Safely convert and validate numeric values"""
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
        """Safely perform division with error handling"""
        try:
            if denominator == 0:
                return None
            result = numerator / denominator
            return self._safe_numeric(result)
        except Exception:
            return None

    def analyze_pairs(
        self,
        pair_dataframes: Dict[str, pd.DataFrame],
        include_forecast: bool = True
    ) -> Dict[str, AnalyticsResults]:
        """Analyze multiple category-value pairs with error handling"""
        results = {}
        
        for pair_key, df in pair_dataframes.items():
            try:
                self.logger.info(f"Analyzing pair: {pair_key}")
                if df is None or df.empty:
                    self.logger.warning(f"Empty dataframe for {pair_key}")
                    continue
                    
                results[pair_key] = self.analyze_pair(df, include_forecast)
            except Exception as e:
                self.logger.error(f"Error analyzing pair {pair_key}: {str(e)}")
                continue
                
        return results

    def analyze_pair(
        self,
        df: pd.DataFrame,
        include_forecast: bool = True
    ) -> AnalyticsResults:
        """Analyze a single category-value pair with numeric safety"""
        try:
            if len(df) < self.config['min_points']:
                raise ValueError(f"Insufficient data points: {len(df)}")

            # Clean numeric values
            df = df.copy()
            df['value'] = df['value'].apply(self._safe_numeric)
            df = df.dropna(subset=['value'])
            
            if df.empty:
                raise ValueError("No valid numeric values after cleaning")

            # Calculate components
            basic_stats = self._calculate_basic_stats(df)
            trend_analysis = self._analyze_trend(df)
            growth_metrics = self._calculate_growth_metrics(df)
            
            # Generate forecast if requested
            forecast = None
            if include_forecast:
                forecast = self._generate_forecast(df)
            
            return AnalyticsResults(
                trend_analysis=trend_analysis,
                growth_metrics=growth_metrics,
                basic_stats=basic_stats,
                forecast=forecast
            )
            
        except Exception as e:
            raise ValueError(f"Error in analyze_pair: {str(e)}")

    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic statistics with numeric safety"""
        try:
            values = df['value'].dropna()
            if values.empty:
                raise ValueError("No valid values for statistics")
                
            return {
                'mean': self._safe_numeric(values.mean()),
                'median': self._safe_numeric(values.median()),
                'std': self._safe_numeric(values.std()),
                'min': self._safe_numeric(values.min()),
                'max': self._safe_numeric(values.max()),
                'last_value': self._safe_numeric(values.iloc[-1])
            }
        except Exception as e:
            self.logger.error(f"Error calculating basic stats: {str(e)}")
            return {
                'mean': None, 'median': None, 'std': None,
                'min': None, 'max': None, 'last_value': None
            }

    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trend with robust numeric handling"""
        try:
            values = df['value'].dropna().values
            X = np.arange(len(values)).reshape(-1, 1)
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, values)
            
            # Calculate trend metrics safely
            slope = self._safe_numeric(float(model.coef_[0]))
            r_squared = self._safe_numeric(model.score(X, values))
            trend_line = [self._safe_numeric(v) for v in model.predict(X)]
            
            # Calculate relative slope
            avg_value = np.mean(values)
            relative_slope = self._safe_division(slope, avg_value) if slope is not None else None
            
            # Determine trend direction
            if relative_slope is None:
                direction = 'unknown'
            elif abs(relative_slope) < self.config['significant_change']:
                direction = 'stable'
            else:
                direction = 'increasing' if slope > 0 else 'decreasing'
            
            return {
                'direction': direction,
                'slope': slope,
                'strength': r_squared,
                'significant': relative_slope is not None and abs(relative_slope) >= self.config['significant_change'],
                'trend_values': trend_line
            }
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {str(e)}")
            return {
                'direction': 'unknown',
                'slope': None,
                'strength': None,
                'significant': False,
                'trend_values': []
            }

    def _calculate_growth_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate growth metrics with safe numeric operations"""
        metrics = {}
        try:
            first_value = self._safe_numeric(df['value'].iloc[0])
            last_value = self._safe_numeric(df['value'].iloc[-1])
            
            # Calculate total growth
            if first_value is not None and last_value is not None:
                total_growth = self._safe_division(
                    last_value - first_value,
                    first_value
                )
            else:
                total_growth = None
            
            metrics['total_growth'] = total_growth
            
            # Calculate window-based growth
            for window in self.config['growth_windows']:
                if len(df) >= window:
                    window_start = self._safe_numeric(df['value'].iloc[-window])
                    window_end = self._safe_numeric(df['value'].iloc[-1])
                    
                    if window_start is not None and window_end is not None:
                        window_growth = self._safe_division(
                            window_end - window_start,
                            window_start
                        )
                    else:
                        window_growth = None
                        
                    metrics[f'{window}d_growth'] = window_growth
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {str(e)}")
            return {'total_growth': None}

    def _generate_forecast(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Generate forecast with numeric safety"""
        try:
            values = df['value'].dropna().values
            X = np.arange(len(values)).reshape(-1, 1)
            
            # Fit model
            model = LinearRegression()
            model.fit(X, values)
            
            # Generate future dates
            future_X = np.arange(
                len(values),
                len(values) + self.config['forecast_days']
            ).reshape(-1, 1)
            
            # Generate predictions
            predictions = [
                self._safe_numeric(v) 
                for v in model.predict(future_X)
            ]
            
            # Calculate error metrics
            historical_pred = model.predict(X)
            mae = self._safe_numeric(mean_absolute_error(values, historical_pred))
            rmse = self._safe_numeric(np.sqrt(mean_squared_error(values, historical_pred)))
            
            # Calculate prediction intervals
            std_err = self._safe_numeric(np.std(values - historical_pred))
            if std_err is not None:
                lower_bound = [
                    self._safe_numeric(pred - (2 * std_err))
                    for pred in predictions
                ]
                upper_bound = [
                    self._safe_numeric(pred + (2 * std_err))
                    for pred in predictions
                ]
            else:
                lower_bound = [None] * len(predictions)
                upper_bound = [None] * len(predictions)
            
            return {
                'predictions': predictions,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'metrics': {
                    'mae': mae,
                    'rmse': rmse,
                    'std_error': std_err
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating forecast: {str(e)}")
            return None

    def get_analysis_summary(self, results: AnalyticsResults) -> Dict[str, Any]:
        """Generate analysis summary with safe value handling"""
        return {
            'trend': {
                'direction': results.trend_analysis['direction'],
                'strength': results.trend_analysis['strength'],
                'significant': results.trend_analysis['significant']
            },
            'growth': {
                'total': (
                    f"{results.growth_metrics['total_growth']:.2%}"
                    if results.growth_metrics['total_growth'] is not None
                    else None
                ),
                'recent': (
                    f"{results.growth_metrics.get('7d_growth', 0):.2%}"
                    if results.growth_metrics.get('7d_growth') is not None
                    else None
                )
            },
            'current_stats': {
                'last_value': results.basic_stats['last_value'],
                'mean': results.basic_stats['mean'],
                'std': results.basic_stats['std']
            },
            'forecast': {
                'available': results.forecast is not None,
                'metrics': results.forecast['metrics'] if results.forecast else None
            }
        }