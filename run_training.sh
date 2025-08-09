#!/bin/bash

echo ""
echo "================================================================="
echo "POORNASREE AI - TRAINING SCRIPT SETUP AND EXECUTION"
echo "================================================================="
echo ""

echo "📦 Installing training dependencies..."
pip install -r training_requirements.txt

echo ""
echo "🔍 Checking if backend server is running..."
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "❌ Backend server is not running!"
    echo "   Please start the server first: python -m uvicorn main:app --reload"
    exit 1
fi

echo "✅ Backend server is running"
echo ""

echo "🚀 Starting AI training script..."
python training_script.py

echo ""
echo "🎉 Training script execution completed!"
