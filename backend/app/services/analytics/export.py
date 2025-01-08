# backend/app/services/analytics/export.py
import pandas as pd
import numpy as np
import json
from typing import Dict, Any, Optional
import io
from datetime import datetime
import logging

class DataExporter:
    """Handles export functionality for analytics results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _safe_numeric(self, value: Any) -> Optional[float]:
        """Safely convert numeric values for export"""
        try:
            if pd.isna(value) or value is None:
                return None
            
            # Convert to float
            value = float(value)
            
            # Check for special cases
            if np.isnan(value) or np.isinf(value):
                return None
                
            # Check value bounds
            if abs(value) > 1e308:  # Max safe JavaScript number
                return None
                
            return value
        except (TypeError, ValueError):
            return None

    def _sanitize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize DataFrame values for export"""
        df = df.copy()
        
        # Convert numeric columns to safe values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df[col] = df[col].apply(self._safe_numeric)
            
        return df

    def export_to_csv(
        self,
        pair_dataframes: Dict[str, pd.DataFrame],
        analysis_results: Dict[str, Any],
        visualizations: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Exports pair data and analysis results to CSV format"""
        output = io.StringIO()
        
        for pair_key, df in pair_dataframes.items():
            # Sanitize data
            safe_df = self._sanitize_dataframe(df)
            
            # Write pair identifier
            output.write(f"\n=== {pair_key} ===\n")
            
            # Write data
            safe_df.to_csv(output, index=True)
            
            # Write analysis results if available
            if pair_key in analysis_results:
                output.write("\nAnalysis Results:\n")
                analysis = analysis_results[pair_key]
                
                # Write trend info safely
                output.write(f"Trend Direction: {analysis.trend_analysis['direction']}\n")
                growth_rate = self._safe_numeric(analysis.growth_metrics['total_growth'])
                output.write(f"Growth Rate: {growth_rate:.2%}\n" if growth_rate is not None else "Growth Rate: N/A\n")
                
                # Write forecast if available
                if analysis.forecast:
                    output.write("\nForecast:\n")
                    forecast_data = {
                        'predicted': [
                            self._safe_numeric(v) for v in analysis.forecast['predictions']
                        ],
                        'lower_bound': [
                            self._safe_numeric(v) for v in analysis.forecast['lower_bound']
                        ],
                        'upper_bound': [
                            self._safe_numeric(v) for v in analysis.forecast['upper_bound']
                        ]
                    }
                    forecast_df = pd.DataFrame(forecast_data).fillna('N/A')
                    forecast_df.to_csv(output)
                
        # Add visualization section if provided
        if visualizations:
            output.write("\n=== Visualization Configurations ===\n")
            for viz_key, viz_config in visualizations.items():
                output.write(f"\n{viz_key}:\n")
                # Convert the config to a flattened string representation
                config_str = json.dumps(viz_config, indent=2, default=str)
                output.write(config_str + "\n")
        
        return output.getvalue().encode('utf-8')
        
    def export_to_json(
        self,
        pair_dataframes: Dict[str, pd.DataFrame],
        analysis_results: Dict[str, Any],
        visualizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exports data and analysis results to JSON format"""
        try:
            export_data = {
                'generated_at': datetime.now().isoformat(),
                'pairs': {}
            }
            
            for pair_key, df in pair_dataframes.items():
                # Sanitize DataFrame
                safe_df = self._sanitize_dataframe(df)
                
                # Convert to records with safe values
                records = []
                for _, row in safe_df.iterrows():
                    record = {}
                    for column, value in row.items():
                        if pd.api.types.is_numeric_dtype(type(value)):
                            record[column] = self._safe_numeric(value)
                        else:
                            record[column] = value
                    records.append(record)
                
                export_data['pairs'][pair_key] = {
                    'data': records,
                    'analysis': self._format_analysis(analysis_results.get(pair_key))
                }
            
            # Add visualizations if provided
            if visualizations:
                export_data['visualizations'] = visualizations

            # Validate JSON serialization
            return json.dumps(export_data, default=str)
            
        except Exception as e:
            self.logger.error(f"Error in JSON export: {str(e)}")
            raise
    
    def _format_analysis(self, analysis: Any) -> Optional[Dict[str, Any]]:
        """Format analysis results for JSON export with safe numeric handling"""
        if not analysis:
            return None
            
        try:
            trend_analysis = analysis.trend_analysis.copy()
            # Sanitize any numeric values in trend analysis
            if 'slope' in trend_analysis:
                trend_analysis['slope'] = self._safe_numeric(trend_analysis['slope'])
            if 'strength' in trend_analysis:
                trend_analysis['strength'] = self._safe_numeric(trend_analysis['strength'])
            if 'trend_values' in trend_analysis:
                trend_analysis['trend_values'] = [
                    self._safe_numeric(v) for v in trend_analysis['trend_values']
                ]
            
            growth_metrics = {}
            for key, value in analysis.growth_metrics.items():
                growth_metrics[key] = self._safe_numeric(value)
            
            basic_stats = {}
            for key, value in analysis.basic_stats.items():
                basic_stats[key] = self._safe_numeric(value)
            
            forecast = None
            if analysis.forecast:
                forecast = {
                    'predictions': [
                        self._safe_numeric(v) for v in analysis.forecast['predictions']
                    ],
                    'lower_bound': [
                        self._safe_numeric(v) for v in analysis.forecast['lower_bound']
                    ],
                    'upper_bound': [
                        self._safe_numeric(v) for v in analysis.forecast['upper_bound']
                    ],
                    'metrics': {
                        k: self._safe_numeric(v)
                        for k, v in analysis.forecast['metrics'].items()
                    }
                }
            
            return {
                'trend': trend_analysis,
                'growth': growth_metrics,
                'statistics': basic_stats,
                'forecast': forecast
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting analysis: {str(e)}")
            return None