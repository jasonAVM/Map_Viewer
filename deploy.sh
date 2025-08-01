#!/bin/bash

# AWS S3 Deployment Script for Longview Map Viewer
# Deploys web files and tiles to S3 bucket: aerialvm-maps/longview/

echo "Starting deployment to S3..."
echo "Bucket: aerialvm-maps"
echo "Path: longview/"
echo "================================"

# Sync web files first (smaller, faster)
echo "Syncing web files..."
aws s3 sync web/ s3://aerialvm-maps/longview/

if [ $? -eq 0 ]; then
    echo "✓ Web files sync completed successfully"
else
    echo "✗ Web files sync failed"
    exit 1
fi

echo ""
echo "Syncing tiles (this may take several minutes)..."

# Sync tiles with parallel uploads for better performance
aws s3 sync tiles/ s3://aerialvm-maps/longview/tiles/

if [ $? -eq 0 ]; then
    echo "✓ Tiles sync completed successfully"
    echo ""
    echo "🎉 Deployment complete!"
    echo "Your map should be available at:"
    echo "https://aerialvm-maps.s3.amazonaws.com/longview/index.html"
    echo "(or your configured S3 website endpoint)"
else
    echo "✗ Tiles sync failed"
    exit 1
fi