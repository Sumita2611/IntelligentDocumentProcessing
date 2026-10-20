import React from 'react';
import { Layers, Cpu, CheckCircle2, Sparkles, BookOpen } from 'lucide-react';

export default function Header({ backendHealth }) {
  return (
    <header className="py-4 mb-4 border-bottom" style={{ borderColor: 'var(--border-card)' }}>
      <div className="container-fluid px-lg-5">
        <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
          
          {/* Logo & Branding */}
          <div className="d-flex align-items-center gap-3">
            <div 
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)'
              }}
            >
              <Layers size={26} color="#ffffff" />
            </div>

            <div>
              <div className="d-flex align-items-center gap-2">
                <h1 className="h4 mb-0 fw-bold tracking-tight" style={{ color: '#fff', letterSpacing: '-0.5px' }}>
                  OmniOCR
                </h1>
                <span className="badge badge-glass-indigo text-uppercase" style={{ fontSize: '0.65rem', letterSpacing: '0.5px' }}>
                  v1.0 • Enterprise
                </span>
              </div>
              <p className="mb-0 text-muted small">
                Document Intelligence <span className="mx-1">•</span> <span style={{ color: 'var(--accent-secondary)' }}>Extract. Understand. Export.</span>
              </p>
            </div>
          </div>

          {/* Engine Status Badges */}
          <div className="d-flex flex-wrap align-items-center gap-2">
            <div className="d-flex align-items-center gap-2 px-3 py-1 rounded-pill" style={{ background: 'rgba(15, 20, 34, 0.8)', border: '1px solid var(--border-card)', fontSize: '0.78rem' }}>
              <span className="d-inline-block rounded-circle bg-success" style={{ width: '8px', height: '8px' }}></span>
              <span className="text-muted">Docling Core:</span>
              <span className="text-light fw-medium">Active</span>
            </div>

            <div className="d-flex align-items-center gap-2 px-3 py-1 rounded-pill" style={{ background: 'rgba(15, 20, 34, 0.8)', border: '1px solid var(--border-card)', fontSize: '0.78rem' }}>
              <span className="d-inline-block rounded-circle bg-info" style={{ width: '8px', height: '8px' }}></span>
              <span className="text-muted">OCR Pipeline:</span>
              <span className="text-light fw-medium">RapidOCR + Tesseract</span>
            </div>

            <div className="d-flex align-items-center gap-2 px-3 py-1 rounded-pill" style={{ background: 'rgba(15, 20, 34, 0.8)', border: '1px solid var(--border-card)', fontSize: '0.78rem' }}>
              <Sparkles size={13} style={{ color: 'var(--accent-primary)' }} />
              <span className="text-muted">TrOCR:</span>
              <span className="text-light fw-medium">Ready</span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
