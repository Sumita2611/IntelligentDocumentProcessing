# ==============================================================================
# Stage 1: Build Frontend Assets
# ==============================================================================
FROM node:22-alpine AS frontend-builder
WORKDIR /build/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci || npm install

# Build production bundle
COPY frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Production Python Backend
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

WORKDIR /app

# Install system dependencies (OpenCV runtime, Tesseract OCR, glib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU first to keep image lightweight and avoid CUDA bloat
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application code and samples
COPY backend/ ./backend/
COPY samples/ ./samples/

# Copy built frontend from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

# Expose server port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch FastAPI with dynamic PORT support for Render
WORKDIR /app/backend
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
