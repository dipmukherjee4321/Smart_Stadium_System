import React from 'react';
import { render, screen } from '@testing-library/react';
import { expect, test, describe } from 'vitest';
import OpsDashboard from '../components/OpsDashboard';

describe('OpsDashboard Component', () => {
  const mockZones = {
    Zone1: { current_density: 30, is_anomaly: false },
    Zone2: { current_density: 70, is_anomaly: true }
  };

  test('renders the Operations Dashboard title', () => {
    render(<OpsDashboard zones={mockZones} isConnected={true} firebaseConnected={true} />);
    expect(screen.getByText(/System Operations Center/i)).toBeInTheDocument();
  });

  test('calculates and displays average density and anomalies correctly', () => {
    render(<OpsDashboard zones={mockZones} isConnected={true} firebaseConnected={true} />);
    
    // avg density of 30 and 70 is 50
    expect(screen.getByText('50%')).toBeInTheDocument();
    
    // 1 anomaly
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  test('displays LIVE for active cloud sync', () => {
    render(<OpsDashboard zones={mockZones} isConnected={true} firebaseConnected={true} />);
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  test('displays IDLE for inactive cloud sync', () => {
    render(<OpsDashboard zones={mockZones} isConnected={true} firebaseConnected={false} />);
    expect(screen.getByText('IDLE')).toBeInTheDocument();
  });

  test('displays STABLE when websocket is connected', () => {
    render(<OpsDashboard zones={mockZones} isConnected={true} firebaseConnected={true} />);
    expect(screen.getByText('STABLE')).toBeInTheDocument();
  });

  test('displays LOST when websocket is disconnected', () => {
    render(<OpsDashboard zones={mockZones} isConnected={false} firebaseConnected={true} />);
    expect(screen.getByText('LOST')).toBeInTheDocument();
  });
});
