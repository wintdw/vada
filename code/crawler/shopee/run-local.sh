#!/bin/bash

# Script to run Shopee Crawler locally
echo "🚀 Starting Shopee Crawler (Local Development)"

# Set Python path
export PYTHONPATH="/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

# Change to project directory
cd "/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local file not found!"
    echo "Please create .env.local with your local configuration"
    exit 1
fi

# Run the FastAPI server
echo "🌐 Starting server on http://localhost:8151"
echo "📝 Using configuration from .env.local"
echo "Press Ctrl+C to stop the server"

uvicorn main:app --host 127.0.0.1 --port 8151 --reload
