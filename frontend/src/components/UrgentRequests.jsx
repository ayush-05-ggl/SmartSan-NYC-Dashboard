import React from 'react'
import './UrgentRequests.css'

function UrgentRequests({ data }) {
  if (!data || !data.urgent_requests || data.urgent_requests.length === 0) {
    return (
      <div className="urgent-requests">
        <h3 className="component-title">
          Urgent Requests
          <span className="badge zero">0</span>
        </h3>
        <p className="no-data">No urgent requests at this time</p>
      </div>
    )
  }

  const { urgent_requests, count } = data

  return (
    <div className="urgent-requests">
      <h3 className="component-title">
        Urgent Requests
        <span className="badge">{count}</span>
      </h3>
      
      <div className="requests-list">
        {urgent_requests.slice(0, 5).map((request, index) => (
          <div key={index} className="request-item" data-priority={request.priority}>
            <div className="request-header">
              <span className="request-type">
                {request.complaint_type || request.request_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              <span className={`priority-badge priority-${request.priority}`}>
                {request.priority}
              </span>
            </div>
            <p className="request-description">
              {request.descriptor || request.description}
            </p>
            {request.incident_address && (
              <p className="request-address">📍 {request.incident_address}</p>
            )}
            <div className="request-footer">
              {request.borough && (
                <span className="request-borough">{request.borough}</span>
              )}
              <span className="request-status">{request.status}</span>
            </div>
          </div>
        ))}
        {urgent_requests.length > 5 && (
          <div className="more-items">+{urgent_requests.length - 5} more requests</div>
        )}
      </div>
    </div>
  )
}

export default UrgentRequests

