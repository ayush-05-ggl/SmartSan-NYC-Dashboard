import React, { useState, useEffect } from 'react'
import { fetchPredictedHotspots, fetchTonnageForecast, fetchRouteOptimization } from '../services/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts'
import './PredictionsPanel.css'

function PredictionsPanel({ selectedZone }) {
  const [hotspots, setHotspots] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [optimization, setOptimization] = useState(null)
  const [loading, setLoading] = useState(false)
  const [daysAhead, setDaysAhead] = useState(7)

  useEffect(() => {
    loadPredictions()
  }, [daysAhead, selectedZone])

  const loadPredictions = async () => {
    setLoading(true)
    try {
      const [hotspotsData, forecastData, optData] = await Promise.all([
        fetchPredictedHotspots(daysAhead),
        selectedZone ? fetchTonnageForecast(selectedZone, daysAhead) : null,
        selectedZone ? fetchRouteOptimization(selectedZone) : null
      ])
      
      setHotspots(hotspotsData)
      setForecast(forecastData)
      setOptimization(optData)
    } catch (err) {
      console.error('Error loading predictions:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="predictions-panel">Loading predictions...</div>
  }

  return (
    <div className="predictions-panel">
      <div className="predictions-header">
        <h2>🔮 Predictive Analytics</h2>
        <div className="prediction-controls">
          <label>Predict Next:</label>
          <select value={daysAhead} onChange={(e) => setDaysAhead(Number(e.target.value))}>
            <option value={3}>3 Days</option>
            <option value={7}>7 Days</option>
            <option value={14}>14 Days</option>
            <option value={30}>30 Days</option>
          </select>
          <button onClick={loadPredictions}>Refresh</button>
        </div>
      </div>

      <div className="predictions-grid">
        {/* Hotspot Predictions */}
        <div className="prediction-card">
          <h3>Predicted Problem Hotspots</h3>
          <p className="data-source">Based on real historical 311 request patterns</p>
          {hotspots && hotspots.predictions && (
            <>
              <div className="hotspots-list">
                {hotspots.predictions.slice(0, 5).map((spot, idx) => (
                  <div key={idx} className="hotspot-item">
                    <div className="hotspot-location">
                      📍 {spot.location.lat.toFixed(4)}, {spot.location.lng.toFixed(4)}
                    </div>
                    <div className="hotspot-stats">
                      <span className="predicted-count">{spot.predicted_requests} requests</span>
                      <span className="confidence">Confidence: {spot.confidence}%</span>
                    </div>
                  </div>
                ))}
              </div>
              {hotspots.predictions.length > 5 && (
                <div className="more-items">+{hotspots.predictions.length - 5} more hotspots</div>
              )}
            </>
          )}
        </div>

        {/* Tonnage Forecast */}
        {forecast && !forecast.error && (
          <div className="prediction-card">
            <h3>Tonnage Forecast - {forecast.zone_id}</h3>
            <p className="data-source">{forecast.data_source}</p>
            <div className="forecast-summary">
              <div className="forecast-total">
                <span className="label">Predicted Total:</span>
                <span className="value">{forecast.total_predicted_tonnage} tons</span>
              </div>
              <div className="forecast-confidence">
                <span className="label">Confidence:</span>
                <span className="value">{forecast.confidence.toFixed(1)}%</span>
              </div>
            </div>
            {forecast.predictions && (
              <div className="forecast-breakdown">
                {Object.entries(forecast.predictions).map(([type, data]) => (
                  <div key={type} className="forecast-item">
                    <span className="waste-type">{type}</span>
                    <span className="tonnage">{data.predicted_tonnage} tons</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Route Optimization */}
        {optimization && !optimization.error && (
          <div className="prediction-card">
            <h3>Route Optimization - {optimization.zone_id}</h3>
            <p className="data-source">{optimization.data_source}</p>
            <div className="optimization-stats">
              <div className="stat-row">
                <span>Current Avg Time:</span>
                <span>{optimization.current_avg_time_minutes} min</span>
              </div>
              <div className="stat-row highlight">
                <span>Optimized Time:</span>
                <span>{optimization.optimized_time_minutes} min</span>
              </div>
              <div className="stat-row savings">
                <span>Time Saved:</span>
                <span>{optimization.time_saved_minutes} min ({optimization.time_saved_percent}%)</span>
              </div>
              <div className="stat-row savings">
                <span>Fuel Saved:</span>
                <span>{optimization.fuel_saved_gallons} gallons/day</span>
              </div>
              <div className="stat-row savings">
                <span>Cost Saved:</span>
                <span>${optimization.cost_saved_per_day}/day</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictionsPanel

