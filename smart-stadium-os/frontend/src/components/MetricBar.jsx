import React from 'react';

/**
 * Metric Bar
 * Visual density representation with color transition.
 */
export default function MetricBar({ value, label }) {
  // Calculate color based on density (0-100)
  // 0% -> Green, 70% -> Amber, 100% -> Red
  const getBarColor = (val) => {
    if (val < 50) return '#10b981'; // Green
    if (val < 80) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <div className="metric-bar-container">
      <div className="metric-label">
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="metric-bg">
        <div 
          className="metric-fill" 
          style={{ 
            width: `${value}%`, 
            backgroundColor: getBarColor(value) 
          }}
        />
      </div>
    </div>
  );
}
