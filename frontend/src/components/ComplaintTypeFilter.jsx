import React, { useState, useEffect } from 'react'
import { fetchComplaintTypes } from '../services/api'
import './ComplaintTypeFilter.css'

function ComplaintTypeFilter({ onFilterChange, selectedType }) {
  const [types, setTypes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTypes()
  }, [])

  const loadTypes = async () => {
    try {
      const data = await fetchComplaintTypes()
      if (data && data.complaint_types) {
        // Filter to show only sanitation-related types
        const sanitationTypes = data.complaint_types.filter(
          t => t.is_sanitation && t.type !== 'other'
        )
        setTypes(sanitationTypes)
      }
    } catch (error) {
      console.error('Error loading complaint types:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="complaint-filter">Loading types...</div>
  }

  return (
    <div className="complaint-filter">
      <h4>Filter by Complaint Type</h4>
      <div className="filter-buttons">
        <button
          className={`filter-btn ${!selectedType ? 'active' : ''}`}
          onClick={() => onFilterChange && onFilterChange(null)}
        >
          All Types
        </button>
        {types.map((type) => (
          <button
            key={type.type}
            className={`filter-btn ${selectedType === type.type ? 'active' : ''}`}
            onClick={() => onFilterChange && onFilterChange(type.type)}
          >
            {type.type.replace('_', ' ')}
            <span className="count-badge">{type.total}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default ComplaintTypeFilter

