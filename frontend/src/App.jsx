import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Layers, 
  Sparkles, 
  ArrowRight, 
  History, 
  CheckCircle, 
  AlertTriangle,
  RotateCcw
} from 'lucide-react';

import Header from './components/Header';
import FileUploader from './components/FileUploader';
import DocumentTypeSelector from './components/DocumentTypeSelector';
import SampleSelector from './components/SampleSelector';
import ResultsViewer from './components/ResultsViewer';

import { 
  fetchDocumentTypes, 
  fetchEngines, 
  fetchSamples, 
  extractDocument, 
  extractSample 
} from './services/api';

export default function App() {
  const [documentTypes, setDocumentTypes] = useState([]);
  const [engines, setEngines] = useState([]);
  const [samples, setSamples] = useState([]);

  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedDocType, setSelectedDocType] = useState('automatic');
  const [selectedEngine, setSelectedEngine] = useState('automatic');
  const [activeSampleId, setActiveSampleId] = useState(null);

  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [extractionResult, setExtractionResult] = useState(null);
  const [history, setHistory] = useState([]);

  // Load initial backend configuration
  useEffect(() => {
    async function loadData() {
      try {
        const [typesData, enginesData, samplesData] = await Promise.all([
          fetchDocumentTypes().catch(() => ({ document_types: [] })),
          fetchEngines().catch(() => ({ engines: [] })),
          fetchSamples().catch(() => ({ samples: [] }))
        ]);
        setDocumentTypes(typesData.document_types || []);
        setEngines(enginesData.engines || []);
        setSamples(samplesData.samples || []);
      } catch (e) {
        console.error('Initial configuration load error:', e);
      }
    }
    loadData();
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setActiveSampleId(null);
    setError(null);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setActiveSampleId(null);
    setError(null);
  };

  const handleExtract = async () => {
    if (!selectedFile && !activeSampleId) {
      setError('Please select a file or choose a sample document first.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      let result;
      if (activeSampleId) {
        result = await extractSample(activeSampleId, selectedEngine);
      } else {
        result = await extractDocument(selectedFile, selectedDocType, selectedEngine);
      }

      setExtractionResult(result);
      // Append to session history (max 8)
      setHistory((prev) => [result, ...prev.filter(h => h.filename !== result.filename)].slice(0, 8));
    } catch (err) {
      setError(err.message || 'An error occurred during extraction.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSelectSample = async (sample) => {
    setActiveSampleId(sample.id);
    setSelectedFile(null);
    setSelectedDocType(sample.doc_type || 'automatic');
    setError(null);

    // Automatically trigger extraction for quick demo
    setIsProcessing(true);
    try {
      const result = await extractSample(sample.id, selectedEngine);
      setExtractionResult(result);
      setHistory((prev) => [result, ...prev.filter(h => h.filename !== result.filename)].slice(0, 8));
    } catch (err) {
      setError(err.message || 'Sample extraction failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex flex-column">
      <Header />

      <main className="container-fluid px-lg-5 flex-grow-1 pb-5">
        <div className="row g-4">
          
          {/* Left Column: Extraction Workspace Controls */}
          <div className="col-12 col-xl-5">
            <div className="glass-panel p-4 h-100 d-flex flex-column justify-content-between">
              <div>
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <div>
                    <h2 className="h5 fw-bold text-light mb-0">
                      Document Extraction Workspace
                    </h2>
                    <p className="text-muted small mb-0">
                      Upload files or select samples to process with multi-format neural pipelines.
                    </p>
                  </div>
                  <span className="badge badge-glass-indigo small">
                    Pipeline Router
                  </span>
                </div>

                {/* Drag and Drop Zone */}
                <div className="mb-4">
                  <FileUploader
                    selectedFile={selectedFile}
                    onFileSelect={handleFileSelect}
                    onClearFile={handleClearFile}
                    error={error}
                  />
                </div>

                {/* Document Type & Engine Selectors */}
                <div className="mb-4">
                  <DocumentTypeSelector
                    documentTypes={documentTypes}
                    selectedDocType={selectedDocType}
                    onSelectDocType={setSelectedDocType}
                    engines={engines}
                    selectedEngine={selectedEngine}
                    onSelectEngine={setSelectedEngine}
                  />
                </div>

                {/* Preloaded Samples Bar */}
                <SampleSelector
                  samples={samples}
                  activeSampleId={activeSampleId}
                  onSelectSample={handleSelectSample}
                  isProcessing={isProcessing}
                />
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-3 border-top" style={{ borderColor: 'var(--border-card)' }}>
                <div className="d-flex align-items-center gap-3">
                  <button
                    type="button"
                    className="btn btn-extract flex-grow-1"
                    disabled={isProcessing || (!selectedFile && !activeSampleId)}
                    onClick={handleExtract}
                  >
                    {isProcessing ? (
                      <>
                        <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                        <span>Extracting Contents...</span>
                      </>
                    ) : (
                      <>
                        <span>Extract Document</span>
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>

                  {(selectedFile || activeSampleId || extractionResult) && (
                    <button
                      type="button"
                      className="btn btn-outline-secondary rounded-3 px-3 py-2 d-flex align-items-center justify-content-center"
                      onClick={() => {
                        handleClearFile();
                        setExtractionResult(null);
                      }}
                      title="Reset workspace"
                    >
                      <RotateCcw size={16} />
                    </button>
                  )}
                </div>
              </div>

            </div>
          </div>

          {/* Right Column: Results & Analytics */}
          <div className="col-12 col-xl-7">
            {/* Session History Quick Selector */}
            {history.length > 0 && (
              <div className="glass-panel p-2 px-3 mb-3 d-flex align-items-center justify-content-between flex-wrap gap-2">
                <span className="small text-muted d-flex align-items-center gap-2">
                  <History size={14} className="text-primary" />
                  Recent extractions ({history.length}):
                </span>
                <div className="d-flex flex-wrap gap-1">
                  {history.map((item, idx) => (
                    <button
                      key={idx}
                      className={`btn btn-sm py-0 px-2 rounded-pill ${extractionResult?.filename === item.filename ? 'btn-primary' : 'btn-outline-secondary'}`}
                      style={{ fontSize: '0.72rem' }}
                      onClick={() => setExtractionResult(item)}
                    >
                      {item.filename.length > 20 ? item.filename.slice(0, 18) + '...' : item.filename}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Results Viewer */}
            <ResultsViewer
              result={extractionResult}
              isProcessing={isProcessing}
            />
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-3 border-top mt-auto text-center text-muted small" style={{ borderColor: 'var(--border-card)' }}>
        <div className="container">
          <span>OmniOCR Document Intelligence Platform</span> <span className="mx-2">•</span> 
          <span>Powered by Docling, RapidOCR, Tesseract, TrOCR & PyMuPDF</span>
        </div>
      </footer>
    </div>
  );
}
