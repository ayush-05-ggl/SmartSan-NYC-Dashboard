import React from 'react'
import './StatsOverview.css'

function StatsOverview({ data }) {
  if (!data) return null

  const { overview, service_requests, performance } = data

  const stats = [
    {
      label: 'Total Zones',
      value: overview?.total_zones || 0,
      icon: '📍',
      color: '#3b82f6'
    },
    {
      label: 'Active Routes',
      value: overview?.active_routes || 0,
      icon: '🚛',
      color: '#10b981'
    },
    {
      label: 'Total Collections',
      value: overview?.total_collections || 0,
      icon: '🗑️',
      color: '#f59e0b'
    },
    {
      label: 'Collection Efficiency',
      value: `${overview?.collection_efficiency_pct?.toFixed(1) || 0}%`,
      icon: '✅',
      color: '#8b5cf6'
    },
    {
      label: 'Total Tonnage',
      value: `${overview?.total_tonnage?.toFixed(1) || 0} tons`,
      icon: '⚖️',
      color: '#ef4444'
    },
    {
      label: 'Open Requests',
      value: service_requests?.open || 0,
      icon: '📋',
      color: '#ec4899'
    }
  ]

  return (
    <div className="stats-overview">
      <h2 className="section-title">Overview</h2>
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card" style={{ borderLeftColor: stat.color }}>
            <div className="stat-icon" style={{ color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default StatsOverview

