import React from 'react';
import './RAGChat.css';

/**
 * RAG Chat component for querying indexed documents
 */
export const RAGChat = ({ onQuery, isLoading }) => {
  const [messages, setMessages] = React.useState([]);
  const [inputValue, setInputValue] = React.useState('');
  const [includeChunks, setIncludeChunks] = React.useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Get RAG response
    try {
      const result = await onQuery(inputValue, includeChunks);

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.answer,
        sources: result.sources,
        confidence: result.confidence,
        chunks: result.retrieved_chunks,
        model: result.model,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="rag-chat">
      <div className="rag-chat-header">
        <h2>📚 Document RAG Chat</h2>
        <label className="include-chunks-toggle">
          <input
            type="checkbox"
            checked={includeChunks}
            onChange={(e) => setIncludeChunks(e.target.checked)}
          />
          Show Retrieved Chunks
        </label>
      </div>

      <div className="rag-chat-messages">
        {messages.length === 0 ? (
          <div className="rag-empty-state">
            <p>Ask a question about your documents...</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`rag-message rag-message-${msg.type}`}>
              {msg.type === 'user' && (
                <div className="rag-message-content">
                  <strong>You:</strong> {msg.content}
                </div>
              )}

              {msg.type === 'assistant' && (
                <div className="rag-message-content">
                  <div className="rag-response-header">
                    <strong>Assistant ({msg.model})</strong>
                    <div className="rag-confidence">
                      Confidence: {(msg.confidence * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="rag-answer">
                    {msg.content}
                    <button
                      className="rag-copy-btn"
                      onClick={() => copyToClipboard(msg.content)}
                      title="Copy answer"
                    >
                      📋
                    </button>
                  </div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="rag-sources">
                      <strong>Sources:</strong>
                      <ul>
                        {msg.sources.map((source, idx) => (
                          <li key={idx}>
                            <span className="source-file">{source.filename}</span>
                            {source.heading && (
                              <span className="source-heading">{source.heading}</span>
                            )}
                            <span className="source-score">
                              ({(source.similarity_score * 100).toFixed(0)}% match)
                            </span>
                            <div className="source-excerpt">{source.excerpt}</div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {msg.chunks && msg.chunks.length > 0 && (
                    <details className="rag-chunks-detail">
                      <summary>View Full Chunks ({msg.chunks.length})</summary>
                      <div className="rag-chunks-container">
                        {msg.chunks.map((chunk, idx) => (
                          <div key={idx} className="rag-chunk">
                            <div className="rag-chunk-header">
                              Chunk {chunk.chunk_index} - {chunk.filename}
                              {chunk.metadata.heading && (
                                <span className="rag-chunk-heading">
                                  {chunk.metadata.heading}
                                </span>
                              )}
                            </div>
                            <div className="rag-chunk-text">{chunk.chunk_text}</div>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}

              {msg.type === 'error' && (
                <div className="rag-error-content">
                  <strong>Error:</strong> {msg.content}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSubmit} className="rag-chat-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={isLoading}
          className="rag-chat-input"
        />
        <button type="submit" disabled={isLoading} className="rag-send-btn">
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};
