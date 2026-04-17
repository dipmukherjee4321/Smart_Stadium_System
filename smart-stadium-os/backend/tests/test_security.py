"""
Comprehensive Security Service Tests.
Covers JWT generation, decoding, password hashing, and unauthorized access.
"""

import pytest
from services.security_service import SecurityService, get_current_user
from fastapi import HTTPException
from datetime import timedelta


class TestJWTTokens:
    """Test suite for JWT operations."""

    def test_create_and_decode_valid_token(self):
        """Should generate a token and successfully decode it."""
        token = SecurityService.create_access_token(
            data={"sub": "admin", "role": "ELITE_ADMIN"},
            expires_delta=timedelta(minutes=10)
        )
        assert token is not None
        payload = SecurityService.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "admin"
        assert payload["role"] == "ELITE_ADMIN"

    def test_decode_invalid_token_returns_none(self):
        """Should return None for a malformed or invalid token."""
        payload = SecurityService.decode_token("this.is.invalid")
        assert payload is None

    def test_decode_tampered_token_returns_none(self):
        """Should reject a token with a tampered payload."""
        token = SecurityService.create_access_token(data={"sub": "admin"})
        tampered = token[:-5] + "XXXXX"
        payload = SecurityService.decode_token(tampered)
        assert payload is None

    def test_expired_token_returns_none(self):
        """Should return None for an expired token."""
        token = SecurityService.create_access_token(
            data={"sub": "admin"},
            expires_delta=timedelta(seconds=-1)  # already expired
        )
        payload = SecurityService.decode_token(token)
        assert payload is None


class TestPasswordHashing:
    """Test suite for password hashing operations."""

    def test_hash_and_verify_password(self):
        """Hashing then verifying the same password should pass."""
        raw = "EliteStadium2026!"
        hashed = SecurityService.get_password_hash(raw)
        assert SecurityService.verify_password(raw, hashed) is True

    def test_wrong_password_verification_fails(self):
        """Verifying a wrong password should fail."""
        hashed = SecurityService.get_password_hash("correct_password")
        assert SecurityService.verify_password("wrong_password", hashed) is False

    def test_hash_is_not_plain_text(self):
        """The generated hash should not equal the original password."""
        raw = "test_password"
        assert SecurityService.get_password_hash(raw) != raw

@pytest.mark.asyncio
async def test_get_current_user_valid():
    """Verify that a valid token correctly retrieves user info."""
    token = SecurityService.create_access_token(data={"sub": "admin"})
    user = await get_current_user(token=token)
    assert user["sub"] == "admin"
    assert user["aud"] == "stadium-ops"

@pytest.mark.asyncio
async def test_get_current_user_invalid():
    """Verify that an invalid token raises HTTPException."""
    try:
        await get_current_user(token="invalid_token")
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 401
        assert "Could not validate neural credentials" in e.detail

def test_missing_audience():
    """Verify default create_access_token adds correct audience."""
    token = SecurityService.create_access_token(data={"sub": "user"})
    payload = SecurityService.decode_token(token)
    assert payload["aud"] == "stadium-ops"

def test_missing_issuer():
    """Verify default create_access_token adds correct issuer."""
    token = SecurityService.create_access_token(data={"sub": "user"})
    payload = SecurityService.decode_token(token)
    assert payload["iss"] == "smart-stadium-os"
