import React, { useState } from 'react'
import './GlobalFilters.css'

function GlobalFilters({ onFilterChange }) {
  const [filters, setFilters] = useState({
    borough: 'All',
    timeRange: 'Last 7 days',
    zipCode: '',
    layers: {
      waste: true,
      airQuality: true
    }
  })

  const boroughs = ['All', 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
  const timeRanges = ['Last 24 hours', 'Last 7 days', 'Last 30 days', 'Last 90 days']

  const handleChange = (key, value) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    if (onFilterChange) onFilterChange(newFilters)
  }

  const toggleLayer = (layer) => {
    const newFilters = {
      ...filters,
      layers: {
        ...filters.layers,
        [layer]: !filters.layers[layer]
      }
    }
    setFilters(newFilters)
    if (onFilterChange) onFilterChange(newFilters)
  }

  return (
    <div className="global-filters">
      <div className="filter-group">
        <label>BOROUGH</label>
        <select 
          value={filters.borough} 
          onChange={(e) => handleChange('borough', e.target.value)}
          className="filter-select"
        >
          {boroughs.map(b => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>TIME RANGE</label>
        <select 
          value={filters.timeRange} 
          onChange={(e) => handleChange('timeRange', e.target.value)}
          className="filter-select"
        >
          {timeRanges.map(tr => (
            <option key={tr} value={tr}>{tr}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>ZIP CODE</label>
        <input
          type="text"
          placeholder="e.g. 10036"
          value={filters.zipCode}
          onChange={(e) => handleChange('zipCode', e.target.value)}
          className="filter-input"
        />
      </div>

      <div className="filter-group layers-group">
        <label>Layers</label>
        <div className="layer-toggles">
          <button
            className={`layer-toggle ${filters.layers.waste ? 'active' : ''}`}
            onClick={() => toggleLayer('waste')}
          >
            Waste
          </button>
          <button
            className={`layer-toggle ${filters.layers.airQuality ? 'active' : ''}`}
            onClick={() => toggleLayer('airQuality')}
          >
            Air Quality
          </button>
        </div>
      </div>
    </div>
  )
}

export default GlobalFilters

