import React from 'react'
import './KeyMetrics.css'

function KeyMetrics({ data }) {
  if (!data) {
    return (
      <div className="key-metrics">
        <div className="metric-card">Loading...</div>
      </div>
    )
  }

  // Calculate metrics from dashboard data
  // Missed pickups = actual missed collection events (not just complaints)
  const missedPickups = data.overview?.today_missed_collections || 0
  const overflowRisk = data.overview?.total_collections ? 
    Math.round(data.overview.total_collections * 0.15) : 0
  const avgAQI = 62 // Placeholder - would come from AQI data
  const totalComplaints = data.service_requests?.open + (data.service_requests?.urgent || 0) || 0

  return (
    <div className="key-metrics">
      <div className="metric-card critical">
        <div className="metric-label">Missed Pickups (today)</div>
        <div className="metric-value">{missedPickups}</div>
      </div>
      
      <div className="metric-card warning">
        <div className="metric-label">Overflow Risk Zones</div>
        <div className="metric-value">{overflowRisk}</div>
      </div>
      
      <div className="metric-card normal">
        <div className="metric-label">Avg AQI Near Waste Zones</div>
        <div className="metric-value">{avgAQI}</div>
      </div>
      
      <div className="metric-card normal">
        <div className="metric-label">Total Active Complaints</div>
        <div className="metric-value">{totalComplaints}</div>
      </div>
    </div>
  )
}

export default KeyMetrics

