# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# PYTHONUNBUFFERED: Unbuffer stdout and stderr to see output in real time
# PYTHONDONTWRITEBYTECODE: Don't write bytecode to disk
# PIP_NO_CACHE_DIR: Don't cache pip downloads
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create directories for data and logs
RUN mkdir -p /app/data

# Set the default command to keep container running
CMD ["tail", "-f", "/dev/null"]

