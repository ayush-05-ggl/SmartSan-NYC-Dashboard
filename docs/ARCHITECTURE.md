# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                  (React Frontend - Port 5173)                │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Dashboard  │  │  Heatmaps   │  │   Charts    │        │
│  │  Components │  │   & Maps    │  │  & Graphs   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                 │               │
│         └────────────────┼─────────────────┘               │
│                          │                                 │
│                  ┌───────▼────────┐                        │
│                  │  API Client    │                        │
│                  │   (api.js)     │                        │
│                  └───────┬───────┘                        │
└──────────────────────────┼─────────────────────────────────┘
                           │ HTTP/REST API
┌──────────────────────────▼─────────────────────────────────┐
│              Application Layer (FastAPI - Port 8000)        │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              API Routes (REST Endpoints)           │   │
│  │  • /api/zones          • /api/collections          │   │
│  │  • /api/requests       • /api/complaints           │   │
│  │  • /api/tonnage        • /api/geo/*                │   │
│  │  • /api/predictions    • /api/metrics              │   │
│  │  • /api/data/refresh-*                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Business Logic Services                │   │
│  │  • PredictionService    • NYCOpenDataClient        │   │
│  │  • Data transformation  • Analytics algorithms     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Data Models (Pydantic)                 │   │
│  │  • SanitationZone    • CollectionEvent             │   │
│  │  • ServiceRequest    • PerformanceMetric            │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│              Data Access Layer                              │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Database Connection (MongoDB)               │   │
│  │  • Connection pooling                              │   │
│  │  • Error handling                                  │   │
│  │  • SSL/TLS support                                 │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│              Data Storage (MongoDB Atlas)                  │
│                                                             │
│  Collections:                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    zones     │  │ collections  │  │   requests   │   │
│  │  (districts) │  │  (tonnage)   │  │  (311 data)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    routes    │  │   vehicles   │  │   metrics    │   │
│  │  (schedules) │  │   (fleet)    │  │  (cached)    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
│  Indexes:                                                   │
│  • Geospatial (2dsphere) on location.coordinates          │
│  • Compound indexes on zone_id + collection_date           │
│  • Text indexes on complaint_type, descriptor              │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│              External Data Sources                          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         NYC Open Data SODA API                      │   │
│  │  • 311 Service Requests (daily updates)             │   │
│  │  • DSNY Monthly Tonnage                             │   │
│  │  • Public Recycling Bins                            │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow
```
NYC Open Data API
    ↓
NYCOpenDataClient (services/nyc_open_data.py)
    ↓
Data Transformation
    ↓
MongoDB Collections
    ↓
API Endpoints
    ↓
Frontend Components
```

### 2. User Request Flow
```
User Interaction (Frontend)
    ↓
API Call (api.js)
    ↓
FastAPI Route Handler
    ↓
Service Layer (Business Logic)
    ↓
Database Query (MongoDB)
    ↓
Response Processing
    ↓
JSON Response
    ↓
Frontend Update
```

### 3. Predictive Analytics Flow
```
Historical Data (MongoDB)
    ↓
PredictionService (services/predictions.py)
    ↓
Time-Series Analysis
    ↓
Linear Regression
    ↓
Forecast Generation
    ↓
API Response
    ↓
Visualization (Frontend)
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.14)
- **Database**: MongoDB Atlas (Cloud)
- **API Client**: Requests library
- **Data Validation**: Pydantic models
- **Rate Limiting**: SlowAPI

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Maps**: Leaflet / React-Leaflet
- **Charts**: Recharts
- **HTTP Client**: Axios

### Infrastructure
- **Database**: MongoDB Atlas (Free Tier - 512MB)
- **API Hosting**: Local development (deployable to Heroku/Railway)
- **Frontend Hosting**: Local development (deployable to Vercel/Netlify)

## Key Design Decisions

1. **MongoDB for Geospatial**: Native support for location queries
2. **FastAPI for Performance**: Async support, automatic docs
3. **React for Interactivity**: Component-based, state management
4. **Real-time Data**: Daily refresh from NYC Open Data
5. **Predictive Models**: Time-series analysis for forecasting

## Security Considerations

- Environment variables for sensitive data
- CORS configuration for frontend access
- Rate limiting on API endpoints
- Input validation with Pydantic
- SSL/TLS for MongoDB connection

## Scalability

- Database indexes for query optimization
- Aggregation pipelines for efficient data processing
- Caching strategies for frequently accessed data
- Batch processing for data refresh
- Pagination support for large datasets

