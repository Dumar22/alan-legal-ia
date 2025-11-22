#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p vector_db

echo "Build completed successfully!"