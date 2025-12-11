import React, { useState, useEffect } from 'react'
import { fetchRequestHotspots, fetchRequestsNearby } from '../services/api'
import './MapVisualization.css'

// Lazy load Leaflet to avoid SSR issues
const MapComponent = React.lazy(() => import('./MapComponent'))

function MapVisualization({ filters }) {
  const [hotspots, setHotspots] = useState(null)
  const [selectedPoint, setSelectedPoint] = useState(null)
  const [nearbyRequests, setNearbyRequests] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadHotspots()
  }, [filters?.timeRange, filters?.borough])

  const loadHotspots = async () => {
    setLoading(true)
    try {
      const days = filters?.timeRange === 'Last 24 hours' ? 1 :
                   filters?.timeRange === 'Last 7 days' ? 7 :
                   filters?.timeRange === 'Last 30 days' ? 30 : 365
      const data = await fetchRequestHotspots(days)
      
      // Filter by borough if specified
      if (data?.hotspots && filters?.borough && filters.borough !== 'All') {
        data.hotspots = data.hotspots.filter(spot => 
          spot.location?.borough && 
          spot.location.borough.toLowerCase() === filters.borough.toLowerCase()
        )
      }
      
      setHotspots(data)
    } catch (err) {
      console.error('Error loading hotspots:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkerClick = async (spot) => {
    setSelectedPoint(spot)
    try {
      const data = await fetchRequestsNearby(spot.location.lat, spot.location.lng, 500)
      setNearbyRequests(data)
    } catch (err) {
      console.error('Error loading nearby requests:', err)
    }
  }

  if (loading) {
    return <div className="map-loading">Loading map data...</div>
  }

  return (
    <div className="map-visualization-new">
      <div className="map-container-new">
        {hotspots?.hotspots && hotspots.hotspots.length > 0 ? (
          <React.Suspense fallback={<div className="map-loading">Loading map...</div>}>
            <MapComponent 
              hotspots={hotspots.hotspots}
              onMarkerClick={handleMarkerClick}
              showWaste={filters?.layers?.waste}
              showAirQuality={filters?.layers?.airQuality}
            />
          </React.Suspense>
        ) : (
          <div className="no-map-data">No hotspot data available</div>
        )}
      </div>
      
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-marker red"></span>
          <span>Waste hotspot</span>
        </div>
        <div className="legend-item">
          <span className="legend-marker orange"></span>
          <span>AQI halo</span>
        </div>
      </div>
    </div>
  )
}

export default MapVisualization
