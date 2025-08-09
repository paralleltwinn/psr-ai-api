# =============================================================================
# POORNASREE AI - AI ROUTER
# =============================================================================

"""
AI endpoints for Weaviate and Google AI services.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any, List
import logging

from ..services.ai_service import ai_service
from ..auth.dependencies import get_current_active_user, require_admin_or_above
from ..database.models import User
from ..api import schemas
from ..api.schemas import (
    TextGenerationRequest, get_current_timestamp,
    StartTrainingRequest, StartTrainingResponse,
    TrainingJobsResponse, UploadTrainingDataResponse,
    DeleteTrainingFileResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["AI Services"],
    responses={404: {"description": "Not found"}}
)


@router.get("/health", response_model=Dict[str, Any])
async def check_ai_health():
    """
    ## 🔍 AI Services Health Check
    
    Check the health and connectivity status of all AI services:
    - **Weaviate**: Vector database connection and cluster status
    - **Google AI**: Gemini model configuration and availability
    
    **Returns comprehensive status including:**
    - Service availability and connection status
    - Version information and capabilities
    - Error details if any issues are detected
    - Overall system health assessment
    
    **Example Response:**
    ```json
    {
      "timestamp": "2025-08-08T10:30:00Z",
      "overall_status": "healthy",
      "services": {
        "weaviate": {
          "service": "Weaviate",
          "connected": true,
          "cluster_name": "poornasreeai",
          "version": "1.25.0"
        },
        "google_ai": {
          "service": "Google AI",
          "configured": true,
          "model": "gemini-2.5-flash-lite",
          "status": "healthy"
        }
      }
    }
    ```
    """
    try:
        health_status = await ai_service.health_check()
        return health_status
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI health check failed: {str(e)}"
        )


@router.post("/initialize", response_model=Dict[str, Any])
async def initialize_ai_services(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🚀 Initialize AI Services
    
    Initialize and configure all AI services. Requires admin privileges.
    
    **Admin Only Endpoint** - Only users with ADMIN or SUPER_ADMIN roles can access.
    
    **Services Initialized:**
    - **Weaviate**: Establishes connection to vector database cluster
    - **Google AI**: Configures Gemini model with API credentials
    
    **Returns:**
    ```json
    {
      "message": "AI services initialization completed",
      "results": {
        "weaviate": true,
        "google_ai": true
      },
      "timestamp": "2025-08-08T10:30:00Z"
    }
    ```
    """
    try:
        results = await ai_service.initialize()
        
        return {
            "message": "AI services initialization completed",
            "results": results,
            "timestamp": get_current_timestamp(),
            "initialized_by": f"{current_user.first_name} {current_user.last_name}"
        }
    except Exception as e:
        logger.error(f"AI services initialization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI services initialization failed: {str(e)}"
        )


@router.get("/weaviate/status", response_model=Dict[str, Any])
async def get_weaviate_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 🗃️ Weaviate Database Status
    
    Get detailed status information for the Weaviate vector database.
    
    **Authenticated endpoint** - Requires valid user session.
    
    **Returns:**
    - Connection status and cluster information
    - Database schema and collections
    - Version and module information
    - Performance metrics if available
    
    **Example Response:**
    ```json
    {
      "service": "Weaviate",
      "connected": true,
      "cluster_name": "poornasreeai",
      "url": "https://chmjnz2nq6wviibztt7chg.c0.asia-southeast1.gcp.weaviate.cloud",
      "version": "1.25.0",
      "collections": ["Documents", "Users"],
      "modules": ["text2vec-openai", "generative-openai"]
    }
    ```
    """
    try:
        weaviate_status = await ai_service.weaviate.health_check()
        
        # Get additional schema information if connected
        if weaviate_status.get("connected"):
            schema_info = await ai_service.weaviate.get_schema()
            weaviate_status.update(schema_info)
        
        return weaviate_status
    except Exception as e:
        logger.error(f"Weaviate status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weaviate status check failed: {str(e)}"
        )


@router.get("/google-ai/status", response_model=Dict[str, Any])
async def get_google_ai_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 🤖 Google AI Service Status
    
    Get detailed status information for Google AI/Gemini integration.
    
    **Authenticated endpoint** - Requires valid user session.
    
    **Returns:**
    - Configuration status and model information
    - Available models and capabilities
    - API connectivity and response test results
    
    **Example Response:**
    ```json
    {
      "service": "Google AI",
      "configured": true,
      "model": "gemini-2.5-flash-lite",
      "status": "healthy",
      "available_models": [
        {
          "name": "models/gemini-2.5-flash-lite",
          "display_name": "Gemini 2.5 Flash Lite",
          "description": "Fast and efficient text generation"
        }
      ]
    }
    ```
    """
    try:
        google_ai_status = await ai_service.google_ai.health_check()
        
        # Get additional model information if configured
        if google_ai_status.get("configured"):
            model_info = await ai_service.google_ai.get_model_info()
            google_ai_status.update(model_info)
        
        return google_ai_status
    except Exception as e:
        logger.error(f"Google AI status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google AI status check failed: {str(e)}"
        )


@router.post("/google-ai/generate", response_model=Dict[str, Any])
async def generate_text(
    request: TextGenerationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    ## ✨ Generate Text with Gemini
    
    Generate text using Google's Gemini AI model.
    
    **Authenticated endpoint** - Requires valid user session.
    
    **Request Body:**
    ```json
    {
      "prompt": "Write a brief introduction to AI vector databases",
      "max_tokens": 500
    }
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "generated_text": "AI vector databases are specialized...",
      "model": "gemini-2.5-flash-lite",
      "tokens_used": 245,
      "generated_by": "John Doe"
    }
    ```
    """
    try:
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )
        
        generated_text = await ai_service.google_ai.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )
        
        if not generated_text:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Text generation failed. Please try again."
            )
        
        return {
            "success": True,
            "generated_text": generated_text,
            "model": ai_service.google_ai.model.model_name if ai_service.google_ai.model else "unknown",
            "prompt_length": len(request.prompt),
            "response_length": len(generated_text),
            "generated_by": f"{current_user.first_name} {current_user.last_name}",
            "timestamp": get_current_timestamp()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_ai_configuration(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## ⚙️ AI Configuration Information
    
    Get AI services configuration details. Admin access required.
    
    **Admin Only Endpoint** - Only users with ADMIN or SUPER_ADMIN roles can access.
    
    **Returns:**
    - Weaviate cluster configuration (without sensitive data)
    - Google AI model configuration
    - Service availability and version information
    
    **Security Note:** API keys and sensitive credentials are not included in the response.
    """
    try:
        from ..config import settings
        
        config_info = {
            "weaviate": {
                "cluster_name": settings.weaviate_cluster_name,
                "url": settings.weaviate_url,
                "grpc_url": settings.weaviate_grpc_url,
                "api_key_configured": bool(settings.weaviate_api_key)
            },
            "google_ai": {
                "model": settings.gemini_model,
                "api_key_configured": bool(settings.google_api_key)
            },
            "timestamp": get_current_timestamp(),
            "requested_by": f"{current_user.first_name} {current_user.last_name}"
        }
        
        return config_info
        
    except Exception as e:
        logger.error(f"Failed to get AI configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI configuration: {str(e)}"
        )


# =============================================================================
# AI TRAINING ENDPOINTS
# =============================================================================

@router.post("/upload-training-data", response_model=UploadTrainingDataResponse)
async def upload_training_data(
    files: List[UploadFile] = File(..., description="Training files to upload"),
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 📤 Upload Training Data Files (Enhanced with PDF Text Extraction)
    
    Upload multiple files for AI model training using Weaviate and Gemini 2.5 Flash.
    Now with advanced PDF text extraction using PyPDF2 for accurate content processing.
    Admin access required.
    
    **Supported File Types:**
    - PDF documents (.pdf) - Enhanced with PyPDF2 text extraction
    - Microsoft Word documents (.doc, .docx)
    - Plain text files (.txt)
    - JSON files (.json)
    - CSV files (.csv)
    
    **Enhanced Processing Features:**
    - Advanced PDF text extraction with page-by-page processing
    - Real-time content quality validation
    - Vector embedding preparation for Weaviate storage
    - Comprehensive metadata tracking and error handling
    - Content preview for uploaded files
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Files uploaded and processed successfully",
      "files_processed": 3,
      "total_size": "2.5MB",
      "file_ids": ["file_123", "file_456"],
      "uploaded_by": "Admin Name",
      "processing_details": {
        "pdf_files": 2,
        "text_extracted": "25.3 KB",
        "pages_processed": 47,
        "weaviate_stored": true
      }
    }
    ```
    """
    try:
        logger.info(f"📤 Enhanced upload request received with {len(files)} files")
        
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided for upload"
            )
        
        # Log detailed file information for processing
        processing_summary = {
            "pdf_files": 0,
            "text_files": 0,
            "json_files": 0,
            "csv_files": 0,
            "other_files": 0
        }
        
        for i, file in enumerate(files):
            content_type = getattr(file, 'content_type', 'unknown')
            logger.info(f"📄 File {i+1}: {file.filename}, type: {content_type}, size: {file.size} bytes")
            
            # Count file types for processing summary
            if content_type == "application/pdf":
                processing_summary["pdf_files"] += 1
            elif content_type == "text/plain":
                processing_summary["text_files"] += 1
            elif content_type == "application/json":
                processing_summary["json_files"] += 1
            elif content_type == "text/csv":
                processing_summary["csv_files"] += 1
            else:
                processing_summary["other_files"] += 1
        
        # Enhanced processing with detailed feedback
        logger.info("🔄 Starting enhanced file processing with PDF text extraction...")
        result = await ai_service.process_training_files(files, current_user.email)
        
        logger.info(f"✅ Enhanced processing completed: {result}")
        
        return UploadTrainingDataResponse(
            success=True,
            message=f"Training data uploaded and processed successfully with enhanced PDF extraction",
            files_processed=result.get("files_processed", 0),
            total_size=result.get("total_size", "0B"),
            file_ids=result.get("file_ids", []),
            uploaded_by=f"{current_user.first_name} {current_user.last_name}",
            timestamp=get_current_timestamp(),
            processing_details={
                "pdf_files_processed": processing_summary["pdf_files"],
                "total_files_by_type": processing_summary,
                "enhanced_extraction": True,
                "weaviate_integration": True,
                "text_extraction_method": "PyPDF2"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced training data upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload and process training data: {str(e)}"
        )


@router.post("/start-training", response_model=StartTrainingResponse)
async def start_training_job(
    request: StartTrainingRequest,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🚀 Start Enhanced AI Model Training
    
    Initiate a new training job using uploaded data with enhanced PDF text extraction,
    Weaviate vector storage, and Gemini 2.5 Flash fine-tuning.
    Admin access required.
    
    **Enhanced Training Process:**
    1. **Data Validation**: Verify uploaded files and extract quality metrics
    2. **Content Processing**: Enhanced PDF text extraction with PyPDF2
    3. **Vector Embedding**: Generate and store embeddings in Weaviate
    4. **Model Training**: Fine-tune using Gemini 2.5 Flash with extracted content
    5. **Quality Validation**: Test model performance and content accuracy
    6. **Deployment**: Activate trained model for production use
    
    **Request Body:**
    ```json
    {
      "name": "Customer Support Training v2.0 - Enhanced PDF",
      "file_ids": ["file-123", "file-456"],
      "training_config": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10,
        "use_enhanced_extraction": true
      }
    }
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "job_id": "training-job-789",
      "status": "initializing",
      "estimated_duration": "2-4 hours",
      "file_count": 5,
      "processing_details": {
        "pdf_files": 3,
        "total_content_size": "1.2 MB",
        "enhanced_extraction": true,
        "weaviate_ready": true
      }
    }
    ```
    """
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Training job name is required"
            )
        
        # Enhanced file validation and processing details
        file_ids = request.file_ids if request.file_ids else []
        if len(file_ids) == 0:
            logger.info("🔄 No specific file IDs provided, using recently uploaded files")
            # Get recent training files
            training_files = await ai_service.get_training_files()
            if training_files:
                file_ids = [f["file_id"] for f in training_files[:10]]  # Use last 10 files
                logger.info(f"📁 Using {len(file_ids)} recent training files")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No training files available. Please upload files first."
                )
        
        # Validate files exist and get processing details
        training_files = await ai_service.get_training_files()
        file_map = {f["file_id"]: f for f in training_files}
        
        valid_files = []
        pdf_count = 0
        total_content_size = 0
        
        for file_id in file_ids:
            if file_id in file_map:
                file_info = file_map[file_id]
                valid_files.append(file_info)
                total_content_size += file_info.get("size", 0)
                
                if file_info.get("content_type") == "application/pdf":
                    pdf_count += 1
            else:
                logger.warning(f"⚠️ File {file_id} not found in training files")
        
        if not valid_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid training files found for the specified file IDs"
            )
        
        # Enhanced training job creation
        logger.info(f"🚀 Starting enhanced training job with {len(valid_files)} files ({pdf_count} PDFs)")
        
        job_result = await ai_service.start_training_job(
            name=request.name.strip(),
            file_ids=[f["file_id"] for f in valid_files],
            training_config=request.training_config.model_dump() if request.training_config else {},
            started_by=current_user.email
        )
        
        return StartTrainingResponse(
            success=True,
            job_id=job_result["job_id"],
            status=job_result["status"],
            message=f"Enhanced training job '{request.name}' started with PDF text extraction",
            estimated_duration=job_result.get("estimated_duration", "2-4 hours"),
            file_count=len(valid_files),
            started_by=current_user.email,
            timestamp=get_current_timestamp(),
            processing_details={
                "pdf_files": pdf_count,
                "text_files": len(valid_files) - pdf_count,
                "total_content_size": f"{total_content_size / (1024*1024):.2f} MB",
                "enhanced_pdf_extraction": True,
                "weaviate_integration": True,
                "gemini_model": "gemini-2.5-flash-lite"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced training job start failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start enhanced training job: {str(e)}"
        )


@router.get("/training-files", response_model=Dict[str, Any])
async def get_training_files(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 📁 Get Training Files
    
    Retrieve all uploaded training files with metadata.
    
    **Returns:**
    ```json
    {
      "success": true,
      "files": [
        {
          "file_id": "file_abc123_1234567890",
          "filename": "training_document.pdf",
          "size": 1048576,
          "content_type": "application/pdf",
          "uploaded_at": "2025-08-09T10:30:00Z"
        }
      ],
      "total_files": 1,
      "total_size": "1.0 MB"
    }
    ```
    """
    try:
        files = await ai_service.get_training_files()
        
        total_size = sum(file.get("size", 0) for file in files)
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "success": True,
            "files": files,
            "total_files": len(files),
            "total_size": f"{total_size_mb:.2f} MB",
            "timestamp": get_current_timestamp(),
            "processing_capabilities": {
                "pdf_extraction": "Enhanced PyPDF2 text extraction",
                "content_preview": "Available for all file types",
                "vector_storage": "Weaviate integration active",
                "supported_formats": ["PDF", "TXT", "JSON", "CSV", "DOC", "DOCX"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get training files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve training files: {str(e)}"
        )


@router.get("/training-files/{file_id}/preview", response_model=Dict[str, Any])
async def get_file_content_preview(
    file_id: str,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 👁️ Get File Content Preview
    
    Get a preview of the extracted content from a training file.
    Shows the actual text extracted by the enhanced PDF processing system.
    
    **Returns:**
    ```json
    {
      "success": true,
      "file_id": "file_abc123",
      "filename": "training_document.pdf",
      "content_preview": "First 500 characters of extracted content...",
      "content_length": 15420,
      "extraction_method": "PyPDF2",
      "pages_processed": 12,
      "content_quality": "high"
    }
    ```
    """
    try:
        # Get file content through AI service
        preview_data = await ai_service.get_file_content_preview(file_id)
        
        if not preview_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training file with ID {file_id} not found"
            )
        
        return {
            "success": True,
            "timestamp": get_current_timestamp(),
            **preview_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file preview for {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file preview: {str(e)}"
        )


@router.get("/training-jobs", response_model=TrainingJobsResponse)
async def get_training_jobs(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 📊 Get Training Jobs Status
    
    Retrieve all training jobs and their current status.
    Admin access required.
    
    **Returns:**
    ```json
    {
      "success": true,
      "jobs": [
        {
          "job_id": "training-job-789",
          "name": "Customer Support Training v1.0",
          "status": "running",
          "progress": 65,
          "started_at": "2025-08-09T10:00:00Z",
          "estimated_completion": "2025-08-09T10:45:00Z",
          "file_count": 3
        }
      ],
      "total_jobs": 1
    }
    ```
    """
    try:
        jobs = await ai_service.get_training_jobs()
        
        return TrainingJobsResponse(
            success=True,
            jobs=jobs,
            total_jobs=len(jobs),
            timestamp=get_current_timestamp()
        )
        
    except Exception as e:
        logger.error(f"Failed to get training jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training jobs: {str(e)}"
        )


@router.delete("/training-files/{file_id}", response_model=DeleteTrainingFileResponse)
async def delete_training_file(
    file_id: str,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🗑️ Delete Training File
    
    Delete a specific training file and clean up all associated data:
    - Remove physical file from storage
    - Clean up Weaviate vector embeddings
    - Update training job references
    
    **Parameters:**
    - `file_id`: Unique identifier of the file to delete
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Training file deleted successfully",
      "file_id": "file_abc123_1234567890",
      "deleted_by": "admin@example.com",
      "weaviate_cleanup": true,
      "affected_jobs": 2
    }
    ```
    """
    try:
        result = await ai_service.delete_training_file(file_id, current_user.email)
        
        return DeleteTrainingFileResponse(
            success=result["success"],
            message=f"Training file {file_id} deleted successfully",
            file_id=file_id,
            deleted_by=result["deleted_by"],
            weaviate_cleanup=result.get("weaviate_cleanup", False),
            affected_jobs=result.get("active_jobs_affected", 0),
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Failed to delete training file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete training file: {str(e)}"
        )


@router.delete("/training-files", response_model=Dict[str, Any])
async def bulk_delete_training_files(
    file_ids: List[str],
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🗑️ Bulk Delete Training Files
    
    Delete multiple training files at once with comprehensive cleanup.
    
    **Request Body:**
    ```json
    ["file_abc123_1234567890", "file_def456_0987654321"]
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "deleted_files": [
        {
          "file_id": "file_abc123_1234567890",
          "status": "deleted"
        }
      ],
      "failed_files": [],
      "total_requested": 2,
      "deleted_by": "admin@example.com"
    }
    ```
    """
    try:
        if not file_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file IDs provided for deletion"
            )
        
        result = await ai_service.bulk_delete_training_files(file_ids, current_user.email)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to bulk delete training files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete training files: {str(e)}"
        )


@router.post("/cleanup-orphaned-data", response_model=Dict[str, Any])
async def cleanup_orphaned_data(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🧹 Cleanup Orphaned Data
    
    Clean up orphaned training data:
    - Files without proper metadata
    - Weaviate data without corresponding files
    - Invalid job references
    
    **Returns:**
    ```json
    {
      "orphaned_files": 2,
      "orphaned_weaviate_data": 1,
      "cleaned_job_references": 0,
      "timestamp": "2025-08-09T10:30:00Z"
    }
    ```
    """
    try:
        result = await ai_service.cleanup_orphaned_data()
        return result
        
    except Exception as e:
        logger.error(f"Failed to cleanup orphaned data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup orphaned data: {str(e)}"
        )


@router.delete("/vector-database/clear", response_model=Dict[str, Any])
async def clear_vector_database(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🗑️ Clear Vector Database
    
    Clear all trained data from the Weaviate vector database.
    This will remove all embeddings and vector data while keeping training files intact.
    
    **⚠️ Warning:** This action cannot be undone!
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Vector database cleared successfully",
      "deleted_collections": ["TrainingDocuments"],
      "deleted_objects": 156,
      "cleared_by": "admin@example.com",
      "timestamp": "2025-08-09T10:30:00Z"
    }
    ```
    """
    try:
        result = await ai_service.clear_vector_database(current_user.email)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "deleted_collections": result.get("deleted_collections", []),
            "deleted_objects": result.get("deleted_objects", 0),
            "cleared_by": current_user.email,
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to clear vector database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear vector database: {str(e)}"
        )


@router.delete("/vector-database/collection/{collection_name}", response_model=Dict[str, Any])
async def clear_vector_collection(
    collection_name: str,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🗑️ Clear Specific Vector Collection
    
    Clear a specific collection from the Weaviate vector database.
    
    **Parameters:**
    - `collection_name`: Name of the collection to clear (e.g., "TrainingDocuments")
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Collection TrainingDocuments cleared successfully",
      "collection_name": "TrainingDocuments",
      "deleted_objects": 156,
      "cleared_by": "admin@example.com",
      "timestamp": "2025-08-09T10:30:00Z"
    }
    ```
    """
    try:
        result = await ai_service.clear_vector_collection(collection_name, current_user.email)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "collection_name": collection_name,
            "deleted_objects": result.get("deleted_objects", 0),
            "cleared_by": current_user.email,
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to clear vector collection {collection_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear vector collection: {str(e)}"
        )


@router.get("/vector-database/status", response_model=Dict[str, Any])
async def get_vector_database_status(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 📊 Vector Database Status
    
    Get detailed status and statistics of the Weaviate vector database.
    
    **Returns:**
    ```json
    {
      "connected": true,
      "collections": [
        {
          "name": "TrainingDocuments",
          "object_count": 156,
          "size": "2.4 MB"
        }
      ],
      "total_objects": 156,
      "total_size": "2.4 MB",
      "last_updated": "2025-08-09T10:30:00Z"
    }
    ```
    """
    try:
        result = await ai_service.get_vector_database_status()
        return result
        
    except Exception as e:
        logger.error(f"Failed to get vector database status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vector database status: {str(e)}"
        )


@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_ai(
    request: schemas.ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 💬 Chat with AI
    
    Have a conversation with the trained AI model using Weaviate and Gemini.
    
    **Example Request:**
    ```json
    {
      "message": "How do I upload training data?",
      "conversation_id": "conv_123"
    }
    ```
    
    **Response:**
    ```json
    {
      "response": "To upload training data, you can use our file upload feature...",
      "conversation_id": "conv_123",
      "timestamp": "2025-08-09T01:53:00Z"
    }
    ```
    """
    try:
        # Ensure Weaviate connection is established before generating response
        if not ai_service.weaviate or not ai_service.weaviate.is_connected:
            logger.info("Establishing Weaviate connection for chat...")
            await ai_service.weaviate.connect()
        
        # Use AI service to generate response
        response = await ai_service.generate_chat_response(
            message=request.message,
            conversation_id=request.conversation_id,
            user_email=current_user.email
        )
        
        return {
            "response": response,
            "conversation_id": request.conversation_id,
            "timestamp": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Chat error for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_knowledge_base(
    request: schemas.SearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 🔍 Search Knowledge Base
    
    Search the trained knowledge base using semantic search with Weaviate.
    
    **Example Request:**
    ```json
    {
      "query": "file upload process",
      "limit": 5
    }
    ```
    
    **Response:**
    ```json
    {
      "results": [
        {
          "content": "To upload files, drag and drop them...",
          "score": 0.95,
          "metadata": {...}
        }
      ],
      "query": "file upload process",
      "total_results": 3
    }
    ```
    """
    try:
        # Ensure Weaviate connection is established before searching
        if not ai_service.weaviate or not ai_service.weaviate.is_connected:
            logger.info("Establishing Weaviate connection for search...")
            await ai_service.weaviate.connect()
        
        # Search using Weaviate
        results = await ai_service.search_knowledge_base(
            query=request.query,
            limit=request.limit or 5,
            user_email=current_user.email
        )
        
        return {
            "results": results,
            "query": request.query,
            "total_results": len(results),
            "timestamp": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Search error for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search processing failed: {str(e)}"
        )
