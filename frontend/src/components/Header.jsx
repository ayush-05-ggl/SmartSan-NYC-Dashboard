import React, { useState } from 'react'
import { refresh311Data } from '../services/api'
import './Header.css'

function Header({ onDataRefresh }) {
  const [refreshing, setRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(null)

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      const result = await refresh311Data()
      setLastRefresh(new Date())
      if (onDataRefresh) {
        onDataRefresh(result)
      }
      alert(`✅ Data refreshed successfully!\n\n${result.records_inserted} records updated from NYC Open Data API`)
    } catch (error) {
      console.error('Error refreshing data:', error)
      alert(`❌ Error refreshing data: ${error.message}`)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <header className="smartsan-header">
      <div className="header-content">
        <div className="header-title">
          <h1>SmartSan NYC</h1>
          <p className="header-subtitle">Smart Sanitation Dashboard</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-refresh" 
            onClick={handleRefresh}
            disabled={refreshing}
            title="Fetch latest data from NYC Open Data API"
          >
            {refreshing ? '🔄 Refreshing...' : '🔄 Refresh Live Data'}
          </button>
          {lastRefresh && (
            <span className="last-refresh">
              Last: {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button className="btn-secondary">Relaunch to update</button>
          <button className="btn-primary">Admin Login</button>
        </div>
      </div>
    </header>
  )
}

export default Header
