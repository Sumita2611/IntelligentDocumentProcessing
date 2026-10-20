import React from 'react';
import { Sparkles, FileSpreadsheet, FileText, Image as ImageIcon, Check } from 'lucide-react';

export default function SampleSelector({ samples, activeSampleId, onSelectSample, isProcessing }) {
  if (!samples || samples.length === 0) return null;

  const getSampleIcon = (type) => {
    if (type.includes('excel')) return <FileSpreadsheet size={15} className="text-success" />;
    if (type.includes('pdf')) return <FileText size={15} className="text-primary" />;
    return <ImageIcon size={15} className="text-info" />;
  };

  return (
    <div className="mt-4 pt-3 border-top" style={{ borderColor: 'var(--border-card)' }}>
      <div className="d-flex align-items-center justify-content-between mb-2">
        <span className="small fw-semibold text-light d-flex align-items-center gap-2">
          <Sparkles size={14} style={{ color: 'var(--accent-secondary)' }} />
          Or Test Drive Pre-loaded Samples
        </span>
        <span className="text-muted small" style={{ fontSize: '0.72rem' }}>
          One-click extraction
        </span>
      </div>

      <div className="d-flex flex-wrap gap-2">
        {samples.map((s) => {
          const isSelected = activeSampleId === s.id;
          return (
            <button
              key={s.id}
              type="button"
              disabled={isProcessing}
              className="btn btn-sm text-start rounded-pill px-3 py-1 d-flex align-items-center gap-2"
              style={{
                background: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                border: `1px solid ${isSelected ? 'rgba(99, 102, 241, 0.5)' : 'var(--border-card)'}`,
                color: isSelected ? '#fff' : 'var(--text-muted)',
                fontSize: '0.78rem',
                transition: 'all 0.2s ease',
              }}
              onClick={() => onSelectSample(s)}
            >
              {getSampleIcon(s.doc_type)}
              <span>{s.title}</span>
              {isSelected && <Check size={13} className="text-info" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
