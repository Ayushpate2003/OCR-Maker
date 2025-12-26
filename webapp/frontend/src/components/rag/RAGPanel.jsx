import React from 'react';
import './RAGPanel.css';
import { RAGChat } from './RAGChat';
import { RAGSettings } from './RAGSettings';
import { RAGIndexer } from './RAGIndexer';
import { useRAGAPI } from '../../hooks/useRAGAPI';

/**
 * Main RAG Panel component
 * Combines chat, settings, and indexing UI
 */
export const RAGPanel = ({ baseUrl = 'http://localhost:8000' }) => {
  const api = useRAGAPI(baseUrl);
  const [config, setConfig] = React.useState(null);
  const [stats, setStats] = React.useState(null);
  const [activeTab, setActiveTab] = React.useState('chat');
  const [health, setHealth] = React.useState(null);

  // Load initial config and stats
  React.useEffect(() => {
    const load = async () => {
      const health = await api.checkHealth();
      setHealth(health);
      const cfg = await api.getConfig();
      setConfig(cfg);
      const st = await api.getStats();
      setStats(st);
    };
    load();
  }, []);

  const handleQuery = async (query, includeChunks) => {
    return await api.queryDocuments(query, config?.top_k || 5, includeChunks);
  };

  const handleConfigChange = async (newConfig) => {
    const updates = {};
    const fields = [
      'chunk_size',
      'chunk_overlap',
      'top_k',
      'similarity_threshold',
      'temperature',
      'max_tokens',
      'ollama_model',
    ];

    for (const field of fields) {
      if (newConfig[field] !== config[field]) {
        updates[field] = newConfig[field];
      }
    }

    if (Object.keys(updates).length > 0) {
      try {
        const updated = await api.updateConfig(updates);
        setConfig(updated);
      } catch (error) {
        console.error('Config update error:', error);
      }
    }
  };

  const handleIndexFile = async (file, clearExisting) => {
    // In a real app, you'd upload the file first
    // For now, we assume it's already available on the server
    const filePath = `/path/to/${file.name}`;
    await api.indexDocument(filePath, clearExisting);
    const updatedStats = await api.getStats();
    setStats(updatedStats);
  };

  const handleRebuildIndex = async () => {
    if (confirm('Rebuild index? This may take a while.')) {
      try {
        await api.clearIndex();
        const updatedStats = await api.getStats();
        setStats(updatedStats);
      } catch (error) {
        console.error('Rebuild error:', error);
      }
    }
  };

  const handleClearIndex = async () => {
    if (confirm('Clear all indexed documents? This cannot be undone.')) {
      try {
        await api.clearIndex();
        const updatedStats = await api.getStats();
        setStats(updatedStats);
      } catch (error) {
        console.error('Clear error:', error);
      }
    }
  };

  if (!config) {
    return <div className="rag-panel rag-loading">Loading RAG system...</div>;
  }

  if (!health?.rag_enabled) {
    return (
      <div className="rag-panel rag-error">
        <p>⚠️ RAG system is not enabled or available.</p>
        <p>Check that Ollama is running and required models are installed.</p>
      </div>
    );
  }

  const systemHealth = health?.ollama_available && health?.embeddings_model_available;

  return (
    <div className="rag-panel">
      <div className="rag-panel-header">
        <h1>🔍 Semantic RAG Search</h1>
        <div className="rag-health-status">
          {systemHealth ? (
            <span className="rag-health-ok">✓ System Ready</span>
          ) : (
            <span className="rag-health-warning">⚠ Check services</span>
          )}
        </div>
      </div>

      <div className="rag-panel-tabs">
        <button
          className={`rag-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button
          className={`rag-tab ${activeTab === 'indexer' ? 'active' : ''}`}
          onClick={() => setActiveTab('indexer')}
        >
          📚 Index
        </button>
        <button
          className={`rag-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className="rag-panel-content">
        {activeTab === 'chat' && (
          <RAGChat onQuery={handleQuery} isLoading={api.loading} />
        )}

        {activeTab === 'indexer' && (
          <RAGIndexer onIndex={handleIndexFile} isLoading={api.loading} />
        )}

        {activeTab === 'settings' && (
          <RAGSettings
            config={config}
            onConfigChange={handleConfigChange}
            onRebuildIndex={handleRebuildIndex}
            onClearIndex={handleClearIndex}
            stats={stats}
            isLoading={api.loading}
          />
        )}
      </div>

      {api.error && (
        <div className="rag-error-notification">
          <strong>Error:</strong> {api.error}
          <button onClick={() => api.setError(null)}>✕</button>
        </div>
      )}
    </div>
  );
};
