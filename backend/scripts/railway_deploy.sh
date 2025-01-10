#!/bin/bash

# backend/scripts/deploy.sh
set -e

echo "Starting deployment process..."

# Step 1: Run database migrations
echo "Running database migrations..."
python scripts/init_db.py

# Step 2: Start the application with production settings
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4 --proxy-headers --forwarded-allow-ips='*'

# Note: This script will be called by Railway automatically
# Make sure to set executable permissions: chmod +x scripts/deploy.sh