"""API routes for tonnage analytics."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/by-borough")
async def get_tonnage_by_borough(
    month: Optional[str] = Query(None, description="Month in format YYYY-MM (e.g., 2025-10)"),
    year: Optional[int] = Query(None, description="Year (e.g., 2025)"),
    month_num: Optional[int] = Query(None, ge=1, le=12, description="Month number (1-12)")
):
    """Get tonnage data aggregated by borough for a specific month.
    
    Returns collected vs not collected tonnage for each borough.
    """
    try:
        db = Database.get_db()
        
        # Determine month filter
        start_date = None
        end_date = None
        
        if month:
            # Format: "2025-10"
            try:
                year, month_num = month.split('-')
                start_date = datetime(int(year), int(month_num), 1)
                # Last day of month
                if int(month_num) == 12:
                    end_date = datetime(int(year) + 1, 1, 1)
                else:
                    end_date = datetime(int(year), int(month_num) + 1, 1)
            except:
                raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
        elif year and month_num:
            start_date = datetime(year, month_num, 1)
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month_num + 1, 1)
        else:
            # Default to current month
            now = datetime.utcnow()
            start_date = datetime(now.year, now.month, 1)
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1)
            else:
                end_date = datetime(now.year, now.month + 1, 1)
        
        # Get all zones with borough info
        zones = {}
        for zone in db.zones.find({}):
            if 'borough' in zone:
                zones[zone['zone_id']] = zone['borough']
        
        # Aggregate tonnage by borough and status
        # First try to use borough field if it exists, otherwise use zone lookup
        pipeline = [
            {
                '$match': {
                    'collection_date': {
                        '$gte': start_date,
                        '$lt': end_date
                    },
                    'tonnage': {'$gt': 0}  # Only non-zero tonnage
                }
            },
            {
                '$addFields': {
                    'borough_field': {
                        '$ifNull': ['$borough', None]
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'borough': {
                            '$ifNull': ['$borough_field', '$zone_id']
                        },
                        'status': '$status'
                    },
                    'total_tonnage': {'$sum': '$tonnage'}
                }
            }
        ]
        
        results = list(db.collections.aggregate(pipeline))
        
        # Organize by borough
        borough_data = {}
        
        for result in results:
            borough_id = result['_id']['borough']
            status = result['_id']['status']
            tonnage = result['total_tonnage']
            
            # Get borough name - either from the field or lookup from zone
            if borough_id in zones.values():
                # Already a borough name
                borough = borough_id
            else:
                # It's a zone_id, look it up
                borough = zones.get(borough_id, 'Unknown')
            
            if borough not in borough_data:
                borough_data[borough] = {
                    'collected': 0.0,
                    'not_collected': 0.0,
                    'total': 0.0
                }
            
            # Categorize: completed = collected, missed/partial = not collected
            # Also handle cases where status might be None or other values
            if status == 'completed':
                borough_data[borough]['collected'] += tonnage
            elif status in ['missed', 'partial']:
                borough_data[borough]['not_collected'] += tonnage
            else:
                # Default: if status is unknown, count as collected (most tonnage data is completed)
                borough_data[borough]['collected'] += tonnage
            
            borough_data[borough]['total'] += tonnage
        
        # Convert to list format
        borough_list = []
        for borough, data in borough_data.items():
            borough_list.append({
                'borough': borough,
                'collected_tonnage': round(data['collected'], 2),
                'not_collected_tonnage': round(data['not_collected'], 2),
                'total_tonnage': round(data['total'], 2)
            })
        
        # Sort by total tonnage (descending)
        borough_list.sort(key=lambda x: x['total_tonnage'], reverse=True)
        
        # Get available months for dropdown
        months_pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$collection_date'},
                        'month': {'$month': '$collection_date'}
                    }
                }
            },
            {
                '$sort': {'_id.year': -1, '_id.month': -1}
            }
        ]
        
        available_months = []
        for month_doc in db.collections.aggregate(months_pipeline):
            year = month_doc['_id']['year']
            month = month_doc['_id']['month']
            available_months.append({
                'year': year,
                'month': month,
                'label': f"{year}-{month:02d}",
                'display': datetime(year, month, 1).strftime('%B %Y')
            })
        
        return {
            'month': start_date.strftime('%Y-%m'),
            'month_display': start_date.strftime('%B %Y'),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'by_borough': borough_list,
            'total_collected': round(sum(b['collected_tonnage'] for b in borough_list), 2),
            'total_not_collected': round(sum(b['not_collected_tonnage'] for b in borough_list), 2),
            'total_tonnage': round(sum(b['total_tonnage'] for b in borough_list), 2),
            'available_months': available_months,
            'count': len(borough_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tonnage by borough: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch tonnage data: {str(e)}")

@router.get("/trends")
async def get_tonnage_trends(
    months_back: int = Query(12, ge=3, le=24, description="Number of months of historical data"),
    months_ahead: int = Query(6, ge=1, le=12, description="Number of months to predict ahead")
):
    """Get tonnage trends over time with predictions - time series data.
    
    Returns historical tonnage by borough over time plus predicted future values.
    Perfect for line charts showing actual vs predicted trends.
    """
    try:
        db = Database.get_db()
        
        # Get all zones with borough info
        zones = {}
        for zone in db.zones.find({}):
            if 'borough' in zone:
                zones[zone['zone_id']] = zone['borough']
        
        # Calculate date range
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, 1) - timedelta(days=30 * months_back)
        end_date = datetime(now.year, now.month, 1)
        
        # Aggregate tonnage by borough and month
        pipeline = [
            {
                '$match': {
                    'collection_date': {
                        '$gte': start_date,
                        '$lt': end_date
                    },
                    'tonnage': {'$gt': 0},
                    'status': 'completed'  # Only collected tonnage for trends
                }
            },
            {
                '$addFields': {
                    'borough_field': {
                        '$ifNull': ['$borough', None]
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'borough': {
                            '$ifNull': ['$borough_field', '$zone_id']
                        },
                        'year': {'$year': '$collection_date'},
                        'month': {'$month': '$collection_date'}
                    },
                    'total_tonnage': {'$sum': '$tonnage'}
                }
            },
            {
                '$sort': {'_id.year': 1, '_id.month': 1}
            }
        ]
        
        results = list(db.collections.aggregate(pipeline))
        
        # Organize by borough and date
        borough_trends = defaultdict(lambda: defaultdict(float))
        borough_names = set()
        
        for result in results:
            borough_id = result['_id']['borough']
            year = result['_id']['year']
            month = result['_id']['month']
            tonnage = result['total_tonnage']
            
            # Get borough name
            if borough_id in zones.values():
                borough = borough_id
            else:
                borough = zones.get(borough_id, 'Unknown')
            
            if borough == 'Unknown':
                continue
                
            borough_names.add(borough)
            date_key = f"{year}-{month:02d}"
            borough_trends[borough][date_key] += tonnage
        
        # Convert to time series format
        # Get all unique months
        all_months = set()
        for borough_data in borough_trends.values():
            all_months.update(borough_data.keys())
        all_months = sorted(all_months)
        
        # Build time series data
        time_series = []
        for month_str in all_months:
            year, month = map(int, month_str.split('-'))
            month_date = datetime(year, month, 1)
            
            data_point = {
                'date': month_str,
                'year': year,
                'month': month,
                'display': month_date.strftime('%b %Y')
            }
            
            # Add actual tonnage for each borough
            for borough in sorted(borough_names):
                tonnage = borough_trends[borough].get(month_str, 0)
                data_point[f'{borough}_actual'] = round(tonnage / 1000, 2)  # Convert to thousands of tons
            
            time_series.append(data_point)
        
        # Generate predictions for future months
        predictions = []
        for i in range(1, months_ahead + 1):
            # Calculate future month
            future_month = now.month + i
            future_year = now.year
            while future_month > 12:
                future_month -= 12
                future_year += 1
            
            month_date = datetime(future_year, future_month, 1)
            month_str = f"{future_year}-{future_month:02d}"
            
            pred_point = {
                'date': month_str,
                'year': future_year,
                'month': future_month,
                'display': month_date.strftime('%b %Y'),
                'is_predicted': True
            }
            
            # Predict for each borough using simple trend
            for borough in sorted(borough_names):
                # Get last 3 months of actual data for trend
                recent_data = [ts.get(f'{borough}_actual', 0) for ts in time_series[-3:]]
                if len(recent_data) > 0 and sum(recent_data) > 0:
                    # Simple average of recent months
                    recent_avg = sum(recent_data) / len(recent_data)
                    # Apply small growth factor (1% per month)
                    predicted = recent_avg * (1.01 ** i)
                else:
                    predicted = 0
                
                pred_point[f'{borough}_predicted'] = round(predicted, 2)
                pred_point[f'{borough}_actual'] = None  # No actual data for future
            
            predictions.append(pred_point)
        
        # Combine actual and predicted
        combined_series = time_series + predictions
        
        # Calculate summary stats
        borough_stats = {}
        for borough in sorted(borough_names):
            actual_values = [ts.get(f'{borough}_actual', 0) for ts in time_series if ts.get(f'{borough}_actual', 0) > 0]
            if actual_values:
                borough_stats[borough] = {
                    'current': round(actual_values[-1], 2),
                    'average': round(sum(actual_values) / len(actual_values), 2),
                    'min': round(min(actual_values), 2),
                    'max': round(max(actual_values), 2),
                    'predicted_next': round(predictions[0].get(f'{borough}_predicted', 0), 2) if predictions else 0
                }
        
        return {
            'time_series': combined_series,
            'boroughs': sorted(borough_names),
            'actual_months': len(time_series),
            'predicted_months': len(predictions),
            'date_range': {
                'start': all_months[0] if all_months else None,
                'end': all_months[-1] if all_months else None,
                'predicted_end': predictions[-1]['date'] if predictions else None
            },
            'borough_stats': borough_stats,
            'data_source': 'Real DSNY monthly tonnage data with trend-based predictions'
        }
        
    except Exception as e:
        logger.error(f"Error fetching tonnage trends: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

