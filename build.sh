#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Building Alana Legal Sense for production..."

# Upgrade pip first
pip install --upgrade pip

# Try production requirements first, fallback to main requirements
if [ -f requirements.production.txt ]; then
    echo "📦 Installing production dependencies..."
    pip install -r requirements.production.txt
else
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p uploads
mkdir -p vector_db
mkdir -p chatbot/__pycache__

# Set proper permissions
chmod -R 755 uploads
chmod -R 755 vector_db

echo "✅ Build completed successfully!"