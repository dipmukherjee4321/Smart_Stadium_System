"""
Schema Validation Tests
=======================
Verifies Pydantic v2 input validation and sanitization.
"""

import pytest
from models.schemas import AlertRequest
from pydantic import ValidationError

def test_alert_request_valid():
    """Verify valid alert payload passes validation."""
    data = {"zone": "North_Gate", "severity": "HIGH", "message": "Smoke detected near gate."}
    req = AlertRequest(**data)
    assert req.zone == "North_Gate"
    assert req.severity == "HIGH"

def test_alert_request_invalid_zone():
    """Verify unknown zones are rejected at the schema level."""
    data = {"zone": "Parking_Lot_B", "severity": "LOW", "message": "Test"}
    with pytest.raises(ValidationError) as exc:
        AlertRequest(**data)
    assert "Unknown zone" in str(exc.value)

def test_alert_request_severity_normalization():
    """Verify severity is normalized to uppercase and validated."""
    data = {"zone": "South_Gate", "severity": "critical", "message": "Test"}
    req = AlertRequest(**data)
    assert req.severity == "CRITICAL"
    
    with pytest.raises(ValidationError):
        AlertRequest(zone="South_Gate", severity="EXTREME", message="X")

def test_alert_request_message_sanitization():
    """Verify message whitespace is stripped and length is bounded."""
    # Test stripping
    req = AlertRequest(zone="South_Gate", message="  Needs attention   ")
    assert req.message == "Needs attention"
    
    # Test length limit
    long_msg = "X" * 501
    with pytest.raises(ValidationError) as exc:
        AlertRequest(zone="South_Gate", message=long_msg)
    assert "500 characters" in str(exc.value)
