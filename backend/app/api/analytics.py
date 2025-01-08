# backend/app/api/analytics.py
import json
import logging
from typing import Dict, Any, Optional
from fastapi import (
    APIRouter, File, UploadFile, Depends, 
    HTTPException, Query, status, Response
)
from datetime import datetime

from ..services.data_processing.data_handler import DataHandler
from ..services.data_processing.cleaner import DataCleaner
from ..services.data_processing.transformer import DataTransformer
from ..services.analytics.statistics import DataAnalytics
from ..services.analytics.export import DataExporter
from ..services.visualization.chart_generator import ChartGenerator
from .deps import (
    get_current_developer, 
    get_api_key_user
)
from ..models.user import User

# Initialize services
data_handler = DataHandler()
data_cleaner = DataCleaner()
data_transformer = DataTransformer()
analytics_service = DataAnalytics()
exporter = DataExporter()
chart_generator = ChartGenerator()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class AnalyticsError(Exception):
    """Custom exception for analytics-related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def _safe_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all numeric values in the response are JSON-safe.
    
    Args:
        data (Dict[str, Any]): Input data to sanitize
    
    Returns:
        Dict[str, Any]: JSON-safe data
    """
    try:
        # Test JSON serialization
        json.dumps(data)
        return data
    except (TypeError, OverflowError):
        # If serialization fails, try to sanitize the data
        if isinstance(data, dict):
            return {k: _safe_json_response(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_safe_json_response(item) for item in data]
        elif isinstance(data, float):
            if not (data <= 1e308 and data >= -1e308):
                return None
            return data
        else:
            return data

@router.post("/analyze")
async def analyze_data(
    file: UploadFile = File(...),
    # Use API key or developer authentication
    _: User = Depends(get_api_key_user),
    include_forecast: bool = Query(True, description="Include forecast in analysis"),
    include_visualizations: bool = Query(False, description="Include visualization configurations in export"),
    export_format: Optional[str] = Query(None, regex="^(csv|json)$"),
):
    """
    Primary endpoint for comprehensive data analysis
    
    Args:
        file (UploadFile): Input data file for analysis
        _: API key validated user
        include_forecast (bool): Flag to include forecasting
        include_visualizations (bool): Flag to include visualization configs
        export_format (Optional[str]): Optional export format
    
    Returns:
        Analysis results with optional export
    
    Raises:
        HTTPException: For various processing errors
    """
    try:
        # 1. Process uploaded file
        try:
            pair_dataframes = await data_handler.process_upload(file)
            if not pair_dataframes:
                raise AnalyticsError("No valid data found in uploaded file")
            logger.info(f"Processed {len(pair_dataframes)} category pairs")
        except Exception as e:
            raise AnalyticsError("Error processing upload", {"error": str(e)})

        # 2. Clean data
        try:
            cleaned_pairs, quality_metrics = data_cleaner.clean_pairs(pair_dataframes)
            if not cleaned_pairs:
                raise AnalyticsError("No valid data after cleaning")
            logger.info("Data cleaning completed")
        except Exception as e:
            raise AnalyticsError("Error cleaning data", {"error": str(e)})

        # 3. Transform data
        try:
            transformed_pairs, transform_metrics = data_transformer.transform_pairs(cleaned_pairs)
            if not transformed_pairs:
                raise AnalyticsError("No valid data after transformation")
            logger.info("Data transformation completed")
        except Exception as e:
            raise AnalyticsError("Error transforming data", {"error": str(e)})

        # 4. Perform analysis
        try:
            analysis_results = analytics_service.analyze_pairs(
                transformed_pairs,
                include_forecast=include_forecast
            )
            if not analysis_results:
                raise AnalyticsError("Analysis produced no valid results")
            logger.info("Analysis completed")
        except Exception as e:
            raise AnalyticsError("Error performing analysis", {"error": str(e)})

        # 5. Generate visualizations
        visualizations = {}
        try:
            for pair_key, analysis in analysis_results.items():
                # Trend chart
                trend_chart = chart_generator.generate_trend_chart(
                    transformed_pairs[pair_key],
                    analysis.trend_analysis,
                    analysis.forecast if include_forecast else None
                )
                if trend_chart:
                    visualizations[f"{pair_key}_trend"] = trend_chart

            # Category strength chart
            strength_chart = chart_generator.generate_category_strength_chart(analysis_results)
            if strength_chart:
                visualizations['category_strength'] = strength_chart
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            # Continue without visualizations if they fail

        # Prepare response
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                pair_key: analytics_service.get_analysis_summary(results)
                for pair_key, results in analysis_results.items()
            },
            "quality_metrics": {
                pair_key: data_cleaner.get_cleaning_summary(metrics)
                for pair_key, metrics in quality_metrics.items()
            },
            "visualizations": visualizations
        }

        # Ensure response is JSON-safe
        safe_response = _safe_json_response(response_data)

        # Export if format specified
        if export_format:
            try:
                if export_format == 'csv':
                    content = exporter.export_to_csv(
                        transformed_pairs, 
                        analysis_results,
                        visualizations if include_visualizations else None
                    )
                    return Response(
                        content=content,
                        media_type="text/csv",
                        headers={
                            "Content-Disposition": f"attachment; filename=analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        }
                    )
                else:  # json
                    content = exporter.export_to_json(
                        transformed_pairs, 
                        analysis_results,
                        visualizations if include_visualizations else None
                    )
                    return Response(
                        content=content,
                        media_type="application/json",
                        headers={
                            "Content-Disposition": f"attachment; filename=analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        }
                    )
            except Exception as e:
                logger.error(f"Export error: {str(e)}")
                # Add more detailed error handling
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": f"Export to {export_format} failed", "error": str(e)}
                )

        return safe_response

    except AnalyticsError as e:
        logger.error(f"Analytics error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing the analysis"
        )

@router.post("/quick-analysis")
async def quick_analysis(
    file: UploadFile = File(...),
    # Require developer role or API key
    _: User = Depends(get_api_key_user),
    category: Optional[str] = Query(None, description="Specific category to analyze")
):
    """
    Quick analysis endpoint for basic trend and growth insights
    
    Args:
        file (UploadFile): Input data file
        _: Validated API key user
        category (Optional[str]): Optional specific category to analyze
    
    Returns:
        Simplified analysis results
    
    Raises:
        HTTPException: For processing errors
    """
    try:
        # 1. Process uploaded file
        try:
            pair_dataframes = await data_handler.process_upload(file)
            if not pair_dataframes:
                raise AnalyticsError("No valid data found in uploaded file")
        except Exception as e:
            raise AnalyticsError("Error processing upload", {"error": str(e)})

        # 2. Clean data
        try:
            cleaned_pairs, _ = data_cleaner.clean_pairs(pair_dataframes)
            if not cleaned_pairs:
                raise AnalyticsError("No valid data after cleaning")
        except Exception as e:
            raise AnalyticsError("Error cleaning data", {"error": str(e)})

        # 3. Filter for specific category if provided
        if category:
            category_key = f"category_{category}"
            if category_key not in cleaned_pairs:
                raise AnalyticsError(f"Category '{category}' not found in data")
            cleaned_pairs = {category_key: cleaned_pairs[category_key]}

        # 4. Perform basic analysis
        try:
            analysis_results = analytics_service.analyze_pairs(
                cleaned_pairs,
                include_forecast=False
            )
            if not analysis_results:
                raise AnalyticsError("Analysis produced no valid results")
        except Exception as e:
            raise AnalyticsError("Error performing analysis", {"error": str(e)})

        # 5. Prepare response
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "results": {
                pair_key: {
                    "trend": results.trend_analysis['direction'],
                    "growth": (
                        f"{results.growth_metrics['total_growth']:.2%}"
                        if results.growth_metrics['total_growth'] is not None
                        else None
                    ),
                    "current_value": results.basic_stats['last_value']
                }
                for pair_key, results in analysis_results.items()
            }
        }

        return _safe_json_response(response_data)

    except AnalyticsError as e:
        logger.error(f"Analytics error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing the quick analysis"
        )

@router.get("/documentation")
async def get_documentation(
    # Require developer role or API key
    _: User = Depends(get_current_developer)
):
    """
    API documentation endpoint for analytics services
    
    Args:
        _: Validated developer user
    
    Returns:
        Comprehensive API documentation
    """
    return {
        "version": "1.0",
        "endpoints": {
            "/analyze": {
                "method": "POST",
                "description": "Complete analysis pipeline with visualizations",
                "parameters": {
                    "file": "CSV or JSON file with time series data",
                    "include_forecast": "Boolean to include forecasting",
                    "include_visualizations": "Boolean to include visualization configurations in export",
                    "export_format": "Optional: 'csv' or 'json'"
                },
                "error_handling": {
                    "400": "Invalid input or processing error",
                    "401": "Invalid API key",
                    "429": "Rate limit exceeded",
                    "500": "Internal server error"
                }
            },
            "/quick-analysis": {
                "method": "POST",
                "description": "Basic trend and growth analysis",
                "parameters": {
                    "file": "CSV or JSON file with time series data",
                    "category": "Optional: specific category to analyze"
                }
            }
        },
        "data_formats": {
            "date-category-value": {
                "description": "Standard format with date, category, and value columns"
            },
            "date-pairs": {
                "description": "Format with date and column-value pairs"
            }
        },
        "numeric_limits": {
            "max_value": 1e308,
            "min_value": -1e308,
            "description": "Values outside these limits will be converted to null"
        }
    }