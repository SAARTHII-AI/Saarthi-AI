# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install OS dependencies, necessary for building Python packages like FAISS and managing sentence-transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY backend ./backend
COPY scripts ./scripts

# Pre-download the HuggingFace embedding model so it's baked into the image
# This prevents the container from downloading the large model on every cold start
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Set PYTHONPATH so Python can find the backend module
ENV PYTHONPATH=/app

# Expose port 8000 for App Runner / ECS
EXPOSE 8000

# Command to run the application using Uvicorn (removed --reload for production)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
