# backend/app/services/data_processing/data_handler.py
from typing import Dict, Any, Union
import pandas as pd
import json
import io
from fastapi import UploadFile
import logging
from datetime import datetime

class DataHandler:
    """
    Handles initial data processing for CSV and JSON files.
    Focuses on converting input data into a standardized DataFrame format
    with datetime index and category-value pairs.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def process_upload(
        self,
        file: Union[UploadFile, io.BytesIO],
        input_format: str = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Process uploaded file into category-value pair dataframes.
        
        Args:
            file: Upload file object (CSV or JSON)
            input_format: Optional format specification ('csv' or 'json')
            
        Returns:
            Dictionary of DataFrames with datetime index and category-value columns
        """
        try:
            # Detect format if not specified
            if not input_format:
                filename = getattr(file, 'filename', '')
                input_format = self._detect_format(filename)

            # Read file content
            if isinstance(file, io.BytesIO):
                content = file.getvalue()
            else:
                content = await file.read()
            
            # Process based on format
            if input_format == 'csv':
                return self._process_csv(content)
            elif input_format == 'json':
                return self._process_json(content)
            else:
                raise ValueError(f"Unsupported format: {input_format}")
                
        except Exception as e:
            self.logger.error(f"Error processing upload: {str(e)}")
            raise ValueError(f"Error processing file: {str(e)}")

    def _detect_format(self, filename: str) -> str:
        """Detect file format from filename."""
        if filename.lower().endswith('.csv'):
            return 'csv'
        elif filename.lower().endswith('.json'):
            return 'json'
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")

    def _process_csv(self, content: bytes) -> Dict[str, pd.DataFrame]:
        """
        Process CSV content into pair dataframes.
        Handles both date-category-value and date-column-value pair formats.
        """
        try:
            # Read CSV
            df = pd.read_csv(io.BytesIO(content))
            self.logger.info(f"Loaded CSV with columns: {df.columns.tolist()}")
            
            # Handle standard format (date, category, value)
            if set(df.columns) == {'date', 'category', 'value'}:
                self.logger.info("Processing standard format")
                return self._process_standard_format(df)
            
        except Exception as e:
            self.logger.error(f"Error processing CSV: {str(e)}")
            raise ValueError(f"Error processing CSV: {str(e)}")

    def _process_json(self, content: bytes) -> Dict[str, pd.DataFrame]:
        """Process JSON content into pair dataframes."""
        try:
            # Parse JSON
            data = json.loads(content.decode('utf-8'))
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                raise ValueError("Invalid JSON structure")
            
            # Process based on format
            if set(df.columns) == {'date', 'category', 'value'}:
                return self._process_standard_format(df)
            
        except Exception as e:
            raise ValueError(f"Error processing JSON: {str(e)}")

    def _process_standard_format(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Process data in date-category-value format."""
        pairs = {}
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Split by category
        for category in df['category'].unique():
            category_df = df[df['category'] == category].copy()
            category_df.set_index('date', inplace=True)
            pairs[f"category_{category}"] = category_df
        
        return pairs

    def export_data(self, data: Dict[str, Any], format: str = 'json') -> Union[str, bytes]:
        """
        Export processed data in specified format.
        
        Args:
            data: Processed data to export
            format: Export format ('json' or 'csv')
            
        Returns:
            Formatted data as string (JSON) or bytes (CSV)
        """
        try:
            if format == 'json':
                export_data = {
                    'metadata': {
                        'exported_at': datetime.now().isoformat(),
                        'format': 'json'
                    },
                    'data': data
                }
                return json.dumps(export_data, default=str)
                
            elif format == 'csv':
                output = io.StringIO()
                for key, df in data.items():
                    output.write(f"=== {key} ===\n")
                    df.to_csv(output)
                    output.write("\n")
                return output.getvalue().encode('utf-8')
                
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise ValueError(f"Error exporting data: {str(e)}")