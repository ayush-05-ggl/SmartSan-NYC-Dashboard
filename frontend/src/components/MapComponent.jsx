import React from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in react-leaflet (required for react-leaflet v4)
if (typeof window !== 'undefined') {
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  })
}

function MapComponent({ hotspots, onMarkerClick, showWaste = true, showAirQuality = false }) {
  // Default center: NYC (Manhattan)
  const defaultCenter = [40.7128, -73.9352]
  const defaultZoom = 11

  // Calculate map bounds from hotspots
  let mapCenter = defaultCenter
  let mapZoom = defaultZoom
  
  if (hotspots && hotspots.length > 0) {
    const lats = hotspots.map(s => s.location.lat)
    const lngs = hotspots.map(s => s.location.lng)
    mapCenter = [
      (Math.min(...lats) + Math.max(...lats)) / 2,
      (Math.min(...lngs) + Math.max(...lngs)) / 2
    ]
  }

  return (
    <MapContainer
      center={mapCenter}
      zoom={mapZoom}
      style={{ height: '100%', width: '100%', minHeight: '400px' }}
      scrollWheelZoom={true}
    >
      {/* Dark theme tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      {showWaste && hotspots.map((spot, index) => (
        <CircleMarker
          key={index}
          center={[spot.location.lat, spot.location.lng]}
          radius={Math.min(spot.request_count * 2, 20)}
          pathOptions={{
            color: spot.urgent_count > 0 ? '#ef4444' : '#ef4444',
            fillColor: spot.urgent_count > 0 ? '#ef4444' : '#ef4444',
            fillOpacity: 0.6,
            weight: 2
          }}
          eventHandlers={{
            click: () => onMarkerClick && onMarkerClick(spot)
          }}
        >
          <Popup>
            <div style={{ minWidth: '200px', color: '#1a1a2e' }}>
              <strong>📍 Location:</strong><br/>
              {spot.location?.address || `${spot.location.lat.toFixed(4)}, ${spot.location.lng.toFixed(4)}`}<br/>
              {spot.location?.borough && <><strong>Borough:</strong> {spot.location.borough}<br/></>}
              <br/>
              <strong>Requests:</strong> {spot.request_count}<br/>
              <strong>Urgent:</strong> {spot.urgent_count}<br/>
              <strong>Types:</strong> {spot.request_types?.map(t => t.replace('_', ' ')).join(', ') || 'N/A'}
            </div>
          </Popup>
        </CircleMarker>
      ))}
      
      {/* AQI halos (orange circles) - placeholder for air quality layer */}
      {showAirQuality && hotspots.slice(0, 5).map((spot, index) => (
        <CircleMarker
          key={`aqi-${index}`}
          center={[spot.location.lat + 0.001, spot.location.lng + 0.001]}
          radius={30}
          pathOptions={{
            color: '#f59e0b',
            fillColor: '#f59e0b',
            fillOpacity: 0.2,
            weight: 1,
            dashArray: '5, 5'
          }}
        />
      ))}
    </MapContainer>
  )
}

export default MapComponent

