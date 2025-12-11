import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './CollectionSummary.css'

function CollectionSummary({ data }) {
  if (!data || !data.by_waste_type) {
    return (
      <div className="collection-summary">
        <h3 className="component-title">Collection Summary</h3>
        <p className="no-data">No summary data available</p>
      </div>
    )
  }

  const { by_waste_type, totals } = data

  // Prepare data for chart
  const chartData = Object.entries(by_waste_type).map(([type, stats]) => ({
    type: type.charAt(0).toUpperCase() + type.slice(1),
    tonnage: stats.tonnage,
    count: stats.count
  }))

  return (
    <div className="collection-summary">
      <h3 className="component-title">Collection Summary (Last 7 Days)</h3>
      
      {totals && (
        <div className="summary-totals">
          <div className="total-item">
            <span className="total-label">Total Collections:</span>
            <span className="total-value">{totals.count}</span>
          </div>
          <div className="total-item">
            <span className="total-label">Total Tonnage:</span>
            <span className="total-value">{totals.tonnage?.toFixed(1)} tons</span>
          </div>
        </div>
      )}

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="tonnage" fill="#3b82f6" name="Tonnage (tons)" />
            <Bar dataKey="count" fill="#10b981" name="Count" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default CollectionSummary

