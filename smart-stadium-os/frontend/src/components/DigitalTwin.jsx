import React, { useState } from 'react';
import Node from './Node';
import Graph from './Graph';
import AlertBanner from './AlertBanner';
import AdvancedAnalyticsPanel from './AdvancedAnalyticsPanel';
import { AnimatePresence } from 'framer-motion';

/**
 * Digital Twin Core — Multi-Path Edition
 * Orchestrates the visualization layers (Graph, Nodes, Radar, Alerts)
 */
export default function DigitalTwin({ engineState, viewMode, multiRoute }) {
  const { zones, topology, edges, alerts } = engineState;
  const [selectedNode, setSelectedNode] = useState(null);

  const handleNodeClick = (nodeName) => {
    setSelectedNode(zones[nodeName]);
  };

  return (
    <div className="canvas-container" aria-label="Stadium Digital Twin Radar">
      {/* Real-time Alert Overlay */}
      <AlertBanner alerts={alerts} />

      {/* Cloud Infrastructure Pulser */}
      <div className="cloud-pulse-container" aria-label="Live connected to Google Cloud Run">
        <div className="pulse-dot"></div>
        <span>LIVE GCP SYNC</span>
      </div>

      {/* Time Machine Overlay */}
      <div className="canvas-header-overlay">
        <h3>Live Operations Radar</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="live-indicator"></div>
          <p style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
            Mode: <strong>{viewMode}</strong> | Tracking {Object.keys(zones || {}).length} Points
          </p>
        </div>
      </div>

      {/* Render All Paths if Multi-Route is available */}
      <Graph 
        topology={topology} 
        edges={edges} 
        primaryPath={multiRoute?.primary?.path}
        altPath={multiRoute?.alternative?.path}
        baselinePath={multiRoute?.baseline?.path}
      />

      <div className="nodes-layer">
        {Object.entries(topology).map(([nodeName, coords]) => (
          <Node 
            key={nodeName} 
            name={nodeName} 
            coords={coords} 
            data={zones[nodeName]} 
            viewMode={viewMode}
            onClick={() => handleNodeClick(nodeName)}
          />
        ))}
      </div>
      
      {/* Scanning Radar Animation effect */}
      <div className="radar-sweep"></div>
      
      {/* UI Grid pattern behind graph */}
      <div className="canvas-grid"></div>

      {/* Analytics Modal Overlay */}
      <AnimatePresence>
        {selectedNode && (
          <AdvancedAnalyticsPanel 
            nodeData={selectedNode} 
            onClose={() => setSelectedNode(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}
