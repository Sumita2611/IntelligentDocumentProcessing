/**
 * OmniOCR API client service
 */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE = RAW_BASE ? `${RAW_BASE.replace(/\/+$/, '')}/api` : '/api';


export async function fetchDocumentTypes() {
  const res = await fetch(`${API_BASE}/document-types`);
  if (!res.ok) throw new Error('Failed to load document types');
  return res.json();
}

export async function fetchEngines() {
  const res = await fetch(`${API_BASE}/engines`);
  if (!res.ok) throw new Error('Failed to load OCR engines');
  return res.json();
}

export async function fetchSamples() {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) throw new Error('Failed to load sample documents');
  return res.json();
}

export async function extractDocument(file, documentType = 'automatic', engine = 'automatic') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);
  formData.append('engine', engine);

  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Extraction failed' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function extractSample(sampleId, engine = 'automatic') {
  const res = await fetch(`${API_BASE}/extract-sample/${sampleId}?engine=${encodeURIComponent(engine)}`, {
    method: 'POST',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Sample extraction failed' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function exportDocument(format, extractionData) {
  const res = await fetch(`${API_BASE}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      format: format.toLowerCase(),
      data: extractionData,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Export failed' }));
    throw new Error(errorData.detail || `Export error (${res.status})`);
  }

  // Trigger browser download
  const blob = await res.blob();
  const disposition = res.headers.get('Content-Disposition') || '';
  let filename = `${extractionData.filename || 'document'}_extracted.${format.toLowerCase()}`;
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  if (filenameMatch && filenameMatch[1]) {
    filename = filenameMatch[1];
  }

  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
