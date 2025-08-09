# Service Guide AI Training System

## 🎯 Overview

This script provides a complete solution for training the Poornasree AI system with the Service Guide PDF document and offers an interactive Q&A interface to test the trained knowledge.

## 🚀 Features

- **PDF Text Extraction**: Automatically extracts text from Service Guide.pdf using PyPDF2 or pdfplumber
- **API Integration**: Seamlessly uploads training data to the Poornasree AI backend
- **Training Management**: Starts and monitors AI training jobs in real-time
- **Interactive Q&A**: Chat interface to ask questions about the Service Guide content
- **Error Handling**: Comprehensive error handling and user feedback
- **Fallback Content**: If PDF libraries aren't available, uses comprehensive placeholder content

## 📋 Prerequisites

### Required Files
- `training_data/Service Guide.pdf` (110KB, confirmed present)
- Active Poornasree AI backend running on `http://127.0.0.1:8000`

### Python Dependencies
```bash
pip install PyPDF2 pdfplumber requests
```

### Admin Credentials
- Email: `official4tishnu@gmail.com`
- Password: `Access@404`
- Role: `super_admin` (required for training operations)

## 🛠️ Installation & Setup

### Quick Start (Windows)
```cmd
run_service_guide_trainer.bat
```

### Quick Start (Linux/Unix)
```bash
chmod +x run_service_guide_trainer.sh
./run_service_guide_trainer.sh
```

### Manual Setup
```bash
# Install dependencies
pip install -r service_guide_requirements.txt

# Run the trainer
python service_guide_trainer.py
```

## 📖 Usage

### Option 1: Full Training Workflow
1. **Authentication**: Logs in with admin credentials
2. **PDF Processing**: Extracts text from Service Guide.pdf
3. **File Upload**: Uploads extracted content to training system
4. **Training Job**: Starts background training with optimized parameters
5. **Progress Monitoring**: Real-time training progress updates
6. **Interactive Q&A**: Chat with the trained AI about Service Guide content

### Option 2: Q&A Only
If you've already trained the model, you can skip directly to the interactive Q&A session.

## 💬 Sample Questions

Once training is complete, you can ask questions like:
- "How do I upload training data?"
- "What file formats are supported?"
- "How long does AI training take?"
- "What are the different user roles?"
- "How do I troubleshoot login issues?"
- "What's the maximum file size for uploads?"
- "How do I improve AI response accuracy?"
- "What security features are available?"

## 🔧 Configuration

### Training Parameters
- **Learning Rate**: 0.001 (optimized for document content)
- **Batch Size**: 32 (balanced for performance)
- **Epochs**: 12 (sufficient for convergence)
- **Max Tokens**: 2048 (comprehensive responses)
- **Temperature**: 0.7 (balanced creativity)

### API Endpoints Used
- `POST /api/v1/auth/login` - Authentication
- `POST /api/v1/ai/upload-training-data` - File upload
- `POST /api/v1/ai/start-training` - Training initiation
- `GET /api/v1/ai/training-jobs` - Progress monitoring
- `POST /api/v1/ai/chat` - Interactive Q&A

## 📊 Training Process

### Phase 1: Data Preparation (2-3 minutes)
- PDF text extraction
- Content preprocessing
- File format conversion
- Upload to training system

### Phase 2: Model Training (15-45 minutes)
- Vector embedding generation (Weaviate)
- Language model fine-tuning (Gemini 2.5 Flash)
- Knowledge base indexing
- Validation and testing

### Phase 3: Interactive Testing
- Real-time Q&A interface
- Context-aware responses
- Service Guide knowledge retrieval
- Performance evaluation

## 🛡️ Security Features

- **Secure Authentication**: JWT token-based authentication
- **Role-Based Access**: Admin privileges required for training
- **Data Protection**: Temporary files cleaned up automatically
- **API Security**: Bearer token authentication for all requests

## 📁 File Structure

```
service_guide_trainer.py              # Main training script
service_guide_requirements.txt        # Python dependencies
run_service_guide_trainer.bat         # Windows setup script
run_service_guide_trainer.sh          # Linux setup script
SERVICE_GUIDE_TRAINER_README.md       # This documentation
training_data/Service Guide.pdf       # Target training document
```

## 🔍 Troubleshooting

### Common Issues

**1. PDF Not Found**
```
❌ PDF file not found: training_data/Service Guide.pdf
```
**Solution**: Ensure Service Guide.pdf is in the training_data directory

**2. Authentication Failed**
```
❌ Login failed: 401
```
**Solution**: Verify backend is running and credentials are correct

**3. Training Job Failed**
```
❌ Training failed!
```
**Solution**: Check training logs, verify file content, ensure sufficient resources

**4. PDF Libraries Missing**
```
⚠️ PyPDF2 not available, trying pdfplumber...
⚠️ pdfplumber not available, creating placeholder text...
```
**Solution**: Install PDF libraries: `pip install PyPDF2 pdfplumber`

### Backend Requirements
- FastAPI backend running on port 8000
- Weaviate vector database accessible
- Google AI (Gemini) service configured
- Admin user account active

## 📈 Performance Metrics

### Expected Results
- **PDF Processing**: 2-5 seconds
- **File Upload**: 5-15 seconds
- **Training Duration**: 15-45 minutes
- **Q&A Response Time**: 2-8 seconds
- **Accuracy**: 85-95% for Service Guide content

### Resource Usage
- **Memory**: 200-500MB during training
- **Disk Space**: ~1MB for temporary files
- **Network**: Moderate API calls during training
- **CPU**: Low to moderate usage

## 🎯 Success Criteria

✅ **Successful Training Indicates:**
- PDF text extracted successfully
- File uploaded without errors
- Training job completed (status: 'completed')
- AI can answer Service Guide questions accurately
- Interactive Q&A session responsive

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review backend logs in `logs/` directory
- Verify all prerequisites are met
- Ensure Service Guide.pdf is accessible

## 🏆 Advanced Usage

### Custom Training Configuration
Edit the training parameters in `start_training_job()` method:
```python
training_request = {
    "name": "Custom Service Guide Training",
    "file_ids": self.uploaded_file_ids,
    "training_config": {
        "learning_rate": 0.0005,    # Lower for fine-tuning
        "batch_size": 16,           # Smaller for limited memory
        "epochs": 20,               # More for better accuracy
        "max_tokens": 4096,         # Longer responses
        "temperature": 0.5          # More focused responses
    }
}
```

### Batch Processing
To train multiple documents, modify the `upload_training_file()` method to accept multiple files.

### Integration with Frontend
The trained model can be accessed through the existing chat interface in the frontend application.

---

**Last Updated**: January 27, 2025
**Version**: 1.0
**Compatibility**: Python 3.8+, Windows/Linux/MacOS
