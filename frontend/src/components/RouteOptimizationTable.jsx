import React, { useState, useEffect } from 'react'
import { fetchRouteOptimization } from '../services/api'
import './RouteOptimizationTable.css'

function RouteOptimizationTable({ selectedZone }) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        // For demo, create sample suggestions based on available data
        // In production, this would come from the API
        const sampleSuggestions = [
          {
            location: 'Times Square (10036)',
            issue: 'Event congestion 4-7 PM',
            recommendation: 'Shift pickups to 7-10 PM, reverse route',
            impact: '-35% delay'
          },
          {
            location: 'Yankee Stadium (10451)',
            issue: 'Game-day overflow',
            recommendation: 'Extra truck on game days + 2 more baskets',
            impact: '-25% overflow'
          },
          {
            location: 'Downtown Brooklyn (11201)',
            issue: 'High AQI near depot',
            recommendation: 'Avoid 3rd Ave during peak, use alt route',
            impact: '-15% NO2'
          }
        ]
        setSuggestions(sampleSuggestions)
      } catch (error) {
        console.error('Error loading route optimization:', error)
      } finally {
        setLoading(false)
      }
    }
    loadSuggestions()
  }, [selectedZone])

  if (loading) {
    return (
      <div className="route-optimization">
        <h3>Route Optimization Suggestions</h3>
        <div className="table-loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="route-optimization">
      <h3>Route Optimization Suggestions</h3>
      <table className="optimization-table">
        <thead>
          <tr>
            <th>Location</th>
            <th>Issue</th>
            <th>Recommendation</th>
            <th>Impact</th>
          </tr>
        </thead>
        <tbody>
          {suggestions.map((suggestion, idx) => (
            <tr key={idx}>
              <td className="location-cell">{suggestion.location}</td>
              <td>{suggestion.issue}</td>
              <td>{suggestion.recommendation}</td>
              <td className="impact-cell positive">{suggestion.impact}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RouteOptimizationTable

