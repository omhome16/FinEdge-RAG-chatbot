"""
FinEdge Backend API v2.0
FastAPI backend with enhanced endpoints for document processing,
dynamic analytics, and RAG chat with citations.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import shutil
import os
import json
from typing import List, Optional, Dict, Any
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import get_rag_chain, query_documents
from src.ingestion import ingest_file, get_ingested_documents, delete_vectorstore, load_documents_metadata
from src.analytics_engine import analyze_document
from src.document_processor import DocumentProcessor
from src.analytics_storage import (
    save_analytics, 
    get_analytics, 
    has_analytics, 
    delete_analytics, 
    clear_all_analytics
)

app = FastAPI(
    title="FinEdge API v2.0",
    description="Financial Document Intelligence Platform",
    version="2.0.0"
)

# Upload folder configuration - use absolute path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploaded")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    sources: List[str]
    tables: List[Dict[str, Any]]

class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    total_pages: int
    total_chunks: int
    total_tables: int

class UploadResponse(BaseModel):
    filename: str
    doc_id: str
    status: str
    pages: int
    chunks: int
    tables: int
    analytics: Optional[Dict[str, Any]] = None

class AnalyticsResponse(BaseModel):
    document_type: str
    summary: str
    metrics: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    key_insights: List[str]


# ============ Startup ============

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG chain on startup if documents exist."""
    try:
        if os.path.exists("vectorstore"):
            chain = get_rag_chain()
            chain.initialize()
            print("RAG chain initialized with existing documents.")
    except Exception as e:
        print(f"Startup warning: {e}")


# ============ Document Endpoints ============

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document (PDF, DOCX, XLSX).
    Returns document info and dynamic analytics.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save file to uploaded folder
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"File saved to: {file_path}")
        
        # Process and ingest
        chunk_count, processed_doc = ingest_file(file_path)
        
        # Re-initialize RAG chain
        chain = get_rag_chain()
        chain.initialize()
        
        # Generate analytics
        full_content = "\n\n".join([c.content for c in processed_doc.chunks])
        tables_data = [t.to_dict() for t in processed_doc.tables]
        analytics = analyze_document(full_content, tables_data)
        
        # Save analytics to persistent storage
        save_analytics(processed_doc.doc_id, analytics)
        print(f"Analytics saved for document: {processed_doc.doc_id}")
        
        return UploadResponse(
            filename=file.filename,
            doc_id=processed_doc.doc_id,
            status="Ingested successfully",
            pages=processed_doc.total_pages,
            chunks=chunk_count,
            tables=len(processed_doc.tables),
            analytics=analytics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of all ingested documents with metadata."""
    try:
        docs = get_ingested_documents()
        return [
            DocumentInfo(
                doc_id=doc.get("doc_id", ""),
                filename=doc.get("filename", ""),
                file_type=doc.get("file_type", ""),
                total_pages=doc.get("total_pages", 0),
                total_chunks=doc.get("total_chunks", 0),
                total_tables=doc.get("total_tables", 0)
            )
            for doc in docs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents")
async def clear_all_documents():
    """Delete all documents and reset the vector store."""
    try:
        delete_vectorstore()
        # Clear analytics cache
        clear_all_analytics()
        
        # Clear uploaded directory (new location)
        if os.path.exists(UPLOAD_FOLDER):
            for f in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, f)
                if os.path.isfile(file_path) and not f.startswith('.'):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
        
        # Also clear legacy data directory
        data_folder = os.path.join(BASE_DIR, "data")
        if os.path.exists(data_folder):
            for f in os.listdir(data_folder):
                file_path = os.path.join(data_folder, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted (legacy): {file_path}")
        
        return {"status": "All documents and analytics cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Chat Endpoints ============

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Query documents with RAG. Returns answer with page citations.
    """
    try:
        response = query_documents(request.query)
        
        # Format sources for backward compatibility
        sources = list(set([
            f"{c.get('source', 'unknown')} (Page {c.get('page_number', 0)})"
            for c in response.get("citations", [])
        ]))
        
        return ChatResponse(
            answer=response.get("answer", "No answer found."),
            citations=response.get("citations", []),
            sources=sources,
            tables=response.get("tables", [])
        )
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=400, 
            detail="No documents uploaded. Please upload a document first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/clear")
async def clear_chat_history():
    """Clear the chat history."""
    try:
        chain = get_rag_chain()
        chain.clear_history()
        return {"status": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Analytics Endpoints ============

@app.get("/analyze/{doc_id}")
async def analyze_document_by_id(doc_id: str, force_refresh: bool = False):
    """
    Get analytics for a specific document by ID.
    Retrieves from cache if available, unless force_refresh=True.
    """
    try:
        # Check cache first (unless force refresh requested)
        if not force_refresh and has_analytics(doc_id):
            cached_analytics = get_analytics(doc_id)
            if cached_analytics:
                print(f"Returning cached analytics for: {doc_id}")
                return cached_analytics
        
        docs = get_ingested_documents()
        doc = next((d for d in docs if d.get("doc_id") == doc_id), None)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Re-process and analyze
        file_path = f"data/{doc.get('filename')}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        processor = DocumentProcessor()
        processed = processor.process_file(file_path)
        
        full_content = "\n\n".join([c.content for c in processed.chunks])
        tables_data = [t.to_dict() for t in processed.tables]
        analytics = analyze_document(full_content, tables_data)
        
        # Save to cache for future requests
        save_analytics(doc_id, analytics)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze")
async def analyze_all_documents():
    """
    Get combined analytics for all uploaded documents.
    """
    try:
        docs = get_ingested_documents()
        
        if not docs:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Combine content from all documents
        all_content = []
        all_tables = []
        
        processor = DocumentProcessor()
        
        for doc in docs:
            file_path = f"data/{doc.get('filename')}"
            if os.path.exists(file_path):
                processed = processor.process_file(file_path)
                all_content.extend([c.content for c in processed.chunks])
                all_tables.extend([t.to_dict() for t in processed.tables])
        
        if not all_content:
            raise HTTPException(status_code=404, detail="No document content found")
        
        combined_content = "\n\n".join(all_content[:50])  # Limit chunks
        analytics = analyze_document(combined_content, all_tables[:10])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ PDF Viewer Endpoint ============

@app.get("/pdf/{doc_id}")
async def get_pdf_file(doc_id: str):
    """
    Serve PDF file for the frontend viewer.
    Returns the PDF file for a given document ID.
    """
    try:
        docs = get_ingested_documents()
        doc = next((d for d in docs if d.get("doc_id") == doc_id), None)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Use absolute path to uploaded folder
        file_path = os.path.join(UPLOAD_FOLDER, doc.get('filename'))
        print(f"Serving PDF from: {file_path}")
        
        if not os.path.exists(file_path):
            # Try legacy data folder as fallback
            legacy_path = os.path.join(BASE_DIR, "data", doc.get('filename'))
            if os.path.exists(legacy_path):
                file_path = legacy_path
            else:
                raise HTTPException(status_code=404, detail=f"PDF file not found: {file_path}")
        
        # Only serve PDFs
        if not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Document is not a PDF")
        
        return FileResponse(
            file_path, 
            media_type="application/pdf",
            filename=doc.get('filename'),
            headers={
                "Content-Disposition": f"inline; filename={doc.get('filename')}",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "vectorstore_exists": os.path.exists("vectorstore"),
        "documents_count": len(get_ingested_documents()) if os.path.exists("vectorstore") else 0
    }
