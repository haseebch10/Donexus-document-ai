"""
In-memory storage for extraction results

This is a simple file-based storage system for the MVP.
Can be replaced with a database later.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.config import settings
from app.schemas import ExtractionResult
from app.logging_config import logger


class Storage:
    """Simple file-based storage for extraction results"""
    
    def __init__(self):
        self.data_file = settings.data_dir / "extractions.json"
        self.extractions: Dict[str, dict] = {}
        self._load()
    
    def _load(self):
        """Load extractions from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.extractions = json.load(f)
                logger.info(f"Loaded {len(self.extractions)} extractions from storage")
            except Exception as e:
                logger.error(f"Failed to load storage: {e}")
                self.extractions = {}
        else:
            self.extractions = {}
    
    def _save(self):
        """Save extractions to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.extractions, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.extractions)} extractions to storage")
        except Exception as e:
            logger.error(f"Failed to save storage: {e}")
    
    def create(self, extraction_data: dict) -> str:
        """Create a new extraction record"""
        extraction_id = str(uuid.uuid4())
        
        self.extractions[extraction_id] = {
            **extraction_data,
            "id": extraction_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._save()
        logger.info(f"Created extraction {extraction_id}")
        
        return extraction_id
    
    def get(self, extraction_id: str) -> Optional[dict]:
        """Get extraction by ID"""
        return self.extractions.get(extraction_id)
    
    def update(self, extraction_id: str, data: dict):
        """Update extraction"""
        if extraction_id in self.extractions:
            self.extractions[extraction_id].update(data)
            self.extractions[extraction_id]["updated_at"] = datetime.utcnow().isoformat()
            self._save()
            logger.info(f"Updated extraction {extraction_id}")
        else:
            logger.warning(f"Extraction {extraction_id} not found for update")
    
    def list(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[dict]:
        """List extractions with pagination"""
        results = list(self.extractions.values())
        
        # Filter by status if provided
        if status:
            results = [r for r in results if r.get("status") == status]
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Paginate
        return results[skip:skip + limit]
    
    def delete(self, extraction_id: str):
        """Delete extraction"""
        if extraction_id in self.extractions:
            del self.extractions[extraction_id]
            self._save()
            logger.info(f"Deleted extraction {extraction_id}")
        else:
            logger.warning(f"Extraction {extraction_id} not found for deletion")
    
    def count(self, status: Optional[str] = None) -> int:
        """Count extractions"""
        if status:
            return len([r for r in self.extractions.values() if r.get("status") == status])
        return len(self.extractions)


# Global storage instance
storage = Storage()
