#!/bin/bash

echo "Initializing Shopee Crawler Database..."

export PYTHONPATH="/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

cd "/Users/datbavip10/Desktop/Work/vada/vada/code/crawler/shopee/shopee_crawler"

echo "Running database initialization..."
python3 init_db.py

if [ $? -eq 0 ]; then
    echo "Database initialization completed successfully!"
else
    echo "Database initialization failed!"
    exit 1
fi
