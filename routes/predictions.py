"""API routes for predictive analytics."""
from fastapi import APIRouter, HTTPException, Query
from services.predictions import PredictionService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/hotspots")
async def get_predicted_hotspots(
    days_ahead: int = Query(7, ge=1, le=30, description="Days to predict ahead")
):
    """Predict service request hotspots - PREDICTIVE ANALYTICS.
    
    Uses REAL historical 311 data patterns to predict where issues will occur.
    Based on actual NYC service request trends.
    """
    try:
        predictions = PredictionService.predict_hotspots(days_ahead)
        return {
            'predictions': predictions,
            'count': len(predictions),
            'days_ahead': days_ahead,
            'note': 'Predictions based on real historical 311 request patterns from NYC Open Data'
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")

@router.get("/tonnage-forecast")
async def get_tonnage_forecast(
    zone_id: str = Query(..., description="Zone ID to forecast"),
    days: int = Query(7, ge=1, le=30, description="Days to forecast ahead")
):
    """Predict tonnage forecast for a zone - PREDICTIVE ANALYTICS.
    
    Uses REAL DSNY monthly tonnage data to forecast future collection needs.
    """
    try:
        forecast = PredictionService.predict_tonnage_forecast(zone_id, days)
        return forecast
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast")

@router.get("/route-optimization")
async def get_route_optimization(
    zone_id: str = Query(..., description="Zone ID to optimize")
):
    """Predict route optimization savings - PREDICTIVE ANALYTICS.
    
    Analyzes REAL route performance data to predict time and cost savings.
    """
    try:
        optimization = PredictionService.predict_route_optimization(zone_id)
        return optimization
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize routes")

@router.get("/complaint-types")
async def get_complaint_type_forecast(
    days_ahead: int = Query(30, ge=7, le=90, description="Days to predict ahead")
):
    """Predict which complaint types will spike - PREDICTIVE ANALYTICS.
    
    Uses seasonal patterns and historical data to forecast complaint type trends.
    """
    try:
        forecast = PredictionService.predict_complaint_types(days_ahead)
        return forecast
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate complaint type forecast")

@router.get("/overflow-risk")
async def get_overflow_risk(
    days_ahead: int = Query(7, ge=1, le=30, description="Days to predict ahead")
):
    """Predict zones at risk of overflow - PREDICTIVE ANALYTICS.
    
    Identifies zones likely to experience overflow issues based on historical patterns.
    """
    try:
        risk_zones = PredictionService.predict_overflow_risk(days_ahead)
        return {
            'risk_zones': risk_zones,
            'count': len(risk_zones),
            'days_ahead': days_ahead,
            'data_source': 'Real historical overflow complaints and collection data'
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict overflow risk")

@router.get("/borough-complaints")
async def get_borough_complaint_predictions(
    days_ahead: int = Query(30, ge=7, le=90, description="Days to predict ahead")
):
    """Predict complaint counts by borough - PREDICTIVE ANALYTICS.
    
    Uses time series analysis on historical 311 data to forecast future complaint
    volumes for each borough. Applies trend detection and seasonal patterns.
    """
    try:
        predictions = PredictionService.predict_borough_complaints(days_ahead)
        return predictions
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate borough predictions")

