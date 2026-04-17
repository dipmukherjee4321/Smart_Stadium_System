import React, { useState, useRef, useId } from 'react';
import MetricBar from './MetricBar';
import { AlertTriangle, Info } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * Stadium Zone Node
 * Fully accessible (WCAG 2.1 AA) interactive map node.
 * Supports full keyboard navigation (Enter/Space to open tooltip, Escape to close).
 */
const Node = React.memo(function Node({ name, coords, data, viewMode, onClick }) {
  const [isOpen, setIsOpen] = useState(false);
  const nodeRef = useRef(null);
  const tooltipId = useId();

  if (!data) return null;

  const displayDensity = viewMode === 'CURRENT'
    ? data.current_density
    : data.predicted_density_10m;

  let riskClass = 'safe';
  let heatmapClass = '';
  if (displayDensity >= 90) {
    riskClass = 'critical';
    heatmapClass = 'heatmap-high';
  }
  else if (displayDensity >= 70) {
    riskClass = 'warn';
    heatmapClass = 'heatmap-warn';
  }

  const friendlyName = name.replace(/_/g, ' ');

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
    if (e.key === 'Escape') {
      setIsOpen(false);
      nodeRef.current?.blur();
    }
  };

  return (
    <motion.div
      ref={nodeRef}
      className={`node ${riskClass} ${heatmapClass} ${data.is_anomaly ? 'anomaly-glow' : ''}`}
      style={{ left: `${coords.x}%`, top: `${coords.y}%` }}
      onClick={() => onClick?.()}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
      onFocus={() => setIsOpen(true)}
      onBlur={() => setIsOpen(false)}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-haspopup="dialog"
      aria-expanded={isOpen}
      aria-controls={tooltipId}
      aria-label={`Zone: ${friendlyName}. Crowd density: ${displayDensity}%. Risk level: ${riskClass}. ${data.is_anomaly ? 'Anomaly detected.' : ''}`}
      
      whileHover={{ scale: 1.15 }}
      whileTap={{ scale: 0.95 }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      <div className="node-density-indicator" aria-hidden="true">
        {data.is_anomaly && <AlertTriangle size={14} className="anomaly-icon" />}
        <span>{displayDensity}%</span>
      </div>

      <div className="node-title" aria-hidden="true">{friendlyName}</div>

      {/* Dynamic Connector Ring */}
      <div className="node-ring" aria-hidden="true" />

      {/* Accessible Tooltip */}
      {isOpen && (
        <motion.div
          id={tooltipId}
          className="node-tooltip"
          role="dialog"
          aria-modal="false"
          aria-label={`${friendlyName} zone details`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <header className="tooltip-header">
            <h4>{friendlyName}</h4>
            {data.is_anomaly && (
              <span className="anomaly-badge" role="status" aria-live="assertive">
                ANOMALY
              </span>
            )}
          </header>

          <div className="tooltip-metrics">
            <MetricBar label="Live Density" value={data.current_density} />
            <MetricBar label="AI Forecast (10m)" value={data.predicted_density_10m} />
          </div>

          <footer className="tooltip-footer">
            <div className="footer-row">
              <Info size={12} aria-hidden="true" />
              <span>Risk: <strong>{data.risk_score}</strong></span>
              <span>Prophet AI: <strong>{(data.confidence_score * 100).toFixed(0)}%</strong></span>
            </div>
            <div style={{ marginTop: '8px', fontSize: '0.65rem', color: '#60a5fa', textAlign: 'center' }}>
              Click to view Advanced Analytics
            </div>
          </footer>
        </motion.div>
      )}
    </motion.div>
  );
});

export default Node;
