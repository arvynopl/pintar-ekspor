#!/bin/bash

# backend/scripts/railway_deploy.sh
set -e

echo "Starting deployment process..."

# Step 1: Run database migrations
echo "Running database migrations..."
python scripts/init_db.py

# Step 2: Configure security
echo "Setting up security configurations..."
bash scripts/setup_firewall.sh

# Step 3: Start the application with production settings
echo "Starting application with Uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 --proxy-headers --forwarded-allow-ips='*'