# =============================================================================
# POORNASREE AI - AI SERVICE
# =============================================================================

"""
AI service for Weaviate vector database and Google AI integration.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import weaviate
    from weaviate.client import WeaviateClient
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for Weaviate vector database operations."""
    
    def __init__(self):
        self.client: Optional[WeaviateClient] = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to Weaviate cluster."""
        if not WEAVIATE_AVAILABLE:
            logger.error("Weaviate client not available. Install with: pip install weaviate-client")
            return False
            
        try:
            # Connect to Weaviate cloud instance
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=settings.weaviate_url,
                auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key)
            )
            
            # Test connection
            if self.client.is_ready():
                self.is_connected = True
                logger.info(f"Successfully connected to Weaviate cluster: {settings.weaviate_cluster_name}")
                return True
            else:
                logger.error("Weaviate client is not ready")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Weaviate."""
        if self.client:
            try:
                self.client.close()
                self.is_connected = False
                logger.info("Disconnected from Weaviate")
            except Exception as e:
                logger.error(f"Error disconnecting from Weaviate: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Weaviate connection."""
        health_status = {
            "service": "Weaviate",
            "available": WEAVIATE_AVAILABLE,
            "connected": False,
            "cluster_name": settings.weaviate_cluster_name,
            "url": settings.weaviate_url,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None
        }
        
        if not WEAVIATE_AVAILABLE:
            health_status["error"] = "Weaviate client not installed"
            return health_status
        
        try:
            if not self.is_connected:
                await self.connect()
            
            if self.client and self.client.is_ready():
                # Get cluster metadata
                meta = self.client.get_meta()
                health_status.update({
                    "connected": True,
                    "version": meta.get("version", "unknown"),
                    "modules": list(meta.get("modules", {}).keys()) if meta.get("modules") else []
                })
            else:
                health_status["error"] = "Client not ready"
                
        except Exception as e:
            health_status["error"] = str(e)
            logger.error(f"Weaviate health check failed: {e}")
        
        return health_status
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get Weaviate schema information."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if self.client:
                collections = self.client.collections.list_all()
                return {
                    "collections": [collection.name for collection in collections],
                    "count": len(collections)
                }
            else:
                return {"error": "Not connected to Weaviate"}
                
        except Exception as e:
            logger.error(f"Failed to get Weaviate schema: {e}")
            return {"error": str(e)}


class GoogleAIService:
    """Service for Google AI/Gemini operations."""
    
    def __init__(self):
        self.is_configured = False
        self.model = None
        
    async def configure(self) -> bool:
        """Configure Google AI with API key."""
        if not GOOGLE_AI_AVAILABLE:
            logger.error("Google AI client not available. Install with: pip install google-generativeai")
            return False
            
        try:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
            self.is_configured = True
            logger.info(f"Successfully configured Google AI with model: {settings.gemini_model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure Google AI: {e}")
            self.is_configured = False
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Google AI connection."""
        health_status = {
            "service": "Google AI",
            "available": GOOGLE_AI_AVAILABLE,
            "configured": False,
            "model": settings.gemini_model,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None
        }
        
        if not GOOGLE_AI_AVAILABLE:
            health_status["error"] = "Google AI client not installed"
            return health_status
        
        try:
            if not self.is_configured:
                await self.configure()
            
            if self.is_configured and self.model:
                # Test with a simple prompt
                response = await self.generate_text("Hello, this is a health check test.")
                health_status.update({
                    "configured": True,
                    "test_response_length": len(response) if response else 0,
                    "status": "healthy" if response else "degraded"
                })
            else:
                health_status["error"] = "Model not configured"
                
        except Exception as e:
            health_status["error"] = str(e)
            logger.error(f"Google AI health check failed: {e}")
        
        return health_status
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Generate text using Gemini model."""
        try:
            if not self.is_configured:
                await self.configure()
            
            if not self.model:
                logger.error("Gemini model not available")
                return None
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            
            return response.text if response and response.text else None
            
        except Exception as e:
            logger.error(f"Failed to generate text with Gemini: {e}")
            return None
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        try:
            if not GOOGLE_AI_AVAILABLE:
                return {"error": "Google AI not available"}
            
            if not self.is_configured:
                await self.configure()
            
            models = genai.list_models()
            available_models = []
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append({
                        "name": model.name,
                        "display_name": model.display_name,
                        "description": model.description
                    })
            
            return {
                "current_model": settings.gemini_model,
                "available_models": available_models,
                "total_count": len(available_models)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"error": str(e)}


class AIService:
    """Combined AI service for Weaviate and Google AI."""
    
    def __init__(self):
        self.weaviate = WeaviateService()
        self.google_ai = GoogleAIService()
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all AI services."""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        # Check Weaviate
        weaviate_health = await self.weaviate.health_check()
        health_status["services"]["weaviate"] = weaviate_health
        
        # Check Google AI
        google_ai_health = await self.google_ai.health_check()
        health_status["services"]["google_ai"] = google_ai_health
        
        # Determine overall status
        errors = []
        if weaviate_health.get("error"):
            errors.append(f"Weaviate: {weaviate_health['error']}")
        if google_ai_health.get("error"):
            errors.append(f"Google AI: {google_ai_health['error']}")
        
        if errors:
            health_status["overall_status"] = "degraded" if len(errors) < 2 else "unhealthy"
            health_status["errors"] = errors
        
        return health_status
    
    async def initialize(self) -> Dict[str, bool]:
        """Initialize all AI services."""
        results = {
            "weaviate": await self.weaviate.connect(),
            "google_ai": await self.google_ai.configure()
        }
        
        return results
    
    async def cleanup(self):
        """Cleanup all AI service connections."""
        await self.weaviate.disconnect()


# Global AI service instance
ai_service = AIService()
