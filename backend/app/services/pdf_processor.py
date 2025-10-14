"""
PDF Processing Service

Extracts text from PDF files using pdfplumber (primary) and PyPDF2 (fallback).
Handles errors gracefully and returns structured text data.
"""

import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Dict, List, Optional, Union
from io import BytesIO

from app.logging_config import logger


class PDFProcessor:
    """Service for extracting text from PDF files"""
    
    def __init__(self):
        self.max_pages = 50  # Safety limit
    
    def extract_text(self, file_path: Union[str, Path]) -> Dict:
        """
        Extract text from PDF with fallback strategy
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with:
                - text: Full extracted text
                - pages: List of page data
                - metadata: PDF metadata
                - method: Extraction method used
                - success: Boolean
                - error: Error message if failed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return self._error_response(f"File not found: {file_path}")
        
        # Try pdfplumber first (better for layout)
        try:
            logger.info(f"Attempting PDF extraction with pdfplumber: {file_path.name}")
            result = self._extract_with_pdfplumber(file_path)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            logger.info(f"Falling back to PyPDF2: {file_path.name}")
            result = self._extract_with_pypdf2(file_path)
            return result
        except Exception as e:
            logger.error(f"Both extraction methods failed: {e}")
            return self._error_response(f"PDF extraction failed: {e}")
    
    def extract_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Dict:
        """
        Extract text from PDF bytes (useful for upload handling)
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename for logging
            
        Returns:
            Same structure as extract_text()
        """
        # Try pdfplumber first
        try:
            logger.info(f"Attempting PDF extraction with pdfplumber: {filename}")
            result = self._extract_with_pdfplumber_bytes(pdf_bytes)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            logger.info(f"Falling back to PyPDF2: {filename}")
            result = self._extract_with_pypdf2_bytes(pdf_bytes)
            return result
        except Exception as e:
            logger.error(f"Both extraction methods failed: {e}")
            return self._error_response(f"PDF extraction failed: {e}")
    
    def _extract_with_pdfplumber(self, file_path: Path) -> Dict:
        """Extract using pdfplumber (layout-aware)"""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pdfplumber',
            'success': False,
            'error': None
        }
        
        with pdfplumber.open(file_path) as pdf:
            # Get metadata
            result['metadata'] = {
                'total_pages': len(pdf.pages),
                'pdf_metadata': pdf.metadata or {}
            }
            
            # Limit pages for safety
            pages_to_process = min(len(pdf.pages), self.max_pages)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages[:pages_to_process], 1):
                try:
                    page_text = page.extract_text() or ""
                    
                    # Get page dimensions
                    bbox = page.bbox if hasattr(page, 'bbox') else None
                    
                    # Try to extract tables (useful for structured data)
                    tables = []
                    try:
                        tables = page.extract_tables() or []
                    except:
                        pass
                    
                    page_data = {
                        'page_num': page_num,
                        'text': page_text,
                        'char_count': len(page_text),
                        'has_tables': len(tables) > 0,
                        'table_count': len(tables),
                        'bbox': bbox
                    }
                    
                    result['pages'].append(page_data)
                    result['text'] += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue
            
            result['success'] = True
            logger.info(f"Successfully extracted {len(result['pages'])} pages with pdfplumber")
            
        return result
    
    def _extract_with_pdfplumber_bytes(self, pdf_bytes: bytes) -> Dict:
        """Extract using pdfplumber from bytes"""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pdfplumber',
            'success': False,
            'error': None
        }
        
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            result['metadata'] = {
                'total_pages': len(pdf.pages),
                'pdf_metadata': pdf.metadata or {}
            }
            
            pages_to_process = min(len(pdf.pages), self.max_pages)
            
            for page_num, page in enumerate(pdf.pages[:pages_to_process], 1):
                try:
                    page_text = page.extract_text() or ""
                    
                    page_data = {
                        'page_num': page_num,
                        'text': page_text,
                        'char_count': len(page_text)
                    }
                    
                    result['pages'].append(page_data)
                    result['text'] += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue
            
            result['success'] = True
            logger.info(f"Successfully extracted {len(result['pages'])} pages with pdfplumber")
            
        return result
    
    def _extract_with_pypdf2(self, file_path: Path) -> Dict:
        """Extract using PyPDF2 (fallback)"""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pypdf2',
            'success': False,
            'error': None
        }
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Get metadata
            result['metadata'] = {
                'total_pages': len(pdf_reader.pages),
                'pdf_metadata': dict(pdf_reader.metadata) if pdf_reader.metadata else {}
            }
            
            pages_to_process = min(len(pdf_reader.pages), self.max_pages)
            
            # Extract text from each page
            for page_num in range(pages_to_process):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text() or ""
                    
                    page_data = {
                        'page_num': page_num + 1,
                        'text': page_text,
                        'char_count': len(page_text)
                    }
                    
                    result['pages'].append(page_data)
                    result['text'] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1}: {e}")
                    continue
            
            result['success'] = True
            logger.info(f"Successfully extracted {len(result['pages'])} pages with PyPDF2")
            
        return result
    
    def _extract_with_pypdf2_bytes(self, pdf_bytes: bytes) -> Dict:
        """Extract using PyPDF2 from bytes"""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pypdf2',
            'success': False,
            'error': None
        }
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        
        result['metadata'] = {
            'total_pages': len(pdf_reader.pages),
            'pdf_metadata': dict(pdf_reader.metadata) if pdf_reader.metadata else {}
        }
        
        pages_to_process = min(len(pdf_reader.pages), self.max_pages)
        
        for page_num in range(pages_to_process):
            try:
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text() or ""
                
                page_data = {
                    'page_num': page_num + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                }
                
                result['pages'].append(page_data)
                result['text'] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        result['success'] = True
        logger.info(f"Successfully extracted {len(result['pages'])} pages with PyPDF2")
        
        return result
    
    def _error_response(self, error_message: str) -> Dict:
        """Return standardized error response"""
        return {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': None,
            'success': False,
            'error': error_message
        }
    
    def validate_pdf(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate PDF file before processing
        
        Returns:
            (is_valid, error_message)
        """
        if not file_path.exists():
            return False, "File does not exist"
        
        if file_path.stat().st_size == 0:
            return False, "File is empty"
        
        if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
            return False, "File too large (max 50MB)"
        
        # Check if it's actually a PDF
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    return False, "Not a valid PDF file"
        except Exception as e:
            return False, f"Cannot read file: {e}"
        
        return True, None
    
    def get_page_count(self, file_path: Path) -> int:
        """Quickly get page count without full extraction"""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except:
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    return len(pdf_reader.pages)
            except:
                return 0


# Global instance
pdf_processor = PDFProcessor()
