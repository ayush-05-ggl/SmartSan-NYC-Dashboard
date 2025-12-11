import React, { useState, useEffect } from 'react'
import { fetchDataSources, refresh311Data } from '../services/api'
import './DataSourcePanel.css'

function DataSourcePanel() {
  const [sources, setSources] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [refreshStatus, setRefreshStatus] = useState(null)

  useEffect(() => {
    loadSources()
  }, [])

  const loadSources = async () => {
    try {
      const data = await fetchDataSources()
      setSources(data)
    } catch (err) {
      console.error('Error loading data sources:', err)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    setRefreshStatus(null)
    try {
      const result = await refresh311Data()
      setRefreshStatus({
        success: true,
        message: `Refreshed ${result.records_inserted} records from NYC Open Data API`,
        details: result
      })
      loadSources() // Reload to show updated counts
    } catch (err) {
      setRefreshStatus({
        success: false,
        message: `Error: ${err.message}`
      })
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="data-source-panel">
      <div className="source-header">
        <h3>📊 Data Sources & Transparency</h3>
        <button 
          onClick={handleRefresh} 
          disabled={refreshing}
          className="refresh-button"
        >
          {refreshing ? 'Refreshing...' : '🔄 Refresh Live Data'}
        </button>
      </div>

      {refreshStatus && (
        <div className={`refresh-status ${refreshStatus.success ? 'success' : 'error'}`}>
          {refreshStatus.message}
        </div>
      )}

      {sources && (
        <>
          <div className="sources-list">
            <h4>Official NYC Open Data Sources:</h4>
            <ul>
              <li>
                <strong>311 Service Requests:</strong>{' '}
                <a href={sources.data_sources.nyc_open_data_311} target="_blank" rel="noopener noreferrer">
                  View Source
                </a>
              </li>
              <li>
                <strong>DSNY Monthly Tonnage:</strong>{' '}
                <a href={sources.data_sources.dsny_tonnage} target="_blank" rel="noopener noreferrer">
                  View Source
                </a>
              </li>
              <li>
                <strong>DSNY Commercial Zones:</strong>{' '}
                <a href={sources.data_sources.dsny_zones} target="_blank" rel="noopener noreferrer">
                  View Source
                </a>
              </li>
            </ul>
          </div>

          <div className="data-stats">
            <h4>Current Data in Database:</h4>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Collections:</span>
                <span className="stat-value">{sources.current_data.collections.total.toLocaleString()}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Service Requests:</span>
                <span className="stat-value">{sources.current_data.requests.total.toLocaleString()}</span>
              </div>
            </div>

            {Object.keys(sources.current_data.collections.sources).length > 0 && (
              <div className="source-breakdown">
                <h5>Collection Data Sources:</h5>
                {Object.entries(sources.current_data.collections.sources).map(([source, count]) => (
                  <div key={source} className="source-item">
                    <span>{source}</span>
                    <span>{count.toLocaleString()} records</span>
                  </div>
                ))}
              </div>
            )}

            {Object.keys(sources.current_data.requests.sources).length > 0 && (
              <div className="source-breakdown">
                <h5>Request Data Sources:</h5>
                {Object.entries(sources.current_data.requests.sources).map(([source, count]) => (
                  <div key={source} className="source-item">
                    <span>{source}</span>
                    <span>{count.toLocaleString()} records</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="transparency-note">
            <p>✅ All data comes from official NYC Open Data sources</p>
            <p>✅ Every record is traceable to its source dataset</p>
            <p>✅ Predictions are based on real historical patterns</p>
          </div>
        </>
      )}
    </div>
  )
}

export default DataSourcePanel

