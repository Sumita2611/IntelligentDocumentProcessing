import React, { useState } from 'react';
import { 
  FileText, 
  Table as TableIcon, 
  Layers, 
  FileCode, 
  Code2, 
  CheckCircle2, 
  Clock, 
  Zap, 
  Search, 
  Copy, 
  Check, 
  ExternalLink 
} from 'lucide-react';
import ExportButtons from './ExportButtons';

export default function ResultsViewer({ result, isProcessing }) {
  const [activeTab, setActiveTab] = useState('text');
  const [activeTableIndex, setActiveTableIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedText, setCopiedText] = useState(false);

  if (isProcessing) {
    return (
      <div className="glass-panel p-5 text-center my-4 processing-active">
        <div className="spinner-border text-primary mb-3" style={{ width: '3.5rem', height: '3.5rem' }} role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <h4 className="fw-bold text-light mb-1">Extracting Document Intelligence</h4>
        <p className="text-muted small mb-0">
          Routing document through neural OCR, layout analysis, and structure reconstruction...
        </p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="glass-panel p-5 text-center my-4 text-muted">
        <div 
          className="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle"
          style={{ width: '64px', height: '64px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-card)' }}
        >
          <FileText size={28} className="text-muted opacity-50" />
        </div>
        <h5 className="fw-semibold text-light mb-1">Results Preview Workspace</h5>
        <p className="small mb-0" style={{ maxWidth: '420px', margin: '0 auto' }}>
          Upload a document or choose a sample above to extract readable text, structured tables, and layout analytics.
        </p>
      </div>
    );
  }

  const tables = result.tables || [];
  const pages = result.pages || [];
  const currentTable = tables[activeTableIndex] || tables[0];

  // Filter text by search term
  const fullText = result.text || '';
  const filteredTextLines = searchTerm
    ? fullText.split('\n').filter(line => line.toLowerCase().includes(searchTerm.toLowerCase()))
    : fullText.split('\n');

  const copyTableCSV = (table) => {
    if (!table) return;
    const headerStr = (table.columns || []).join(',');
    const rowsStr = (table.rows || []).map(r => r.join(',')).join('\n');
    const csvContent = `${headerStr}\n${rowsStr}`;
    navigator.clipboard.writeText(csvContent);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  return (
    <div className="glass-panel overflow-hidden my-4">
      {/* Top Metadata Header */}
      <div className="p-3 px-4 glass-header d-flex flex-wrap align-items-center justify-content-between gap-3">
        <div>
          <div className="d-flex align-items-center gap-2 mb-1">
            <span className="fw-bold text-light fs-5">
              {result.filename}
            </span>
            <span className="badge badge-glass-indigo" style={{ fontSize: '0.72rem' }}>
              {result.detected_type_label || result.detected_type}
            </span>
          </div>

          <div className="d-flex flex-wrap align-items-center gap-3 text-muted small" style={{ fontSize: '0.8rem' }}>
            <span className="d-flex align-items-center gap-1">
              <Zap size={14} className="text-warning" />
              Engine: <strong className="text-light">{result.routed_engine}</strong>
            </span>
            <span className="d-flex align-items-center gap-1">
              <Clock size={14} className="text-info" />
              Time: <strong className="text-light">{result.processing_time_seconds}s</strong>
            </span>
            <span className="d-flex align-items-center gap-1">
              <CheckCircle2 size={14} className="text-success" />
              Confidence: <strong className="text-light">{result.confidence_score}%</strong>
            </span>
            <span>Words: <strong className="text-light">{result.word_count || 0}</strong></span>
            {tables.length > 0 && (
              <span>Tables: <strong className="text-light">{tables.length}</strong></span>
            )}
            {pages.length > 0 && (
              <span>Pages: <strong className="text-light">{pages.length}</strong></span>
            )}
          </div>
        </div>

        {/* Confidence Progress Ring */}
        <div className="d-flex align-items-center gap-2">
          <div 
            className="px-3 py-1 rounded-pill"
            style={{ 
              background: result.confidence_score > 90 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              border: `1px solid ${result.confidence_score > 90 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`,
              fontSize: '0.82rem',
              color: result.confidence_score > 90 ? '#6ee7b7' : '#fcd34d'
            }}
          >
            {result.confidence_score > 90 ? 'High Fidelity' : 'Good Confidence'} ({result.confidence_score}%)
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="px-4 pt-3 border-bottom d-flex align-items-center justify-content-between flex-wrap gap-2" style={{ borderColor: 'var(--border-card)' }}>
        <ul className="nav nav-pills nav-pills-custom gap-2 mb-2">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'text' ? 'active' : ''}`}
              onClick={() => setActiveTab('text')}
            >
              <FileText size={16} />
              <span>Extracted Text</span>
            </button>
          </li>

          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'tables' ? 'active' : ''}`}
              onClick={() => setActiveTab('tables')}
            >
              <TableIcon size={16} />
              <span>Tables ({tables.length})</span>
            </button>
          </li>

          {pages.length > 0 && (
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'pages' ? 'active' : ''}`}
                onClick={() => setActiveTab('pages')}
              >
                <Layers size={16} />
                <span>Pages ({pages.length})</span>
              </button>
            </li>
          )}

          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'markdown' ? 'active' : ''}`}
              onClick={() => setActiveTab('markdown')}
            >
              <FileCode size={16} />
              <span>Markdown</span>
            </button>
          </li>

          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'json' ? 'active' : ''}`}
              onClick={() => setActiveTab('json')}
            >
              <Code2 size={16} />
              <span>Raw JSON</span>
            </button>
          </li>
        </ul>

        {/* Quick Search in Extracted Text */}
        {activeTab === 'text' && (
          <div className="position-relative mb-2" style={{ minWidth: '220px' }}>
            <Search size={14} className="position-absolute text-muted" style={{ left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search in text..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-control form-control-dark form-control-sm ps-4"
              style={{ fontSize: '0.8rem', height: '32px' }}
            />
          </div>
        )}
      </div>

      {/* Tab Panels */}
      <div className="p-4">
        {/* Tab 1: Extracted Text */}
        {activeTab === 'text' && (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="small text-muted">
                Showing {filteredTextLines.length} lines of extracted text
                {searchTerm && ` (filtered by "${searchTerm}")`}
              </span>
            </div>
            <pre className="code-preview" style={{ maxHeight: '480px' }}>
              {filteredTextLines.length > 0
                ? filteredTextLines.join('\n')
                : '(No matching text found)'}
            </pre>
          </div>
        )}

        {/* Tab 2: Structured Tables */}
        {activeTab === 'tables' && (
          <div>
            {tables.length === 0 ? (
              <div className="text-center py-5 text-muted">
                <TableIcon size={36} className="mb-2 opacity-50" />
                <p className="mb-0">No structured tabular data detected in this document.</p>
              </div>
            ) : (
              <div>
                {/* Multi-table picker pills if more than 1 table */}
                {tables.length > 1 && (
                  <div className="d-flex flex-wrap gap-2 mb-3">
                    {tables.map((tbl, i) => (
                      <button
                        key={tbl.id || i}
                        className={`btn btn-sm rounded-pill px-3 py-1 ${activeTableIndex === i ? 'btn-primary' : 'btn-outline-secondary'}`}
                        style={{ fontSize: '0.8rem' }}
                        onClick={() => setActiveTableIndex(i)}
                      >
                        {tbl.title || `Table ${i + 1}`} ({tbl.row_count || tbl.rows?.length || 0} rows)
                      </button>
                    ))}
                  </div>
                )}

                {/* Table Title and Actions */}
                <div className="d-flex align-items-center justify-content-between mb-2">
                  <div className="d-flex align-items-center gap-2">
                    <span className="fw-semibold text-light">
                      {currentTable.title || `Table ${activeTableIndex + 1}`}
                    </span>
                    <span className="badge badge-glass-cyan small">
                      {currentTable.rows?.length || 0} rows × {currentTable.columns?.length || 0} cols
                    </span>
                  </div>

                  <button
                    type="button"
                    className="btn btn-sm btn-outline-light rounded-pill px-2 py-1 d-flex align-items-center gap-1"
                    style={{ fontSize: '0.75rem' }}
                    onClick={() => copyTableCSV(currentTable)}
                  >
                    {copiedText ? <Check size={13} className="text-success" /> : <Copy size={13} />}
                    <span>{copiedText ? 'Copied CSV' : 'Copy Table as CSV'}</span>
                  </button>
                </div>

                {/* Interactive Table Grid */}
                <div className="table-responsive rounded-3 border" style={{ borderColor: 'var(--border-card)', maxHeight: '450px' }}>
                  <table className="table table-custom table-hover">
                    <thead>
                      <tr>
                        <th style={{ width: '40px' }}>#</th>
                        {(currentTable.columns || []).map((col, idx) => (
                          <th key={idx}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(currentTable.rows || []).map((row, rIdx) => (
                        <tr key={rIdx}>
                          <td className="text-muted small">{rIdx + 1}</td>
                          {row.map((cell, cIdx) => (
                            <td key={cIdx}>
                              {cell !== null && cell !== undefined ? String(cell) : ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Pages & Layout */}
        {activeTab === 'pages' && (
          <div className="row g-3">
            {pages.map((p) => (
              <div key={p.page_number} className="col-12 col-md-6">
                <div className="p-3 rounded-3 h-100" style={{ background: 'rgba(15, 20, 34, 0.7)', border: '1px solid var(--border-card)' }}>
                  <div className="d-flex align-items-center justify-content-between mb-2 pb-2 border-bottom" style={{ borderColor: 'var(--border-card)' }}>
                    <span className="fw-semibold text-light small">
                      Page {p.page_number}
                    </span>
                    <div className="d-flex gap-2">
                      <span className="badge badge-glass-indigo small">{p.word_count || 0} words</span>
                      <span className="badge badge-glass-emerald small">{p.confidence || 98}% conf</span>
                    </div>
                  </div>
                  <pre className="text-muted small mb-0" style={{ maxHeight: '200px', overflowY: 'auto', whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                    {p.text || '(No text on this page)'}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 4: Markdown Preview */}
        {activeTab === 'markdown' && (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="small text-muted">GitHub-Flavored Markdown preview</span>
            </div>
            <pre className="code-preview" style={{ maxHeight: '480px' }}>
              {result.markdown || '(No markdown generated)'}
            </pre>
          </div>
        )}

        {/* Tab 5: Raw JSON */}
        {activeTab === 'json' && (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="small text-muted">Complete JSON payload with bounding boxes and metadata</span>
            </div>
            <pre className="code-preview" style={{ maxHeight: '480px' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Export Bar */}
      <ExportButtons extractionResult={result} />
    </div>
  );
}
