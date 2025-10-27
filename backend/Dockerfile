FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Download InsightFace models
RUN mkdir -p /root/.insightface/models && \
    cd /root/.insightface/models && \
    wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip && \
    unzip buffalo_l.zip && \
    rm buffalo_l.zip

# Copy project
COPY . .

# Create directories
RUN mkdir -p logs media staticfiles

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "safenest.asgi:application"]
