import React from 'react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './TrendChart.css'

function TrendChart({ data, title, dataKey, color = '#3b82f6' }) {
  if (!data || !data.length) {
    return (
      <div className="trend-chart">
        <h4>{title}</h4>
        <p className="no-data">No data available</p>
      </div>
    )
  }

  return (
    <div className="trend-chart">
      <h4>{title}</h4>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color} 
            fill={`url(#gradient-${dataKey})`}
            name={title}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default TrendChart

