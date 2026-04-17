import React, { useMemo } from 'react';
import { Activity, ShieldCheck, Database, Server } from 'lucide-react';

/**
 * Operations Dashboard
 * Displays global system health, cloud sync status, and crowd flow analytics.
 * Includes WCAG 2.1 AA compliant aria labels.
 */
export default function OpsDashboard({ zones, isConnected, firebaseConnected }) {
  // Compute global metrics
  const globalMetrics = useMemo(() => {
    const totalZones = Object.keys(zones || {}).length;
    if (totalZones === 0) return { avgDensity: 0, anomalies: 0, totalZones: 0 };
    
    let avgDensity = 0;
    let anomalies = 0;
    
    Object.values(zones).forEach(z => {
      avgDensity += z.current_density;
      if (z.is_anomaly) anomalies++;
    });

    return {
      avgDensity: Math.round(avgDensity / totalZones),
      anomalies,
      totalZones
    };
  }, [zones]);

  return (
    <section className="glass-panel ops-dashboard-container" aria-label="System Operations Dashboard">
      <h3 className="section-title">
        <Server size={18} className="icon-ops" aria-hidden="true" /> System Operations Center
      </h3>

      <div className="ops-grid" aria-live="polite">
        <div className="ops-card" tabIndex={0} aria-label={`Average load is ${globalMetrics.avgDensity}%`}>
          <Activity size={16} aria-hidden="true" />
          <div className="ops-stat">
            <span className="stat-label">Load Avg</span>
            <span className="stat-value">{globalMetrics.avgDensity}%</span>
          </div>
        </div>

        <div className="ops-card" tabIndex={0} aria-label={globalMetrics.anomalies > 0 ? `Warning: ${globalMetrics.anomalies} active alerts` : "System clear, 0 alerts"}>
          <ShieldCheck size={16} color={globalMetrics.anomalies > 0 ? '#ef4444' : '#10b981'} aria-hidden="true" />
          <div className="ops-stat">
            <span className="stat-label">Alerts</span>
            <span className="stat-value">{globalMetrics.anomalies}</span>
          </div>
        </div>

        <div className="ops-card" tabIndex={0} aria-label={firebaseConnected ? "Cloud sync is live" : "Cloud sync is idle"}>
          <Database size={16} color={firebaseConnected ? '#f59e0b' : '#334155'} aria-hidden="true" />
          <div className="ops-stat">
            <span className="stat-label">Cloud Sync</span>
            <span className="stat-value">{firebaseConnected ? 'LIVE' : 'IDLE'}</span>
          </div>
        </div>
      </div>

      <div className="system-health-bar" role="status" aria-label={`Neural link is ${isConnected ? 'stable' : 'lost'}`}>
         <div className="health-label">
            <span>Neural Link (WebSocket)</span>
            <span className={isConnected ? 'text-safe' : 'text-critical'}>
              {isConnected ? 'STABLE' : 'LOST'}
            </span>
         </div>
         <div className="health-track">
            <div className={`health-fill ${isConnected ? 'active' : 'inactive'}`}></div>
         </div>
      </div>

      <div className="mini-chart-container" style={{ height: '80px', marginTop: '15px' }} aria-hidden="true">
         <p style={{ fontSize: '0.7rem', color: '#94a3b8', textAlign: 'center' }}>
           Real-time Telemetry Streamed from Edge Inference
         </p>
      </div>
    </section>
  );
}
