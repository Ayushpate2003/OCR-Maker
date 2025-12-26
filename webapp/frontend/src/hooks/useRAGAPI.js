import { useState } from 'react';

/**
 * Custom hook for RAG API interactions
 */
export const useRAGAPI = (baseUrl = 'http://localhost:8000') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = `${baseUrl}/api/rag`;

  const checkHealth = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) throw new Error('Health check failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const indexDocument = async (filePath, clearExisting = false) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/index`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          clear_existing: clearExisting,
        }),
      });
      if (!response.ok) throw new Error('Indexing failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const queryDocuments = async (query, topK = 5, includeChunks = false) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          top_k: topK,
          include_chunks: includeChunks,
        }),
      });
      if (!response.ok) throw new Error('Query failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/config`);
      if (!response.ok) throw new Error('Config fetch failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async (configUpdates) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configUpdates),
      });
      if (!response.ok) throw new Error('Config update failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/stats`);
      if (!response.ok) throw new Error('Stats fetch failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clearIndex = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/clear`, { method: 'POST' });
      if (!response.ok) throw new Error('Clear failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    setError,
    checkHealth,
    indexDocument,
    queryDocuments,
    getConfig,
    updateConfig,
    getStats,
    clearIndex,
  };
};
