import React, { useState, useEffect } from 'react'
import { fetchRequestsByType, fetchComplaintsByBorough } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './FilteredComplaints.css'

function FilteredComplaints({ complaintType, borough, zipCode }) {
  const [requests, setRequests] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (complaintType) {
      loadFilteredData()
    } else {
      setRequests(null)
      setStats(null)
    }
  }, [complaintType, borough, zipCode])

  const loadFilteredData = async () => {
    if (!complaintType) return
    
    setLoading(true)
    try {
      const params = { limit: 100 }
      if (borough && borough !== 'All') params.borough = borough
      
      const [requestsData, boroughData] = await Promise.all([
        fetchRequestsByType(complaintType, params),
        fetchComplaintsByBorough(complaintType)
      ])
      
      setRequests(requestsData)
      
      // Calculate stats
      if (requestsData && requestsData.requests) {
        const statusCounts = {}
        const priorityCounts = {}
        const boroughCounts = {}
        
        requestsData.requests.forEach(req => {
          // Status counts
          statusCounts[req.status] = (statusCounts[req.status] || 0) + 1
          
          // Priority counts
          priorityCounts[req.priority] = (priorityCounts[req.priority] || 0) + 1
          
          // Borough counts
          if (req.borough) {
            boroughCounts[req.borough] = (boroughCounts[req.borough] || 0) + 1
          }
        })
        
        setStats({
          statusCounts,
          priorityCounts,
          boroughCounts,
          total: requestsData.total || requestsData.requests.length
        })
      }
    } catch (err) {
      console.error('Error loading filtered data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!complaintType) {
    return (
      <div className="filtered-complaints">
        <div className="no-selection">
          <p>👆 Select a complaint type above to see detailed analysis</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="filtered-complaints">
        <div className="loading">Loading filtered data...</div>
      </div>
    )
  }

  // Prepare chart data
  const statusChartData = stats ? Object.entries(stats.statusCounts).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count
  })) : []

  const priorityChartData = stats ? Object.entries(stats.priorityCounts).map(([priority, count]) => ({
    name: priority.charAt(0).toUpperCase() + priority.slice(1),
    value: count
  })) : []

  const boroughChartData = stats ? Object.entries(stats.boroughCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([borough, count]) => ({
      name: borough,
      value: count
    })) : []

  const COLORS = ['#4ade80', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6']

  return (
    <div className="filtered-complaints">
      <div className="filtered-header">
        <h3>{complaintType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Analysis</h3>
        <div className="filter-info">
          {borough && borough !== 'All' && <span className="filter-badge">Borough: {borough}</span>}
          {zipCode && <span className="filter-badge">ZIP: {zipCode}</span>}
          <span className="total-badge">{stats?.total || 0} total requests</span>
        </div>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Status Breakdown</h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={statusChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={60}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="stat-card">
            <h4>Priority Distribution</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={priorityChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#2d2d44', 
                    border: '1px solid #3d3d54',
                    borderRadius: '6px',
                    color: 'white'
                  }}
                />
                <Bar dataKey="value" fill="#4ade80" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="stat-card">
            <h4>Top Boroughs</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={boroughChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#2d2d44', 
                    border: '1px solid #3d3d54',
                    borderRadius: '6px',
                    color: 'white'
                  }}
                />
                <Bar dataKey="value" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {requests && requests.requests && requests.requests.length > 0 && (
        <div className="requests-list">
          <h4>Recent Requests ({requests.requests.length} shown)</h4>
          <div className="requests-grid">
            {requests.requests.slice(0, 12).map((req, idx) => (
              <div key={idx} className="complaint-card">
                <div className="card-header">
                  <span className={`status-badge status-${req.status}`}>
                    {req.status}
                  </span>
                  <span className={`priority-badge priority-${req.priority}`}>
                    {req.priority}
                  </span>
                </div>
                <div className="card-body">
                  <p className="complaint-description">
                    {req.descriptor || req.description || 'No description'}
                  </p>
                  {req.incident_address && (
                    <div className="address">📍 {req.incident_address}</div>
                  )}
                  {req.borough && (
                    <div className="borough">🏙️ {req.borough}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FilteredComplaints

