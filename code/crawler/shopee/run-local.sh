#!/bin/bash

echo "Starting Shopee Crawler (Local Development)"

export PYTHONPATH="/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

cd "/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

echo "🌐 Starting server on http://localhost:8151"
echo "📝 Using configuration from .env.local"
echo "Press Ctrl+C to stop the server"

uvicorn main:app --host 127.0.0.1 --port 8151 --reload
