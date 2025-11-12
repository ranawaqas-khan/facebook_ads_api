#!/bin/bash
PORT=${PORT:-8000}
echo "🚀 Starting FastAPI on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
