import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { fetchTonnageTrends } from '../services/api'
import './TonnageByBorough.css'

// Color palette for boroughs (matching the example)
const BOROUGH_COLORS = {
  'Brooklyn': { actual: '#22c55e', predicted: '#86efac' },      // Green
  'Queens': { actual: '#3b82f6', predicted: '#93c5fd' },        // Blue
  'Manhattan': { actual: '#f97316', predicted: '#fbbf24' },     // Orange
  'Bronx': { actual: '#ec4899', predicted: '#f9a8d4' },        // Pink
  'Staten Island': { actual: '#eab308', predicted: '#60a5fa' }  // Gold
}

function TonnageByBorough() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [monthsBack, setMonthsBack] = useState(12)
  const [monthsAhead, setMonthsAhead] = useState(6)

  useEffect(() => {
    loadTonnageData()
  }, [monthsBack, monthsAhead])

  const loadTonnageData = async () => {
    try {
      setLoading(true)
      const result = await fetchTonnageTrends(monthsBack, monthsAhead)
      setData(result)
    } catch (error) {
      console.error('Error loading tonnage trends:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="tonnage-by-borough">
        <div className="loading">Loading tonnage trends...</div>
      </div>
    )
  }

  if (!data || !data.time_series || data.time_series.length === 0) {
    return (
      <div className="tonnage-by-borough">
        <div className="no-data">No tonnage trend data available</div>
      </div>
    )
  }

  // Find the split point between actual and predicted
  const splitIndex = data.time_series.findIndex(point => point.is_predicted)
  const actualData = splitIndex > 0 ? data.time_series.slice(0, splitIndex) : data.time_series.filter(p => !p.is_predicted)
  const predictedData = data.time_series.filter(p => p.is_predicted)

  return (
    <div className="tonnage-by-borough">
      <div className="tonnage-header">
        <h3>NYC Garbage Collection — Actual & Predicted Trends</h3>
        <div className="controls">
          <div className="control-group">
            <label htmlFor="months-back">Historical:</label>
            <select
              id="months-back"
              value={monthsBack}
              onChange={(e) => setMonthsBack(Number(e.target.value))}
              className="control-select"
            >
              <option value={6}>6 months</option>
              <option value={12}>12 months</option>
              <option value={18}>18 months</option>
              <option value={24}>24 months</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="months-ahead">Forecast:</label>
            <select
              id="months-ahead"
              value={monthsAhead}
              onChange={(e) => setMonthsAhead(Number(e.target.value))}
              className="control-select"
            >
              <option value={3}>3 months</option>
              <option value={6}>6 months</option>
              <option value={12}>12 months</option>
            </select>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          <LineChart
            data={data.time_series}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
            <XAxis 
              dataKey="display"
              angle={-45}
              textAnchor="end"
              height={80}
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />
            <YAxis 
              label={{ value: 'Tons Collected (thousand tons)', angle: -90, position: 'insideLeft', style: { fill: '#94a3b8' } }}
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a1a2e', 
                border: '1px solid #2d2d44',
                borderRadius: '6px',
                color: '#fff'
              }}
              formatter={(value, name) => {
                if (value === null || value === undefined) return 'N/A'
                return [`${value.toFixed(1)}k tons`, name]
              }}
            />
            <Legend 
              wrapperStyle={{ color: '#94a3b8', paddingTop: '20px' }}
            />
            
            {/* Render lines for each borough - Actual and Predicted */}
            {data.boroughs.map(borough => {
              const colors = BOROUGH_COLORS[borough] || { actual: '#94a3b8', predicted: '#cbd5e1' }
              
              return (
                <React.Fragment key={borough}>
                  {/* Actual data line (solid with markers) */}
                  <Line
                    type="monotone"
                    dataKey={`${borough}_actual`}
                    name={`${borough} (Actual)`}
                    stroke={colors.actual}
                    strokeWidth={2.5}
                    dot={{ r: 4, fill: colors.actual }}
                    activeDot={{ r: 6 }}
                    connectNulls={false}
                  />
                  {/* Predicted data line (dashed, no markers) */}
                  <Line
                    type="monotone"
                    dataKey={`${borough}_predicted`}
                    name={`${borough} (Predicted)`}
                    stroke={colors.predicted}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    activeDot={{ r: 4 }}
                    connectNulls={false}
                  />
                </React.Fragment>
              )
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Summary stats */}
      {data.borough_stats && (
        <div className="trend-summary">
          <h4>Current Status & Forecast</h4>
          <div className="stats-grid">
            {data.boroughs.map(borough => {
              const stats = data.borough_stats[borough]
              if (!stats) return null
              return (
                <div key={borough} className="stat-card">
                  <div className="stat-borough">{borough}</div>
                  <div className="stat-row">
                    <span className="stat-label">Current:</span>
                    <span className="stat-value">{stats.current}k tons</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Avg:</span>
                    <span className="stat-value">{stats.average}k tons</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Next Month:</span>
                    <span className="stat-value predicted">{stats.predicted_next}k tons</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default TonnageByBorough
