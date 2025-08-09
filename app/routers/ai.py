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
    ## 📤 Upload Training Data Files
    
    Upload multiple files for AI model training using Weaviate and Gemini 2.5 Flash.
    Admin access required.
    
    **Supported File Types:**
    - PDF documents (.pdf)
    - Microsoft Word documents (.doc, .docx)
    - Plain text files (.txt)
    - JSON files (.json)
    - CSV files (.csv)
    
    **Processing:**
    - Files are processed and stored for vector embedding
    - Content is extracted and prepared for Weaviate indexing
    - Metadata is stored for training job management
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Files uploaded successfully",
      "files_processed": 3,
      "total_size": "2.5MB",
      "uploaded_by": "Admin Name"
    }
    ```
    """
    try:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided for upload"
            )
        
        # Process uploaded files through AI service
        result = await ai_service.process_training_files(files, current_user.email)
        
        return UploadTrainingDataResponse(
            success=True,
            message="Training data uploaded successfully",
            files_processed=result.get("files_processed", 0),
            total_size=result.get("total_size", "0B"),
            file_ids=result.get("file_ids", []),
            uploaded_by=f"{current_user.first_name} {current_user.last_name}",
            timestamp=get_current_timestamp()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training data upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload training data: {str(e)}"
        )


@router.post("/start-training", response_model=StartTrainingResponse)
async def start_training_job(
    request: StartTrainingRequest,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🚀 Start AI Model Training
    
    Initiate a new training job using uploaded data with Weaviate and Gemini 2.5 Flash.
    Admin access required.
    
    **Training Process:**
    1. **Data Preparation**: Process uploaded files and extract content
    2. **Vector Embedding**: Generate embeddings using Weaviate
    3. **Model Training**: Fine-tune using Gemini 2.5 Flash
    4. **Validation**: Test model performance and accuracy
    
    **Request Body:**
    ```json
    {
      "name": "Customer Support Training v1.0",
      "file_ids": ["file-123", "file-456"],
      "training_config": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10
      }
    }
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "job_id": "training-job-789",
      "status": "queued",
      "estimated_duration": "45 minutes"
    }
    ```
    """
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Training job name is required"
            )
        
        # Make file_ids optional - use recently uploaded files if not provided
        file_ids = request.file_ids if request.file_ids else []
        if len(file_ids) == 0:
            logger.info("No specific file IDs provided, using available training data")
            # In a real implementation, you'd fetch recently uploaded files
            file_ids = ["mock-file-1", "mock-file-2"]  # Mock file IDs for now
        
        # Start training job through AI service
        job_result = await ai_service.start_training_job(
            name=request.name.strip(),
            file_ids=file_ids,
            training_config=request.training_config.dict() if request.training_config else {},
            started_by=current_user.email
        )
        
        return StartTrainingResponse(
            success=True,
            job_id=job_result["job_id"],
            status=job_result["status"],
            message=f"Training job '{request.name}' started successfully",
            estimated_duration=job_result.get("estimated_duration", "2-4 hours"),
            file_count=len(file_ids),
            started_by=current_user.email,
            timestamp=get_current_timestamp()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training job start failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start training job: {str(e)}"
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
            "timestamp": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Failed to get training files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve training files: {str(e)}"
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


@router.delete("/training-files/{file_id}", response_model=DeleteTrainingFileResponse)
async def delete_training_file(
    file_id: str,
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 🗑️ Delete Training Data File
    
    Delete a specific training data file.
    Admin access required.
    
    **Path Parameters:**
    - `file_id`: Unique identifier of the file to delete
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Training file deleted successfully"
    }
    ```
    """
    try:
        if not file_id or not file_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File ID is required"
            )
        
        await ai_service.delete_training_file(file_id, current_user.email)
        
        return DeleteTrainingFileResponse(
            success=True,
            message="Training file deleted successfully",
            file_id=file_id,
            deleted_by=f"{current_user.first_name} {current_user.last_name}",
            timestamp=get_current_timestamp()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete training file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete training file: {str(e)}"
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
