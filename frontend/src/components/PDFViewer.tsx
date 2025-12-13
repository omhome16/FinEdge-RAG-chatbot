import { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, FileText, ExternalLink, AlertCircle, RefreshCw } from 'lucide-react';
import { getPdfUrl, type Citation } from '../api';

interface PDFViewerProps {
    isOpen: boolean;
    onClose: () => void;
    citation: Citation | null;
    docId: string;
}

/**
 * PDFViewer Sidebar Component
 * Opens when a citation is clicked, showing the relevant PDF page.
 * Uses object tag to display PDF with page navigation.
 */
export default function PDFViewer({ isOpen, onClose, citation, docId }: PDFViewerProps) {
    const [currentPage, setCurrentPage] = useState(1);
    const [zoom, setZoom] = useState(100);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const [loadKey, setLoadKey] = useState(0);

    useEffect(() => {
        if (citation?.page_number) {
            setCurrentPage(citation.page_number);
        }
        // Reset states when citation changes
        setLoading(true);
        setError(false);
        setLoadKey(prev => prev + 1);
    }, [citation, docId]);

    // Auto-hide loading spinner after 2 seconds (iframe onLoad is unreliable for PDFs)
    useEffect(() => {
        if (loading && isOpen && docId) {
            const timer = setTimeout(() => {
                setLoading(false);
            }, 2000);
            return () => clearTimeout(timer);
        }
    }, [loading, isOpen, docId, loadKey]);

    if (!isOpen || !docId) return null;

    const pdfUrl = getPdfUrl(docId);
    // Add page parameter and timestamp to avoid caching issues
    const pdfUrlWithPage = `${pdfUrl}#page=${currentPage}`;

    const handlePrevPage = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
        setLoading(true);
    };

    const handleNextPage = () => {
        setCurrentPage((prev) => prev + 1);
        setLoading(true);
    };

    const handleZoomIn = () => {
        setZoom((prev) => Math.min(200, prev + 25));
    };

    const handleZoomOut = () => {
        setZoom((prev) => Math.max(50, prev - 25));
    };

    const handleRetry = () => {
        setError(false);
        setLoading(true);
        setLoadKey(prev => prev + 1);
    };

    return (
        <div className="pdf-viewer-sidebar">
            {/* Header */}
            <div className="pdf-viewer-header">
                <div className="pdf-viewer-title">
                    <FileText size={18} />
                    <span>Document Viewer</span>
                </div>
                <button className="pdf-viewer-close" onClick={onClose}>
                    <X size={20} />
                </button>
            </div>

            {/* Citation Info */}
            {citation && (
                <div className="pdf-citation-info">
                    <div className="citation-source">
                        <strong>{citation.source}</strong>
                        <span className="citation-page">Page {citation.page_number}</span>
                    </div>
                    {citation.text_snippet && (
                        <div className="citation-snippet">
                            "{citation.text_snippet.slice(0, 150)}..."
                        </div>
                    )}
                </div>
            )}

            {/* Controls */}
            <div className="pdf-viewer-controls">
                <div className="page-controls">
                    <button onClick={handlePrevPage} disabled={currentPage <= 1}>
                        <ChevronLeft size={18} />
                    </button>
                    <span className="page-indicator">Page {currentPage}</span>
                    <button onClick={handleNextPage}>
                        <ChevronRight size={18} />
                    </button>
                </div>
                <div className="zoom-controls">
                    <button onClick={handleZoomOut} disabled={zoom <= 50}>
                        <ZoomOut size={18} />
                    </button>
                    <span className="zoom-indicator">{zoom}%</span>
                    <button onClick={handleZoomIn} disabled={zoom >= 200}>
                        <ZoomIn size={18} />
                    </button>
                </div>
                <a
                    href={pdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="open-external"
                    title="Open in new tab"
                >
                    <ExternalLink size={18} />
                </a>
            </div>

            {/* PDF Display */}
            <div className="pdf-viewer-content">
                {loading && !error && (
                    <div className="pdf-loading">
                        <div className="loading-spinner"></div>
                        <span>Loading PDF...</span>
                    </div>
                )}

                {error && (
                    <div className="pdf-error">
                        <AlertCircle size={48} className="text-red-500" />
                        <p>Failed to load PDF</p>
                        <button onClick={handleRetry} className="retry-button">
                            <RefreshCw size={16} />
                            Retry
                        </button>
                        <a href={pdfUrl} target="_blank" rel="noopener noreferrer" className="open-external-link">
                            Open in new tab instead
                        </a>
                    </div>
                )}

                {!error && (
                    <iframe
                        key={loadKey}
                        src={pdfUrlWithPage}
                        title="PDF Viewer"
                        style={{
                            width: '100%',
                            height: '100%',
                            border: 'none',
                            transform: `scale(${zoom / 100})`,
                            transformOrigin: 'top left',
                        }}
                    />
                )}

                {/* Highlight overlay - visible when bbox is provided */}
                {citation?.bbox && !loading && !error && (
                    <div
                        className="pdf-highlight-overlay"
                        style={{
                            position: 'absolute',
                            left: `${(citation.bbox[0] / 612) * 100}%`,
                            top: `${(citation.bbox[1] / 792) * 100}%`,
                            width: `${((citation.bbox[2] - citation.bbox[0]) / 612) * 100}%`,
                            height: `${((citation.bbox[3] - citation.bbox[1]) / 792) * 100}%`,
                            backgroundColor: 'rgba(255, 235, 59, 0.3)',
                            border: '2px solid #FFC107',
                            pointerEvents: 'none',
                        }}
                    />
                )}
            </div>
        </div>
    );
}
