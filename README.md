<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Gemini_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/FAISS-00599C?style=for-the-badge&logo=meta&logoColor=white" alt="FAISS">
</p>

<h1 align="center">🏦 FinEdge - Financial Document Intelligence Platform</h1>

<p align="center">
  <strong>AI-Powered RAG System for Financial Document Analysis with Dynamic Analytics</strong>
</p>

<p align="center">
  <a href="https://main.d3d2dikr0bk2py.amplifyapp.com/">🌐 Live Demo</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a>
</p>

---

## 📋 Overview

**FinEdge** is a production-ready Financial Document Intelligence Platform that leverages **Retrieval-Augmented Generation (RAG)** and **AI-powered analytics** to transform how organizations interact with financial documents. Upload annual reports, balance sheets, income statements, or any financial PDF, and instantly query your documents with natural language while receiving AI-generated insights, metrics, and visualizations.

### 🎯 Problem Solved

Financial professionals spend hours manually extracting data from lengthy reports. FinEdge automates this process by:
- **Intelligent Document Processing** - Extracts text, tables, and even OCR content from images
- **Natural Language Querying** - Ask questions in plain English and get cited answers
- **Dynamic Analytics Generation** - AI automatically identifies key metrics and generates relevant charts
- **Citation Tracking** - Every answer includes page-level citations for verification

---

## ✨ Features

### 🔍 Intelligent RAG Chat System
- **Context-Aware Responses** - Powered by Google Gemini 2.5 Pro for accurate, contextual answers
- **Smart Query Routing** - Automatically distinguishes between greetings and financial queries
- **Page-Level Citations** - Every response includes clickable citations with source documents
- **Conversation Memory** - Maintains context across multiple questions

### 📊 AI-Powered Dynamic Analytics
- **Automatic Document Classification** - Identifies document types (Income Statement, Balance Sheet, etc.)
- **Smart Table Categorization** - Prioritizes PRIMARY, SECONDARY, and REFERENCE tables
- **Dynamic Chart Generation** - Bar, Line, Pie, and Area charts based on document content
- **Key Metrics Extraction** - Revenue, profit margins, growth rates, and financial ratios

### 📄 Advanced Document Processing
- **Multi-Format Support** - PDF, DOCX, XLSX file processing
- **Table Extraction** - Uses pdfplumber for accurate table detection with bounding boxes
- **OCR Capabilities** - pytesseract integration for extracting text from embedded images
- **Smart Chunking** - Structure-aware text splitting with 1500-char chunks and 200-char overlap

### 🖥️ Modern React Frontend
- **PDF Viewer Integration** - View documents with highlighted citations
- **Interactive Charts** - Recharts-powered visualizations
- **Dark/Light Theme** - User preference toggle
- **Responsive Design** - Works across desktop and mobile devices

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FINEDGE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐ │
│  │   Frontend   │────▶│   FastAPI    │────▶│   Document Processor  │ │
│  │   (React)    │     │   Backend    │     │   (PDF/DOCX/XLSX)     │ │
│  └──────────────┘     └──────────────┘     └──────────────────────┘ │
│         │                    │                        │              │
│         │                    ▼                        ▼              │
│         │             ┌──────────────┐     ┌──────────────────────┐ │
│         │             │  RAG Pipeline │────▶│  FAISS Vector Store  │ │
│         │             │  (LangChain)  │     │  (HuggingFace Emb)   │ │
│         │             └──────────────┘     └──────────────────────┘ │
│         │                    │                                       │
│         │                    ▼                                       │
│         │             ┌──────────────┐     ┌──────────────────────┐ │
│         └────────────▶│   Analytics  │────▶│   Gemini 2.5 Pro     │ │
│                       │    Engine    │     │   (Google GenAI)     │ │
│                       └──────────────┘     └──────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, TypeScript, TailwindCSS, Framer Motion, Recharts |
| **Backend** | FastAPI, Python 3.11+, Uvicorn |
| **AI/ML** | LangChain, Google Gemini 2.5 Pro, HuggingFace Embeddings |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Document Processing** | PyMuPDF, pdfplumber, pytesseract, python-docx, openpyxl |
| **Deployment** | Docker, AWS Amplify, AWS Elastic Beanstalk |

---

## 📁 Project Structure

```
FinEdge-RAG-FineTuning/
├── backend/
│   ├── main.py              # FastAPI application with all endpoints
│   └── vectorstore/         # FAISS index storage
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── FileUploader.tsx
│   │   │   ├── PDFViewer.tsx
│   │   │   ├── AnalyticsGrid.tsx
│   │   │   └── charts/      # Chart components
│   │   ├── api.ts           # API client
│   │   └── App.tsx          # Main application
│   └── package.json
├── src/
│   ├── rag_pipeline.py      # Enhanced RAG chain with citations
│   ├── document_processor.py # Multi-format document processing
│   ├── analytics_engine.py  # AI-powered analytics generation
│   ├── ingestion.py         # Document ingestion pipeline
│   └── analytics_storage.py # Analytics caching
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── amplify.yml             # AWS Amplify build config
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google AI API Key (for Gemini)
- Tesseract OCR (optional, for image text extraction)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/FinEdge-RAG-FineTuning.git
cd FinEdge-RAG-FineTuning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the backend
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t finedge-backend .

# Run the container
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key finedge-backend
```

---

## 💡 Usage

### 1. Upload Documents
Upload financial documents (PDF, DOCX, XLSX) through the intuitive drag-and-drop interface. The system automatically:
- Extracts text and tables
- Generates document embeddings
- Creates AI-powered analytics

### 2. Chat with Documents
Ask natural language questions like:
- *"What was the total revenue in 2024?"*
- *"Compare operating expenses across quarters"*
- *"What are the key risk factors mentioned?"*

### 3. Explore Analytics
View AI-generated insights including:
- Key financial metrics with YoY changes
- Dynamic charts (revenue trends, expense breakdowns)
- Highlighted key insights and patterns

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload and process a document |
| `GET` | `/documents` | List all uploaded documents |
| `DELETE` | `/documents` | Clear all documents |
| `POST` | `/chat` | Query documents with RAG |
| `GET` | `/analyze/{doc_id}` | Get analytics for a document |
| `GET` | `/pdf/{doc_id}` | Serve PDF for viewing |
| `GET` | `/health` | Health check endpoint |

---

## 🎨 Key Implementation Highlights

### Smart Table Prioritization
```python
class TableCategorizer:
    """
    Categorizes tables into priority tiers:
    - PRIMARY: Income Statement, Balance Sheet, Cash Flow
    - SECONDARY: Segment data, Quarterly comparisons
    - REFERENCE: Notes, Disclosures
    """
```

### RAG with Intent Classification
```python
class EnhancedRAGChain:
    """
    - Classifies queries as FINANCIAL or CASUAL
    - Only searches vector store for relevant queries
    - Maintains conversation history for context
    """
```

### Citation-Enabled Responses
Every answer includes:
- Source document name
- Page number
- Relevant text snippet
- Bounding box coordinates for PDF highlighting

---

## 📈 Performance Metrics

- **Document Processing**: ~2-5 seconds for typical 50-page PDF
- **Query Response**: ~1-3 seconds with citations
- **Analytics Generation**: ~3-5 seconds per document
- **Embedding Model**: `all-mpnet-base-v2` (768 dimensions)

---

## 🌐 Live Demo

Experience FinEdge in action: **[https://main.d3d2dikr0bk2py.amplifyapp.com/](https://main.d3d2dikr0bk2py.amplifyapp.com/)**

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

Built with 💙 as a demonstration of AI/ML engineering capabilities in document intelligence and RAG systems.

---

<p align="center">
  <strong>⭐ Star this repository if you find it helpful!</strong>
</p>
