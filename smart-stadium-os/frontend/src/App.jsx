import React, { useState, useEffect } from 'react';
import { BrainCircuit, Zap, ShieldAlert, Cpu, Activity, BarChart3, LayoutDashboard, Lock } from 'lucide-react';
import DigitalTwin from './components/DigitalTwin';
import InsightPanel from './components/InsightPanel';
import OpsDashboard from './components/OpsDashboard';
import useWebSocket from './hooks/useWebSocket';
import useAuthToken from './hooks/useAuthToken';

export default function App() {
  const { data: engineState, isConnected } = useWebSocket('/ws/stream');
  const { authFetch, isAuthLoading } = useAuthToken();
  const [viewMode, setViewMode] = useState('CURRENT');
  
  const [startZone, setStartZone] = useState('North_Gate');
  const [endZone, setEndZone] = useState('South_Gate');
  const [multiRoute, setMultiRoute] = useState(null);
  const [isRouting, setIsRouting] = useState(false);
  const [showOps, setShowOps] = useState(true);

  const requestRoute = async () => {
    setIsRouting(true);
    try {
      const data = await authFetch(`/route?start=${startZone}&end=${endZone}`);
      // Simulate neural analysis delay for premium UX
      setTimeout(() => {
        setMultiRoute(data);
        setIsRouting(false);
      }, 900);
    } catch (err) {
      console.error('Neural route request failed:', err);
      setIsRouting(false);
    }
  };

  const emergencyEvac = async () => {
    try {
      await authFetch('/api/safety/alert', {
        method: "POST",
        body: JSON.stringify({ 
          zone: "Food_Court", 
          severity: "CRITICAL",
          message: "EXECUTIVE OVERRIDE: Global evacuaton trigger detected." 
        })
      });
    } catch (err) {
      console.error("Failed to broadcast alert:", err);
    }
  };

  if (!engineState) {
    return (
      <div className="loader-container">
        <div className="neural-boot-content">
          <BrainCircuit size={64} className="icon-spin-neural" />
          <h2 className="glitch-text" data-text="SMART STADIUM OS">SMART STADIUM OS</h2>
          <p>Authenticating Elite AI Core & Google Cloud Services...</p>
          <div className="boot-progress-bar">
             <div className="boot-progress-fill"></div>
          </div>
        </div>
      </div>
    );
  }

  const { zones, insights } = engineState;

  return (
    <div className="dashboard-engine">
      <header className="glass-header" role="banner" aria-label="Smart Stadium OS Navigation">
        <div className="header-brand">
          <BrainCircuit size={32} className="icon-ai-glow" />
          <div className="brand-text">
            <h1>Smart Stadium OS <span className="version-tag">ELITE v2.2</span></h1>
            <p className="brand-sub">Neural Infrastructure Management</p>
          </div>
        </div>
        
        <div className="header-controls">
           <div className="view-mode-toggle">
              <button 
                className={`btn-toggle ${viewMode === 'CURRENT' ? 'active' : ''}`} 
                onClick={() => setViewMode('CURRENT')}
              >
                <Activity size={16} /> Live Nodes
              </button>
              <button 
                className={`btn-toggle ${viewMode === 'PREDICTED' ? 'active' : ''}`} 
                onClick={() => setViewMode('PREDICTED')}
              >
                <BarChart3 size={16} /> AI Forecast
              </button>
           </div>

           <button 
              className={`btn-icon-toggle ${showOps ? 'active' : ''}`}
              onClick={() => setShowOps(!showOps)}
              title="Toggle Operations Center"
           >
             <LayoutDashboard size={20} />
           </button>

           <div className={`connection-status ${isConnected ? 'online' : 'offline'}`}>
              <div className="status-dot"></div>
              {isConnected ? 'Neural Link Active' : 'Link Offline'}
           </div>
        </div>
      </header>

      <main className="twin-layout" id="main-content" role="main" aria-label="Stadium Operations Centre">
        
        <DigitalTwin 
          engineState={engineState} 
          viewMode={viewMode} 
          multiRoute={multiRoute} 
        />

        <aside className="sidebar">
          
          {showOps && (
            <OpsDashboard 
              zones={zones} 
              isConnected={isConnected} 
              firebaseConnected={true} // Inferred based on backend status
            />
          )}

          <InsightPanel insights={insights} />

          <div className="glass-panel routing-panel">
            <h3 className="section-title">
               <Zap size={18} className="icon-zap" /> AI Multi-Pathfinding
            </h3>
            
            <div className="routing-selectors">
              <div className="control-group">
                <label>Origin</label>
                <select value={startZone} onChange={e => setStartZone(e.target.value)}>
                  {Object.keys(zones).sort().map(k => <option key={k} value={k}>{k.replace('_', ' ')}</option>)}
                </select>
              </div>
              
              <div className="control-group">
                <label>Target</label>
                <select value={endZone} onChange={e => setEndZone(e.target.value)}>
                  {Object.keys(zones).sort().map(k => <option key={k} value={k}>{k.replace('_', ' ')}</option>)}
                </select>
              </div>
            </div>

            <button className="btn-primary-action elite-btn" onClick={requestRoute} disabled={isRouting}>
              {isRouting ? (
                <>
                  <Cpu size={18} className="icon-spin" />
                  Analyzing Graph Weights...
                </>
              ) : 'Execute Neural Route'}
            </button>

            {multiRoute && !isRouting && (
              <div className="multi-route-results">
                <div className="route-comparison-card primary">
                  <header>
                    <div className="dot"></div>
                    <strong>Neural Optimal</strong>
                    <span className="saving-tag">-{multiRoute.primary.time_saved_estimate}m</span>
                  </header>
                  <p>{multiRoute.primary.ai_narrative}</p>
                </div>

                <div className="route-comparison-card alternative">
                  <header>
                    <div className="dot dashed"></div>
                    <strong>Safety Fallback</strong>
                  </header>
                  <p>{multiRoute.alternative.ai_narrative}</p>
                </div>
              </div>
            )}
          </div>

          <button className="btn-emergency-v2" onClick={emergencyEvac}>
            <ShieldAlert size={18}/> Emergency Protocols
          </button>
        </aside>
      </main>
    </div>
  );
}
