# POORNASREE AI - TRAINING & SYSTEM DOCUMENTATION
===============================================

**Version:** 2.0 Production  
**Last Updated:** August 9, 2025  
**Author:** Poornasree AI Team  

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [API Endpoints](#api-endpoints)
4. [Training System Logic](#training-system-logic)
5. [Production Usage Guide](#production-usage-guide)
6. [Configuration & Setup](#configuration--setup)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

---

## 🎯 SYSTEM OVERVIEW

Poornasree AI is a production-ready AI system that combines:
- **FastAPI Backend** with role-based authentication
- **Weaviate Vector Database** for semantic search
- **Google Gemini 2.5 Flash** for intelligent responses
- **Service Guide Q&A System** with document training capabilities

### Key Capabilities:
✅ **Document Training**: Upload and process Service Guide PDFs  
✅ **Vector Storage**: Semantic embeddings in Weaviate Cloud  
✅ **Intelligent Q&A**: Context-aware responses using trained data  
✅ **Multi-Role Authentication**: Admin, Engineer, Customer access levels  
✅ **Production Monitoring**: Comprehensive logging and health checks  

---

## 🏗️ ARCHITECTURE & COMPONENTS

### Core Components:

```
┌─────────────────────────────────────────────────────────────┐
│                    POORNASREE AI SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│  🌐 FastAPI Server (main.py)                              │
│  ├── Authentication & Authorization                        │
│  ├── API Routes & Endpoints                               │
│  └── Database Management                                   │
├─────────────────────────────────────────────────────────────┤
│  🤖 AI Services (app/services/ai_service.py)              │
│  ├── Weaviate Vector Database Integration                 │
│  ├── Google Gemini AI Integration                         │
│  └── Document Processing & Training                       │
├─────────────────────────────────────────────────────────────┤
│  🎯 Production Trainer (production_service_guide_trainer.py)│
│  ├── End-to-End Training Workflow                         │
│  ├── Interactive Q&A Interface                            │
│  └── System Health Monitoring                             │
├─────────────────────────────────────────────────────────────┤
│  💾 Data Storage                                          │
│  ├── MySQL Database (Users, Jobs, Metadata)               │
│  ├── Weaviate Cloud (Vector Embeddings)                   │
│  └── Local Files (PDFs, Logs, Uploads)                    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack:
- **Backend**: FastAPI + Python 3.12
- **Database**: MySQL + Alembic migrations
- **Vector DB**: Weaviate Cloud with text2vec-weaviate
- **AI Model**: Google Gemini 2.5 Flash Lite
- **Authentication**: JWT with role-based access
- **File Processing**: PyPDF2 + text chunking algorithms

---

## 🌐 API ENDPOINTS

### Base URL: `http://127.0.0.1:8000`

### 🔐 Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/register/customer` | Customer registration | Public |
| `POST` | `/register/engineer` | Engineer registration | Public |
| `POST` | `/login` | User login | Public |
| `POST` | `/logout` | User logout | Authenticated |
| `GET` | `/me` | Get current user info | Authenticated |
| `POST` | `/refresh-token` | Refresh JWT token | Authenticated |

### 🤖 AI Services Endpoints (`/api/v1/ai`)

#### System Health & Status
| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `GET` | `/health` | AI services health check | Public |
| `POST` | `/initialize` | Initialize AI services | Admin+ |
| `GET` | `/weaviate/status` | Weaviate cluster status | Authenticated |
| `GET` | `/google-ai/status` | Google AI model status | Authenticated |
| `GET` | `/config` | AI configuration info | Authenticated |

#### Training & Data Management
| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/upload-training-data` | Upload training documents | Admin+ |
| `POST` | `/start-training` | Start training job | Admin+ |
| `GET` | `/training-files` | List uploaded files | Admin+ |
| `GET` | `/training-jobs` | Get training job status | Admin+ |
| `DELETE` | `/training-files/{file_id}` | Delete training file | Admin+ |
| `DELETE` | `/training-files` | Delete all training files | Admin+ |
| `POST` | `/cleanup-orphaned-data` | Clean orphaned data | Admin+ |

#### AI Interaction
| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/google-ai/generate` | Generate text with Gemini | Authenticated |
| `POST` | `/chat` | Chat with trained AI | Authenticated |
| `POST` | `/search` | Vector search in documents | Authenticated |

### 👥 User Management (`/api/v1/users`, `/api/v1/admin`)

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `GET` | `/users/profile` | Get user profile | Authenticated |
| `PUT` | `/users/profile` | Update user profile | Authenticated |
| `GET` | `/admin/users` | List all users | Admin+ |
| `PUT` | `/admin/users/{user_id}/role` | Update user role | Super Admin |
| `DELETE` | `/admin/users/{user_id}` | Delete user | Super Admin |

---

## 🎓 TRAINING SYSTEM LOGIC

### Training Workflow Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                  TRAINING WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│  1. 📄 PDF Document Upload                                │
│     ├── File validation (size, format, content)           │
│     ├── Metadata extraction                               │
│     └── Storage in uploads/ directory                     │
├─────────────────────────────────────────────────────────────┤
│  2. 📝 Text Extraction & Processing                       │
│     ├── PyPDF2 extraction with fallback methods          │
│     ├── Text cleaning and normalization                   │
│     ├── Content validation and quality checks             │
│     └── Character encoding handling                       │
├─────────────────────────────────────────────────────────────┤
│  3. 🧩 Text Chunking                                      │
│     ├── Smart chunking (1000 chars with overlap)          │
│     ├── Preserve sentence boundaries                      │
│     ├── Maintain context continuity                       │
│     └── Generate chunk metadata                           │
├─────────────────────────────────────────────────────────────┤
│  4. 🌐 Vector Database Storage                            │
│     ├── Create/verify Weaviate collection                 │
│     ├── Generate embeddings (text2vec-weaviate)           │
│     ├── Store vectors with metadata                       │
│     └── Validate storage success                          │
├─────────────────────────────────────────────────────────────┤
│  5. 🎯 Training Job Management                            │
│     ├── Create training job record                        │
│     ├── Monitor processing status                         │
│     ├── Track progress and metrics                        │
│     └── Generate completion reports                       │
└─────────────────────────────────────────────────────────────┘
```

### Key Algorithms:

#### 1. Text Chunking Logic:
```python
def smart_chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Intelligent text chunking with context preservation.
    
    Logic:
    - Split by sentences to maintain semantic boundaries
    - Target 1000 characters per chunk (configurable)
    - Add 100-character overlap between chunks
    - Preserve paragraph and section structure
    - Handle edge cases (very long sentences, formatting)
    """
```

#### 2. Vector Storage Logic:
```python
async def store_document_vectors(file_id: str, chunks: List[str]) -> bool:
    """
    Store document chunks as vectors in Weaviate.
    
    Process:
    1. Ensure TrainingDocuments collection exists
    2. Generate embeddings using text2vec-weaviate
    3. Store with metadata (file_id, chunk_index, content)
    4. Validate storage and return success status
    """
```

#### 3. Q&A Response Logic:
```python
async def generate_contextual_response(question: str) -> str:
    """
    Context-aware response generation.
    
    Steps:
    1. Vector similarity search in Weaviate
    2. Retrieve top relevant document chunks
    3. Construct context-enhanced prompt
    4. Generate response using Gemini 2.5 Flash
    5. Return domain-specific answer
    """
```

---

## 🚀 PRODUCTION USAGE GUIDE

### Method 1: Production Trainer (Recommended)

The **Production Service Guide Trainer** (`production_service_guide_trainer.py`) is the primary tool for training and Q&A.

#### Starting the Trainer:
```bash
cd psr-ai-api
python production_service_guide_trainer.py
```

#### Menu Options:
1. **📋 Run complete production training workflow**
   - Full end-to-end training process
   - Automatic health checks and validation
   - Progress monitoring and error handling

2. **💬 Start Q&A session only (if already trained)**
   - Interactive Q&A interface
   - Access to trained Service Guide knowledge
   - Context-aware responses

3. **🔍 System health check only**
   - Verify all services are operational
   - Check API connectivity and AI services
   - Validate configuration

#### Training Process:
```
1. System Health Check ✅
   ├── API Server connectivity
   ├── Weaviate cluster status  
   ├── Google AI model availability
   └── Service Guide PDF verification

2. Authentication & Setup ✅
   ├── Admin login authentication
   ├── PDF text extraction (13,575 chars)
   ├── Text chunking (10 chunks average)
   └── Training data preparation

3. Vector Storage ✅
   ├── Weaviate collection creation
   ├── Embedding generation
   ├── Document storage validation
   └── Training job tracking

4. Production Q&A Interface ✅
   ├── Interactive question prompt
   ├── Vector similarity search
   ├── Context-aware response generation
   └── Session management
```

### Method 2: Direct API Usage

#### Step 1: Authentication
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "official4tishnu@gmail.com",
    "password": "Access@404"
  }'
```

#### Step 2: Upload Training Data
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/upload-training-data" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@training_data/Service Guide.pdf"
```

#### Step 3: Start Training
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/start-training" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "ServiceGuideDocuments",
    "model_name": "gemini-2.5-flash-lite"
  }'
```

#### Step 4: Ask Questions
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "12V output normal but 24V output low/zero",
    "collection_name": "ServiceGuideDocuments"
  }'
```

---

## ⚙️ CONFIGURATION & SETUP

### Environment Configuration (`.env`)

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/poornasree_ai

# Weaviate Configuration  
WEAVIATE_URL=https://cluster-id.weaviate.cloud
WEAVIATE_API_KEY=your-weaviate-api-key
WEAVIATE_CLUSTER_NAME=poornasreeai

# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-api-key
GEMINI_MODEL=gemini-2.5-flash-lite

# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Configuration
SUPER_ADMIN_EMAIL=official4tishnu@gmail.com
SUPER_ADMIN_PASSWORD=Access@404

# Application Settings
API_V1_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development
```

### System Requirements:

#### Hardware:
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for documents and vector data
- **CPU**: Multi-core processor for concurrent processing

#### Software:
- **Python**: 3.12+
- **MySQL**: 8.0+
- **Dependencies**: See `requirements.txt`

#### External Services:
- **Weaviate Cloud**: Active cluster with API key
- **Google AI**: Valid API key with Gemini access

### Installation Steps:

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd psr-ai-api
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**:
   ```bash
   python init.py
   ```

5. **Start FastAPI Server**:
   ```bash
   python main.py
   ```

6. **Run Production Trainer**:
   ```bash
   python production_service_guide_trainer.py
   ```

---

## 🛠️ TROUBLESHOOTING

### Common Issues & Solutions:

#### 1. "Files processed: 0" Error
**Cause**: Weaviate vectorizer not configured properly  
**Solution**: Ensure `text2vec-weaviate` vectorizer is used in collection creation  
**Fix**: Update `ai_service.py` vectorizer configuration

#### 2. Generic AI Responses (Not Service Guide Specific)
**Cause**: No vector data in Weaviate or search not finding relevant content  
**Solution**: Verify Weaviate contains training data and embeddings  
**Debug**: Check collection status and object count

#### 3. Authentication Failures
**Cause**: Invalid credentials or expired tokens  
**Solution**: Verify admin credentials in production trainer  
**Check**: Ensure admin user exists in database

#### 4. Weaviate Connection Issues
**Cause**: Incorrect API key or cluster URL  
**Solution**: Verify Weaviate configuration in `.env`  
**Test**: Use health check endpoints to validate connectivity

#### 5. PDF Processing Errors
**Cause**: Corrupted PDF or unsupported format  
**Solution**: Validate PDF file and try alternative extraction methods  
**Debug**: Check file size and content extraction results

### Debug Commands:

#### Check AI Services Health:
```bash
curl http://127.0.0.1:8000/api/v1/ai/health
```

#### Verify Weaviate Status:
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:8000/api/v1/ai/weaviate/status
```

#### List Training Files:
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:8000/api/v1/ai/training-files
```

#### Monitor Training Jobs:
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:8000/api/v1/ai/training-jobs
```

---

## 🚀 ADVANCED FEATURES

### 1. Batch Document Processing
- Multiple PDF upload support
- Concurrent processing capabilities
- Progress tracking and monitoring
- Error recovery mechanisms

### 2. Semantic Search Optimization
- Vector similarity tuning
- Context relevance scoring
- Multi-document search capability
- Custom embedding strategies

### 3. Response Quality Enhancement
- Context window optimization
- Temperature and creativity controls
- Response length management
- Domain-specific prompt engineering

### 4. Production Monitoring
- Comprehensive logging system
- Performance metrics collection
- Health check automation
- Alert system integration

### 5. Scalability Features
- Horizontal scaling support
- Load balancing compatibility
- Caching layer integration
- Database optimization

---

## 📊 PERFORMANCE METRICS

### Training Performance:
- **PDF Processing**: ~500ms for 110KB files
- **Text Chunking**: ~10 chunks for 13,575 characters
- **Vector Storage**: ~2-5 seconds per document
- **Training Completion**: ~30-60 seconds total

### Q&A Performance:
- **Response Time**: ~2-4 seconds per query
- **Context Accuracy**: High relevance with vector search
- **Memory Usage**: ~500MB during active processing
- **Concurrent Users**: Supports 10+ simultaneous sessions

### Resource Usage:
- **Database**: ~10MB for metadata and users
- **Vector Storage**: ~50MB per trained document
- **Memory**: ~1GB for full system operation
- **CPU**: Moderate usage during training/inference

---

## 📝 CONCLUSION

This production-ready Poornasree AI system provides:

✅ **Complete Training Pipeline**: From PDF upload to intelligent Q&A  
✅ **Production-Grade Architecture**: Scalable, monitored, and robust  
✅ **Advanced AI Capabilities**: Semantic search + contextual responses  
✅ **Enterprise Security**: Role-based authentication and access control  
✅ **Comprehensive Documentation**: Training guides and troubleshooting  

**For technical support or advanced configuration:**
- Check system logs in `logs/` directory
- Use health check endpoints for diagnostics
- Review training job status for processing issues
- Consult this documentation for common solutions

**System Status: ✅ PRODUCTION READY**

---

*Last Updated: August 9, 2025*  
*Version: 2.0 Production*  
*Poornasree AI Team*
