"""
FinEdge RAG Pipeline v2.0
Enhanced RAG with page citations and multi-document support.
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os

load_dotenv()


@dataclass
class Citation:
    """A citation reference to a document."""
    source: str
    page_number: int
    text_snippet: str
    doc_id: Optional[str] = None
    chunk_type: Optional[str] = None
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1] for highlighting


@dataclass
class HighlightInfo:
    """Information for PDF highlighting in the viewer."""
    doc_id: str
    page_number: int
    bbox: Optional[List[float]] = None
    text: str = ""


@dataclass  
class RAGResponse:
    """Complete RAG response with citations."""
    answer: str
    citations: List[Citation]
    source_documents: List[Dict]
    tables: List[Dict]
    is_financial_query: bool = True  # Whether RAG search was performed
    
    def to_dict(self) -> Dict:
        return {
            "answer": self.answer,
            "citations": [
                {
                    "source": c.source,
                    "page_number": c.page_number,
                    "text_snippet": c.text_snippet,
                    "doc_id": c.doc_id,
                    "chunk_type": c.chunk_type,
                    "bbox": c.bbox
                }
                for c in self.citations
            ],
            "source_documents": self.source_documents,
            "tables": self.tables,
            "is_financial_query": self.is_financial_query
        }


def get_embeddings():
    """Get embedding model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


def get_retriever(index_path: str = "vectorstore/fintech_index", k: int = 5):
    """Get the FAISS retriever."""
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Vector store not found at {index_path}. Please upload documents first.")
    
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": k}
    )
    return retriever


class EnhancedRAGChain:
    """
    Enhanced RAG chain with citation support, memory, and smart query routing.
    Uses LLM to determine if a query is financial-document-related before performing RAG search.
    """
    
    SYSTEM_PROMPT = """You are a highly knowledgeable financial analyst AI assistant.
Your role is to provide precise, comprehensive, and professional answers based on the provided documents.

RESPONSE RULES:
1. Answer ONLY using the context from the documents provided.
2. If the answer is not found, say: "I could not find information regarding this in the provided documents."
3. ALWAYS cite your sources using this format: [Source: filename, Page X]
4. When referencing tables, describe the relevant data clearly and include key figures.
5. Maintain a professional and formal tone.
6. If multiple documents are relevant, cite each one.
7. Structure your response clearly with proper formatting when appropriate.
8. For numerical data, be precise and include units (currency, percentages, etc.).
9. When discussing trends or changes, provide context and comparisons.
10. If the question involves calculations or comparisons, show your reasoning.

FORMATTING:
- Use bullet points for lists of items
- Use bold for key figures and important terms
- Organize complex answers with clear sections"""

    INTENT_PROMPT = """You are a query classifier. Determine if the user's query is related to financial documents or is asking about financial/business information that would require searching uploaded documents.

Respond with ONLY one word:
- "FINANCIAL" if the query is about financial data, documents, reports, business metrics, company information, or anything that would benefit from searching financial documents
- "CASUAL" if the query is a greeting (hi, hello, hey), small talk (how are you), or completely unrelated to finance/documents

User query: "{query}"

Classification:"""

    GREETING_RESPONSES = [
        "Hello! I'm your financial document assistant. I'm here to help you analyze and extract insights from your uploaded financial documents. What would you like to know about your documents?",
        "Hi there! I'm ready to help you with your financial documents. You can ask me about revenue, expenses, profit margins, balance sheets, or any other financial data in your uploaded documents.",
        "Hey! I'm your AI financial analyst. Please ask me a specific question about your financial documents, and I'll provide detailed insights with citations.",
    ]

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1
        )
        self.chat_history: List = []
        self.retriever = None
        self._greeting_index = 0
        
    def initialize(self, index_path: str = "vectorstore/fintech_index"):
        """Initialize the retriever."""
        try:
            self.retriever = get_retriever(index_path)
            return True
        except FileNotFoundError:
            return False
    
    def _classify_query(self, query: str) -> str:
        """
        Use LLM to classify if query is financial-related or casual.
        Returns 'FINANCIAL' or 'CASUAL'.
        """
        try:
            prompt = ChatPromptTemplate.from_template(self.INTENT_PROMPT)
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"query": query})
            classification = result.strip().upper()
            
            if "FINANCIAL" in classification:
                return "FINANCIAL"
            return "CASUAL"
        except Exception as e:
            print(f"Intent classification error: {e}")
            # Default to financial for safety
            return "FINANCIAL"
    
    def _get_greeting_response(self) -> str:
        """Get a varied greeting response."""
        response = self.GREETING_RESPONSES[self._greeting_index % len(self.GREETING_RESPONSES)]
        self._greeting_index += 1
        return response
    
    def query(self, question: str) -> RAGResponse:
        """
        Query the RAG system with smart intent classification.
        """
        # First, classify the query intent
        intent = self._classify_query(question)
        
        if intent == "CASUAL":
            # Return greeting response without RAG search
            return RAGResponse(
                answer=self._get_greeting_response(),
                citations=[],
                source_documents=[],
                tables=[],
                is_financial_query=False
            )
        
        # Financial query - proceed with RAG
        if not self.retriever:
            if not self.initialize():
                return RAGResponse(
                    answer="No documents have been uploaded yet. Please upload a document first.",
                    citations=[],
                    source_documents=[],
                    tables=[],
                    is_financial_query=True
                )
        
        # Retrieve relevant documents
        docs = self.retriever.invoke(question)
        
        # Format context with metadata
        context_parts = []
        citations = []
        tables = []
        
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page_number", doc.metadata.get("page", 1))
            chunk_type = doc.metadata.get("chunk_type", "text")
            doc_id = doc.metadata.get("doc_id", "")
            
            context_parts.append(
                f"[Source: {source}, Page {page}]\n{doc.page_content}"
            )
            
            citations.append(Citation(
                source=source,
                page_number=page,
                text_snippet=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                doc_id=doc_id,
                chunk_type=chunk_type
            ))
            
            # Extract table data if present
            if chunk_type == "table" or doc.metadata.get("is_table"):
                tables.append({
                    "source": source,
                    "page": page,
                    "content": doc.page_content
                })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build prompt with history
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        for msg in self.chat_history[-6:]:  # Last 3 exchanges
            messages.append(msg)
        
        messages.append({
            "role": "user", 
            "content": f"""Context from Documents:
{context}

Question: {question}

Provide a comprehensive answer with citations:"""
        })
        
        # Get response
        prompt = ChatPromptTemplate.from_messages([
            (msg["role"], msg["content"]) for msg in messages
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        answer = chain.invoke({})
        
        # Update history
        self.chat_history.append({"role": "user", "content": question})
        self.chat_history.append({"role": "assistant", "content": answer})
        
        # Deduplicate citations by source+page
        seen = set()
        unique_citations = []
        for c in citations:
            key = (c.source, c.page_number)
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)
        
        return RAGResponse(
            answer=answer,
            citations=unique_citations,
            source_documents=[
                {
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page_number", doc.metadata.get("page")),
                    "content": doc.page_content[:500],
                    "doc_id": doc.metadata.get("doc_id", "")
                }
                for doc in docs
            ],
            tables=tables,
            is_financial_query=True
        )
    
    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []


# Global instance
_rag_chain = None


def get_rag_chain() -> EnhancedRAGChain:
    """Get or create the RAG chain singleton."""
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = EnhancedRAGChain()
    return _rag_chain


def query_documents(question: str) -> Dict:
    """Convenience function to query documents."""
    chain = get_rag_chain()
    response = chain.query(question)
    return response.to_dict()
