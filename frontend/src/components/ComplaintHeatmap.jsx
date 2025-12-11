import React, { useState, useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { fetchComplaintHeatmap } from '../services/api'
import './ComplaintHeatmap.css'

// Fix for default marker icons
if (typeof window !== 'undefined') {
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  })
}

// NYC bounds
const NYC_CENTER = [40.7128, -73.9352]
const NYC_ZOOM = 11

// Color scale function (similar to weather map)
// Green (low) -> Yellow -> Orange -> Red (high)
function getColorForIntensity(intensity) {
  // intensity is 0-100
  if (intensity < 20) {
    // Green shades (low complaints)
    const ratio = intensity / 20
    return `rgb(${Math.round(34 + ratio * 100)}, ${Math.round(139 + ratio * 60)}, ${Math.round(34)})`
  } else if (intensity < 40) {
    // Yellow shades
    const ratio = (intensity - 20) / 20
    return `rgb(${Math.round(255 - ratio * 55)}, ${Math.round(255 - ratio * 15)}, ${Math.round(34 + ratio * 20)})`
  } else if (intensity < 60) {
    // Orange shades
    const ratio = (intensity - 40) / 20
    return `rgb(${Math.round(255 - ratio * 30)}, ${Math.round(140 + ratio * 60)}, ${Math.round(0)})`
  } else if (intensity < 80) {
    // Red shades
    const ratio = (intensity - 60) / 20
    return `rgb(${Math.round(255 - ratio * 30)}, ${Math.round(0)}, ${Math.round(0)})`
  } else {
    // Dark red (very high)
    const ratio = (intensity - 80) / 20
    return `rgb(${Math.round(139 - ratio * 39)}, ${Math.round(0)}, ${Math.round(0)})`
  }
}

function ComplaintHeatmap({ filters, complaintType }) {
  const [heatmapData, setHeatmapData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHeatmapData()
  }, [filters?.timeRange, filters?.borough, complaintType])

  const loadHeatmapData = async () => {
    try {
      setLoading(true)
      const days = filters?.timeRange === 'Last 24 hours' ? 1 :
                   filters?.timeRange === 'Last 7 days' ? 7 :
                   filters?.timeRange === 'Last 30 days' ? 30 : 365
      
      // Use larger grid size (0.02) to reduce clustering and create smoother visualization
      const data = await fetchComplaintHeatmap(0.02, days, complaintType, filters?.borough)
      setHeatmapData(data)
    } catch (error) {
      console.error('Error loading heatmap data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="complaint-heatmap">
        <div className="map-loading">Loading heatmap data...</div>
      </div>
    )
  }

  if (!heatmapData || !heatmapData.heatmap_data || heatmapData.heatmap_data.length === 0) {
    return (
      <div className="complaint-heatmap">
        <div className="no-data">No heatmap data available</div>
      </div>
    )
  }

  // Calculate map bounds from data
  const lats = heatmapData.heatmap_data.map(d => d.location.lat)
  const lngs = heatmapData.heatmap_data.map(d => d.location.lng)
  const center = [
    (Math.min(...lats) + Math.max(...lats)) / 2,
    (Math.min(...lngs) + Math.max(...lngs)) / 2
  ]

  return (
    <div className="complaint-heatmap">
      <div className="heatmap-header">
        <div className="heatmap-info">
          <span className="data-count">{heatmapData.count} locations</span>
          <span className="range-info">
            Range: {heatmapData.min_count} - {heatmapData.max_count} complaints
          </span>
        </div>
        <div className="color-legend">
          <span className="legend-label">Low</span>
          <div className="legend-gradient"></div>
          <span className="legend-label">High</span>
        </div>
      </div>
      
      <div className="map-container-heatmap">
        <MapContainer
          center={center.length === 2 && !isNaN(center[0]) ? center : NYC_CENTER}
          zoom={NYC_ZOOM}
          style={{ height: '100%', width: '100%', minHeight: '500px' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          {heatmapData.heatmap_data
            .filter(point => point.count >= 2) // Only show areas with at least 2 complaints to reduce clutter
            .map((point, index) => {
            const color = getColorForIntensity(point.intensity)
            // Use consistent radius with opacity based on intensity for smoother blending
            const radius = 15 + (point.intensity / 100) * 20 // 15-35px radius
            const opacity = 0.4 + (point.intensity / 100) * 0.4 // 0.4-0.8 opacity
            
            return (
              <CircleMarker
                key={index}
                center={[point.location.lat, point.location.lng]}
                radius={radius}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: opacity,
                  weight: 0, // No border for smoother blending
                  stroke: false
                }}
              >
                <Popup>
                  <div className="heatmap-popup">
                    <strong>Complaint Density</strong><br/>
                    <span className="popup-count">{point.count} complaints</span><br/>
                    {point.urgent_count > 0 && (
                      <span className="popup-urgent">{point.urgent_count} urgent</span>
                    )}
                    <br/>
                    <span className="popup-location">
                      {point.location.lat.toFixed(4)}, {point.location.lng.toFixed(4)}
                    </span>
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>
    </div>
  )
}

export default ComplaintHeatmap

