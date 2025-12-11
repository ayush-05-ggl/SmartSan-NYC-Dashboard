# Smart City Dashboard - Frontend

React frontend for the NYC Department of Sanitation Smart City Dashboard.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Build for Production

```bash
npm run build
```

## 🎨 Features

- **Real-time Dashboard**: Live data from FastAPI backend
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Visualizations using Recharts
- **Persona-Specific Views**: Tailored for NYC Sanitation Department

## 📊 Components

- **StatsOverview**: High-level KPIs and metrics
- **TodayCollections**: Today's collection operations
- **UrgentRequests**: High-priority service requests
- **CollectionSummary**: Aggregated collection data with charts
- **BoroughBreakdown**: NYC borough statistics

## 🔧 Configuration

The frontend connects to the backend API. To change the API URL:

1. Create `.env` file in `frontend/` directory:
```
VITE_API_URL=http://localhost:8000
```

2. Or modify `src/services/api.js` directly

## 🎯 Customization

All components are modular and easy to customize:

- **Colors**: Modify CSS variables in component CSS files
- **Layout**: Adjust grid layouts in `Dashboard.css`
- **Charts**: Customize Recharts components
- **Styling**: Match your Figma design by updating CSS

## 📱 Responsive Design

The dashboard is fully responsive:
- Desktop: Full grid layout
- Tablet: Adjusted grid columns
- Mobile: Single column layout

## 🔗 API Integration

The frontend uses these backend endpoints:
- `/api/metrics/dashboard` - Dashboard overview
- `/api/collections/today` - Today's collections
- `/api/requests/urgent` - Urgent requests
- `/api/collections/summary` - Collection summary
- `/api/zones/boroughs` - Borough data

## 🎨 Matching Your Figma Design

To match your Figma design:

1. **Colors**: Update color values in component CSS files
2. **Typography**: Modify font families and sizes
3. **Layout**: Adjust grid and spacing in `Dashboard.css`
4. **Components**: Add/remove components as needed
5. **Icons**: Replace emoji icons with your icon library

All components are in `src/components/` and can be easily modified!

