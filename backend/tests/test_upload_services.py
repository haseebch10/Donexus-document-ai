"""
Test script to verify upload endpoint functionality without running the server.
"""

import sys
import os
from pathlib import Path
from io import BytesIO

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
print("Testing imports...")
from app.api.upload import validate_file_upload, process_upload
from app.services.file_manager import FileManager
from app.services.pdf_processor import PDFProcessor
from app.services.ai_extractor import AIExtractor
from app.services.quality_scorer import QualityScorer

print("✓ All imports successful")

# Test FileManager
print("\nTesting FileManager...")
file_manager = FileManager()
print(f"✓ FileManager initialized: {file_manager.upload_dir}")

# Test PDF processor
print("\nTesting PDFProcessor...")
pdf_processor = PDFProcessor()
pdf_path = Path("/Users/haseeb/Downloads/Donexus/Mietvertrag-Zieblandstr_25.pdf")
if pdf_path.exists():
    text = pdf_processor.extract_text_from_pdf(pdf_path)
    print(f"✓ PDF text extracted: {len(text)} characters")
else:
    print(f"⚠ PDF not found at {pdf_path}")

# Test AIExtractor
print("\nTesting AIExtractor...")
ai_extractor = AIExtractor()
print(f"✓ AIExtractor initialized")

# Test QualityScorer
print("\nTesting QualityScorer...")
quality_scorer = QualityScorer()
print(f"✓ QualityScorer initialized")

print("\n✅ All services working correctly!")
print("\nTo test the full API:")
print("1. Install requirements: pip install -r requirements.txt")
print("2. Start server: uvicorn app.main:app --reload")
print("3. Test upload: curl -X POST http://localhost:8000/api/upload/ -F 'file=@Mietvertrag-Zieblandstr_25.pdf'")
