#!/bin/bash

echo "========================================"
echo "Service Guide AI Training Setup"
echo "========================================"

echo ""
echo "Installing PDF processing dependencies..."
pip install PyPDF2 pdfplumber requests

echo ""
echo "Checking if Service Guide PDF exists..."
if [ -f "training_data/Service Guide.pdf" ]; then
    echo "✅ Service Guide.pdf found!"
else
    echo "❌ Service Guide.pdf not found in training_data directory"
    echo "Please ensure the PDF file is in the correct location."
    exit 1
fi

echo ""
echo "Starting Service Guide Trainer..."
python service_guide_trainer.py

echo ""
echo "Training script completed."
