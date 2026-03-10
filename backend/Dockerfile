# Use the official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS dependencies, necessary for building Python packages like FAISS and managing sentence-transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Pre-download the HuggingFace embedding model so it's baked into the image
# This prevents the container from downloading the large model on every cold start
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true

# Set PYTHONPATH so Python can find the modules
ENV PYTHONPATH=/app

# Expose port 8000 for App Runner
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Command to run the application using Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
