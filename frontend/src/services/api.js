import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API service functions
export const fetchDashboardMetrics = async (days = 7) => {
  const response = await api.get(`/api/metrics/dashboard?days=${days}`)
  return response.data
}

export const fetchTodayCollections = async () => {
  const response = await api.get('/api/collections/today')
  return response.data
}

export const fetchUrgentRequests = async () => {
  const response = await api.get('/api/requests/urgent')
  return response.data
}

export const fetchZones = async (params = {}) => {
  const response = await api.get('/api/zones', { params })
  return response.data
}

export const fetchZoneStats = async (zoneId) => {
  const response = await api.get(`/api/zones/${zoneId}/stats`)
  return response.data
}

export const fetchBoroughs = async () => {
  const response = await api.get('/api/zones/boroughs')
  return response.data
}

export const fetchCollections = async (params = {}) => {
  const response = await api.get('/api/collections', { params })
  return response.data
}

export const fetchCollectionSummary = async (days = 7) => {
  const response = await api.get(`/api/collections/summary?days=${days}`)
  return response.data
}

export const fetchActiveRoutes = async () => {
  const response = await api.get('/api/routes/active')
  return response.data
}

export const fetchAvailableVehicles = async () => {
  const response = await api.get('/api/vehicles/available')
  return response.data
}

export const fetchRequestsByTypeOld = async () => {
  const response = await api.get('/api/requests/by-type')
  return response.data
}

// Predictive Analytics
export const fetchPredictedHotspots = async (daysAhead = 7) => {
  const response = await api.get(`/api/predictions/hotspots?days_ahead=${daysAhead}`)
  return response.data
}

export const fetchTonnageForecast = async (zoneId, days = 7) => {
  const response = await api.get(`/api/predictions/tonnage-forecast?zone_id=${zoneId}&days=${days}`)
  return response.data
}

export const fetchRouteOptimization = async (zoneId) => {
  const response = await api.get(`/api/predictions/route-optimization?zone_id=${zoneId}`)
  return response.data
}

export const fetchComplaintTypeForecast = async (daysAhead = 30) => {
  const response = await api.get(`/api/predictions/complaint-types?days_ahead=${daysAhead}`)
  return response.data
}

export const fetchOverflowRisk = async (daysAhead = 7) => {
  const response = await api.get(`/api/predictions/overflow-risk?days_ahead=${daysAhead}`)
  return response.data
}

export const fetchBoroughComplaintPredictions = async (daysAhead = 30) => {
  const response = await api.get(`/api/predictions/borough-complaints?days_ahead=${daysAhead}`)
  return response.data
}

// Geospatial
export const fetchRequestsNearby = async (lat, lng, radiusMeters = 1000) => {
  const response = await api.get(`/api/geo/requests/nearby?lat=${lat}&lng=${lng}&radius_meters=${radiusMeters}`)
  return response.data
}

export const fetchRequestHotspots = async (days = 30) => {
  const response = await api.get(`/api/geo/requests/hotspots?days=${days}`)
  return response.data
}

export const fetchComplaintHeatmap = async (gridSize = 0.01, days = 30, complaintType = null, borough = null) => {
  const params = { grid_size: gridSize, days }
  if (complaintType) params.complaint_type = complaintType
  if (borough && borough !== 'All') params.borough = borough
  const response = await api.get('/api/geo/requests/heatmap', { params })
  return response.data
}

export const fetchTonnageByBorough = async (month = null) => {
  const params = {}
  if (month) params.month = month
  const response = await api.get('/api/tonnage/by-borough', { params })
  return response.data
}

export const fetchTonnageTrends = async (monthsBack = 12, monthsAhead = 6) => {
  const response = await api.get(`/api/tonnage/trends?months_back=${monthsBack}&months_ahead=${monthsAhead}`)
  return response.data
}

// Data Management
export const refresh311Data = async () => {
  const response = await api.post('/api/data/refresh-311')
  return response.data
}

export const fetchDataSources = async () => {
  const response = await api.get('/api/data/data-sources')
  return response.data
}

// Complaint filtering
export const fetchComplaintTypes = async () => {
  const response = await api.get('/api/complaints/types')
  return response.data
}

export const fetchRequestsByType = async (complaintType, params = {}) => {
  const response = await api.get(`/api/complaints/by-type/${complaintType}`, { params })
  return response.data
}

export const fetchComplaintsByBorough = async (complaintType = null) => {
  const params = complaintType ? { complaint_type: complaintType } : {}
  const response = await api.get('/api/complaints/by-borough', { params })
  return response.data
}

export const fetchComplaintStats = async (days = 30) => {
  const response = await api.get(`/api/complaints/stats?days=${days}`)
  return response.data
}

export default api

