"""
Upload API endpoint for document processing.

This module provides the main API endpoint for uploading lease documents,
processing them through the AI extraction pipeline, and storing results.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from decimal import Decimal

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.services.file_manager import FileManager
from app.services.pdf_processor import PDFProcessor
from app.services.ai_extractor import AIExtractor
from app.services.quality_scorer import QualityScorer
from app.schemas import LeaseExtraction, QualityMetrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Initialize services as singletons
file_manager = FileManager()
pdf_processor = PDFProcessor()
ai_extractor = AIExtractor()
quality_scorer = QualityScorer()


class UploadResponse(BaseModel):
    """Response model for successful upload"""
    
    success: bool = Field(..., description="Whether the upload was successful")
    extraction_id: str = Field(..., description="Unique ID for this extraction")
    file_path: str = Field(..., description="Path where file was saved")
    extraction: LeaseExtraction = Field(..., description="Extracted lease data")
    quality_metrics: QualityMetrics = Field(..., description="Quality assessment metrics")
    processing_time_seconds: float = Field(..., description="Total processing time")
    
    class Config:
        json_encoders = {
            Decimal: str  # Convert Decimal to string for JSON serialization
        }


class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    success: bool = False
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file meets requirements.
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )
    
    # Sanitize filename to prevent path traversal
    if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Filename cannot contain path separators or '..'."
        )
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Check content type
    if file.content_type and "pdf" not in file.content_type.lower():
        logger.warning(f"Unexpected content type: {file.content_type} for file: {file.filename}")
    
    logger.info(f"File validation passed: {file.filename}")


async def process_upload(
    file: UploadFile,
    file_path: Path,
    extraction_id: str
) -> Dict[str, Any]:
    """
    Process uploaded file through the extraction pipeline.
    
    This is the main processing function that orchestrates:
    1. PDF text extraction
    2. AI-powered data extraction
    3. Quality assessment
    
    Args:
        file: Uploaded file object
        file_path: Path where file was saved
        extraction_id: Unique extraction ID
        
    Returns:
        Dictionary with extraction results and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Extract text from PDF
        logger.info(f"[{extraction_id}] Extracting text from PDF")
        pdf_result = pdf_processor.extract_text(file_path)
        pdf_text = pdf_result.get("text", "")
        
        if not pdf_text or len(pdf_text.strip()) < 100:
            raise HTTPException(
                status_code=422,
                detail="PDF appears to be empty or unreadable. Ensure the PDF contains text (not scanned images)."
            )
        
        logger.info(f"[{extraction_id}] Extracted {len(pdf_text)} characters from PDF")
        
        # Step 2: AI extraction
        logger.info(f"[{extraction_id}] Starting AI extraction")
        extraction_dict = await ai_extractor.extract(pdf_text)
        
        # Add metadata to the dictionary
        extraction_dict['extraction_timestamp'] = datetime.now().isoformat()
        
        # Convert to LeaseExtraction model
        extraction = LeaseExtraction(**extraction_dict)
        
        logger.info(f"[{extraction_id}] AI extraction completed using {extraction.ai_model_used}")
        
        # Step 3: Quality assessment
        logger.info(f"[{extraction_id}] Assessing extraction quality")
        quality_metrics = quality_scorer.assess_quality(extraction)
        
        logger.info(
            f"[{extraction_id}] Quality assessment complete: "
            f"{quality_metrics.quality_tier} (score: {quality_metrics.overall_score:.1f})"
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "extraction_id": extraction_id,
            "file_path": str(file_path),
            "extraction": extraction,
            "quality_metrics": quality_metrics,
            "processing_time_seconds": processing_time
        }
        
    except ValidationError as e:
        logger.error(f"[{extraction_id}] Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation failed",
                "error_type": "ValidationError",
                "details": e.errors()
            }
        )
    except Exception as e:
        logger.error(f"[{extraction_id}] Processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_type": type(e).__name__,
                "details": {"extraction_id": extraction_id}
            }
        )


@router.post(
    "/",
    response_model=UploadResponse,
    responses={
        200: {"description": "File successfully processed"},
        400: {"description": "Invalid file upload", "model": ErrorResponse},
        422: {"description": "Processing error", "model": ErrorResponse},
        500: {"description": "Server error", "model": ErrorResponse}
    },
    summary="Upload and process lease document",
    description="""
    Upload a PDF lease document for AI-powered extraction and analysis.
    
    The endpoint will:
    1. Validate the uploaded file
    2. Extract text from the PDF
    3. Use AI (OpenAI GPT-4) to extract structured data
    4. Assess the quality of extraction
    5. Return structured lease data with quality metrics
    
    **Supported formats:** PDF only
    
    **Processing time:** 15-30 seconds depending on document size and AI response time
    """
)
async def upload_lease_document(
    request: Request,
    file: UploadFile = File(
        ...,
        description="PDF file containing the lease contract"
    )
) -> UploadResponse:
    """
    Upload and process a lease document.
    
    Args:
        request: FastAPI request object (for request ID)
        file: Uploaded PDF file
        
    Returns:
        UploadResponse with extraction results and quality metrics
        
    Raises:
        HTTPException: If upload or processing fails
    """
    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(f"[{request_id}] Upload request received: {file.filename}")
    
    try:
        # Validate file
        validate_file_upload(file)
        
        # Save uploaded file
        logger.info(f"[{request_id}] Saving uploaded file")
        try:
            file_path = file_manager.save_uploaded_file(
                file.file,
                file.filename
            )
        except ValueError as e:
            # File size exceeded
            raise HTTPException(
                status_code=413,
                detail=str(e)
            )
        
        logger.info(f"[{request_id}] File saved to: {file_path}")
        
        # Process file through extraction pipeline
        result = await process_upload(
            file=file,
            file_path=file_path,
            extraction_id=request_id
        )
        
        # Build response
        response = UploadResponse(
            success=True,
            extraction_id=result["extraction_id"],
            file_path=result["file_path"],
            extraction=result["extraction"],
            quality_metrics=result["quality_metrics"],
            processing_time_seconds=result["processing_time_seconds"]
        )
        
        logger.info(
            f"[{request_id}] Upload processing complete in {result['processing_time_seconds']:.2f}s"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An unexpected error occurred",
                "error_type": type(e).__name__,
                "details": {"request_id": request_id}
            }
        )


@router.post(
    "/batch",
    response_model=Dict[str, Any],
    summary="Upload multiple PDF documents",
    description="Upload and process up to 3 PDF documents simultaneously"
)
async def upload_multiple_documents(
    request: Request,
    files: list[UploadFile] = File(..., description="PDF files to process (max 3)")
) -> Dict[str, Any]:
    """
    Upload and process multiple PDF documents.
    
    This endpoint accepts up to 3 PDF files and processes them through
    the extraction pipeline, returning results for each file.
    
    Args:
        request: FastAPI request object
        files: List of uploaded PDF files (max 3)
        
    Returns:
        Dictionary containing results for each file
        
    Raises:
        HTTPException: If validation or processing fails
    """
    request_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Validate number of files
    max_files = 3
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {max_files} files allowed per request. Got {len(files)}."
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    logger.info(f"[{request_id}] ━━━ Processing batch upload: {len(files)} files ━━━")
    for idx, f in enumerate(files):
        logger.info(f"[{request_id}] File {idx + 1}: {f.filename} ({f.size / 1024:.2f} KB)")
    
    results = []
    errors = []
    
    # Process each file
    for idx, file in enumerate(files):
        try:
            logger.info(f"[{request_id}] ━━━ Processing file {idx + 1}/{len(files)}: {file.filename} ━━━")
            
            # Validate file
            validate_file_upload(file)
            logger.info(f"[{request_id}] ✓ Validation passed for {file.filename}")
            
            # Generate unique extraction ID
            extraction_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}"
            
            # Save file
            try:
                file_path = file_manager.save_uploaded_file(
                    file.file,
                    file.filename
                )
            except ValueError as ve:
                # File size exceeded - treat as error
                raise HTTPException(status_code=413, detail=str(ve))
            
            logger.info(f"[{extraction_id}] ✓ File saved to: {file_path}")
            
            # Process the file
            logger.info(f"[{extraction_id}] Starting PDF processing pipeline...")
            result = await process_upload(file, file_path, extraction_id)
            result["success"] = True
            result["file_index"] = idx
            result["original_filename"] = file.filename
            
            results.append(result)
            logger.info(f"[{extraction_id}] ✓ Successfully processed file {idx + 1}/{len(files)}: {file.filename}")
            
        except HTTPException as e:
            error_result = {
                "success": False,
                "file_index": idx,
                "original_filename": file.filename,
                "error": e.detail,
                "error_type": "HTTPException",
                "status_code": e.status_code
            }
            errors.append(error_result)
            logger.error(f"[{request_id}] ✗ Failed to process file {idx + 1}/{len(files)} ({file.filename}): {e.detail}")
            
        except Exception as e:
            error_result = {
                "success": False,
                "file_index": idx,
                "original_filename": file.filename,
                "error": str(e),
                "error_type": type(e).__name__
            }
            errors.append(error_result)
            logger.error(f"[{request_id}] ✗ Unexpected error processing file {idx + 1}/{len(files)} ({file.filename}): {e}", exc_info=True)
    
    # Return combined results
    logger.info(
        f"[{request_id}] ━━━ Batch upload complete ━━━\n"
        f"  Total: {len(files)} | Success: {len(results)} | Failed: {len(errors)}"
    )
    
    return {
        "request_id": request_id,
        "total_files": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors if errors else None
    }


@router.get(
    "/health",
    summary="Check upload service health",
    description="Verify that all upload pipeline services are initialized and ready"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for upload service.
    
    Returns:
        Dictionary with service status information
    """
    return {
        "status": "healthy",
        "services": {
            "file_manager": "initialized",
            "pdf_processor": "initialized",
            "ai_extractor": "initialized",
            "quality_scorer": "initialized"
        },
        "timestamp": datetime.now().isoformat()
    }
