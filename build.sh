#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔍 Checking environment variables..."
echo "DATABASE_URL: ${DATABASE_URL:0:30}... (${#DATABASE_URL} chars)"
echo "CLOUDINARY_URL: ${CLOUDINARY_URL:0:30}... (${#CLOUDINARY_URL} chars)"
echo "SECRET_KEY: ${SECRET_KEY:0:20}... (${#SECRET_KEY} chars)"
echo "RENDER: ${RENDER:-not set}"
echo ""

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "✅ Build completed successfully!"
