import React, { useState } from 'react';
import { Download, FileText, Code2, Table, FileCode, Check, Copy } from 'lucide-react';
import { exportDocument } from '../services/api';

export default function ExportButtons({ extractionResult }) {
  const [copied, setCopied] = useState(false);
  const [exportingFormat, setExportingFormat] = useState(null);

  if (!extractionResult) return null;

  const handleExport = async (format) => {
    try {
      setExportingFormat(format);
      await exportDocument(format, extractionResult);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setExportingFormat(null);
    }
  };

  const handleCopyText = () => {
    if (extractionResult?.text) {
      navigator.clipboard.writeText(extractionResult.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 p-3 border-top" style={{ borderColor: 'var(--border-card)', background: 'rgba(15, 20, 34, 0.4)' }}>
      <div className="d-flex align-items-center gap-2">
        <span className="small text-muted fw-semibold text-uppercase" style={{ fontSize: '0.75rem', letterSpacing: '0.5px' }}>
          Export Formats:
        </span>
        <button
          type="button"
          className="btn btn-export"
          disabled={exportingFormat !== null}
          onClick={() => handleExport('txt')}
          title="Download plain text"
        >
          <FileText size={14} className="text-primary" />
          <span>TXT</span>
        </button>

        <button
          type="button"
          className="btn btn-export"
          disabled={exportingFormat !== null}
          onClick={() => handleExport('json')}
          title="Download JSON structured representation"
        >
          <Code2 size={14} className="text-warning" />
          <span>JSON</span>
        </button>

        <button
          type="button"
          className="btn btn-export"
          disabled={exportingFormat !== null}
          onClick={() => handleExport('csv')}
          title="Download tabular CSV"
        >
          <Table size={14} className="text-success" />
          <span>CSV</span>
        </button>

        <button
          type="button"
          className="btn btn-export"
          disabled={exportingFormat !== null}
          onClick={() => handleExport('markdown')}
          title="Download GitHub-Flavored Markdown"
        >
          <FileCode size={14} className="text-info" />
          <span>Markdown</span>
        </button>
      </div>

      <div>
        <button
          type="button"
          className="btn btn-sm btn-outline-light d-flex align-items-center gap-2 rounded-pill px-3 py-1"
          style={{ fontSize: '0.8rem', borderColor: 'var(--border-card)' }}
          onClick={handleCopyText}
        >
          {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
          <span>{copied ? 'Copied to Clipboard' : 'Copy All Text'}</span>
        </button>
      </div>
    </div>
  );
}
