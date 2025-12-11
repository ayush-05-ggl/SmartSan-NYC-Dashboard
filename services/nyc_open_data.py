"""NYC Open Data API client for live data integration."""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NYCOpenDataClient:
    """Client for NYC Open Data SODA API."""
    
    BASE_URL = "https://data.cityofnewyork.us/resource"
    
    # Dataset resource IDs
    DATASETS = {
        '311': 'erm2-nwe9',  # NYC 311 Service Requests from 2010 to Present (DAILY UPDATING)
        '311_old': 'jrb2-thup',  # Old 311 dataset (deprecated)
        'dsny_tonnage': 'ebb7-mvp5',  # DSNY Monthly Tonnage
        'recycling_bins': 'sxx4-xhzg',  # Public Recycling Bins
    }
    
    def __init__(self, app_token: Optional[str] = None):
        """Initialize client.
        
        Args:
            app_token: NYC Open Data app token (optional but recommended)
        """
        self.app_token = app_token
        self.session = requests.Session()
        if app_token:
            self.session.headers.update({'X-App-Token': app_token})
    
    def get_311_requests(self, 
                       agency: str = 'DSNY',
                       days_back: int = 30,
                       limit: int = 5000,
                       offset: int = 0) -> List[Dict]:
        """Get 311 service requests from NYC Open Data API.
        
        Args:
            agency: Agency filter (default: DSNY)
            days_back: Number of days to look back
            limit: Maximum records to return
            offset: Offset for pagination
            
        Returns:
            List of request dictionaries
        """
        try:
            dataset_id = self.DATASETS['311']
            url = f"{self.BASE_URL}/{dataset_id}.json"
            
            # Filter for DSNY/Sanitation
            # Try to get recent data first (2024-2025)
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%S')
            
            # First try to get recent data
            params = {
                '$where': f"agency_name = 'Department of Sanitation' AND created_date >= '{cutoff_date}'",
                '$limit': limit,
                '$offset': offset,
                '$order': 'created_date DESC'
            }
            
            # If no recent data, fall back to all DSNY records
            # (This handles the case where DSNY data in 311 is older)
            
            logger.info(f"Fetching 311 requests from NYC Open Data API...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data)} 311 requests from API")
            
            # Add metadata
            for record in data:
                record['_data_source'] = 'NYC Open Data - 311 Service Requests'
                record['_fetched_at'] = datetime.utcnow().isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching 311 data: {e}")
            raise
    
    def get_dsny_tonnage(self,
                         months_back: int = 12,
                         limit: int = 1000) -> List[Dict]:
        """Get DSNY monthly tonnage data.
        
        Args:
            months_back: Number of months to retrieve
            limit: Maximum records
            
        Returns:
            List of tonnage records
        """
        try:
            dataset_id = self.DATASETS['dsny_tonnage']
            url = f"{self.BASE_URL}/{dataset_id}.json"
            
            # DSNY tonnage uses format "YYYY / MM" - get recent months
            # Just get the most recent records (they're already sorted by month DESC)
            params = {
                '$limit': limit,
                '$order': 'month DESC'
            }
            
            logger.info(f"Fetching DSNY tonnage from NYC Open Data API...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data)} tonnage records from API")
            
            # Add metadata
            for record in data:
                record['_data_source'] = 'NYC Open Data - DSNY Monthly Tonnage'
                record['_fetched_at'] = datetime.utcnow().isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching tonnage data: {e}")
            raise
    
    def get_recycling_bins(self, limit: int = 1000) -> List[Dict]:
        """Get public recycling bin locations.
        
        Returns:
            List of recycling bin records with coordinates
        """
        try:
            dataset_id = self.DATASETS['recycling_bins']
            url = f"{self.BASE_URL}/{dataset_id}.json"
            
            params = {
                '$limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for record in data:
                record['_data_source'] = 'NYC Open Data - Public Recycling Bins'
                record['_fetched_at'] = datetime.utcnow().isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching recycling bins: {e}")
            raise

