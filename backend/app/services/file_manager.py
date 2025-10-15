"""
File Manager Service for handling file uploads and storage.

This module provides utilities for saving uploaded files with proper
organization, naming conventions, and storage management.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Union, BinaryIO
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class FileManager:
    """
    Service for managing file uploads and storage.
    
    Implements singleton pattern for consistent file management across the application.
    Handles file storage with UUID-based naming and date-based organization.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize file manager"""
        if self._initialized:
            return
            
        self.upload_dir = Path(settings.upload_dir)
        self._ensure_upload_directory()
        self._initialized = True
        
        logger.info(f"FileManager initialized with upload directory: {self.upload_dir}")
    
    def _ensure_upload_directory(self) -> None:
        """Ensure upload directory exists"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Upload directory verified: {self.upload_dir}")
    
    def _get_date_directory(self) -> Path:
        """
        Get or create date-based subdirectory for uploads.
        
        Organizes uploads by date in format: YYYY-MM-DD
        
        Returns:
            Path to today's upload directory
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.upload_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        return date_dir
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename while preserving the original extension.
        
        Args:
            original_filename: Original filename from upload
            
        Returns:
            Unique filename in format: uuid_originalname.ext
        """
        file_path = Path(original_filename)
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
        
        # Sanitize original filename (remove special characters)
        safe_name = "".join(c for c in file_path.stem if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.replace(' ', '_')
        
        return f"{unique_id}_{safe_name}{file_path.suffix}"
    
    def save_uploaded_file(
        self,
        file_content: BinaryIO,
        filename: str
    ) -> Path:
        """
        Save an uploaded file to storage with proper organization.
        
        Args:
            file_content: File content as binary stream
            filename: Original filename
            
        Returns:
            Path to saved file
            
        Raises:
            IOError: If file save fails
        """
        try:
            # Get date-based directory
            date_dir = self._get_date_directory()
            
            # Generate unique filename
            unique_filename = self._generate_unique_filename(filename)
            file_path = date_dir / unique_filename
            
            logger.info(f"Saving file: {filename} as {unique_filename}")
            
            # Save file
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file_content, f)
            
            # Verify file was saved
            if not file_path.exists():
                raise IOError(f"File save verification failed: {file_path}")
            
            file_size = file_path.stat().st_size
            logger.info(f"File saved successfully: {file_path} ({file_size} bytes)")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}", exc_info=True)
            raise IOError(f"Failed to save file: {e}")
    
    def get_file_path(self, filename: str, date: Union[str, None] = None) -> Union[Path, None]:
        """
        Get path to a previously uploaded file.
        
        Args:
            filename: Filename to search for
            date: Optional date string (YYYY-MM-DD) to narrow search
            
        Returns:
            Path to file if found, None otherwise
        """
        if date:
            # Search in specific date directory
            date_dir = self.upload_dir / date
            file_path = date_dir / filename
            return file_path if file_path.exists() else None
        
        # Search in all date directories
        for date_dir in self.upload_dir.iterdir():
            if date_dir.is_dir():
                file_path = date_dir / filename
                if file_path.exists():
                    return file_path
        
        return None
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if file was deleted, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return False
            
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
            return False
    
    def list_files(self, date: Union[str, None] = None) -> list[Path]:
        """
        List files in storage.
        
        Args:
            date: Optional date string (YYYY-MM-DD) to filter by
            
        Returns:
            List of file paths
        """
        files = []
        
        if date:
            # List files in specific date directory
            date_dir = self.upload_dir / date
            if date_dir.exists():
                files = [f for f in date_dir.iterdir() if f.is_file()]
        else:
            # List all files in all date directories
            for date_dir in self.upload_dir.iterdir():
                if date_dir.is_dir():
                    files.extend([f for f in date_dir.iterdir() if f.is_file()])
        
        return sorted(files)
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage metrics
        """
        total_files = 0
        total_size = 0
        
        for file_path in self.list_files():
            total_files += 1
            total_size += file_path.stat().st_size
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "upload_directory": str(self.upload_dir)
        }
