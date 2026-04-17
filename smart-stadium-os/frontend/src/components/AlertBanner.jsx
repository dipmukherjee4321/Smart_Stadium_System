import React, { useEffect, useState } from 'react';
import { ShieldAlert, X } from 'lucide-react';

/**
 * Global Alert Banner
 * Displays emergency broadcast events across the top of the radar.
 * Fully accessible: uses role="alert" and aria-live="assertive" for 
 * immediate screen-reader announcement of critical events.
 */
export default function AlertBanner({ alerts }) {
  const [visible, setVisible] = useState(false);
  const [currentAlert, setCurrentAlert] = useState(null);

  useEffect(() => {
    if (alerts && alerts.length > 0) {
      setCurrentAlert(alerts[0]);
      setVisible(true);
    }
  }, [alerts]);

  if (!visible || !currentAlert) return null;

  const severityLabel = currentAlert.severity?.toLowerCase() ?? 'high';

  return (
    <div
      className={`alert-banner-overlay severity-${severityLabel}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      aria-label={`Emergency: ${currentAlert.severity} priority alert`}
    >
      <div className="alert-content">
        <ShieldAlert size={24} className="alert-icon-pulse" aria-hidden="true" />
        <div className="alert-text" id="alert-message">
          <strong>{currentAlert.severity} PRIORITY:</strong>{' '}
          {currentAlert.message}
        </div>
        <button
          className="btn-close-alert"
          onClick={() => setVisible(false)}
          aria-label="Dismiss emergency alert"
        >
          <X size={18} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
