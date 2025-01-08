# backend/app/services/visualization/chart_generator.py
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from decimal import Decimal, InvalidOperation

class ChartGenerator:
    """
    Chart generator for trend and category strength visualizations.
    Includes robust handling of floating-point values and JSON serialization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Basic chart configuration
        self.config = {
            'colors': {
                'actual': '#4E79A7',    # Blue
                'forecast': '#F28E2B',   # Orange
                'bounds': '#E5E7EB',     # Light gray
                'trend': '#59A14F'       # Green
            },
            'max_points': 100,           # Maximum points to display
            'value_limits': {
                'max': 1e308,            # Max safe JavaScript number
                'min': -1e308,           # Min safe JavaScript number
                'null_value': None       # Value to use for invalid/extreme numbers
            }
        }

    def _sanitize_float(self, value: Any) -> Optional[float]:
        """
        Sanitize float values for JSON serialization.
        Handles inf, nan, and extremely large numbers.
        """
        try:
            # Convert to float if not already
            if isinstance(value, (int, float, np.number)):
                value = float(value)
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, str):
                try:
                    value = float(value)
                except (ValueError, InvalidOperation):
                    return None
            else:
                return None

            # Check for special cases
            if pd.isna(value) or np.isnan(value):
                return None
            if np.isinf(value):
                return None
            
            # Check for extremely large/small numbers
            if abs(value) > self.config['value_limits']['max']:
                self.logger.warning(f"Value {value} exceeds safe limits, converting to None")
                return None
            
            # Return the sanitized value
            return value
        except Exception as e:
            self.logger.error(f"Error sanitizing float value: {str(e)}")
            return None

    def _prepare_time_series(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare time series data for charting with robust value handling"""
        try:
            # Ensure value column exists
            if 'value' not in df.columns:
                raise ValueError("DataFrame must contain 'value' column")

            # Convert values to float and handle problematic values
            df = df.copy()
            df['value'] = df['value'].apply(self._sanitize_float)

            # Downsample if too many points
            if len(df) > self.config['max_points']:
                df = df.resample('D').agg({'value': 'mean'}).dropna()

            # Format for chart
            chart_data = []
            for index, row in df.iterrows():
                if pd.notnull(row['value']):  # Only include non-null values
                    chart_data.append({
                        'x': index.isoformat(),
                        'y': row['value']
                    })

            return chart_data
        except Exception as e:
            self.logger.error(f"Error preparing time series: {str(e)}")
            return []

    def generate_trend_chart(
        self,
        df: pd.DataFrame,
        trend_analysis: Dict[str, Any],
        forecast: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate trend chart data with robust error handling"""
        try:
            # Validate input data
            if df.empty:
                raise ValueError("Empty DataFrame provided")

            # Prepare actual data points
            actual_data = self._prepare_time_series(df)
            if not actual_data:
                raise ValueError("No valid data points after processing")

            # Prepare trend line with sanitized values
            trend_values = [self._sanitize_float(v) for v in trend_analysis.get('trend_values', [])]
            trend_data = [
                {'x': date.isoformat(), 'y': value}
                for date, value in zip(df.index, trend_values)
                if value is not None
            ]

            # Initialize datasets
            datasets = [
                {
                    'label': 'Actual Values',
                    'data': actual_data,
                    'borderColor': self.config['colors']['actual'],
                    'backgroundColor': 'transparent',
                    'type': 'line'
                }
            ]

            # Add trend line if available
            if trend_data:
                datasets.append({
                    'label': 'Trend',
                    'data': trend_data,
                    'borderColor': self.config['colors']['trend'],
                    'backgroundColor': 'transparent',
                    'borderDash': [5, 5],
                    'type': 'line'
                })

            # Add forecast if available and valid
            if forecast:
                forecast_datasets = self._prepare_forecast_datasets(df.index[-1], forecast)
                if forecast_datasets:
                    datasets.extend(forecast_datasets)

            return {
                'type': 'line',
                'data': {'datasets': datasets},
                'options': {
                    'responsive': True,
                    'scales': {
                        'x': {
                            'type': 'time',
                            'time': {'unit': 'day'},
                            'title': {'display': True, 'text': 'Date'}
                        },
                        'y': {
                            'title': {'display': True, 'text': 'Value'}
                        }
                    }
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating trend chart: {str(e)}")
            return None

    def generate_category_strength_chart(
        self,
        analysis_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate category strength chart with robust value handling"""
        try:
            categories = []
            growth_rates = []
            trend_strengths = []

            for category, results in analysis_results.items():
                # Extract and sanitize values
                growth_rate = self._sanitize_float(
                    results.growth_metrics.get('total_growth', 0) * 100
                )
                trend_strength = self._sanitize_float(
                    results.trend_analysis.get('strength', 0) * 100
                )

                if growth_rate is not None and trend_strength is not None:
                    categories.append(category.replace('category_', ''))
                    growth_rates.append(growth_rate)
                    trend_strengths.append(trend_strength)

            if not categories:
                raise ValueError("No valid categories after processing")

            # Sort by growth rate
            sorted_indices = np.argsort(growth_rates)[::-1]

            return {
                'type': 'bar',
                'data': {
                    'labels': [categories[i] for i in sorted_indices],
                    'datasets': [
                        {
                            'label': 'Growth Rate (%)',
                            'data': [growth_rates[i] for i in sorted_indices],
                            'backgroundColor': self.config['colors']['actual'],
                            'yAxisID': 'y'
                        },
                        {
                            'label': 'Trend Strength (%)',
                            'data': [trend_strengths[i] for i in sorted_indices],
                            'backgroundColor': self.config['colors']['trend'],
                            'yAxisID': 'y'
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'title': {
                                'display': True,
                                'text': 'Percentage (%)'
                            }
                        }
                    }
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating category strength chart: {str(e)}")
            return None

    def _prepare_forecast_datasets(
        self,
        last_date: pd.Timestamp,
        forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prepare forecast datasets with sanitized values"""
        try:
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=len(forecast['predictions']),
                freq='D'
            )

            # Sanitize forecast values
            predictions = [self._sanitize_float(v) for v in forecast['predictions']]
            lower_bounds = [self._sanitize_float(v) for v in forecast['lower_bound']]
            upper_bounds = [self._sanitize_float(v) for v in forecast['upper_bound']]

            # Prepare forecast data
            forecast_data = [
                {'x': date.isoformat(), 'y': pred}
                for date, pred in zip(future_dates, predictions)
                if pred is not None
            ]

            # Prepare bounds data
            bounds_data = [
                {'x': date.isoformat(), 'y0': lower, 'y1': upper}
                for date, lower, upper in zip(future_dates, lower_bounds, upper_bounds)
                if lower is not None and upper is not None
            ]

            datasets = []
            if forecast_data:
                datasets.append({
                    'label': 'Forecast',
                    'data': forecast_data,
                    'borderColor': self.config['colors']['forecast'],
                    'backgroundColor': 'transparent',
                    'type': 'line'
                })

            if bounds_data:
                datasets.append({
                    'label': 'Forecast Range',
                    'data': bounds_data,
                    'backgroundColor': self.config['colors']['bounds'],
                    'borderWidth': 0,
                    'type': 'area'
                })

            return datasets

        except Exception as e:
            self.logger.error(f"Error preparing forecast datasets: {str(e)}")
            return []