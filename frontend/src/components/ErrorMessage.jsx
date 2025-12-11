import React from 'react'
import './ErrorMessage.css'

function ErrorMessage({ message }) {
  return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h2>Connection Error</h2>
      <p>{message}</p>
      <div className="error-actions">
        <button onClick={() => window.location.reload()}>Retry</button>
        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
          Check API Docs
        </a>
      </div>
    </div>
  )
}

export default ErrorMessage

