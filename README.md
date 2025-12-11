# SmartSan NYC - Smart Sanitation Dashboard

A comprehensive data-driven dashboard for NYC Department of Sanitation, providing real-time insights, predictive analytics, and operational visibility into waste collection and sanitation services.

![Dashboard](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![React](https://img.shields.io/badge/React-18-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)

## 🎯 Overview

SmartSan NYC integrates **real-time data** from NYC Open Data APIs to provide:
- **Live Data Integration**: Real-time 311 service requests and DSNY tonnage data (no seed/synthetic data)
- **Predictive Analytics**: Borough-wise complaint forecasting and hotspot prediction
- **Interactive Visualizations**: Weather-map style heatmaps, charts, and geospatial maps
- **Operational Insights**: Collection efficiency, complaint tracking, and resource optimization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │   Heatmaps   │  │   Charts     │         │
│  │  Components  │  │   & Maps     │  │   & Graphs   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼────────┐                            │
│                    │   API Service │                            │
│                    │   (api.js)    │                            │
│                    └───────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Routes     │  │   Services   │  │   Models     │         │
│  │  - Zones     │  │  - Predictions│  │  - Sanitation│         │
│  │  - Collections│ │  - NYC Data   │  │  - Requests │         │
│  │  - Requests  │  │               │  │  - Metrics  │         │
│  │  - Tonnage   │  │               │  │             │         │
│  │  - Geo       │  │               │  │             │         │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼────────┐                            │
│                    │   Database     │                            │
│                    │   Connection   │                            │
│                    └───────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              MongoDB Atlas (Cloud Database)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Collections│  │   Requests   │  │   Zones      │         │
│  │   (Tonnage)  │  │   (311 Data) │  │   (Districts)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │         Geospatial Indexes (2dsphere)               │      │
│  │  - location.coordinates for proximity queries        │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              External Data Sources                                │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  NYC Open Data SODA API                               │      │
│  │  - 311 Service Requests (erm2-nwe9)                   │      │
│  │  - DSNY Monthly Tonnage (ebb7-mvp5)                   │      │
│  │  - Public Recycling Bins (sxx4-xhzg)                 │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
SmartCityDashboard/
├── app.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # MongoDB connection handler
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
│
├── models/                # Data models
│   └── sanitation.py     # Pydantic models for collections, requests, zones
│
├── routes/                # API endpoints
│   ├── zones.py          # Zone management
│   ├── collections.py    # Collection events
│   ├── requests.py       # Service requests
│   ├── complaints.py     # Complaint analytics
│   ├── tonnage.py        # Tonnage analytics
│   ├── geospatial.py     # Location-based queries
│   ├── predictions.py    # Predictive analytics
│   ├── metrics.py        # Dashboard metrics
│   └── data_refresh.py   # Data refresh endpoints
│
├── services/              # Business logic
│   ├── nyc_open_data.py  # NYC Open Data API client
│   └── predictions.py    # Prediction algorithms
│
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ComplaintHeatmap.jsx
│   │   │   ├── TonnageByBorough.jsx
│   │   │   └── ...
│   │   └── services/
│   │       └── api.js    # API client
│   └── package.json
│
├── scripts/               # Utility scripts
│   ├── import_tonnage_csv.py
│   ├── setup_geospatial_indexes.py
│   └── ...
│
├── tests/                 # Test files
│   └── test_api.py
│
└── docs/                  # Documentation
    └── PRESENTATION_NARRATION.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Node.js 18+
- MongoDB Atlas account (free tier works)

### Backend Setup

1. **Clone and navigate to project:**
```bash
cd SmartCityDashboard
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
Create a `.env` file with your MongoDB connection string:
```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=citydata
CORS_ORIGINS=http://localhost:5173
```

5. **Set up geospatial indexes:**
```bash
python scripts/setup_geospatial_indexes.py
```

6. **Refresh data from NYC Open Data:**
```bash
# Refresh 311 service requests
curl -X POST http://localhost:8000/api/data/refresh-311?limit=2000

# Refresh tonnage data
curl -X POST http://localhost:8000/api/data/refresh-tonnage
```

7. **Run the backend:**
```bash
uvicorn app:app --reload
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run development server:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📊 Key Features

### 1. Real-time Data Integration
- Automatic daily refresh from NYC Open Data API
- Manual refresh button in dashboard header
- Handles 2,000+ records per refresh

### 2. Complaint Density Heatmap
- Weather-map style visualization
- Color-coded by complaint intensity (green → red)
- Interactive markers with detailed popups
- Filterable by borough and time range

### 3. Predictive Analytics
- Borough-wise complaint forecasting (30-day predictions)
- Hotspot identification
- Overflow risk assessment
- Confidence scoring for predictions

### 4. Tonnage Analysis
- Multiple bar chart by borough
- Collected vs Not Collected comparison
- Month selector for historical analysis
- Summary statistics

### 5. Geospatial Queries
- Find complaints near a location
- Hotspot detection
- Bounding box queries
- Uses MongoDB 2dsphere indexes

## 🔌 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/metrics/dashboard` - Dashboard metrics
- `GET /api/zones` - Zone management
- `GET /api/collections` - Collection events
- `GET /api/requests` - Service requests

### Analytics Endpoints
- `GET /api/complaints/types` - Complaint type breakdown
- `GET /api/complaints/by-borough` - Borough aggregation
- `GET /api/tonnage/by-borough` - Tonnage by borough
- `GET /api/predictions/borough-complaints` - Complaint forecasts

### Geospatial Endpoints
- `GET /api/geo/requests/nearby` - Find nearby requests
- `GET /api/geo/requests/heatmap` - Heatmap data
- `GET /api/geo/requests/hotspots` - Complaint hotspots

### Data Management
- `POST /api/data/refresh-311` - Refresh 311 data
- `POST /api/data/refresh-tonnage` - Refresh tonnage data

Full API documentation: `http://localhost:8000/docs`

## 🗄️ Database Schema

### Collections
- **zones**: Sanitation districts with borough, population, collection schedules
- **collections**: Waste collection events with tonnage, status, dates
- **requests**: 311 service requests with location, type, priority, status
- **routes**: Collection routes with zones and schedules
- **vehicles**: Fleet management
- **metrics**: Performance metrics (cached)

### Geospatial Indexes
```javascript
db.requests.createIndex({ "location.coordinates": "2dsphere" })
```

## 🔧 Configuration

Key environment variables (`.env`):
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=citydata
CORS_ORIGINS=http://localhost:5173
```

## 📈 Data Sources

All data is fetched live from NYC Open Data APIs:

- **311 Service Requests**: `https://data.cityofnewyork.us/resource/erm2-nwe9.json`
  - Daily updating dataset with DSNY-related complaints
  - Includes location, complaint type, status, dates
  - Filtered for Department of Sanitation agency

- **DSNY Monthly Tonnage**: `https://data.cityofnewyork.us/resource/ebb7-mvp5.json`
  - Monthly collection tonnage by borough and district
  - Includes collected and uncollected waste
  - Historical data for trend analysis

- **Public Recycling Bins**: `https://data.cityofnewyork.us/resource/sxx4-xhzg.json`
  - Location data for public recycling infrastructure

**Note**: The dashboard uses **real data only** - no seed or synthetic data. Use the refresh endpoints to pull the latest data from NYC Open Data.

## 🧪 Testing

```bash
# Backend tests
python -m pytest tests/

# API testing
curl http://localhost:8000/api/health
```

## 🚢 Deployment

### Backend
- Deploy to Heroku, Railway, or AWS
- Set environment variables
- MongoDB Atlas connection string required

### Frontend
- Build: `npm run build`
- Deploy to Vercel, Netlify, or static hosting
- Update API URL in `api.js`

## 👥 Team Roles

- **Project Manager**: Project coordination, documentation, presentation
- **Data Engineer**: Data pipeline, database design, ETL processes
- **Backend Developer**: FastAPI development, API endpoints, geospatial queries
- **Frontend Developer**: React dashboard, visualizations, UI/UX
- **Data Analyst**: Predictive models, analytics, insights
- **Product Designer**: User research, information architecture, design

## 📝 License

This project is developed for educational/hackathon purposes.

## 🙏 Acknowledgments

- NYC Open Data for providing public APIs
- MongoDB Atlas for free tier database hosting
- FastAPI and React communities for excellent documentation

---

**Built with ❤️ for NYC Department of Sanitation**
