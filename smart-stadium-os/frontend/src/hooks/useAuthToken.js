/**
 * Frontend Security Utilities — useAuthToken hook
 * Manages JWT token retrieval, caching, and auto-refresh for
 * making authenticated requests to the AI routing engine.
 */
import { useState, useCallback } from 'react';

const TOKEN_KEY = 'stadium_auth_token';
const TOKEN_EXPIRY_KEY = 'stadium_auth_expiry';

/**
 * Checks if a stored token is still valid (not expired).
 * @returns {boolean}
 */
const isTokenValid = () => {
  const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
  return expiry && Date.now() < parseInt(expiry, 10);
};

/**
 * useAuthToken — React hook for managing the session JWT.
 * Caches token in localStorage and auto-relogins on expiry.
 */
export default function useAuthToken() {
  const [token, setToken] = useState(() =>
    isTokenValid() ? localStorage.getItem(TOKEN_KEY) : null
  );
  const [isAuthLoading, setIsAuthLoading] = useState(false);

  const fetchToken = useCallback(async () => {
    // Return cached valid token
    if (isTokenValid()) return localStorage.getItem(TOKEN_KEY);

    setIsAuthLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', 'admin');
      formData.append('password', 'stadium_elite');

      const res = await fetch('/api/security/login', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Authentication failed');

      const { access_token } = await res.json();
      
      // Cache with a 55-minute expiry buffer (token lives 60m)
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(TOKEN_EXPIRY_KEY, String(Date.now() + 55 * 60 * 1000));
      setToken(access_token);
      return access_token;
    } catch (err) {
      console.error('Neural auth failed:', err);
      return null;
    } finally {
      setIsAuthLoading(false);
    }
  }, []);

  /**
   * Makes an authenticated GET request with automatic token injection.
   * @param {string} url - The endpoint to call.
   * @returns {Promise<any>} Parsed JSON response.
   */
  const authFetch = useCallback(async (url) => {
    const t = await fetchToken();
    const res = await fetch(url, {
      headers: t ? { Authorization: `Bearer ${t}` } : {},
    });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }, [fetchToken]);

  return { token, isAuthLoading, authFetch };
}
