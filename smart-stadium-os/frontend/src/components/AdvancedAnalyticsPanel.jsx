import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, Zap } from 'lucide-react';

export default function AdvancedAnalyticsPanel({ nodeData, onClose }) {
  if (!nodeData) return null;

  // Generate synthetic timeline data connecting historical and predicted data
  const chartData = useMemo(() => {
    const data = [];
    const now = new Date();
    
    // Process historical data (Assume density_history = array of last 10 ticks = 30 mins)
    const history = nodeData.density_history || [nodeData.current_density];
    history.forEach((val, idx) => {
      const t = new Date(now.getTime() - (history.length - idx) * 3 * 60000);
      data.push({
        time: t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        history: val,
        forecast: null,
      });
    });

    // Current point
    data.push({
      time: 'Now',
      history: nodeData.current_density,
      forecast: nodeData.current_density, // Intersect
    });

    // Forecast point (t + 10 mins)
    const futureT = new Date(now.getTime() + 10 * 60000);
    data.push({
      time: futureT.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      history: null,
      forecast: nodeData.predicted_density_10m,
    });

    return data;
  }, [nodeData]);

  const isCritical = nodeData.predicted_density_10m > 85;

  return (
    <motion.div 
      className="analytics-modal-backdrop"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div 
        className="analytics-modal-content cyber-glass"
        initial={{ y: 50, opacity: 0, scale: 0.95 }}
        animate={{ y: 0, opacity: 1, scale: 1 }}
        exit={{ y: 50, opacity: 0, scale: 0.95 }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="analytics-header">
          <div>
            <h3>{nodeData.name.replace(/_/g, ' ')}</h3>
            <span className="subtitle">AI Prophecy Engine & Telemetry</span>
          </div>
          <button className="btn-icon-toggle" onClick={onClose}>&times;</button>
        </header>

        <div className="analytics-metrics-row">
          <div className="metric-box">
            <Activity size={16} className="text-ai-glow" />
            <div className="metric-data">
              <label>Current Load</label>
              <strong>{nodeData.current_density}%</strong>
            </div>
          </div>
          <div className="metric-box">
            <Zap size={16} className={isCritical ? 'text-critical' : 'text-warn'} />
            <div className="metric-data">
              <label>Predicted +10m</label>
              <strong>{nodeData.predicted_density_10m}%</strong>
            </div>
          </div>
          <div className="metric-box">
            <ShieldAlert size={16} className="text-safe" />
            <div className="metric-data">
              <label>AI Confidence</label>
              <strong>{((nodeData.confidence_score || 0.9) * 100).toFixed(1)}%</strong>
            </div>
          </div>
        </div>

        {isCritical && (
          <motion.div 
            className="analytics-alert-box"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
          >
            <strong>Warning:</strong> Crowd saturation projected to rise exponentially in 10 minutes.
          </motion.div>
        )}

        <div className="analytics-chart-wrapper">
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={chartData} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorHistory" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={isCritical ? "#ef4444" : "#f59e0b"} stopOpacity={0.6}/>
                  <stop offset="95%" stopColor={isCritical ? "#ef4444" : "#f59e0b"} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickMargin={10} />
              <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                itemStyle={{ fontSize: '0.85rem' }}
                labelStyle={{ color: '#f8fafc', marginBottom: '5px' }}
              />
              <ReferenceLine y={85} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'top', value: 'High Risk Threshold', fill: '#ef4444', fontSize: '10px' }} />
              
              <Area 
                type="monotone" 
                dataKey="history" 
                name="Historical Trend"
                stroke="#3b82f6" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorHistory)" 
                activeDot={{ r: 6, fill: '#3b82f6' }}
              />
              <Area 
                type="monotone" 
                dataKey="forecast" 
                name="AI Prediction"
                stroke={isCritical ? "#ef4444" : "#f59e0b"} 
                strokeWidth={3}
                strokeDasharray="5 5"
                fillOpacity={1} 
                fill="url(#colorForecast)" 
                activeDot={{ r: 6, fill: isCritical ? '#ef4444' : '#f59e0b' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </motion.div>
  );
}
