"""
FinEdge Ingestion Module v2.0
Handles document ingestion using the new DocumentProcessor.
Supports PDF, DOCX, XLSX with table extraction.
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.document_processor import DocumentProcessor, ProcessedDocument

DB_PATH = "vectorstore/fintech_index"
METADATA_PATH = "vectorstore/documents_metadata.json"


def get_embeddings():
    """Get the embedding model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


def load_documents_metadata() -> Dict:
    """Load metadata about all ingested documents."""
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    return {"documents": {}}


def save_documents_metadata(metadata: Dict):
    """Save documents metadata."""
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)


def ingest_file(file_path: str) -> Tuple[int, ProcessedDocument]:
    """
    Ingests a single file into the vector store using the new DocumentProcessor.
    
    Returns:
        Tuple of (chunk_count, ProcessedDocument)
    """
    print(f"Starting ingestion for: {file_path}")
    
    # 1. Process document with new processor
    processor = DocumentProcessor()
    processed_doc = processor.process_file(file_path)
    
    print(f"Processed: {processed_doc.total_pages} pages, {len(processed_doc.chunks)} chunks, {len(processed_doc.tables)} tables")
    
    # 2. Convert chunks to LangChain Documents
    langchain_docs = []
    for chunk in processed_doc.chunks:
        doc = Document(
            page_content=chunk.content,
            metadata={
                "source": processed_doc.filename,
                "doc_id": processed_doc.doc_id,
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "chunk_type": chunk.chunk_type,
                "section_title": chunk.section_title,
                "file_type": processed_doc.file_type,
                **chunk.metadata
            }
        )
        langchain_docs.append(doc)
    
    # 3. Get embeddings
    embeddings = get_embeddings()
    
    # 4. Update or Create Vector Store
    if os.path.exists(DB_PATH):
        try:
            vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_documents(langchain_docs)
            print("Added to existing index.")
        except Exception as e:
            print(f"Error loading existing index, creating new one: {e}")
            vectorstore = FAISS.from_documents(langchain_docs, embeddings)
    else:
        print("Creating new index.")
        vectorstore = FAISS.from_documents(langchain_docs, embeddings)
    
    # 5. Save vectorstore
    vectorstore.save_local(DB_PATH)
    print(f"Vectorstore saved at {DB_PATH}")
    
    # 6. Save document metadata for tracking
    metadata = load_documents_metadata()
    metadata["documents"][processed_doc.doc_id] = {
        "filename": processed_doc.filename,
        "file_type": processed_doc.file_type,
        "total_pages": processed_doc.total_pages,
        "total_chunks": len(processed_doc.chunks),
        "total_tables": len(processed_doc.tables),
        "tables": [t.to_dict() for t in processed_doc.tables]
    }
    save_documents_metadata(metadata)
    
    return len(langchain_docs), processed_doc


def get_ingested_documents() -> List[Dict]:
    """Get list of all ingested documents with metadata."""
    metadata = load_documents_metadata()
    return [
        {
            "doc_id": doc_id,
            **doc_info
        }
        for doc_id, doc_info in metadata.get("documents", {}).items()
    ]


def delete_document(doc_id: str):
    """
    Remove a specific document from the vector store.
    Note: FAISS doesn't support deletion, so we'd need to rebuild.
    For now, this just removes from metadata.
    """
    metadata = load_documents_metadata()
    if doc_id in metadata.get("documents", {}):
        del metadata["documents"][doc_id]
        save_documents_metadata(metadata)
        return True
    return False


def delete_vectorstore():
    """Delete the entire vector store."""
    if os.path.exists("vectorstore"):
        shutil.rmtree("vectorstore")
        print("Vectorstore deleted.")


def get_document_page_content(doc_id: str, page_number: int) -> Optional[str]:
    """Get the content of a specific page for citation preview."""
    metadata = load_documents_metadata()
    if doc_id not in metadata.get("documents", {}):
        return None
    
    doc_info = metadata["documents"][doc_id]
    # For now, we'd need to re-read the file
    # In production, we'd cache page content
    return None
