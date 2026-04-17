/**
 * Frontend Component Tests — Smart Stadium OS
 * Tests for Node, MetricBar, and Graph components using Vitest + Testing Library.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Node from '../components/Node';
import Graph from '../components/Graph';

// --------------------------------------------------------------------------
// Node Component Tests
// --------------------------------------------------------------------------
describe('Node Component', () => {
  const mockData = {
    current_density: 45,
    predicted_density_10m: 60,
    risk_score: 'LOW',
    confidence_score: 0.92,
    is_anomaly: false,
  };

  const mockCoords = { x: 30, y: 40 };

  it('renders the zone name correctly', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    expect(screen.getByText('North Gate')).toBeInTheDocument();
  });

  it('displays current density in CURRENT view mode', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  it('displays predicted density in PREDICTED view mode', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="PREDICTED" />);
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('has the correct aria-label for screen readers', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    const node = screen.getByRole('button');
    expect(node).toHaveAttribute('aria-label', expect.stringContaining('North Gate'));
    expect(node).toHaveAttribute('aria-label', expect.stringContaining('45%'));
  });

  it('is keyboard focusable (has tabIndex)', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    const node = screen.getByRole('button');
    expect(node).toHaveAttribute('tabIndex', '0');
  });

  it('shows tooltip on focus', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    const node = screen.getByRole('button');
    fireEvent.focus(node);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('hides tooltip on blur', () => {
    render(<Node name="North_Gate" coords={mockCoords} data={mockData} viewMode="CURRENT" />);
    const node = screen.getByRole('button');
    fireEvent.focus(node);
    fireEvent.blur(node);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('shows ANOMALY badge when is_anomaly is true', () => {
    const anomalyData = { ...mockData, is_anomaly: true };
    render(<Node name="Food_Court" coords={mockCoords} data={anomalyData} viewMode="CURRENT" />);
    fireEvent.focus(screen.getByRole('button'));
    expect(screen.getByText('ANOMALY')).toBeInTheDocument();
  });

  it('applies critical class when density >= 90', () => {
    const criticalData = { ...mockData, current_density: 95 };
    render(<Node name="Section_101" coords={mockCoords} data={criticalData} viewMode="CURRENT" />);
    expect(screen.getByRole('button')).toHaveClass('critical');
  });

  it('applies warn class when density is between 70-89', () => {
    const warnData = { ...mockData, current_density: 75 };
    render(<Node name="Section_101" coords={mockCoords} data={warnData} viewMode="CURRENT" />);
    expect(screen.getByRole('button')).toHaveClass('warn');
  });

  it('returns null when data is not provided', () => {
    const { container } = render(
      <Node name="North_Gate" coords={mockCoords} data={null} viewMode="CURRENT" />
    );
    expect(container).toBeEmptyDOMElement();
  });
});

// --------------------------------------------------------------------------
// Graph Component Tests
// --------------------------------------------------------------------------
describe('Graph Component', () => {
  const mockTopology = {
    North_Gate: { x: 20, y: 10 },
    South_Gate: { x: 80, y: 90 },
  };
  const mockEdges = {
    North_Gate: { South_Gate: 1.0 },
    South_Gate: { North_Gate: 1.0 },
  };

  it('renders an SVG with role="img"', () => {
    render(
      <Graph
        topology={mockTopology}
        edges={mockEdges}
        primaryPath={null}
        altPath={null}
        baselinePath={null}
      />
    );
    expect(screen.getByRole('img')).toBeInTheDocument();
  });

  it('has a descriptive aria-label on the SVG', () => {
    render(
      <Graph
        topology={mockTopology}
        edges={mockEdges}
        primaryPath={['North_Gate', 'South_Gate']}
        altPath={null}
        baselinePath={null}
      />
    );
    const svg = screen.getByRole('img');
    expect(svg).toHaveAttribute('aria-label', expect.stringContaining('Neural optimal route active'));
  });

  it('shows no active routes label when all paths are null', () => {
    render(
      <Graph
        topology={mockTopology}
        edges={mockEdges}
        primaryPath={null}
        altPath={null}
        baselinePath={null}
      />
    );
    const svg = screen.getByRole('img');
    expect(svg).toHaveAttribute('aria-label', expect.stringContaining('No active routes'));
  });
});
