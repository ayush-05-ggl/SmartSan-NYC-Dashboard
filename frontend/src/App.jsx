import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorMessage from './components/ErrorMessage'
import ErrorBoundary from './components/ErrorBoundary'
import { fetchDashboardMetrics, fetchTodayCollections, fetchUrgentRequests } from './services/api'

function App() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Test API connection on mount
    const testConnection = async () => {
      try {
        await fetchDashboardMetrics()
        setLoading(false)
      } catch (err) {
        console.error('API connection error:', err)
        setError('Failed to connect to API. Make sure the backend server is running on http://localhost:8000')
        setLoading(false)
      }
    }
    testConnection()
  }, [])

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <ErrorMessage message={error} />
  }

  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  )
}

export default App

