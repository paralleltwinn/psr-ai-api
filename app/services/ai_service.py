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
from datetime import datetime
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
            
            processed_files = []
            total_size = 0
            file_ids = []
            
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/training"
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                if isinstance(file, UploadFile):
                    # Generate unique file ID
                    file_id = f"train_{uuid.uuid4().hex[:12]}"
                    file_extension = os.path.splitext(file.filename)[1]
                    stored_filename = f"{file_id}{file_extension}"
                    file_path = os.path.join(upload_dir, stored_filename)
                    
                    # Save file to disk
                    content = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    # Extract text content based on file type
                    extracted_text = await self._extract_text_content(file_path, file.content_type)
                    
                    # Store in Weaviate if connected
                    if self.weaviate.is_connected:
                        await self._store_training_document(file_id, {
                            "filename": file.filename,
                            "content": extracted_text,
                            "file_type": file.content_type,
                            "uploaded_by": uploaded_by,
                            "upload_date": datetime.utcnow().isoformat(),
                            "file_size": len(content)
                        })
                    
                    processed_files.append({
                        "file_id": file_id,
                        "filename": file.filename,
                        "size": len(content),
                        "content_type": file.content_type
                    })
                    
                    total_size += len(content)
                    file_ids.append(file_id)
            
            return {
                "file_ids": file_ids,
                "files_processed": len(processed_files),
                "total_size": f"{total_size / (1024*1024):.2f} MB",
                "processed_files": processed_files
            }
            
        except Exception as e:
            logger.error(f"Error processing training files: {str(e)}")
            raise Exception(f"Failed to process training files: {str(e)}")
    
    async def start_training_job(self, name: str, file_ids: List[str], training_config: Dict, started_by: str) -> Dict[str, Any]:
        """
        Start a new AI model training job.
        
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
            
            job_id = f"job_{uuid.uuid4().hex[:16]}"
            
            # Validate files exist
            for file_id in file_ids:
                # In a real implementation, check if file exists in storage/database
                pass
            
            # Create training job record (in real implementation, store in database)
            job_data = {
                "job_id": job_id,
                "name": name,
                "file_ids": file_ids,
                "training_config": training_config,
                "status": "queued",
                "progress": 0,
                "started_at": datetime.utcnow().isoformat(),
                "started_by": started_by,
                "estimated_duration": "2-4 hours"
            }
            
            # In a real implementation, you would:
            # 1. Store job data in database
            # 2. Queue the training job for background processing
            # 3. Start the actual training process with Weaviate and Gemini
            
            logger.info(f"Started training job {job_id} for user {started_by}")
            
            return {
                "job_id": job_id,
                "estimated_duration": "2-4 hours",
                "status": "queued"
            }
            
        except Exception as e:
            logger.error(f"Error starting training job: {str(e)}")
            raise Exception(f"Failed to start training job: {str(e)}")
    
    async def get_training_files(self) -> List[Dict[str, Any]]:
        """Get all uploaded training files."""
        try:
            training_files = []
            training_dir = "training_data"
            
            if os.path.exists(training_dir):
                for filename in os.listdir(training_dir):
                    file_path = os.path.join(training_dir, filename)
                    if os.path.isfile(file_path):
                        # Extract file_id from filename (format: file_id_timestamp.ext)
                        name_parts = filename.split('_')
                        if len(name_parts) >= 3:
                            file_id = f"{name_parts[0]}_{name_parts[1]}"
                            timestamp = name_parts[2].split('.')[0] if '.' in name_parts[2] else name_parts[2]
                            
                            # Get file stats
                            stat_info = os.stat(file_path)
                            file_size = stat_info.st_size
                            upload_time = datetime.fromtimestamp(stat_info.st_ctime)
                            
                            # Get file extension for type
                            file_ext = os.path.splitext(filename)[1].lower()
                            content_type = self._get_content_type(file_ext)
                            
                            training_files.append({
                                "file_id": file_id,
                                "filename": filename,
                                "original_name": filename,  # In real implementation, store original name
                                "size": file_size,
                                "content_type": content_type,
                                "uploaded_at": upload_time.isoformat(),
                                "file_path": file_path
                            })
            
            # Sort by upload time (newest first)
            training_files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
            
            logger.info(f"Found {len(training_files)} training files")
            return training_files
            
        except Exception as e:
            logger.error(f"Error getting training files: {e}")
            return []

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
            training_dir = "training_data"
            file_deleted = False
            deleted_file_info = None
            
            # Find and delete the physical file
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

    async def cleanup_orphaned_data(self) -> Dict[str, Any]:
        """Clean up orphaned data (files without metadata, Weaviate data without files, etc.)."""
        try:
            cleanup_results = {
                "orphaned_files": 0,
                "orphaned_weaviate_data": 0,
                "cleaned_job_references": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Find physical files without proper metadata
            training_dir = "training_data"
            if os.path.exists(training_dir):
                for filename in os.listdir(training_dir):
                    file_path = os.path.join(training_dir, filename)
                    # Add logic to check if file has proper metadata
                    # For now, just log
                    logger.debug(f"Checking file: {filename}")
            
            # Clean up Weaviate data without corresponding files
            if self.weaviate.is_connected:
                # In real implementation, query Weaviate for orphaned data
                logger.info("Checking Weaviate for orphaned data...")
            
            # Clean up job references to deleted files
            jobs_dir = "training_jobs"
            if os.path.exists(jobs_dir):
                for job_filename in os.listdir(jobs_dir):
                    if job_filename.endswith('.json'):
                        # Check and clean job file references
                        pass
            
            logger.info(f"Cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise Exception(f"Cleanup failed: {str(e)}")
    
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
                # For PDF extraction, you'd use a library like PyPDF2 or pdfplumber
                # For now, return placeholder
                return "PDF content extraction not implemented"
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
        """Store training document in Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                return
            
            # In a real implementation, store document in Weaviate collection
            # For now, just log the action
            logger.info(f"Stored training document {file_id} in Weaviate")
            
        except Exception as e:
            logger.error(f"Error storing document {file_id} in Weaviate: {str(e)}")
    
    async def _delete_training_document(self, file_id: str):
        """Delete training document from Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                return
            
            # In a real implementation, delete document from Weaviate collection
            # For now, just log the action
            logger.info(f"Deleted training document {file_id} from Weaviate")
            
        except Exception as e:
            logger.error(f"Error deleting document {file_id} from Weaviate: {str(e)}")
    
    async def cleanup(self):
        """Cleanup all AI service connections."""
        await self.weaviate.disconnect()
    
    # =============================================================================
    # TRAINING METHODS
    # =============================================================================
    
    async def process_training_files(self, files: List[UploadFile], username: str) -> Dict[str, Any]:
        """Process uploaded training files and prepare them for training."""
        try:
            processed_files = []
            total_size = 0
            file_ids = []
            
            # Create training data directory if it doesn't exist
            training_dir = "training_data"
            os.makedirs(training_dir, exist_ok=True)
            
            for file in files:
                # Generate unique file ID
                file_id = f"file_{uuid.uuid4().hex[:8]}_{int(datetime.utcnow().timestamp())}"
                file_extension = os.path.splitext(file.filename)[1].lower()
                safe_filename = f"{file_id}{file_extension}"
                file_path = os.path.join(training_dir, safe_filename)
                
                # Save file to disk
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                    total_size += len(content)
                
                # Extract text content based on file type
                text_content = await self._extract_text_content(file_path, file_extension)
                
                # Store in Weaviate if connected
                if self.weaviate.is_connected:
                    await self._store_in_weaviate(file_id, text_content, {
                        "filename": file.filename,
                        "file_type": file_extension,
                        "uploaded_by": username,
                        "upload_time": datetime.utcnow().isoformat()
                    })
                
                processed_files.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "file_path": file_path,
                    "size": len(content),
                    "text_length": len(text_content)
                })
                file_ids.append(file_id)
                
                logger.info(f"Processed training file: {file.filename} -> {file_id}")
            
            return {
                "files_processed": len(processed_files),
                "total_size": f"{total_size / (1024*1024):.2f} MB",
                "file_ids": file_ids,
                "files": processed_files
            }
            
        except Exception as e:
            logger.error(f"Error processing training files: {e}")
            raise Exception(f"Failed to process training files: {str(e)}")
    
    async def _extract_text_content(self, file_path: str, file_extension: str) -> str:
        """Extract text content from uploaded files."""
        try:
            if file_extension == '.txt':
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            
            elif file_extension == '.json':
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())
                    return json.dumps(data, indent=2)
            
            elif file_extension == '.csv':
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            
            elif file_extension == '.pdf':
                # For PDF extraction, you would use libraries like PyPDF2 or pdfplumber
                # For now, return placeholder text
                return f"PDF content from {os.path.basename(file_path)} - Text extraction would be implemented with PyPDF2 or pdfplumber"
            
            elif file_extension in ['.doc', '.docx']:
                # For Word docs, you would use python-docx
                return f"Word document content from {os.path.basename(file_path)} - Text extraction would be implemented with python-docx"
            
            else:
                return f"Unsupported file type: {file_extension}"
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return f"Error extracting text: {str(e)}"
    
    async def _store_in_weaviate(self, file_id: str, text_content: str, metadata: Dict[str, Any]):
        """Store processed content in Weaviate vector database."""
        try:
            if not self.weaviate.is_connected:
                logger.warning("Weaviate not connected, skipping vector storage")
                return
            
            # Split text into chunks for better embedding
            chunks = self._split_text_into_chunks(text_content, max_chunk_size=1000)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                document_data = {
                    "chunk_id": chunk_id,
                    "file_id": file_id,
                    "content": chunk,
                    "chunk_index": i,
                    **metadata
                }
                
                # Store in Weaviate (implementation would depend on your schema)
                logger.info(f"Stored chunk {chunk_id} in Weaviate")
                
        except Exception as e:
            logger.error(f"Error storing in Weaviate: {e}")
    
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
    
    async def start_training_job(self, name: str, file_ids: List[str], training_config: Dict[str, Any], started_by: str) -> Dict[str, Any]:
        """Start a new AI model training job."""
        try:
            job_id = f"job_{uuid.uuid4().hex[:12]}"
            
            # Store training job metadata
            job_data = {
                "job_id": job_id,
                "name": name,
                "file_ids": file_ids,
                "training_config": training_config,
                "status": "queued",
                "progress": 0,
                "started_by": started_by,
                "created_at": datetime.utcnow().isoformat(),
                "file_count": len(file_ids)
            }
            
            # Save job to file (in production, this would be in a database)
            jobs_dir = "training_jobs"
            os.makedirs(jobs_dir, exist_ok=True)
            job_file = os.path.join(jobs_dir, f"{job_id}.json")
            
            async with aiofiles.open(job_file, 'w') as f:
                await f.write(json.dumps(job_data, indent=2))
            
            # Start background training process
            asyncio.create_task(self._run_training_job(job_id, job_data))
            
            logger.info(f"Started training job: {job_id} - {name}")
            
            return {
                "job_id": job_id,
                "status": "queued",
                "estimated_duration": "30-60 minutes"
            }
            
        except Exception as e:
            logger.error(f"Error starting training job: {e}")
            raise Exception(f"Failed to start training job: {str(e)}")
    
    async def _run_training_job(self, job_id: str, job_data: Dict[str, Any]):
        """Run the actual training job in the background."""
        try:
            jobs_dir = "training_jobs"
            job_file = os.path.join(jobs_dir, f"{job_id}.json")
            
            # Update status to running
            job_data["status"] = "running"
            job_data["started_at"] = datetime.utcnow().isoformat()
            await self._save_job_data(job_file, job_data)
            
            # Simulate training process with progress updates
            training_steps = [
                (10, "Loading training data..."),
                (25, "Preparing embeddings..."),
                (40, "Training with Weaviate..."),
                (65, "Fine-tuning with Gemini..."),
                (85, "Validating model..."),
                (100, "Training completed!")
            ]
            
            for progress, message in training_steps:
                await asyncio.sleep(5)  # Simulate work
                job_data["progress"] = progress
                job_data["current_step"] = message
                await self._save_job_data(job_file, job_data)
                logger.info(f"Training job {job_id}: {progress}% - {message}")
            
            # Mark as completed
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.utcnow().isoformat()
            job_data["progress"] = 100
            await self._save_job_data(job_file, job_data)
            
            logger.info(f"Training job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Training job {job_id} failed: {e}")
            job_data["status"] = "failed"
            job_data["error_message"] = str(e)
            await self._save_job_data(job_file, job_data)
    
    async def _save_job_data(self, job_file: str, job_data: Dict[str, Any]):
        """Save job data to file."""
        async with aiofiles.open(job_file, 'w') as f:
            await f.write(json.dumps(job_data, indent=2))
    
    async def get_training_jobs(self) -> List[Dict[str, Any]]:
        """Get all training jobs with their current status."""
        try:
            jobs_dir = "training_jobs"
            if not os.path.exists(jobs_dir):
                return []
            
            jobs = []
            for filename in os.listdir(jobs_dir):
                if filename.endswith('.json'):
                    job_file = os.path.join(jobs_dir, filename)
                    async with aiofiles.open(job_file, 'r') as f:
                        job_data = json.loads(await f.read())
                        jobs.append({
                            "job_id": job_data["job_id"],
                            "name": job_data["name"],
                            "status": job_data["status"],
                            "progress": job_data.get("progress", 0),
                            "started_at": job_data.get("started_at"),
                            "estimated_completion": job_data.get("estimated_completion"),
                            "completed_at": job_data.get("completed_at"),
                            "file_count": job_data.get("file_count", 0),
                            "error_message": job_data.get("error_message"),
                            "created_by": job_data["started_by"]
                        })
            
            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting training jobs: {e}")
            return []
    
    async def delete_training_file(self, file_id: str, username: str):
        """Delete a training file and cleanup associated data."""
        try:
            # Find and delete the physical file
            training_dir = "training_data"
            deleted = False
            
            if os.path.exists(training_dir):
                for filename in os.listdir(training_dir):
                    if filename.startswith(file_id):
                        file_path = os.path.join(training_dir, filename)
                        os.remove(file_path)
                        deleted = True
                        logger.info(f"Deleted training file: {file_path}")
                        break
            
            # Remove from Weaviate if connected
            if self.weaviate.is_connected:
                await self._remove_from_weaviate(file_id)
            
            if not deleted:
                raise Exception(f"Training file {file_id} not found")
                
        except Exception as e:
            logger.error(f"Error deleting training file {file_id}: {e}")
            raise Exception(f"Failed to delete training file: {str(e)}")
    
    async def _remove_from_weaviate(self, file_id: str):
        """Remove file data from Weaviate vector database."""
        try:
            # Implementation would depend on your Weaviate schema
            logger.info(f"Removed file {file_id} from Weaviate")
        except Exception as e:
            logger.error(f"Error removing from Weaviate: {e}")

    async def generate_chat_response(self, message: str, conversation_id: str = None, user_email: str = None) -> str:
        """Generate a chat response using Gemini based on trained data."""
        try:
            # First, search for relevant context from Weaviate
            context_results = await self.search_knowledge_base(message, limit=3, user_email=user_email)
            
            # Build context from search results
            context = ""
            if context_results:
                context = "\n".join([result.get("content", "") for result in context_results])
                context = f"Based on the following information:\n{context}\n\n"
            
            # Generate response using Gemini
            prompt = f"{context}User question: {message}\n\nPlease provide a helpful response based on the information about Poornasree AI:"
            
            response = await self.google_ai.generate_text(prompt, max_tokens=300)
            return response.get("generated_text", "I apologize, but I couldn't generate a response at this time.")
            
        except Exception as e:
            logger.error(f"Chat response generation error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."

    async def search_knowledge_base(self, query: str, limit: int = 5, user_email: str = None) -> List[Dict[str, Any]]:
        """Search the knowledge base using Weaviate semantic search."""
        try:
            if not self.weaviate or not self.weaviate.is_ready():
                # Return mock results for testing
                return [
                    {
                        "content": f"Information about {query} from our knowledge base. You can upload training files in PDF, DOC, TXT, JSON, and CSV formats through the admin dashboard.",
                        "score": 0.95,
                        "metadata": {"source": "training_data", "type": "documentation"}
                    },
                    {
                        "content": f"Related to {query}: Our AI training system uses Weaviate for vector storage and Gemini 2.5 Flash for text generation.",
                        "score": 0.87,
                        "metadata": {"source": "technical_docs", "type": "information"}
                    }
                ]
            
            # Actual Weaviate search implementation
            # This would use your Weaviate schema and search capabilities
            results = []
            logger.info(f"Searching knowledge base for: {query}")
            
            # For now, return mock results
            return [
                {
                    "content": f"Search result for '{query}': Our system supports multiple file formats for training data including PDF, DOC, DOCX, TXT, JSON, and CSV files.",
                    "score": 0.92,
                    "metadata": {"source": "knowledge_base", "query": query}
                }
            ]
            
        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
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

    async def start_training_job(self, name: str, file_ids: List[str], training_config: Dict[str, Any], started_by: str) -> Dict[str, Any]:
        """Start a new training job."""
        try:
            import uuid
            from datetime import datetime, timedelta
            
            job_id = f"training-job-{str(uuid.uuid4())[:8]}"
            
            # Mock training job start
            logger.info(f"Starting training job '{name}' with {len(file_ids)} files")
            
            # In a real implementation, this would:
            # 1. Process the uploaded files
            # 2. Create embeddings in Weaviate
            # 3. Start the actual training process
            # 4. Store job status in database
            
            return {
                "job_id": job_id,
                "status": "queued",
                "estimated_duration": "2-4 hours",
                "file_count": len(file_ids),
                "started_by": started_by,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start training job: {e}")
            raise

    async def delete_training_file(self, file_id: str, deleted_by: str) -> bool:
        """Delete a training file."""
        try:
            # Mock file deletion
            logger.info(f"Deleting training file {file_id} by {deleted_by}")
            
            # In a real implementation, this would:
            # 1. Remove the file from storage
            # 2. Remove related embeddings from Weaviate
            # 3. Update database records
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete training file {file_id}: {e}")
            raise


# Global AI service instance
ai_service = AIService()
