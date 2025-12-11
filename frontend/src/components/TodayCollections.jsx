import React from 'react'
import './TodayCollections.css'

function TodayCollections({ data }) {
  if (!data || !data.collections) {
    return (
      <div className="today-collections">
        <h3 className="component-title">Today's Collections</h3>
        <p className="no-data">No collection data available</p>
      </div>
    )
  }

  const { collections, summary } = data

  return (
    <div className="today-collections">
      <h3 className="component-title">Today's Collections</h3>
      
      {summary && (
        <div className="summary-stats">
          <div className="summary-item">
            <span className="summary-label">Scheduled:</span>
            <span className="summary-value">{summary.total_scheduled}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Completed:</span>
            <span className="summary-value success">{summary.completed}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">In Progress:</span>
            <span className="summary-value warning">{summary.in_progress}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Tonnage:</span>
            <span className="summary-value">{summary.total_tonnage?.toFixed(1)} tons</span>
          </div>
        </div>
      )}

      <div className="collections-list">
        {collections.slice(0, 5).map((collection, index) => (
          <div key={index} className="collection-item">
            <div className="collection-info">
              <span className="collection-zone">{collection.zone_id}</span>
              <span className="collection-type">{collection.waste_type}</span>
            </div>
            <div className="collection-details">
              <span className={`collection-status status-${collection.status}`}>
                {collection.status}
              </span>
              <span className="collection-tonnage">{collection.tonnage?.toFixed(1)} tons</span>
            </div>
          </div>
        ))}
        {collections.length > 5 && (
          <div className="more-items">+{collections.length - 5} more collections</div>
        )}
      </div>
    </div>
  )
}

export default TodayCollections

