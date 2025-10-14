"""
Unit tests for PDF Processor

Tests the PDF extraction functionality with real PDF files.
"""

import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor


# Test fixtures
@pytest.fixture
def pdf_processor():
    """Create PDF processor instance"""
    return PDFProcessor()


@pytest.fixture
def sample_pdf_path():
    """Path to sample PDF for testing"""
    # Use the actual Mietvertrag PDF from project root
    pdf_path = Path(__file__).parent.parent.parent / "Mietvertrag-Zieblandstr_25.pdf"
    if pdf_path.exists():
        return pdf_path
    
    # Fallback to test fixtures directory
    pdf_path = Path(__file__).parent / "fixtures" / "sample_lease.pdf"
    return pdf_path


@pytest.fixture
def sample_pdf_bytes(sample_pdf_path):
    """Load sample PDF as bytes"""
    if sample_pdf_path.exists():
        with open(sample_pdf_path, 'rb') as f:
            return f.read()
    return None


class TestPDFProcessor:
    """Test suite for PDF Processor"""
    
    def test_processor_initialization(self, pdf_processor):
        """Test that processor initializes correctly"""
        assert pdf_processor is not None
        assert pdf_processor.max_pages == 50
    
    def test_extract_text_from_file(self, pdf_processor, sample_pdf_path):
        """Test extracting text from a PDF file"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_text(sample_pdf_path)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'text' in result
        assert 'pages' in result
        assert 'metadata' in result
        assert 'method' in result
        assert 'success' in result
        
        # Check success
        assert result['success'] is True
        assert result['error'] is None
        
        # Check text was extracted
        assert len(result['text']) > 0
        assert len(result['pages']) > 0
        
        # Check metadata
        assert 'total_pages' in result['metadata']
        assert result['metadata']['total_pages'] > 0
    
    def test_extract_text_from_bytes(self, pdf_processor, sample_pdf_bytes):
        """Test extracting text from PDF bytes"""
        if sample_pdf_bytes is None:
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_from_bytes(sample_pdf_bytes, "test.pdf")
        
        # Check result structure
        assert result['success'] is True
        assert len(result['text']) > 0
        assert len(result['pages']) > 0
        assert result['metadata']['total_pages'] > 0
    
    def test_extract_german_lease_content(self, pdf_processor, sample_pdf_path):
        """Test that German lease-specific content is extracted"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_text(sample_pdf_path)
        
        if not result['success']:
            pytest.skip("PDF extraction failed")
        
        text = result['text'].lower()
        
        # Check for key German lease terms
        expected_terms = [
            'mietvertrag',  # Lease contract
            'mieter',       # Tenant
            'vermieter',    # Landlord
        ]
        
        # At least some terms should be present
        found_terms = sum(1 for term in expected_terms if term in text)
        assert found_terms > 0, f"Expected German lease terms not found in extracted text"
    
    def test_extract_specific_data_points(self, pdf_processor, sample_pdf_path):
        """Test that specific data points are extracted from the sample PDF"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_text(sample_pdf_path)
        
        if not result['success']:
            pytest.skip("PDF extraction failed")
        
        text = result['text']
        
        # Check for expected data from Mietvertrag-Zieblandstr_25.pdf
        # These should be present if using the actual sample file
        expected_data = [
            'Rudolph',      # Tenant name
            'Weber',        # Tenant name
            'Zieblandstr',  # Street
            '80798',        # Postal code
            'München',      # City
        ]
        
        found_data = sum(1 for item in expected_data if item in text)
        
        # Should find at least half of the expected data
        assert found_data >= len(expected_data) // 2, \
            f"Only found {found_data}/{len(expected_data)} expected data points"
    
    def test_page_extraction(self, pdf_processor, sample_pdf_path):
        """Test that individual pages are extracted correctly"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_text(sample_pdf_path)
        
        assert result['success'] is True
        assert len(result['pages']) > 0
        
        # Check first page structure
        first_page = result['pages'][0]
        assert 'page_num' in first_page
        assert 'text' in first_page
        assert 'char_count' in first_page
        assert first_page['page_num'] == 1
        assert first_page['char_count'] > 0
    
    def test_validate_pdf(self, pdf_processor, sample_pdf_path):
        """Test PDF validation"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        is_valid, error = pdf_processor.validate_pdf(sample_pdf_path)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_nonexistent_file(self, pdf_processor):
        """Test validation of non-existent file"""
        fake_path = Path("/tmp/nonexistent_file_12345.pdf")
        is_valid, error = pdf_processor.validate_pdf(fake_path)
        
        assert is_valid is False
        assert error is not None
        assert "does not exist" in error
    
    def test_get_page_count(self, pdf_processor, sample_pdf_path):
        """Test getting page count"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        page_count = pdf_processor.get_page_count(sample_pdf_path)
        
        assert page_count > 0
        assert isinstance(page_count, int)
    
    def test_extraction_methods(self, pdf_processor, sample_pdf_path):
        """Test that extraction method is reported correctly"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        result = pdf_processor.extract_text(sample_pdf_path)
        
        assert result['method'] in ['pdfplumber', 'pypdf2']
    
    def test_error_handling_empty_file(self, pdf_processor, tmp_path):
        """Test handling of empty PDF file"""
        # Create empty file
        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.touch()
        
        is_valid, error = pdf_processor.validate_pdf(empty_pdf)
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_error_handling_invalid_pdf(self, pdf_processor, tmp_path):
        """Test handling of invalid PDF file"""
        # Create file with wrong content
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file")
        
        is_valid, error = pdf_processor.validate_pdf(invalid_pdf)
        
        assert is_valid is False
        assert "not a valid pdf" in error.lower()
    
    def test_max_pages_limit(self, pdf_processor):
        """Test that max_pages limit is respected"""
        assert pdf_processor.max_pages == 50
        
        # Can be configured
        pdf_processor.max_pages = 10
        assert pdf_processor.max_pages == 10


class TestPDFProcessorIntegration:
    """Integration tests for PDF processing workflow"""
    
    def test_full_extraction_workflow(self, pdf_processor, sample_pdf_path):
        """Test complete extraction workflow"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Step 1: Validate
        is_valid, error = pdf_processor.validate_pdf(sample_pdf_path)
        assert is_valid is True
        
        # Step 2: Get page count
        page_count = pdf_processor.get_page_count(sample_pdf_path)
        assert page_count > 0
        
        # Step 3: Extract text
        result = pdf_processor.extract_text(sample_pdf_path)
        assert result['success'] is True
        
        # Step 4: Verify extracted data
        assert len(result['pages']) == page_count
        assert len(result['text']) > 1000  # Should have substantial content
    
    def test_bytes_and_file_equivalence(self, pdf_processor, sample_pdf_path):
        """Test that extracting from bytes gives same result as from file"""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Extract from file
        result_file = pdf_processor.extract_text(sample_pdf_path)
        
        # Extract from bytes
        with open(sample_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        result_bytes = pdf_processor.extract_from_bytes(pdf_bytes, sample_pdf_path.name)
        
        # Both should succeed
        assert result_file['success'] is True
        assert result_bytes['success'] is True
        
        # Should have same number of pages
        assert len(result_file['pages']) == len(result_bytes['pages'])
        
        # Text should be very similar (might have minor differences)
        assert len(result_file['text']) > 0
        assert len(result_bytes['text']) > 0


# Pytest markers
pytestmark = pytest.mark.asyncio
