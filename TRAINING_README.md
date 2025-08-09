# 🚀 Poornasree AI Training System

Comprehensive AI model training system using **Weaviate vector database** and **Gemini 2.5 Flash** for advanced customer support and AI capabilities.

## 📋 Overview

This training system provides:
- **Automated file upload and processing** (PDF, DOC, DOCX, TXT, JSON, CSV)
- **Weaviate vector database integration** for semantic search and embeddings
- **Gemini 2.5 Flash model training** for enhanced AI responses
- **Real-time training progress monitoring**
- **Complete job management and error handling**

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install training script dependencies
pip install -r training_requirements.txt

# Optional: Install enhanced file processing libraries
pip install PyPDF2 pdfplumber python-docx openpyxl
```

### 2. Start Backend Server

```bash
# Make sure the FastAPI server is running
python -m uvicorn main:app --reload --port 8000
```

### 3. Verify Server Status

Visit `http://127.0.0.1:8000/docs` to see the Swagger API documentation and verify all endpoints are available.

## 🚀 Running the Training Script

### Option 1: Automated Script (Recommended)

**Windows:**
```cmd
run_training.bat
```

**Linux/Mac:**
```bash
chmod +x run_training.sh
./run_training.sh
```

### Option 2: Manual Execution

```bash
python training_script.py
```

## 📊 What the Training Script Does

### 1. Authentication
- Logs in as admin user using configured credentials
- Obtains JWT token for API authentication

### 2. Health Check
- Verifies AI services (Weaviate + Gemini) are available
- Reports service status and connectivity

### 3. Sample Data Creation
- **PDF**: Customer support guide with procedures and best practices
- **TXT**: AI training instructions and sample customer interactions
- **JSON**: Training configuration and metadata

### 4. File Upload
- Uploads all sample files to the training system
- Validates file types and sizes
- Returns file IDs for training job creation

### 5. Training Job Creation
- Starts a new training job with uploaded files
- Configures training parameters (learning rate, batch size, etc.)
- Returns job ID for monitoring

### 6. Progress Monitoring
- Real-time progress tracking with status updates
- Shows training phases: data loading, embedding, training, validation
- Monitors until completion or failure

### 7. Results Verification
- Confirms training job completed successfully
- Displays training statistics and metrics

## 📁 File Structure

```
psr-ai-api/
├── training_script.py          # Main training automation script
├── training_requirements.txt   # Additional dependencies
├── run_training.bat           # Windows automation script
├── run_training.sh            # Unix automation script
├── training_data/             # Uploaded training files (created automatically)
├── training_jobs/             # Job status and metadata (created automatically)
└── TRAINING_README.md         # This documentation
```

## 🔧 Configuration Options

### Admin Credentials
Update in `training_script.py`:
```python
self.admin_credentials = {
    "email": "your-admin@email.com",
    "password": "your-password"
}
```

### Training Parameters
Modify in the training job creation:
```python
"training_config": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10,
    "max_tokens": 2048,
    "temperature": 0.7
}
```

### API Endpoint
Change the base URL if needed:
```python
self.base_url = "http://127.0.0.1:8000"
```

## 📊 Training Process Details

### Data Processing Pipeline
1. **File Upload** → Validates and stores files securely
2. **Text Extraction** → Extracts content from various file formats
3. **Content Chunking** → Splits large documents into manageable chunks
4. **Vector Embedding** → Generates embeddings using Weaviate
5. **Model Training** → Fine-tunes Gemini model with processed data
6. **Validation** → Tests model performance and accuracy

### Training Phases
- **10%** - Loading training data and initializing systems
- **25%** - Preparing embeddings and vector representations
- **40%** - Training with Weaviate vector database integration
- **65%** - Fine-tuning with Gemini 2.5 Flash model
- **85%** - Validating model performance and accuracy
- **100%** - Training completed and model ready for deployment

## 🎯 Expected Outcomes

After successful training, the AI system will have:
- **Enhanced customer service capabilities** with context-aware responses
- **Improved technical support guidance** based on training materials
- **Better understanding of user intent** and conversation context
- **More accurate and helpful responses** across various scenarios

## 📈 Performance Metrics

The training system monitors:
- **Response Accuracy**: Target ≥90%
- **Response Time**: Target ≤2 seconds
- **Customer Satisfaction**: Target ≥4.5/5
- **Issue Resolution Rate**: Target ≥85%

## 🔍 Troubleshooting

### Common Issues

**Error: "Authentication failed"**
- Verify admin credentials in `training_script.py`
- Ensure the admin user exists and has proper permissions

**Error: "Backend server not running"**
- Start the FastAPI server: `python -m uvicorn main:app --reload`
- Check server status at `http://127.0.0.1:8000/health`

**Error: "File upload failed"**
- Check file size limits (max 100MB total)
- Verify supported file types: PDF, DOC, DOCX, TXT, JSON, CSV
- Ensure proper admin authentication

**Error: "Training job failed"**
- Check server logs for detailed error information
- Verify Weaviate and Gemini AI service connectivity
- Ensure sufficient system resources for training

### Debug Mode

Enable verbose logging by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🌟 Advanced Usage

### Custom Training Data

Replace the sample data creation with your own files:
```python
# Instead of creating sample files, use your own
sample_files = [
    "/path/to/your/training/data/file1.pdf",
    "/path/to/your/training/data/file2.txt",
    "/path/to/your/training/data/file3.json"
]
```

### Batch Training

Run multiple training jobs with different configurations:
```python
configs = [
    {"learning_rate": 0.001, "epochs": 10},
    {"learning_rate": 0.002, "epochs": 15},
    {"learning_rate": 0.0005, "epochs": 20}
]

for config in configs:
    job_id = await self.start_training_job(file_ids, config)
    await self.monitor_training_job(job_id)
```

## 📞 Support

For issues or questions:
1. Check the server logs at `logs/` directory
2. Verify API documentation at `http://127.0.0.1:8000/docs`
3. Review training job status at `/api/v1/ai/training-jobs`
4. Contact the development team with error details

## 🎉 Success Indicators

Training is successful when you see:
- ✅ All files uploaded without errors
- ✅ Training job starts and progresses through all phases
- ✅ Job status shows "completed" with 100% progress
- ✅ No error messages in the logs
- ✅ AI responses show improved quality and context awareness

---

**Happy Training! 🚀**
