import React from 'react';
import './RAGSettings.css';

/**
 * RAG Settings panel for configuration
 */
export const RAGSettings = ({
  config,
  onConfigChange,
  onRebuildIndex,
  onClearIndex,
  stats,
  isLoading,
}) => {
  const [showAdvanced, setShowAdvanced] = React.useState(false);

  const handleInputChange = (field, value) => {
    onConfigChange({
      ...config,
      [field]: value,
    });
  };

  return (
    <div className="rag-settings">
      <div className="rag-settings-header">
        <h3>⚙️ RAG Configuration</h3>
        <button
          className="rag-toggle-advanced"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '▼' : '▶'} Advanced
        </button>
      </div>

      <div className="rag-settings-content">
        {/* Chunk Size */}
        <div className="rag-setting-group">
          <label htmlFor="chunk-size">
            📄 Chunk Size (tokens): {config.chunk_size}
          </label>
          <input
            id="chunk-size"
            type="range"
            min="200"
            max="2000"
            step="100"
            value={config.chunk_size}
            onChange={(e) => handleInputChange('chunk_size', parseInt(e.target.value))}
            disabled={isLoading}
          />
          <small>Larger chunks = more context per retrieval, but slower processing</small>
        </div>

        {/* Chunk Overlap */}
        {showAdvanced && (
          <div className="rag-setting-group">
            <label htmlFor="chunk-overlap">
              🔗 Chunk Overlap (tokens): {config.chunk_overlap}
            </label>
            <input
              id="chunk-overlap"
              type="range"
              min="0"
              max="500"
              step="50"
              value={config.chunk_overlap}
              onChange={(e) => handleInputChange('chunk_overlap', parseInt(e.target.value))}
              disabled={isLoading}
            />
            <small>Overlap helps maintain context across chunk boundaries</small>
          </div>
        )}

        {/* Embedding Model */}
        <div className="rag-setting-group">
          <label htmlFor="embedding-model">🧠 Embedding Model</label>
          <select
            id="embedding-model"
            value={config.embedding_model}
            onChange={(e) => handleInputChange('embedding_model', e.target.value)}
            disabled={isLoading}
          >
            <option value="all-MiniLM-L6-v2">MiniLM-L6 (Fast, Recommended)</option>
            <option value="all-MiniLM-L12-v2">MiniLM-L12 (Better Quality)</option>
            <option value="all-mpnet-base-v2">MPNet-Base (Larger, Better)</option>
          </select>
        </div>

        {/* Ollama Model */}
        <div className="rag-setting-group">
          <label htmlFor="ollama-model">🦙 Ollama Model</label>
          <select
            id="ollama-model"
            value={config.ollama_model}
            onChange={(e) => handleInputChange('ollama_model', e.target.value)}
            disabled={isLoading}
          >
            <option value="gemma2:2b">Gemma2 2B (Fast)</option>
            <option value="llama2:7b">Llama2 7B (Balanced)</option>
            <option value="llama3:8b">Llama3 8B (Better Quality)</option>
            <option value="qwen2.5:7b">Qwen2.5 7B (Multilingual)</option>
          </select>
          <small>Requires Ollama installed and model pulled</small>
        </div>

        {/* Top-K Results */}
        <div className="rag-setting-group">
          <label htmlFor="top-k">🎯 Retrieved Results (Top-K): {config.top_k}</label>
          <input
            id="top-k"
            type="range"
            min="1"
            max="10"
            step="1"
            value={config.top_k}
            onChange={(e) => handleInputChange('top_k', parseInt(e.target.value))}
            disabled={isLoading}
          />
          <small>Number of most relevant chunks to retrieve for each query</small>
        </div>

        {showAdvanced && (
          <>
            {/* Similarity Threshold */}
            <div className="rag-setting-group">
              <label htmlFor="similarity-threshold">
                📊 Similarity Threshold: {(config.similarity_threshold || 0.3).toFixed(2)}
              </label>
              <input
                id="similarity-threshold"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.similarity_threshold || 0.3}
                onChange={(e) =>
                  handleInputChange('similarity_threshold', parseFloat(e.target.value))
                }
                disabled={isLoading}
              />
              <small>Minimum similarity score for results to be included</small>
            </div>

            {/* Temperature */}
            <div className="rag-setting-group">
              <label htmlFor="temperature">
                🌡️ Temperature: {(config.temperature || 0.3).toFixed(2)}
              </label>
              <input
                id="temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.temperature || 0.3}
                onChange={(e) =>
                  handleInputChange('temperature', parseFloat(e.target.value))
                }
                disabled={isLoading}
              />
              <small>Lower = more deterministic, Higher = more creative</small>
            </div>

            {/* Max Tokens */}
            <div className="rag-setting-group">
              <label htmlFor="max-tokens">
                📝 Max Response Tokens: {config.max_tokens}
              </label>
              <input
                id="max-tokens"
                type="range"
                min="128"
                max="2048"
                step="128"
                value={config.max_tokens}
                onChange={(e) => handleInputChange('max_tokens', parseInt(e.target.value))}
                disabled={isLoading}
              />
            </div>
          </>
        )}

        {/* Storage Path */}
        {showAdvanced && (
          <div className="rag-setting-group">
            <label>📁 Vector DB Path</label>
            <div className="rag-readonly-field">{config.vector_db_path}</div>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="rag-stats">
            <h4>📈 Statistics</h4>
            <ul>
              <li>
                <strong>Documents Indexed:</strong> {stats.vector_store?.document_count || 0}
              </li>
              <li>
                <strong>Embedding Dimension:</strong> {stats.embedding_model?.embedding_dimension}
              </li>
              <li>
                <strong>Collection:</strong> {stats.config?.collection_name}
              </li>
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="rag-settings-actions">
          <button
            className="rag-btn rag-btn-primary"
            onClick={onRebuildIndex}
            disabled={isLoading}
          >
            🔄 Rebuild Index
          </button>
          <button
            className="rag-btn rag-btn-danger"
            onClick={onClearIndex}
            disabled={isLoading}
          >
            🗑️ Clear All
          </button>
        </div>
      </div>
    </div>
  );
};
