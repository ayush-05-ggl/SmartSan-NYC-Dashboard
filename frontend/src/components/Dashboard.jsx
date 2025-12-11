import React, { useState, useEffect } from 'react'
import Header from './Header'
import GlobalFilters from './GlobalFilters'
import KeyMetrics from './KeyMetrics'
import MapVisualization from './MapVisualization'
import ComplaintsByDistrict from './ComplaintsByDistrict'
import PredictiveAnalyticsPanel from './PredictiveAnalyticsPanel'
import ComplaintHeatmap from './ComplaintHeatmap'
import ComplaintTypeFilter from './ComplaintTypeFilter'
import FilteredComplaints from './FilteredComplaints'
import BoroughPredictions from './BoroughPredictions'
import TonnageByBorough from './TonnageByBorough'
import LoadingSpinner from './LoadingSpinner'
import { 
  fetchDashboardMetrics, 
  fetchRequestHotspots
} from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [filters, setFilters] = useState({
    borough: 'All',
    timeRange: 'Last 7 days',
    zipCode: '',
    layers: {
      waste: true,
      airQuality: true
    }
  })
  const [selectedComplaintType, setSelectedComplaintType] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const days = filters.timeRange === 'Last 24 hours' ? 1 :
                     filters.timeRange === 'Last 7 days' ? 7 :
                     filters.timeRange === 'Last 30 days' ? 30 : 90
        
        const [dashboard] = await Promise.all([
          fetchDashboardMetrics(days)
        ])
        
        setDashboardData(dashboard)
        setLoading(false)
      } catch (err) {
        console.error('Error loading dashboard data:', err)
        setError(err.message)
        setLoading(false)
      }
    }

    loadData()
    
    // Refresh data every 5 minutes
    const interval = setInterval(loadData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [filters.timeRange, filters.borough])

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  if (loading && !dashboardData) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
      </div>
    )
  }

  const handleDataRefresh = (result) => {
    // Reload dashboard data after refresh
    const days = filters.timeRange === 'Last 24 hours' ? 1 :
                 filters.timeRange === 'Last 7 days' ? 7 :
                 filters.timeRange === 'Last 30 days' ? 30 : 90
    
    fetchDashboardMetrics(days).then(setDashboardData)
  }

  return (
    <div className="smartsan-dashboard">
      <Header onDataRefresh={handleDataRefresh} />
      <GlobalFilters onFilterChange={handleFilterChange} />
      <KeyMetrics data={dashboardData} />
      
      {/* Complaint Type Filter */}
      <div className="dashboard-section full-width">
        <ComplaintTypeFilter 
          onFilterChange={setSelectedComplaintType}
          selectedType={selectedComplaintType}
        />
      </div>

      {/* Filtered Complaints Display */}
      {selectedComplaintType && (
        <div className="dashboard-section full-width">
          <FilteredComplaints 
            complaintType={selectedComplaintType}
            borough={filters.borough}
            zipCode={filters.zipCode}
          />
        </div>
      )}
      
      <div className="dashboard-main">
        <div className="dashboard-left">
          <div className="map-section">
            <h3>Complaint Density Heatmap</h3>
            <ComplaintHeatmap filters={filters} complaintType={selectedComplaintType} />
          </div>
          
          <div className="map-section">
            <h3>Waste + Air Quality Map</h3>
            <MapVisualization filters={filters} />
          </div>
        </div>
        
        <div className="dashboard-right">
          <div className="chart-section">
            <ComplaintsByDistrict 
              borough={filters.borough}
              complaintType={selectedComplaintType}
            />
          </div>
          
          <div className="chart-section">
            <PredictiveAnalyticsPanel />
          </div>
        </div>
      </div>

      {/* Tonnage by Borough Section */}
      <div className="dashboard-section full-width">
        <TonnageByBorough />
      </div>

      {/* Borough Predictions Section */}
      <div className="dashboard-section full-width">
        <BoroughPredictions daysAhead={30} />
      </div>
    </div>
  )
}

export default Dashboard

