"""Main FastAPI application for Smart City Dashboard - NYC Sanitation Backend."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from database import Database
from config import config
import logging
from datetime import datetime

# Import routers
from routes import zones, routes, collections, requests, metrics, vehicles, geospatial, predictions, data_refresh, tonnage_refresh, complaints, tonnage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Create and configure FastAPI app."""
    cfg = config[config_name]()
    
    # Create FastAPI app
    app = FastAPI(
        title="NYC Department of Sanitation API",
        description="Backend API for Smart City Dashboard - Sanitation Management",
        version="1.0.0",
        docs_url="/docs",  # Swagger UI at /docs
        redoc_url="/redoc"  # ReDoc at /redoc
    )
    
    # Initialize rate limiter
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Connect to database
    try:
        Database.connect(config_name)
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # Don't fail startup, but log the error
    
    # Include routers
    app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
    app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])
    app.include_router(collections.router, prefix="/api/collections", tags=["Collections"])
    app.include_router(requests.router, prefix="/api/requests", tags=["Service Requests"])
    app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
    app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
    app.include_router(geospatial.router, prefix="/api/geo", tags=["Geospatial"])
    app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
    app.include_router(data_refresh.router, prefix="/api/data", tags=["Data Management"])
    app.include_router(tonnage_refresh.router, prefix="/api/data", tags=["Data Management"])
    app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
    app.include_router(tonnage.router, prefix="/api/tonnage", tags=["Tonnage Analytics"])
    
    # Health check endpoint
    @app.get("/api/health", tags=["Health"])
    async def health_check():
        """Health check endpoint to verify API and database connectivity."""
        try:
            db = Database.get_db()
            # Test connection by doing a simple query
            db.zones.count_documents({})
            return {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    'status': 'unhealthy',
                    'database': 'disconnected',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
    
    # Root API info endpoint
    @app.get("/api", tags=["Info"])
    async def api_info():
        """API information and available endpoints."""
        return {
            'name': 'NYC Department of Sanitation API',
            'version': '1.0.0',
            'description': 'Backend API for Smart City Dashboard - Sanitation Management',
            'docs': '/docs',
            'endpoints': {
                'zones': '/api/zones',
                'routes': '/api/routes',
                'collections': '/api/collections',
                'requests': '/api/requests',
                'metrics': '/api/metrics',
                'vehicles': '/api/vehicles'
            }
        }
    
    # Root endpoint
    @app.get("/", tags=["Info"])
    async def root():
        """Root endpoint - redirects to API info."""
        return {
            'message': 'NYC Department of Sanitation API',
            'docs': '/docs',
            'api': '/api'
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
