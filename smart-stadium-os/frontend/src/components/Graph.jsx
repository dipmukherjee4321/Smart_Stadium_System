import React from 'react';

/**
 * Multi-Path Graph Layer — ARIA Enhanced
 * Renders SVG connections with weighted styles for:
 * - Primary Neural Route (Solid Blue)
 * - Alternative Safety Route (Dashed Amber)
 * - Baseline Shortest Path (Dotted Gray)
 *
 * Fully accessible: SVG uses role="img" with a descriptive aria-label.
 * Each path group uses aria-label to describe its route type.
 */
const Graph = React.memo(function Graph({ topology, edges, primaryPath, altPath, baselinePath }) {

  const getPathStatus = (from, to) => {
    const check = (path) => {
      if (!path) return false;
      for (let i = 0; i < path.length - 1; i++) {
        if ((path[i] === from && path[i + 1] === to) || (path[i] === to && path[i + 1] === from)) return true;
      }
      return false;
    };
    return {
      isPrimary: check(primaryPath),
      isAlt: check(altPath),
      isBaseline: check(baselinePath),
    };
  };

  const renderEdges = () => {
    const lines = [];
    const processed = new Set();

    Object.keys(edges).forEach(fromNode => {
      Object.keys(edges[fromNode]).forEach(toNode => {
        const edgeId = [fromNode, toNode].sort().join('-');
        if (processed.has(edgeId)) return;
        processed.add(edgeId);

        const p1 = topology[fromNode];
        const p2 = topology[toNode];
        if (!p1 || !p2) return;

        const { isPrimary, isAlt, isBaseline } = getPathStatus(fromNode, toNode);
        const key = `edge-${fromNode}-${toNode}`;
        const fromLabel = fromNode.replace(/_/g, ' ');
        const toLabel = toNode.replace(/_/g, ' ');

        lines.push(
          <g key={key} role="presentation">
            {/* Base Connector */}
            <line
              x1={`${p1.x}%`} y1={`${p1.y}%`}
              x2={`${p2.x}%`} y2={`${p2.y}%`}
              className="edge-base flow-arrow-path"
              aria-hidden="true"
            />
            {/* Ambient Flow Packets */}
            <circle r="2" fill="rgba(96, 165, 250, 0.8)" aria-hidden="true">
              <animate attributeName="cx" from={`${p1.x}%`} to={`${p2.x}%`} dur="3s" repeatCount="indefinite" />
              <animate attributeName="cy" from={`${p1.y}%`} to={`${p2.y}%`} dur="3s" repeatCount="indefinite" />
            </circle>

            {isBaseline && (
              <line
                x1={`${p1.x}%`} y1={`${p1.y}%`}
                x2={`${p2.x}%`} y2={`${p2.y}%`}
                className="path-baseline-overlay"
                aria-label={`Baseline path segment: ${fromLabel} to ${toLabel}`}
              />
            )}

            {isAlt && (
              <line
                x1={`${p1.x}%`} y1={`${p1.y}%`}
                x2={`${p2.x}%`} y2={`${p2.y}%`}
                className="path-alt-overlay pulse-path"
                aria-label={`Safety fallback path segment: ${fromLabel} to ${toLabel}`}
              />
            )}

            {isPrimary && (
              <>
                <line
                  x1={`${p1.x}%`} y1={`${p1.y}%`}
                  x2={`${p2.x}%`} y2={`${p2.y}%`}
                  className="path-primary-overlay"
                  aria-label={`Neural optimal path segment: ${fromLabel} to ${toLabel}`}
                />
                <circle r="3" fill="#3b82f6" className="neural-data-packet" aria-hidden="true">
                  <animate attributeName="cx" from={`${p1.x}%`} to={`${p2.x}%`} dur="1s" repeatCount="indefinite" />
                  <animate attributeName="cy" from={`${p1.y}%`} to={`${p2.y}%`} dur="1s" repeatCount="indefinite" />
                </circle>
              </>
            )}
          </g>
        );
      });
    });
    return lines;
  };

  const pathSummary = [
    primaryPath ? `Neural optimal route active` : '',
    altPath ? `Safety fallback route active` : '',
    baselinePath ? `Baseline shortest route active` : '',
  ].filter(Boolean).join('. ') || 'No active routes selected.';

  return (
    <svg
      className="svg-canvas"
      preserveAspectRatio="none"
      role="img"
      aria-label={`Stadium navigation graph. ${pathSummary}`}
    >
      <title>Stadium Multi-Path Navigation Graph</title>
      <desc>{pathSummary}</desc>
      {renderEdges()}
    </svg>
  );
});

export default Graph;
