import React from 'react';
import './RAGIndexer.css';

/**
 * RAG Indexer component for indexing documents
 */
export const RAGIndexer = ({ onIndex, onSuccess, isLoading }) => {
  const [selectedFiles, setSelectedFiles] = React.useState([]);
  const [progress, setProgress] = React.useState(null);
  const [clearExisting, setClearExisting] = React.useState(false);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(files);
  };

  const handleIndexClick = async () => {
    if (selectedFiles.length === 0) return;

    for (let file of selectedFiles) {
      try {
        setProgress(`Indexing ${file.name}...`);
        await onIndex(file, clearExisting);
        setProgress(`✓ Indexed ${file.name}`);
      } catch (error) {
        setProgress(`✗ Failed to index ${file.name}: ${error.message}`);
      }
    }

    setProgress(null);
    setSelectedFiles([]);
    if (onSuccess) onSuccess();
  };

  return (
    <div className="rag-indexer">
      <div className="rag-indexer-header">
        <h3>📚 Index Documents</h3>
      </div>

      <div className="rag-indexer-content">
        <p>Select Markdown or JSON files to index for RAG search.</p>

        <div className="rag-file-input-group">
          <input
            type="file"
            multiple
            accept=".md,.json,.markdown"
            onChange={handleFileSelect}
            disabled={isLoading}
            className="rag-file-input"
          />
          <div className="rag-selected-files">
            {selectedFiles.length > 0 && (
              <>
                <strong>Selected Files ({selectedFiles.length}):</strong>
                <ul>
                  {selectedFiles.map((file, idx) => (
                    <li key={idx}>{file.name}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>

        <label className="rag-clear-checkbox">
          <input
            type="checkbox"
            checked={clearExisting}
            onChange={(e) => setClearExisting(e.target.checked)}
            disabled={isLoading}
          />
          Clear existing index before indexing
        </label>

        <div className="rag-indexer-actions">
          <button
            className="rag-btn rag-btn-primary"
            onClick={handleIndexClick}
            disabled={isLoading || selectedFiles.length === 0}
          >
            {isLoading ? '⏳ Indexing...' : '📤 Index Documents'}
          </button>
        </div>

        {progress && (
          <div className="rag-progress-message">
            {progress}
          </div>
        )}
      </div>
    </div>
  );
};
