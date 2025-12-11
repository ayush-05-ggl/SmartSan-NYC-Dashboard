import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import './BoroughBreakdown.css'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

function BoroughBreakdown({ data }) {
  if (!data || !data.boroughs || data.boroughs.length === 0) {
    return (
      <div className="borough-breakdown">
        <h3 className="component-title">Borough Breakdown</h3>
        <p className="no-data">No borough data available</p>
      </div>
    )
  }

  const { boroughs } = data

  const chartData = boroughs.map((borough, index) => ({
    name: borough.borough,
    value: borough.zone_count,
    population: borough.total_population
  }))

  return (
    <div className="borough-breakdown">
      <h3 className="component-title">Borough Breakdown</h3>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="borough-list">
        {boroughs.map((borough, index) => (
          <div key={index} className="borough-item">
            <div className="borough-name">{borough.borough}</div>
            <div className="borough-stats">
              <span>{borough.zone_count} zones</span>
              <span>{borough.total_population?.toLocaleString()} people</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default BoroughBreakdown

