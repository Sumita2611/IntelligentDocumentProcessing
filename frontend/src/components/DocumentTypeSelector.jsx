import React from 'react';
import { Cpu, FileText, CheckCircle2, Sliders, Info } from 'lucide-react';

const DOC_TYPE_DETAILS = {
  automatic: {
    method: 'Dynamic Router — Auto detects format and content stream',
    output: 'Text, tables, and structured metadata',
    badge: 'Recommended'
  },
  scanned_pdf: {
    method: 'PDF pages → High-DPI render → OCR + layout analysis',
    output: 'Text per page + reconstructed layout',
    badge: 'OCR Pipeline'
  },
  digital_pdf: {
    method: 'Direct text stream extraction + layout block parsing',
    output: 'Lossless text + detected native tables',
    badge: 'Fast Parser'
  },
  handwritten_image: {
    method: 'Line segmentation → TrOCR VisionEncoderDecoder model',
    output: 'Recognized handwriting transcription',
    badge: 'Deep Learning'
  },
  printed_image: {
    method: 'Image contrast enhancement → Docling / RapidOCR / Tesseract',
    output: 'Text blocks with bounding box confidences',
    badge: 'OCR Engine'
  },
  excel_csv: {
    method: 'openpyxl & pandas native sheet and delimiter parser',
    output: 'Sheet names, structured grid cells, and metrics',
    badge: 'Tabular Data'
  },
  table_image: {
    method: 'OCR text line coordinate clustering & grid boundary recovery',
    output: 'Structured rows and columns table matrix',
    badge: 'Table Reconstructor'
  }
};

export default function DocumentTypeSelector({
  documentTypes,
  selectedDocType,
  onSelectDocType,
  engines,
  selectedEngine,
  onSelectEngine
}) {
  const currentDetail = DOC_TYPE_DETAILS[selectedDocType] || DOC_TYPE_DETAILS.automatic;

  return (
    <div className="d-flex flex-column gap-3">
      {/* Document Type Dropdown */}
      <div>
        <label htmlFor="docTypeSelect" className="form-label text-light small fw-semibold d-flex align-items-center justify-content-between mb-2">
          <span className="d-flex align-items-center gap-2">
            <FileText size={16} className="text-primary" />
            Document Type
          </span>
          {currentDetail.badge && (
            <span className="badge badge-glass-indigo" style={{ fontSize: '0.7rem' }}>
              {currentDetail.badge}
            </span>
          )}
        </label>
        
        <select
          id="docTypeSelect"
          className="form-select form-select-dark"
          value={selectedDocType}
          onChange={(e) => onSelectDocType(e.target.value)}
        >
          {documentTypes && documentTypes.length > 0 ? (
            documentTypes.map((dt) => (
              <option key={dt.key} value={dt.key}>
                {dt.label} {dt.badge ? `(${dt.badge})` : ''}
              </option>
            ))
          ) : (
            <>
              <option value="automatic">Automatic detection (Recommended)</option>
              <option value="scanned_pdf">Scanned PDF</option>
              <option value="digital_pdf">Digital PDF</option>
              <option value="handwritten_image">Handwritten image</option>
              <option value="printed_image">Printed document image</option>
              <option value="excel_csv">Excel / CSV</option>
              <option value="table_image">Photograph of a table</option>
            </>
          )}
        </select>

        {/* Method & Output Preview Box */}
        <div 
          className="mt-2 p-2 px-3 rounded-2 small"
          style={{ 
            background: 'rgba(99, 102, 241, 0.08)', 
            border: '1px solid rgba(99, 102, 241, 0.2)',
            fontSize: '0.78rem',
            lineHeight: 1.4
          }}
        >
          <div className="text-light">
            <span className="text-muted">Method:</span> {currentDetail.method}
          </div>
          <div className="text-light mt-1">
            <span className="text-muted">Output:</span> <span style={{ color: 'var(--accent-secondary)' }}>{currentDetail.output}</span>
          </div>
        </div>
      </div>

      {/* Extraction Engine Dropdown */}
      <div>
        <label htmlFor="engineSelect" className="form-label text-light small fw-semibold d-flex align-items-center justify-content-between mb-2">
          <span className="d-flex align-items-center gap-2">
            <Sliders size={16} className="text-info" />
            Extraction Engine
          </span>
          <span className="text-muted small" style={{ fontSize: '0.72rem' }}>
            Multi-engine Router
          </span>
        </label>

        <select
          id="engineSelect"
          className="form-select form-select-dark"
          value={selectedEngine}
          onChange={(e) => onSelectEngine(e.target.value)}
        >
          {engines && engines.length > 0 ? (
            engines.map((eng) => (
              <option key={eng.key} value={eng.key}>
                {eng.label}
              </option>
            ))
          ) : (
            <>
              <option value="automatic">Automatic — choose the appropriate processing pipeline</option>
              <option value="docling">Docling Document Intelligence</option>
              <option value="rapidocr">RapidOCR Deep Engine (ONNX)</option>
              <option value="tesseract">Tesseract OCR</option>
              <option value="trocr">TrOCR (Transformer Handwriting)</option>
              <option value="spreadsheet">openpyxl + pandas Parser</option>
            </>
          )}
        </select>
      </div>
    </div>
  );
}
