import React from 'react';
import { render, screen } from '@testing-library/react';
import { expect, test, describe } from 'vitest';
import DigitalTwin from '../components/DigitalTwin';

describe('DigitalTwin Component', () => {
  const mockEngineState = {
    zones: {
      North_Gate: { current_density: 30, predicted_density_10m: 40, risk_score: "LOW" }
    },
    topology: {
      North_Gate: { x: 50, y: 10 }
    },
    edges: {},
    alerts: []
  };

  test('renders without crashing and displays header', () => {
    render(<DigitalTwin engineState={mockEngineState} viewMode="current" />);
    // Check header text
    expect(screen.getByText(/Live Operations Radar/i)).toBeInTheDocument();
    
    // Check mode text
    expect(screen.getByText(/current/i)).toBeInTheDocument();
  });

  test('renders correct number of tracked points', () => {
    render(<DigitalTwin engineState={mockEngineState} viewMode="current" />);
    expect(screen.getByText(/Tracking 1 Points/i)).toBeInTheDocument();
  });

  test('handles multiRoute prop without crashing', () => {
    const mockMultiRoute = {
      primary: { path: ["North_Gate"] },
      alternative: { path: [] },
      baseline: { path: ["North_Gate"] }
    };
    render(<DigitalTwin engineState={mockEngineState} viewMode="current" multiRoute={mockMultiRoute} />);
    expect(screen.getByText(/Live Operations Radar/i)).toBeInTheDocument();
  });
});
