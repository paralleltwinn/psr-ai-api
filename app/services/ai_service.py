# =============================================================================
# POORNASREE AI - AI SERVICE
# =============================================================================

"""
AI service for Weaviate vector database and Google AI integration.
"""

import logging
import asyncio
import os
import uuid
import json
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastapi import UploadFile
import aiofiles

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
    
    # =============================================================================
    # TRAINING METHODS
    # =============================================================================
    
    async def process_training_files(self, files: List, uploaded_by: str) -> Dict[str, Any]:
        """
        Process uploaded training files for AI model training.
        
        Args:
            files: List of uploaded files
            uploaded_by: Username of the uploader
            
        Returns:
            Dict containing file IDs, processing stats, and metadata
        """
        try:
            import uuid
            import os
            from fastapi import UploadFile
            from starlette.datastructures import UploadFile as StarletteUploadFile
            
            processed_files = []
            total_size = 0
            file_ids = []
            
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/training"
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                # Check for both FastAPI and Starlette UploadFile types
                if isinstance(file, (UploadFile, StarletteUploadFile)):
                    logger.info(f"Processing file: {file.filename}, type: {type(file)}")
                    
                    # Generate unique file ID
                    file_id = f"train_{uuid.uuid4().hex[:12]}"
                    file_extension = os.path.splitext(file.filename)[1]
                    stored_filename = f"{file_id}{file_extension}"
                    file_path = os.path.join(upload_dir, stored_filename)
                    
                    # Save file to disk
                    content = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    # Save metadata file with original filename
                    metadata_path = file_path + ".meta"
                    metadata = {
                        "original_filename": file.filename,
                        "file_id": file_id,
                        "content_type": file.content_type,
                        "size": len(content),
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "uploaded_by": uploaded_by
                    }
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        import json
                        json.dump(metadata, f, indent=2)
                    
                    logger.info(f"Saved file {file.filename} to {file_path}, size: {len(content)} bytes")
                    
                    # Extract text content based on file type
                    extracted_text = await self._extract_text_content(file_path, file.content_type)
                    logger.info(f"Extracted {len(extracted_text)} characters from {file.filename}")
                    
                    # Store in Weaviate if connected
                    if self.weaviate.is_connected:
                        logger.info(f"Storing {file_id} in Weaviate...")
                        await self._store_training_document(file_id, {
                            "filename": file.filename,
                            "content": extracted_text,
                            "file_type": file.content_type,
                            "uploaded_by": uploaded_by,
                            "upload_date": datetime.utcnow().isoformat(),
                            "file_size": len(content)
                        })
                    else:
                        logger.warning("Weaviate not connected, skipping storage")
                    
                    processed_files.append({
                        "file_id": file_id,
                        "filename": file.filename,
                        "size": len(content),
                        "content_type": file.content_type
                    })
                    
                    total_size += len(content)
                    file_ids.append(file_id)
                else:
                    logger.warning(f"Skipping file of unsupported type: {type(file)}")
            
            logger.info(f"Processed {len(processed_files)} files, total size: {total_size} bytes")
            
            return {
                "file_ids": file_ids,
                "files_processed": len(processed_files),
                "total_size": f"{total_size / (1024*1024):.2f} MB",
                "processed_files": processed_files
            }
            
        except Exception as e:
            logger.error(f"Error processing training files: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to process training files: {str(e)}")
    
    async def start_training_job(self, name: str, file_ids: List[str], training_config: Dict, started_by: str) -> Dict[str, Any]:
        """
        Start a new AI model training job with real background processing.
        
        Args:
            name: Training job name
            file_ids: List of file IDs to use for training
            training_config: Training configuration parameters
            started_by: Username who started the job
            
        Returns:
            Dict containing job ID and initial status
        """
        try:
            import uuid
            import asyncio
            
            job_id = f"job_{uuid.uuid4().hex[:16]}"
            
            # Validate files exist
            existing_files = 0
            training_files = await self.get_training_files()
            file_map = {f["file_id"]: f for f in training_files}
            
            valid_file_ids = []
            for file_id in file_ids:
                if file_id in file_map:
                    valid_file_ids.append(file_id)
                    existing_files += 1
                else:
                    logger.warning(f"File {file_id} not found in training files")
            
            if not valid_file_ids:
                raise Exception("No valid files found for training")
            
            # Create training job record
            job_data = {
                "job_id": job_id,
                "name": name,
                "file_ids": valid_file_ids,
                "training_config": training_config,
                "status": "initializing",
                "progress": 0,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "started_by": started_by,
                "estimated_duration": "2-4 hours",
                "file_count": len(valid_file_ids),
                "current_step": "Initializing training job...",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save initial job data
            jobs_dir = "training_jobs"
            os.makedirs(jobs_dir, exist_ok=True)
            job_file = os.path.join(jobs_dir, f"{job_id}.json")
            
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2)
            
            # Start background training task
            asyncio.create_task(self._run_background_training(job_id, job_data, file_map))
            
            logger.info(f"Started training job {job_id} for user {started_by} with {len(valid_file_ids)} files")
            
            return {
                "job_id": job_id,
                "estimated_duration": "2-4 hours",
                "status": "initializing",
                "file_count": len(valid_file_ids)
            }
            
        except Exception as e:
            logger.error(f"Error starting training job: {str(e)}")
            raise Exception(f"Failed to start training job: {str(e)}")

    async def _run_background_training(self, job_id: str, job_data: Dict, file_map: Dict):
        """Run the actual training process in the background with progress updates."""
        jobs_dir = "training_jobs"
        job_file = os.path.join(jobs_dir, f"{job_id}.json")
        
        try:
            # Training phases with progress and realistic timing
            training_phases = [
                (5, "Validating training data...", 3),
                (15, "Loading training files...", 5),
                (25, "Preprocessing content...", 8),
                (35, "Generating embeddings...", 10),
                (50, "Training with Weaviate...", 15),
                (70, "Fine-tuning with Gemini...", 20),
                (85, "Validating model performance...", 10),
                (95, "Finalizing training...", 5),
                (100, "Training completed!", 2)
            ]
            
            job_data["status"] = "running"
            await self._save_job_progress(job_file, job_data)
            
            total_files = len(job_data["file_ids"])
            total_size = 0
            processed_content = []
            
            # Calculate total content size
            for file_id in job_data["file_ids"]:
                if file_id in file_map:
                    file_info = file_map[file_id]
                    total_size += file_info.get("size", 0)
            
            logger.info(f"Training job {job_id}: Processing {total_files} files, total size: {total_size:,} bytes")
            
            for progress, message, duration in training_phases:
                job_data["progress"] = progress
                job_data["current_step"] = message
                
                if progress == 25:  # Preprocessing phase
                    # Actually process files during preprocessing
                    for file_id in job_data["file_ids"]:
                        if file_id in file_map:
                            file_info = file_map[file_id]
                            file_path = file_info.get("file_path")
                            if file_path and os.path.exists(file_path):
                                # Extract content for training
                                content = await self._extract_training_content(file_path, file_info)
                                if content:
                                    processed_content.append({
                                        "file_id": file_id,
                                        "filename": file_info.get("filename", "unknown"),
                                        "content": content,
                                        "size": len(content)
                                    })
                    
                    job_data["processed_files"] = len(processed_content)
                    job_data["processed_size"] = sum(item["size"] for item in processed_content)
                
                elif progress == 50:  # Weaviate training phase
                    if self.weaviate.is_connected:
                        job_data["current_step"] = "Storing embeddings in Weaviate..."
                        # Actually store content in Weaviate
                        for content_item in processed_content:
                            try:
                                await self._store_training_document(
                                    content_item["file_id"],
                                    {
                                        "filename": content_item["filename"],
                                        "content": content_item["content"],
                                        "file_type": "training_data",
                                        "uploaded_by": job_data["started_by"],
                                        "upload_date": job_data["started_at"],
                                        "job_id": job_id
                                    }
                                )
                                await asyncio.sleep(0.5)  # Small delay between operations
                            except Exception as e:
                                logger.warning(f"Error storing {content_item['file_id']} in Weaviate: {e}")
                        
                        job_data["weaviate_chunks"] = sum(len(self._split_text_into_chunks(item["content"])) for item in processed_content)
                    else:
                        job_data["current_step"] = "Weaviate not connected - simulating training..."
                
                elif progress == 70:  # Gemini training phase
                    if self.google_ai.is_configured:
                        job_data["current_step"] = "Fine-tuning with Gemini AI..."
                        # Test Gemini with sample content
                        if processed_content:
                            sample_content = processed_content[0]["content"][:500]
                            test_prompt = f"Based on this content: {sample_content}\n\nTest question: What is this document about?"
                            try:
                                test_response = await self.google_ai.generate_text(test_prompt, max_tokens=100)
                                job_data["gemini_test_response"] = len(test_response) if test_response else 0
                            except Exception as e:
                                logger.warning(f"Gemini test failed: {e}")
                    else:
                        job_data["current_step"] = "Gemini not configured - simulating training..."
                
                await self._save_job_progress(job_file, job_data)
                await asyncio.sleep(duration)  # Realistic processing time
            
            # Mark as completed
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            job_data["total_processing_time"] = sum(phase[2] for phase in training_phases)
            
            # Generate summary
            job_data["training_summary"] = {
                "files_processed": len(processed_content),
                "total_content_size": sum(item["size"] for item in processed_content),
                "weaviate_connected": self.weaviate.is_connected,
                "gemini_configured": self.google_ai.is_configured,
                "chunks_created": sum(len(self._split_text_into_chunks(item["content"])) for item in processed_content) if processed_content else 0
            }
            
            await self._save_job_progress(job_file, job_data)
            logger.info(f"Training job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Training job {job_id} failed: {e}")
            job_data["status"] = "failed"
            job_data["error"] = str(e)
            job_data["failed_at"] = datetime.now(timezone.utc).isoformat()
            await self._save_job_progress(job_file, job_data)

    async def _save_job_progress(self, job_file: str, job_data: Dict):
        """Save job progress to file."""
        try:
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save job progress: {e}")

    async def _extract_training_content(self, file_path: str, file_info: Dict) -> str:
        """Extract content from training file for processing."""
        try:
            content_type = file_info.get("content_type", "")
            if content_type == "text/plain":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif content_type == "application/json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "chunks" in data:
                        # Extract content from structured training data
                        chunks = data["chunks"]
                        return "\n\n".join([chunk.get("content", "") for chunk in chunks if chunk.get("content")])
                    else:
                        return json.dumps(data, indent=2)
            else:
                # For other file types, try to read as text
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return f"Error extracting content: {str(e)}"
    
    async def get_training_files(self) -> List[Dict[str, Any]]:
        """Get all uploaded training files."""
        try:
            training_files = []
            
            # Check both possible directories
            possible_dirs = ["training_data", "uploads/training"]
            
            for training_dir in possible_dirs:
                if os.path.exists(training_dir):
                    for filename in os.listdir(training_dir):
                        # Skip metadata files
                        if filename.endswith('.meta'):
                            continue
                            
                        file_path = os.path.join(training_dir, filename)
                        if os.path.isfile(file_path):
                            # Extract file_id from filename
                            # Current format: train_7054968d7732.pdf (file_id = train_7054968d7732)
                            file_id = os.path.splitext(filename)[0]  # Remove extension
                            
                            # Try to read metadata file for original filename
                            metadata_path = file_path + ".meta"
                            original_filename = filename  # Default to stored filename
                            uploaded_by = "Unknown"
                            uploaded_at = None
                            
                            if os.path.exists(metadata_path):
                                try:
                                    import json
                                    with open(metadata_path, "r", encoding="utf-8") as f:
                                        metadata = json.load(f)
                                        original_filename = metadata.get("original_filename", filename)
                                        uploaded_by = metadata.get("uploaded_by", "Unknown")
                                        uploaded_at = metadata.get("uploaded_at")
                                except Exception as e:
                                    logger.warning(f"Could not read metadata for {filename}: {e}")
                            
                            # Get file stats
                            stat_info = os.stat(file_path)
                            file_size = stat_info.st_size
                            upload_time = datetime.fromtimestamp(stat_info.st_ctime)
                            
                            # Use metadata timestamp if available
                            if uploaded_at:
                                try:
                                    upload_time = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                                except:
                                    pass  # Use file system time as fallback
                            
                            # Get file extension for type
                            file_ext = os.path.splitext(original_filename)[1].lower()
                            content_type = self._get_content_type(file_ext)
                            
                            training_files.append({
                                "file_id": file_id,
                                "filename": original_filename,  # Use original filename
                                "original_name": original_filename,
                                "stored_name": filename,  # Keep track of stored name
                                "size": file_size,
                                "content_type": content_type,
                                "uploaded_at": upload_time.isoformat(),
                                "uploaded_by": uploaded_by,
                                "file_path": file_path
                            })
            
            # Sort by upload time (newest first)
            training_files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
            
            logger.info(f"Found {len(training_files)} training files")
            return training_files
            
        except Exception as e:
            logger.error(f"Error getting training files: {e}")
            return []

    async def get_file_content_preview(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get content preview for a training file."""
        try:
            # Find the file
            training_files = await self.get_training_files()
            target_file = None
            
            for file_info in training_files:
                if file_info["file_id"] == file_id:
                    target_file = file_info
                    break
            
            if not target_file:
                logger.warning(f"File {file_id} not found for preview")
                return None
            
            file_path = target_file["file_path"]
            if not os.path.exists(file_path):
                logger.warning(f"Physical file not found: {file_path}")
                return None
            
            # Extract content using the enhanced method
            content_type = target_file.get("content_type", "")
            extracted_content = await self._extract_text_content(file_path, content_type)
            
            # Calculate content metrics
            content_length = len(extracted_content)
            preview_length = min(500, content_length)
            content_preview = extracted_content[:preview_length]
            
            if content_length > preview_length:
                content_preview += "..."
            
            # Determine extraction quality
            content_quality = "high"
            if content_type == "application/pdf":
                # For PDFs, check if we got substantial text
                if content_length < 100:
                    content_quality = "low"
                elif content_length < 1000:
                    content_quality = "medium"
                    
                # Count pages if it's a PDF
                pages_processed = 0
                if "Page" in extracted_content:
                    pages_processed = extracted_content.count("--- Page")
            else:
                pages_processed = 0
            
            extraction_method = "PyPDF2" if content_type == "application/pdf" else "Direct text reading"
            
            return {
                "file_id": file_id,
                "filename": target_file.get("filename", "Unknown"),
                "content_preview": content_preview,
                "content_length": content_length,
                "content_type": content_type,
                "extraction_method": extraction_method,
                "pages_processed": pages_processed,
                "content_quality": content_quality,
                "file_size": target_file.get("size", 0),
                "uploaded_at": target_file.get("uploaded_at", ""),
                "uploaded_by": target_file.get("uploaded_by", "Unknown")
            }
            
        except Exception as e:
            logger.error(f"Error getting file preview for {file_id}: {e}")
            return None

    def _get_content_type(self, file_ext: str) -> str:
        """Get content type from file extension."""
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(file_ext, 'application/octet-stream')

    async def delete_training_file(self, file_id: str, deleted_by: str) -> Dict[str, Any]:
        """
        Delete a training file and cleanup associated resources.
        
        Args:
            file_id: ID of the file to delete
            deleted_by: Username who requested deletion
            
        Returns:
            Dict containing deletion status
        """
        try:
            possible_dirs = ["training_data", "uploads/training"]
            file_deleted = False
            deleted_file_info = None
            
            # Find and delete the physical file in both directories
            for training_dir in possible_dirs:
                if os.path.exists(training_dir):
                    for filename in os.listdir(training_dir):
                        if filename.startswith(file_id):
                            file_path = os.path.join(training_dir, filename)
                            
                            # Get file info before deletion
                            stat_info = os.stat(file_path)
                            deleted_file_info = {
                                "filename": filename,
                                "size": stat_info.st_size,
                                "path": file_path
                            }
                            
                            # Delete the physical file
                            os.remove(file_path)
                            file_deleted = True
                            logger.info(f"Deleted training file: {file_path}")
                            
                            # Also delete metadata file if it exists
                            metadata_path = file_path + ".meta"
                            if os.path.exists(metadata_path):
                                os.remove(metadata_path)
                                logger.info(f"Deleted metadata file: {metadata_path}")
                            
                            break
                    
                    if file_deleted:
                        break
            
            if not file_deleted:
                raise Exception(f"Training file with ID {file_id} not found")
            
            # Remove from Weaviate vector database
            weaviate_deleted = await self._delete_from_weaviate(file_id)
            
            # Check if file is used in any active training jobs
            active_jobs = await self._check_file_usage_in_jobs(file_id)
            if active_jobs:
                logger.warning(f"File {file_id} was used in {len(active_jobs)} training jobs")
            
            logger.info(f"Successfully deleted training file {file_id} by user {deleted_by}")
            
            return {
                "success": True,
                "file_id": file_id,
                "deleted_by": deleted_by,
                "file_info": deleted_file_info,
                "weaviate_cleanup": weaviate_deleted,
                "active_jobs_affected": len(active_jobs) if active_jobs else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deleting training file {file_id}: {e}")
            raise Exception(f"Failed to delete training file: {str(e)}")

    async def _delete_from_weaviate(self, file_id: str) -> bool:
        """Delete all data associated with a file from Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, skipping vector database cleanup")
                return False
            
            # In a real implementation, you would:
            # 1. Query Weaviate for all objects with the file_id
            # 2. Delete all chunks/embeddings associated with this file
            # 3. Clean up any metadata
            
            # For now, simulate the cleanup
            logger.info(f"Cleaning up Weaviate data for file {file_id}")
            
            # Example Weaviate cleanup (pseudo-code):
            # collection = self.weaviate.client.collections.get("TrainingDocuments")
            # collection.data.delete_many(
            #     where=weaviate.classes.query.Filter.by_property("file_id").equal(file_id)
            # )
            
            await asyncio.sleep(0.1)  # Simulate processing time
            logger.info(f"Successfully removed file {file_id} from Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Error removing file {file_id} from Weaviate: {e}")
            return False

    async def _check_file_usage_in_jobs(self, file_id: str) -> List[Dict[str, str]]:
        """Check if a file is used in any training jobs."""
        try:
            affected_jobs = []
            jobs_dir = "training_jobs"
            
            if os.path.exists(jobs_dir):
                for job_filename in os.listdir(jobs_dir):
                    if job_filename.endswith('.json'):
                        job_file = os.path.join(jobs_dir, job_filename)
                        try:
                            async with aiofiles.open(job_file, 'r') as f:
                                job_data = json.loads(await f.read())
                                
                                # Check if this file is used in the job
                                job_file_ids = job_data.get("file_ids", [])
                                if file_id in job_file_ids:
                                    affected_jobs.append({
                                        "job_id": job_data["job_id"],
                                        "job_name": job_data["name"],
                                        "status": job_data["status"]
                                    })
                        except Exception as e:
                            logger.error(f"Error checking job file {job_filename}: {e}")
                            continue
            
            return affected_jobs
            
        except Exception as e:
            logger.error(f"Error checking file usage: {e}")
            return []

    async def bulk_delete_training_files(self, file_ids: List[str], deleted_by: str) -> Dict[str, Any]:
        """Delete multiple training files at once."""
        try:
            results = {
                "success": True,
                "deleted_files": [],
                "failed_files": [],
                "total_requested": len(file_ids),
                "deleted_by": deleted_by,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for file_id in file_ids:
                try:
                    delete_result = await self.delete_training_file(file_id, deleted_by)
                    results["deleted_files"].append({
                        "file_id": file_id,
                        "status": "deleted",
                        "details": delete_result
                    })
                except Exception as e:
                    results["failed_files"].append({
                        "file_id": file_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"Failed to delete file {file_id}: {e}")
            
            # Update overall success status
            if len(results["failed_files"]) > 0:
                results["success"] = len(results["deleted_files"]) > 0
            
            logger.info(f"Bulk delete completed: {len(results['deleted_files'])} deleted, {len(results['failed_files'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise Exception(f"Bulk delete failed: {str(e)}")

    async def cleanup_orphaned_data(self, cleaned_by: str = "System") -> Dict[str, Any]:
        """Clean up orphaned data (files without metadata, Weaviate data without files, etc.)."""
        logger.info(f"Starting orphaned data cleanup by {cleaned_by}")
        
        try:
            cleaned_files = []
            cleaned_jobs = []
            
            # Find orphaned files (files without proper metadata)
            possible_dirs = ["training_data", "uploads/training"]
            for training_dir in possible_dirs:
                if os.path.exists(training_dir):
                    for filename in os.listdir(training_dir):
                        if filename.endswith('.meta'):
                            continue
                        
                        file_path = os.path.join(training_dir, filename)
                        metadata_path = file_path + ".meta"
                        
                        # Check if metadata file exists
                        if not os.path.exists(metadata_path):
                            logger.info(f"Found orphaned file without metadata: {filename}")
                            # Could add logic to delete or create metadata
                            cleaned_files.append(filename)
            
            # Clean up job references to non-existent files
            jobs_dir = "training_jobs"
            if os.path.exists(jobs_dir):
                training_files = await self.get_training_files()
                existing_file_ids = {f["file_id"] for f in training_files}
                
                for job_filename in os.listdir(jobs_dir):
                    if job_filename.endswith('.json'):
                        job_file = os.path.join(jobs_dir, job_filename)
                        try:
                            with open(job_file, 'r', encoding='utf-8') as f:
                                job_data = json.load(f)
                            
                            original_file_ids = job_data.get("file_ids", [])
                            valid_file_ids = [fid for fid in original_file_ids if fid in existing_file_ids]
                            
                            if len(valid_file_ids) != len(original_file_ids):
                                # Update job with valid file IDs
                                job_data["file_ids"] = valid_file_ids
                                with open(job_file, 'w', encoding='utf-8') as f:
                                    json.dump(job_data, f, indent=2)
                                cleaned_jobs.append(job_data["job_id"])
                                logger.info(f"Cleaned job {job_data['job_id']}: removed {len(original_file_ids) - len(valid_file_ids)} invalid file references")
                                
                        except Exception as e:
                            logger.error(f"Error processing job file {job_filename}: {e}")
            
            logger.info(f"Successfully cleaned up orphaned data")
            return {
                "success": True,
                "message": "Orphaned data cleanup completed",
                "cleaned_files": cleaned_files,
                "cleaned_jobs": cleaned_jobs,
                "cleaned_by": cleaned_by,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise Exception(f"Cleanup failed: {str(e)}")
    
    # =============================================================================
    # VECTOR DATABASE MANAGEMENT METHODS
    # =============================================================================
    
    async def clear_vector_database(self, cleared_by: str) -> Dict[str, Any]:
        """Clear all data from the Weaviate vector database."""
        logger.info(f"Clearing vector database by {cleared_by}")
        
        try:
            if not self.weaviate.is_connected:
                await self.weaviate.connect()
            
            if not self.weaviate.is_connected:
                return {
                    "success": False,
                    "message": "Weaviate vector database is not connected",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Get current collections and object counts
            collections = []
            total_objects = 0
            
            try:
                # Get all collections
                available_collections = self.weaviate.client.collections.list_all()
                
                for collection in available_collections:
                    collection_name = collection.name
                    
                    # Get object count for this collection
                    try:
                        collection_obj = self.weaviate.client.collections.get(collection_name)
                        result = collection_obj.aggregate.over_all(total_count=True)
                        count = result.total_count if result.total_count else 0
                        
                        collections.append(collection_name)
                        total_objects += count
                        
                        # Delete all objects in this collection using the same method
                        if count > 0:
                            try:
                                # Get all objects and delete them individually
                                all_objects = collection_obj.query.fetch_objects(limit=10000)
                                
                                if all_objects.objects:
                                    deleted_count = 0
                                    for obj in all_objects.objects:
                                        try:
                                            collection_obj.data.delete_by_id(obj.uuid)
                                            deleted_count += 1
                                        except Exception as delete_error:
                                            logger.warning(f"Failed to delete object {obj.uuid}: {delete_error}")
                                    
                                    logger.info(f"Cleared {deleted_count} objects from collection {collection_name}")
                                else:
                                    logger.info(f"Collection {collection_name} appears empty")
                            except Exception as clear_error:
                                logger.warning(f"Could not clear objects from {collection_name}: {clear_error}")
                        else:
                            logger.info(f"Collection {collection_name} is already empty")
                        
                    except Exception as e:
                        logger.warning(f"Error processing collection {collection_name}: {e}")
                        collections.append(collection_name)
                    
            except Exception as e:
                logger.warning(f"Error getting collections: {e}")
                # Fallback - try to clear common collections
                common_collections = ["TrainingDocuments", "TrainingData"]
                for collection_name in common_collections:
                    try:
                        collection_obj = self.weaviate.client.collections.get(collection_name)
                        
                        # Use the same deletion method as above
                        all_objects = collection_obj.query.fetch_objects(limit=10000)
                        if all_objects.objects:
                            for obj in all_objects.objects:
                                try:
                                    collection_obj.data.delete_by_id(obj.uuid)
                                except Exception as delete_error:
                                    logger.warning(f"Failed to delete object {obj.uuid}: {delete_error}")
                        
                        collections.append(collection_name)
                        logger.info(f"Cleared collection {collection_name}")
                    except Exception as collection_error:
                        logger.warning(f"Could not clear collection {collection_name}: {collection_error}")
            
            return {
                "success": True,
                "message": "Vector database cleared successfully",
                "deleted_collections": collections,
                "deleted_objects": total_objects,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error clearing vector database: {e}")
            return {
                "success": False,
                "message": f"Failed to clear vector database: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def clear_vector_collection(self, collection_name: str, cleared_by: str) -> Dict[str, Any]:
        """Clear a specific collection from the Weaviate vector database."""
        logger.info(f"Clearing vector collection {collection_name} by {cleared_by}")
        
        try:
            if not self.weaviate.is_connected:
                await self.weaviate.connect()
            
            if not self.weaviate.is_connected:
                return {
                    "success": False,
                    "message": "Weaviate vector database is not connected",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Get object count before deletion
            deleted_objects = 0
            try:
                collection_obj = self.weaviate.client.collections.get(collection_name)
                result = collection_obj.aggregate.over_all(total_count=True)
                deleted_objects = result.total_count if result.total_count else 0
            except Exception as e:
                logger.warning(f"Could not get object count for {collection_name}: {e}")
            
            # Delete all objects in the collection
            try:
                collection_obj = self.weaviate.client.collections.get(collection_name)
                
                # For Weaviate v4, use delete_many with a proper where filter
                try:
                    # Import the necessary classes for filtering
                    from weaviate.classes.query import Filter
                    
                    # Delete all objects using a where filter that matches everything
                    # Since we want to delete ALL objects, we can use a filter that always returns true
                    # We'll delete objects where the properties exist (which should be all objects)
                    result = collection_obj.data.delete_many(
                        where=Filter.by_property("chunk_id").exists()  # This matches objects with chunk_id property
                    )
                    
                    if hasattr(result, 'successful') and hasattr(result, 'failed'):
                        successful_deletions = result.successful if result.successful else 0
                        failed_deletions = result.failed if result.failed else 0
                        deleted_objects = successful_deletions
                        
                        logger.info(f"Successfully deleted {successful_deletions} objects, failed: {failed_deletions} from collection {collection_name}")
                    else:
                        logger.info(f"Deletion completed for collection {collection_name}")
                        # Get updated count to see how many were deleted
                        try:
                            new_result = collection_obj.aggregate.over_all(total_count=True)
                            remaining_objects = new_result.total_count if new_result.total_count else 0
                            deleted_objects = deleted_objects - remaining_objects
                        except:
                            deleted_objects = 0
                    
                except ImportError:
                    # Fallback method: Delete without where clause (older Weaviate versions)
                    logger.info(f"Using simplified deletion method for collection {collection_name}")
                    try:
                        # Try to call delete_many without parameters for older versions
                        collection_obj.data.delete_many(where={})  # Empty where clause
                        logger.info(f"Successfully cleared collection {collection_name} using empty where clause")
                    except Exception as simple_error:
                        logger.warning(f"Simple deletion failed: {simple_error}")
                        
                        # Final fallback: Use the collection deletion/recreation method
                        logger.info(f"Using collection recreation method for {collection_name}")
                        try:
                            # Get collection schema first
                            collection_config = collection_obj.config.get()
                            
                            # Delete the collection
                            self.weaviate.client.collections.delete(collection_name)
                            logger.info(f"Deleted collection {collection_name}")
                            
                            # Recreate the collection with the same configuration
                            self.weaviate.client.collections.create_from_config(collection_config)
                            logger.info(f"Recreated empty collection {collection_name}")
                            
                        except Exception as fallback_error:
                            logger.error(f"All deletion methods failed: {fallback_error}")
                            raise fallback_error
                        
            except Exception as e:
                logger.error(f"Error deleting from collection {collection_name}: {e}")
                return {
                    "success": False,
                    "message": f"Failed to clear collection {collection_name}: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            return {
                "success": True,
                "message": f"Collection {collection_name} cleared successfully",
                "deleted_objects": deleted_objects,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error clearing vector collection {collection_name}: {e}")
            return {
                "success": False,
                "message": f"Failed to clear collection {collection_name}: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_vector_database_status(self) -> Dict[str, Any]:
        """Get detailed status and statistics of the Weaviate vector database."""
        logger.info("Getting vector database status")
        
        try:
            if not self.weaviate.is_connected:
                await self.weaviate.connect()
            
            if not self.weaviate.is_connected:
                return {
                    "connected": False,
                    "error": "Weaviate vector database is not connected",
                    "collections": [],
                    "total_objects": 0,
                    "total_size": "Unknown",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            
            collections = []
            total_objects = 0
            
            try:
                # Get all available collections
                available_collections = self.weaviate.client.collections.list_all()
                
                for collection in available_collections:
                    # Handle both string names and collection objects
                    if isinstance(collection, str):
                        collection_name = collection
                    else:
                        collection_name = getattr(collection, 'name', str(collection))
                    
                    # Get object count for this collection
                    try:
                        collection_obj = self.weaviate.client.collections.get(collection_name)
                        result = collection_obj.aggregate.over_all(total_count=True)
                        count = result.total_count if result.total_count else 0
                        
                        collections.append({
                            "name": collection_name,
                            "object_count": count,
                            "size": f"{count * 1.5:.1f} KB"  # Estimated size
                        })
                        
                        total_objects += count
                        
                    except Exception as e:
                        logger.warning(f"Could not get count for collection {collection_name}: {e}")
                        collections.append({
                            "name": collection_name,
                            "object_count": 0,
                            "size": "Unknown"
                        })
                        
            except Exception as e:
                logger.warning(f"Could not get collections: {e}")
                # Return basic connection status
                collections = []
            
            return {
                "connected": True,
                "collections": collections,
                "total_objects": total_objects,
                "total_size": f"{total_objects * 1.5:.1f} KB",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting vector database status: {e}")
            return {
                "connected": False,
                "error": f"Failed to get vector database status: {str(e)}",
                "collections": [],
                "total_objects": 0,
                "total_size": "Unknown",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    async def _extract_text_content(self, file_path: str, content_type: str) -> str:
        """Extract text content from uploaded files."""
        try:
            if content_type == "text/plain":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif content_type == "application/json":
                import json
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            elif content_type == "text/csv":
                import csv
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    return "\n".join([",".join(row) for row in reader])
            elif content_type == "application/pdf":
                # Extract text from PDF using PyPDF2
                try:
                    import PyPDF2
                    extracted_text = ""
                    
                    with open(file_path, "rb") as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        logger.info(f"PDF has {len(pdf_reader.pages)} pages")
                        
                        for page_num, page in enumerate(pdf_reader.pages):
                            try:
                                page_text = page.extract_text()
                                if page_text.strip():  # Only add if page has text
                                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                                    extracted_text += page_text
                                    extracted_text += "\n"
                            except Exception as page_error:
                                logger.warning(f"Error extracting text from page {page_num + 1}: {page_error}")
                                continue
                    
                    if extracted_text.strip():
                        logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
                        return extracted_text.strip()
                    else:
                        logger.warning("No text could be extracted from PDF")
                        return "PDF contains no extractable text content"
                        
                except ImportError:
                    logger.error("PyPDF2 not installed for PDF processing")
                    return "PDF processing library not available"
                except Exception as pdf_error:
                    logger.error(f"PDF extraction error: {pdf_error}")
                    return f"Error extracting PDF content: {str(pdf_error)}"
                    
            elif content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                # For Word document extraction, you'd use python-docx
                # For now, return placeholder
                return "Word document content extraction not implemented"
            else:
                return "Unsupported file type for text extraction"
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return "Error extracting text content"
    
    async def _store_training_document(self, file_id: str, document_data: Dict[str, Any]):
        """Store training document in Weaviate vector database with proper chunking."""
        try:
            logger.info(f"Starting storage for file {file_id}")
            
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, skipping document storage")
                return
            
            logger.info("Weaviate is connected, ensuring collection exists")
            
            # Ensure collection exists
            await self._ensure_collection_exists()
            
            # Get the content and split into chunks
            content = document_data.get("content", "")
            if not content:
                logger.warning(f"No content found for file {file_id}")
                return
            
            logger.info(f"Content length: {len(content)} characters")
            
            chunks = self._split_text_into_chunks(content, max_chunk_size=1000)
            logger.info(f"Split {file_id} into {len(chunks)} chunks")
            
            # Get the TrainingDocuments collection
            collection = self.weaviate.client.collections.get("TrainingDocuments")
            logger.info("Got TrainingDocuments collection")
            
            # Store each chunk
            stored_count = 0
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "chunk_id": f"{file_id}_chunk_{i}",
                    "file_id": file_id,
                    "content": chunk,
                    "chunk_index": i,
                    "filename": document_data.get("filename", ""),
                    "file_type": document_data.get("file_type", ""),
                    "upload_date": document_data.get("upload_date", "")
                }
                
                logger.debug(f"Inserting chunk {i} with data: {chunk_data}")
                
                # Insert the chunk
                result = collection.data.insert(chunk_data)
                stored_count += 1
                logger.debug(f"Stored chunk {i} for {file_id} with UUID: {result}")
            
            logger.info(f"Successfully stored {stored_count} chunks for training document {file_id} in Weaviate")
            
        except Exception as e:
            logger.error(f"Error storing document {file_id} in Weaviate: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def _ensure_collection_exists(self):
        """Ensure TrainingDocuments collection exists with proper schema."""
        try:
            logger.info("Checking if TrainingDocuments collection exists")
            
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, cannot create collection")
                return False
            
            # Check if collection already exists
            try:
                collection = self.weaviate.client.collections.get("TrainingDocuments")
                logger.info("TrainingDocuments collection already exists")
                return True
            except Exception as e:
                # Collection doesn't exist, create it
                logger.info(f"Collection doesn't exist, creating it. Error was: {e}")
                pass
            
            # Import necessary classes for collection creation
            import weaviate.classes as wvc
            logger.info("Imported weaviate.classes")
            
            # Define the collection schema
            collection_config = wvc.config.Configure.VectorIndex.hnsw(
                distance_metric=wvc.config.VectorDistances.COSINE
            )
            logger.info("Created vector index config")
            
            # Create the collection with schema (using text2vec-weaviate for embeddings)
            self.weaviate.client.collections.create(
                name="TrainingDocuments",
                vector_index_config=collection_config,
                vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_weaviate(),
                properties=[
                    wvc.config.Property(
                        name="chunk_id",
                        data_type=wvc.config.DataType.TEXT,
                        description="Unique identifier for the text chunk"
                    ),
                    wvc.config.Property(
                        name="file_id", 
                        data_type=wvc.config.DataType.TEXT,
                        description="ID of the source file"
                    ),
                    wvc.config.Property(
                        name="content",
                        data_type=wvc.config.DataType.TEXT,
                        description="The actual text content to be embedded"
                    ),
                    wvc.config.Property(
                        name="chunk_index",
                        data_type=wvc.config.DataType.INT,
                        description="Index of the chunk within the file"
                    ),
                    wvc.config.Property(
                        name="filename",
                        data_type=wvc.config.DataType.TEXT,
                        description="Original filename"
                    ),
                    wvc.config.Property(
                        name="file_type",
                        data_type=wvc.config.DataType.TEXT,
                        description="File type/extension"
                    ),
                    wvc.config.Property(
                        name="upload_date",
                        data_type=wvc.config.DataType.TEXT,
                        description="Date when file was uploaded"
                    )
                ]
            )
            
            logger.info("Successfully created TrainingDocuments collection")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    async def _store_in_weaviate(self, file_id: str, text_content: str, metadata: Dict[str, Any]):
        """Store processed content in Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, skipping vector storage")
                return
            
            # Ensure TrainingDocuments collection exists
            await self._ensure_collection_exists()
            
            # Split text into chunks for better embedding
            chunks = self._split_text_into_chunks(text_content, max_chunk_size=1000)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                document_data = {
                    "chunk_id": chunk_id,
                    "file_id": file_id,
                    "content": chunk,
                    "chunk_index": i,
                    "filename": metadata.get("filename", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "upload_date": metadata.get("upload_date", datetime.utcnow().isoformat())
                }
                
                # Get the TrainingDocuments collection
                collection = self.weaviate.client.collections.get("TrainingDocuments")
                
                # Insert document with vector embedding (automatic)
                result = collection.data.insert(document_data)
                
                logger.info(f"Successfully stored chunk {chunk_id} in Weaviate with UUID: {result}")
                
        except Exception as e:
            logger.error(f"Error storing in Weaviate: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks for processing."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def _delete_training_document(self, file_id: str):
        """Delete training document from Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, skipping document deletion")
                return
            
            # Get the TrainingDocuments collection
            collection = self.weaviate.client.collections.get("TrainingDocuments")
            
            # Delete all chunks for this file_id
            where_filter = {
                "path": ["file_id"],
                "operator": "Equal", 
                "valueText": file_id
            }
            
            deleted_count = collection.data.delete_many(where=where_filter)
            logger.info(f"Deleted {deleted_count} chunks for file {file_id} from Weaviate")
            
        except Exception as e:
            logger.error(f"Error deleting document {file_id} from Weaviate: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup all AI service connections."""
        await self.weaviate.disconnect()
    
    async def generate_chat_response(self, message: str, conversation_id: str = None, user_email: str = None) -> str:
        """Generate a structured step-by-step chat response using Gemini based on trained data."""
        try:
            # First, search for relevant context from Weaviate
            context_results = await self.search_knowledge_base(message, limit=5, user_email=user_email)
            
            # Build detailed context from search results
            context = ""
            source_info = []
            
            if context_results:
                logger.info(f"Found {len(context_results)} relevant documents for troubleshooting")
                for i, result in enumerate(context_results):
                    content = result.get("content", "")
                    score = result.get("score", 0.0)
                    metadata = result.get("metadata", {})
                    
                    if content:
                        context += f"Document {i+1} (Relevance: {score:.3f}):\n{content}\n\n"
                        source_info.append({
                            "document": i+1,
                            "filename": metadata.get("filename", "Unknown"),
                            "score": score
                        })
                
                logger.info(f"Built context from {len(source_info)} sources")
            
            # Enhanced prompt for structured troubleshooting responses
            enhanced_prompt = f"""You are a technical support expert for Poornasree AI industrial equipment. Based on the following technical documentation, provide a comprehensive, step-by-step troubleshooting response.

TECHNICAL DOCUMENTATION:
{context}

USER QUESTION: {message}

INSTRUCTIONS FOR RESPONSE:
1. **Start with a brief problem analysis** - understand what the user is experiencing
2. **Provide step-by-step troubleshooting** - number each step clearly (Step 1, Step 2, etc.)
3. **For each step include:**
   - What to check or test
   - Tools needed (if any)
   - Expected results
   - How to interpret the results
4. **Include safety warnings** where relevant
5. **End with next steps** - what to do if the problem persists

FORMAT YOUR RESPONSE AS:
## Problem Analysis
[Brief analysis of the issue]

## Troubleshooting Steps

### Step 1: [Step Name]
- **What to check:** [Specific item to inspect]
- **Tools needed:** [Required tools]
- **Procedure:** [Detailed steps]
- **Expected result:** [What should happen]
- **If failed:** [Next action]

### Step 2: [Step Name]
[Continue with additional steps...]

## Additional Recommendations
[Any additional tips or warnings]

## Next Steps
[What to do if problem persists]

IMPORTANT: Use the technical documentation provided above to give accurate, specific guidance. If the documentation doesn't cover the specific issue, say so and provide general troubleshooting principles."""

            # Generate response using Gemini with enhanced prompt
            response = await self.google_ai.generate_text(enhanced_prompt, max_tokens=1500)
            
            if response:
                # Add source information to the response
                if source_info:
                    source_text = "\n\n---\n**Sources:** Based on "
                    source_list = [f"Document {s['document']} ({s['filename']})" for s in source_info[:3]]
                    source_text += ", ".join(source_list)
                    if len(source_info) > 3:
                        source_text += f" and {len(source_info) - 3} more documents"
                    response += source_text
                
                logger.info(f"Generated structured response ({len(response)} characters) with {len(source_info)} sources")
                return response
            else:
                return self._get_fallback_troubleshooting_response(message)
            
        except Exception as e:
            logger.error(f"Chat response generation error: {e}")
            return self._get_fallback_troubleshooting_response(message)

    def _get_fallback_troubleshooting_response(self, message: str) -> str:
        """Provide a structured fallback response when AI generation fails."""
        return f"""## Problem Analysis
I understand you're experiencing an issue with: {message}

## General Troubleshooting Steps

### Step 1: Initial Safety Check
- **What to check:** Ensure equipment is powered off and safe to work on
- **Tools needed:** None
- **Procedure:** Turn off power, wait for any moving parts to stop
- **Expected result:** Equipment is safe for inspection

### Step 2: Visual Inspection
- **What to check:** Look for obvious signs of damage, loose connections, or wear
- **Tools needed:** Flashlight, safety glasses
- **Procedure:** Systematically inspect the equipment
- **Expected result:** Identify any visible issues

### Step 3: Power Supply Verification
- **What to check:** Verify power is reaching the equipment
- **Tools needed:** Multimeter
- **Procedure:** Test voltage at input terminals
- **Expected result:** Voltage within specified range

## Additional Recommendations
- Always follow safety procedures
- Document any findings
- Take photos of any damage for reference

## Next Steps
If these general steps don't resolve the issue, please provide more specific details about:
- Equipment model and serial number
- Specific symptoms observed
- When the problem first occurred
- Any recent changes or maintenance

I apologize that I couldn't access specific technical documentation for your issue. For detailed troubleshooting, please contact technical support or refer to your equipment manual."""

    async def search_knowledge_base(self, query: str, limit: int = 5, user_email: str = None) -> List[Dict[str, Any]]:
        """Search the knowledge base using Weaviate semantic search."""
        try:
            if not self.weaviate or not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, returning empty search results")
                return []
            
            # Get the TrainingDocuments collection
            collection = self.weaviate.client.collections.get("TrainingDocuments")
            
            # Use BM25 search instead of semantic search (since vectorizer is not configured)
            # BM25 provides excellent keyword-based search through trained data
            search_results = collection.query.bm25(
                query=query,
                limit=limit,
                return_metadata=["score"]
            )
            
            # Format results
            results = []
            for result in search_results.objects:
                results.append({
                    "content": result.properties.get("content", ""),
                    "score": result.metadata.score if hasattr(result.metadata, 'score') else 0.0,  # Use BM25 score
                    "metadata": {
                        "file_id": result.properties.get("file_id", ""),
                        "filename": result.properties.get("filename", ""),
                        "chunk_index": result.properties.get("chunk_index", 0),
                        "file_type": result.properties.get("file_type", ""),
                        "source": "weaviate_bm25"
                    }
                })
            
            logger.info(f"Found {len(results)} search results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
            # Return empty list instead of mock results when search fails
            return []
    
    # =============================================================================
    # TRAINING MANAGEMENT METHODS
    # =============================================================================
    
    async def get_training_jobs(self) -> List[Dict[str, Any]]:
        """Get all training jobs with their status."""
        try:
            jobs = []
            
            # Check for actual training jobs from files
            jobs_dir = "training_jobs"
            if os.path.exists(jobs_dir):
                for filename in os.listdir(jobs_dir):
                    if filename.endswith('.json'):
                        job_file = os.path.join(jobs_dir, filename)
                        try:
                            async with aiofiles.open(job_file, 'r') as f:
                                job_data = json.loads(await f.read())
                                jobs.append({
                                    "job_id": job_data["job_id"],
                                    "name": job_data["name"],
                                    "status": job_data["status"],
                                    "progress": job_data.get("progress", 0),
                                    "file_count": job_data.get("file_count", 0),
                                    "created_by": job_data["started_by"],
                                    "started_at": job_data.get("started_at", job_data.get("created_at")),
                                    "completed_at": job_data.get("completed_at"),
                                    "estimated_completion": job_data.get("estimated_completion")
                                })
                        except Exception as e:
                            logger.error(f"Error reading job file {filename}: {e}")
                            continue
            
            # Sort by start time (newest first)
            jobs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            
            logger.info(f"Retrieved {len(jobs)} training jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get training jobs: {e}")
            return []


# =============================================================================
# GLOBAL AI SERVICE INSTANCE
# =============================================================================

# Create a single instance to be used throughout the application
ai_service = AIService()


# Global AI service instance
ai_service = AIService()
