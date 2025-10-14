"""
File management utilities for handling uploaded PDFs
"""

import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, BinaryIO

from app.config import settings
from app.logging_config import logger


class FileManager:
    """Manages file uploads and storage"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
        
    def save_uploaded_file(
        self, 
        file_content: bytes | BinaryIO, 
        original_filename: str
    ) -> tuple[str, Path]:
        """
        Save uploaded file to organized directory structure
        
        Args:
            file_content: File bytes or file object
            original_filename: Original filename from upload
            
        Returns:
            (file_id, file_path): UUID and full path to saved file
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create date-based subdirectory (YYYY-MM-DD)
        date_dir = self.upload_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean filename and prepend UUID
        clean_filename = self._sanitize_filename(original_filename)
        final_filename = f"{file_id}_{clean_filename}"
        file_path = date_dir / final_filename
        
        # Save file
        if isinstance(file_content, bytes):
            with open(file_path, 'wb') as f:
                f.write(file_content)
        else:
            # It's a file object
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_content, f)
        
        logger.info(f"Saved file: {final_filename} ({self._format_size(file_path.stat().st_size)})")
        
        return file_id, file_path
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file before processing
        
        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            return False, "Only PDF files are allowed"
        
        # Check file size
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / 1024 / 1024
            return False, f"File too large (max {max_mb:.0f}MB)"
        
        return True, None
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        Find file by ID (searches all date directories)
        
        Args:
            file_id: UUID of the file
            
        Returns:
            Path to file or None if not found
        """
        # Search in all subdirectories
        for date_dir in self.upload_dir.iterdir():
            if date_dir.is_dir():
                for file_path in date_dir.glob(f"{file_id}_*"):
                    return file_path
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file by ID
        
        Returns:
            True if deleted, False if not found
        """
        file_path = self.get_file_path(file_id)
        if file_path and file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path.name}")
            return True
        
        logger.warning(f"File not found for deletion: {file_id}")
        return False
    
    def cleanup_old_files(self, days_old: int = 30):
        """
        Delete files older than specified days
        
        Args:
            days_old: Delete files older than this many days
        """
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for date_dir in self.upload_dir.iterdir():
            if date_dir.is_dir():
                for file_path in date_dir.glob("*.pdf"):
                    if file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} files older than {days_old} days")
        return deleted_count
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and special characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Get just the filename (remove any path)
        filename = Path(filename).name
        
        # Remove or replace problematic characters
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\x00']
        for char in forbidden_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1)
            filename = name[:95] + '.' + ext
        
        return filename
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_storage_stats(self) -> dict:
        """Get statistics about stored files"""
        total_files = 0
        total_size = 0
        
        for date_dir in self.upload_dir.iterdir():
            if date_dir.is_dir():
                files = list(date_dir.glob("*.pdf"))
                total_files += len(files)
                total_size += sum(f.stat().st_size for f in files)
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_formatted': self._format_size(total_size),
            'upload_directory': str(self.upload_dir)
        }


# Global instance
file_manager = FileManager()
