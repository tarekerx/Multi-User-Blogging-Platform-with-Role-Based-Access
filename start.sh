#!/bin/bash
set -e

echo "🛠️ Running database migrations..."
flask db upgrade

echo "🚀 Starting Gunicorn"
gunicorn app:app

echo "👋 Goodbye!"