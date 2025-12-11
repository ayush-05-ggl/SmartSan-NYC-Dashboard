import React, { useState, useEffect } from 'react'
import { fetchComplaintTypeForecast, fetchOverflowRisk, fetchPredictedHotspots } from '../services/api'
import './PredictiveAnalyticsPanel.css'

function PredictiveAnalyticsPanel() {
  const [complaintForecast, setComplaintForecast] = useState(null)
  const [overflowRisk, setOverflowRisk] = useState(null)
  const [hotspots, setHotspots] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('complaints')

  useEffect(() => {
    loadPredictions()
  }, [])

  const loadPredictions = async () => {
    try {
      setLoading(true)
      const [forecast, risk, hotspotData] = await Promise.all([
        fetchComplaintTypeForecast(30),
        fetchOverflowRisk(7),
        fetchPredictedHotspots(7)
      ])
      setComplaintForecast(forecast)
      setOverflowRisk(risk)
      setHotspots(hotspotData)
    } catch (error) {
      console.error('Error loading predictions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="predictive-panel">
        <h3>Predictive Analytics</h3>
        <div className="loading">Loading predictions...</div>
      </div>
    )
  }

  return (
    <div className="predictive-panel">
      <div className="panel-header">
        <h3>Predictive Analytics</h3>
        <div className="tabs">
          <button 
            className={activeTab === 'complaints' ? 'active' : ''}
            onClick={() => setActiveTab('complaints')}
          >
            Complaint Forecast
          </button>
          <button 
            className={activeTab === 'overflow' ? 'active' : ''}
            onClick={() => setActiveTab('overflow')}
          >
            Overflow Risk
          </button>
          <button 
            className={activeTab === 'hotspots' ? 'active' : ''}
            onClick={() => setActiveTab('hotspots')}
          >
            Hotspots
          </button>
        </div>
      </div>

      <div className="panel-content">
        {activeTab === 'complaints' && complaintForecast && (
          <div className="forecast-section">
            <div className="forecast-header">
              <span className="forecast-period">
                {complaintForecast.current_month} → {complaintForecast.target_month}
              </span>
            </div>
            <div className="forecast-list">
              {complaintForecast.predictions.slice(0, 8).map((pred, idx) => (
                <div key={idx} className="forecast-item">
                  <div className="forecast-type">
                    <span className="type-name">{pred.complaint_type.replace('_', ' ')}</span>
                    <span className={`trend-badge ${pred.trend}`}>
                      {pred.trend === 'increasing' ? '↑' : pred.trend === 'decreasing' ? '↓' : '→'}
                    </span>
                  </div>
                  <div className="forecast-stats">
                    <span className="predicted-count">{pred.predicted_count}</span>
                    <span className="confidence">Confidence: {Math.round(pred.confidence)}%</span>
                  </div>
                  {pred.seasonal_factor > 1.2 && (
                    <div className="seasonal-note">
                      Seasonal spike expected (factor: {pred.seasonal_factor}x)
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'overflow' && overflowRisk && (
          <div className="risk-section">
            <div className="risk-list">
              {overflowRisk.risk_zones.slice(0, 8).map((zone, idx) => (
                <div key={idx} className={`risk-item ${zone.risk_level}`}>
                  <div className="risk-header">
                    <span className="zone-id">{zone.zone_id}</span>
                    <span className={`risk-score ${zone.risk_level}`}>
                      {zone.risk_score}% risk
                    </span>
                  </div>
                  <div className="risk-details">
                    <span>Overflow complaints (90d): {zone.overflow_count_90d}</span>
                    <span>Collections (7d): {zone.recent_collections_7d}</span>
                  </div>
                  <div className="risk-recommendation">
                    {zone.recommendation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'hotspots' && hotspots && (
          <div className="hotspots-section">
            <div className="hotspots-list">
              {hotspots.predictions.slice(0, 8).map((spot, idx) => (
                <div key={idx} className="hotspot-item">
                  <div className="hotspot-header">
                    <span className="hotspot-location">
                      {spot.location.lat.toFixed(3)}, {spot.location.lng.toFixed(3)}
                    </span>
                    <span className="hotspot-confidence">
                      {spot.confidence}% confidence
                    </span>
                  </div>
                  <div className="hotspot-prediction">
                    Predicted: {spot.predicted_requests} requests in next {spot.days_ahead} days
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictiveAnalyticsPanel

