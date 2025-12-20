# FinEdge RAG Backend - Docker Deployment
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# FIX: Move vectorstore and uploaded from backend/ to app root if they exist there
# The code expects 'vectorstore' at the root (/app/vectorstore)
# But locally it might be in 'backend/vectorstore', so we move it.
RUN if [ -d "backend/vectorstore" ]; then \
        # If root vectorstore exists, remove it first to avoid conflict, or merge? 
        # Safest is to use the one from backend if it exists
        rm -rf vectorstore && \
        mv backend/vectorstore . && \
        echo "Moved vectorstore from backend/ to root"; \
    fi

RUN if [ -d "backend/uploaded" ]; then \
        rm -rf uploaded && \
        mv backend/uploaded . && \
        echo "Moved uploaded from backend/ to root"; \
    fi

# Ensure directories exist
RUN mkdir -p /app/uploaded /app/vectorstore /app/data

# Environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
