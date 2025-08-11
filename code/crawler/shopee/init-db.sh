#!/bin/bash

# Script to initialize database tables
echo "🔧 Initializing Shopee Crawler Database..."

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

# Run database initialization
echo "🚀 Running database initialization..."
python3 init_db.py

if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed successfully!"
else
    echo "❌ Database initialization failed!"
    exit 1
fi
