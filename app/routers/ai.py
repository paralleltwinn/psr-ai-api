# =============================================================================
# POORNASREE AI - AI ROUTER
# =============================================================================

"""
AI endpoints for Weaviate and Google AI services.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from ..services.ai_service import ai_service
from ..auth.dependencies import get_current_active_user, require_admin_or_above
from ..database.models import User
from ..api import schemas
from ..api.schemas import TextGenerationRequest, get_current_timestamp

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
