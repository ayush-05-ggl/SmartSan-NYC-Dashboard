import React, { useState, useEffect } from 'react'
import { fetchComplaintTypes, fetchRequestsByType } from '../services/api'
import './ComplaintFilters.css'

function ComplaintFilters({ onFilterChange, selectedType }) {
  const [types, setTypes] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTypes()
  }, [])

  const loadTypes = async () => {
    setLoading(true)
    try {
      const data = await fetchComplaintTypes()
      setTypes(data)
    } catch (err) {
      console.error('Error loading complaint types:', err)
      setTypes({ complaint_types: [], total: 0 }) // Set empty to prevent crash
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="complaint-filters">Loading filters...</div>
  }

  if (!types || !types.complaint_types) {
    return <div className="complaint-filters">No complaint types available</div>
  }

  // Filter to show only sanitation-related types
  const complaintTypes = types.complaint_types || []
  const sanitationTypes = complaintTypes.filter(ct => ct && ct.is_sanitation)

  return (
    <div className="complaint-filters">
      <h3>Filter by Complaint Type</h3>
      <div className="filter-buttons">
        <button
          className={`filter-btn ${!selectedType ? 'active' : ''}`}
          onClick={() => onFilterChange(null)}
        >
          All ({types.total || 0})
        </button>
        {sanitationTypes.map(type => (
          <button
            key={type.type}
            className={`filter-btn ${selectedType === type.type ? 'active' : ''}`}
            onClick={() => onFilterChange(type.type)}
          >
            {type.type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || type.type}
            <span className="count">({type.total || 0})</span>
            {type.urgent > 0 && <span className="urgent-badge">{type.urgent}</span>}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ComplaintFilters

