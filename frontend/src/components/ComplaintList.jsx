import React, { useState, useEffect } from 'react'
import { fetchRequestsByType } from '../services/api'
import './ComplaintList.css'

function ComplaintList({ complaintType, borough }) {
  const [requests, setRequests] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (complaintType) {
      loadRequests()
    } else {
      setRequests(null)
    }
  }, [complaintType, borough])

  const loadRequests = async () => {
    if (!complaintType) return
    
    setLoading(true)
    try {
      const params = { limit: 50 }
      if (borough) params.borough = borough
      const data = await fetchRequestsByType(complaintType, params)
      setRequests(data)
    } catch (err) {
      console.error('Error loading requests:', err)
      setRequests({ requests: [], total: 0 }) // Set empty to prevent crash
    } finally {
      setLoading(false)
    }
  }

  if (!complaintType) {
    return (
      <div className="complaint-list">
        <p className="no-selection">Select a complaint type to view requests</p>
      </div>
    )
  }

  if (loading) {
    return <div className="complaint-list">Loading requests...</div>
  }

  if (!requests || !requests.requests || requests.requests.length === 0) {
    return (
      <div className="complaint-list">
        <p className="no-data">No requests found for this type</p>
      </div>
    )
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="complaint-list">
      <div className="list-header">
        <h3>
          {complaintType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Requests
        </h3>
        <span className="total-count">{requests.total} total</span>
      </div>

      <div className="requests-grid">
        {requests.requests.map((req, idx) => (
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
              <h4 className="complaint-title">{req.complaint_type || req.request_type}</h4>
              <p className="complaint-description">{req.descriptor || req.description}</p>
              
              <div className="location-info">
                {req.incident_address && (
                  <div className="info-item">
                    <span className="label">📍 Address:</span>
                    <span className="value">{req.incident_address}</span>
                  </div>
                )}
                {req.borough && (
                  <div className="info-item">
                    <span className="label">🏙️ Borough:</span>
                    <span className="value">{req.borough}</span>
                  </div>
                )}
                {req.incident_zip && (
                  <div className="info-item">
                    <span className="label">📮 Zip:</span>
                    <span className="value">{req.incident_zip}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="card-footer">
              <div className="date-info">
                <span className="date-label">Created:</span>
                <span className="date-value">{formatDate(req.created_date || req.reported_at)}</span>
              </div>
              {req.closed_date && (
                <div className="date-info">
                  <span className="date-label">Closed:</span>
                  <span className="date-value">{formatDate(req.closed_date)}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ComplaintList

