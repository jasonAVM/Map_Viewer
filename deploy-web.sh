#!/bin/bash

# AWS S3 Deployment Script for Web Files Only (no tiles)
# Deploys HTML/CSS/JS files to S3 bucket: aerialvm-maps/longview/

echo "Syncing web files to S3 (excluding tiles)..."
echo "Bucket: aerialvm-maps"
echo "Path: longview/"
echo "================================"

# Sync only web files, excluding tiles directory
aws s3 sync web/ s3://aerialvm-maps/longview/ \
    --exclude "tiles/*" \
    --exclude "*.tif" \
    --exclude "*.tiff"

if [ $? -eq 0 ]; then
    echo "✓ Web files sync completed successfully"
    echo ""
    echo "Files synced:"
    echo "- index.html"
    echo "- css/style.css"
    echo "- js/map.js"
    echo ""
    echo "Map available at:"
    echo "https://aerialvm-maps.s3.amazonaws.com/longview/index.html"
else
    echo "✗ Web files sync failed"
    exit 1
fi