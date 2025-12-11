import React, { useState, useEffect } from 'react'
import { fetchBoroughComplaintPredictions } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts'
import './BoroughPredictions.css'

function BoroughPredictions({ daysAhead = 30 }) {
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState('bar') // 'bar' or 'comparison'

  useEffect(() => {
    loadPredictions()
  }, [daysAhead])

  const loadPredictions = async () => {
    try {
      setLoading(true)
      const data = await fetchBoroughComplaintPredictions(daysAhead)
      setPredictions(data)
    } catch (error) {
      console.error('Error loading borough predictions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="borough-predictions">
        <h3>Borough Complaint Predictions</h3>
        <div className="loading">Loading predictions...</div>
      </div>
    )
  }

  if (!predictions || !predictions.predictions || predictions.predictions.length === 0) {
    return (
      <div className="borough-predictions">
        <h3>Borough Complaint Predictions</h3>
        <div className="no-data">No prediction data available</div>
      </div>
    )
  }

  // Prepare chart data
  const chartData = predictions.predictions.map(pred => ({
    borough: pred.borough,
    predicted: pred.predicted_complaints,
    current: Math.round(pred.current_daily_avg * daysAhead),
    historical: Math.round(pred.historical_daily_avg * daysAhead),
    confidence: pred.confidence
  }))

  // Sort by predicted complaints
  chartData.sort((a, b) => b.predicted - a.predicted)

  return (
    <div className="borough-predictions">
      <div className="predictions-header">
        <h3>Borough Complaint Predictions</h3>
        <div className="header-controls">
          <span className="forecast-period">Next {daysAhead} days</span>
          <div className="view-toggle">
            <button
              className={viewMode === 'bar' ? 'active' : ''}
              onClick={() => setViewMode('bar')}
            >
              Bar Chart
            </button>
            <button
              className={viewMode === 'comparison' ? 'active' : ''}
              onClick={() => setViewMode('comparison')}
            >
              Comparison
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'bar' ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
            <XAxis 
              dataKey="borough" 
              stroke="#94a3b8"
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                background: '#2d2d44', 
                border: '1px solid #3d3d54',
                borderRadius: '6px',
                color: 'white'
              }}
              formatter={(value) => [value.toLocaleString(), 'Predicted Complaints']}
            />
            <Bar 
              dataKey="predicted" 
              fill="#4ade80" 
              radius={[4, 4, 0, 0]}
              name="Predicted"
            />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
            <XAxis 
              dataKey="borough" 
              stroke="#94a3b8"
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                background: '#2d2d44', 
                border: '1px solid #3d3d54',
                borderRadius: '6px',
                color: 'white'
              }}
            />
            <Legend />
            <Bar dataKey="predicted" fill="#4ade80" name="Predicted" radius={[4, 4, 0, 0]} />
            <Bar dataKey="current" fill="#f59e0b" name="Current Trend" radius={[4, 4, 0, 0]} />
            <Bar dataKey="historical" fill="#3d3d54" name="Historical Avg" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      <div className="predictions-table">
        <h4>Detailed Predictions</h4>
        <table>
          <thead>
            <tr>
              <th>Borough</th>
              <th>Predicted</th>
              <th>Daily Avg</th>
              <th>Trend</th>
              <th>Change</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {predictions.predictions.map((pred, idx) => (
              <tr key={idx}>
                <td className="borough-name">{pred.borough}</td>
                <td className="predicted-value">
                  {pred.predicted_complaints.toLocaleString()}
                </td>
                <td>{pred.predicted_daily_avg}</td>
                <td>
                  <span className={`trend-badge trend-${pred.trend}`}>
                    {pred.trend === 'increasing' ? '↑' : pred.trend === 'decreasing' ? '↓' : '→'} {pred.trend}
                  </span>
                </td>
                <td className={pred.percent_change >= 0 ? 'positive' : 'negative'}>
                  {pred.percent_change >= 0 ? '+' : ''}{pred.percent_change}%
                </td>
                <td>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${pred.confidence}%` }}
                    />
                    <span className="confidence-text">{pred.confidence}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default BoroughPredictions

