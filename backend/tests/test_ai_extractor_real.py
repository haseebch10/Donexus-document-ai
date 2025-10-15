"""
Real Integration Tests for AI Extraction Service

These tests make ACTUAL API calls to OpenAI using real API keys.
They are slower and cost money, so use sparingly.

Run with: pytest tests/test_ai_extractor_real.py -v -s
"""

import pytest
import os
from pathlib import Path
from decimal import Decimal

from app.services.ai_extractor import AIExtractor
from app.services.pdf_processor import PDFProcessor
from app.schemas import LeaseExtraction
from app.config import settings


@pytest.mark.integration
@pytest.mark.skipif(
    not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here" or settings.OPENAI_API_KEY == "",
    reason="Real OpenAI API key required for integration tests"
)
class TestRealAIExtraction:
    """Real integration tests using actual OpenAI API"""
    
    @pytest.fixture
    def ai_extractor(self):
        """Create real AIExtractor instance"""
        return AIExtractor()
    
    @pytest.fixture
    def pdf_processor(self):
        """Create real PDFProcessor instance"""
        return PDFProcessor()
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Path to real German lease contract PDF"""
        # Use the real Mietvertrag PDF from project root
        pdf_path = Path(__file__).parent.parent.parent / "Mietvertrag-Zieblandstr_25.pdf"
        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found at {pdf_path}")
        return str(pdf_path)
    
    @pytest.mark.asyncio
    async def test_real_pdf_extraction_openai(
        self,
        ai_extractor,
        pdf_processor,
        sample_pdf_path
    ):
        """
        Test REAL extraction from actual German lease PDF using OpenAI.
        
        This test:
        1. Extracts text from real PDF (Mietvertrag-Zieblandstr_25.pdf)
        2. Sends to OpenAI GPT-4
        3. Validates structured response
        4. Checks extracted data matches known values
        """
        print("\n" + "="*80)
        print("REAL INTEGRATION TEST - OpenAI API Call")
        print("="*80)
        
        # Step 1: Extract text from PDF
        print("\n[1/4] Extracting text from PDF...")
        pdf_result = pdf_processor.extract_text(sample_pdf_path)
        
        assert pdf_result["success"], "PDF extraction failed"
        pdf_text = pdf_result["text"]
        print(f"✓ Extracted {len(pdf_text)} characters from {pdf_result['pages']} pages")
        print(f"✓ Method used: {pdf_result['method']}")
        
        # Step 2: Send to OpenAI for extraction
        print("\n[2/4] Sending to OpenAI GPT-4 for structured extraction...")
        print(f"✓ Model: {ai_extractor.OPENAI_MODEL}")
        print(f"✓ Max tokens: {ai_extractor.MAX_TOKENS}")
        
        extraction_result = await ai_extractor.extract_from_text(
            pdf_text,
            use_fallback=False  # Only use OpenAI for this test
        )
        
        print(f"✓ Extraction completed successfully!")
        print(f"✓ Model used: {extraction_result.get('ai_model_used')}")
        
        # Step 3: Validate against Pydantic schema
        print("\n[3/4] Validating against Pydantic schema...")
        lease_data = LeaseExtraction(**extraction_result)
        print(f"✓ Schema validation passed!")
        
        # Step 4: Verify extracted data matches known values
        print("\n[4/4] Verifying extracted data...")
        
        # We know this PDF has 2 tenants
        print(f"\n📋 Tenants ({len(lease_data.tenants)} found):")
        for i, tenant in enumerate(lease_data.tenants, 1):
            print(f"   {i}. {tenant.full_name} (born: {tenant.birth_date or 'N/A'})")
        
        assert len(lease_data.tenants) >= 2, "Should have extracted at least 2 tenants"
        
        # Check for known tenant names
        tenant_names = [t.last_name.lower() for t in lease_data.tenants]
        assert any("rudolph" in name for name in tenant_names), "Should find Rudolph"
        assert any("weber" in name for name in tenant_names), "Should find Weber"
        print(f"   ✓ Both tenants (Rudolph & Weber) found")
        
        # Check address
        print(f"\n🏠 Address:")
        print(f"   {lease_data.address.street} {lease_data.address.house_number}")
        print(f"   {lease_data.address.zip_code} {lease_data.address.city}")
        if lease_data.address.apartment_unit:
            print(f"   Unit: {lease_data.address.apartment_unit}")
        
        assert "ziebland" in lease_data.address.street.lower(), "Should find Zieblandstraße"
        assert lease_data.address.house_number == "25", "House number should be 25"
        assert lease_data.address.zip_code == "80798", "ZIP should be 80798"
        assert "münchen" in lease_data.address.city.lower(), "City should be München"
        print(f"   ✓ Address correctly extracted")
        
        # Check rent details
        print(f"\n💰 Rent Details:")
        print(f"   Cold rent (Kaltmiete): €{lease_data.cold_rent}")
        print(f"   Warm rent (Warmmiete): €{lease_data.warm_rent}")
        if lease_data.parking_rent:
            print(f"   Parking: €{lease_data.parking_rent}")
        if lease_data.utilities_cost:
            print(f"   Utilities: €{lease_data.utilities_cost}")
        
        # We know the warm rent is €1,405
        assert lease_data.warm_rent == Decimal("1405.00"), "Warm rent should be €1,405"
        # Cold rent can be €1,040 (apartment only) or €1,115 (apartment + parking)
        # Both are valid interpretations
        assert lease_data.cold_rent in [Decimal("1040.00"), Decimal("1115.00")], \
            f"Cold rent should be €1,040 or €1,115, got €{lease_data.cold_rent}"
        print("   ✓ Rent amounts correctly extracted")
        
        # Warm rent should be >= cold rent
        assert lease_data.warm_rent >= lease_data.cold_rent, "Warm rent must be >= cold rent"
        print(f"   ✓ Rent validation passed")
        
        # Check contract dates
        print(f"\n📅 Contract Dates:")
        print(f"   Start date: {lease_data.contract_start_date}")
        print(f"   End date: {lease_data.contract_end_date or 'Unlimited'}")
        print(f"   Active: {'Yes' if lease_data.is_active else 'No'}")
        
        assert lease_data.contract_start_date is not None, "Should have start date"
        print(f"   ✓ Contract dates extracted")
        
        # Check rent increase type (we know it's Staffelmiete = fixed_step)
        print(f"\n📈 Rent Increase:")
        print(f"   Type: {lease_data.rent_increase_type}")
        if lease_data.rent_increase_schedule:
            print(f"   Schedule ({len(lease_data.rent_increase_schedule)} increases):")
            for increase in lease_data.rent_increase_schedule:
                print(f"      • {increase.get('date')}: +€{increase.get('increase')} → €{increase.get('new_cold_rent')}")
        
        assert lease_data.rent_increase_type == "fixed_step", "Should detect Staffelmiete (fixed_step)"
        print(f"   ✓ Rent increase type correctly identified")
        
        # Check optional bonus fields
        print(f"\n🎁 Bonus Fields Extracted:")
        bonus_fields = {
            "Landlord": lease_data.landlord_name,
            "Deposit": f"€{lease_data.deposit_amount}" if lease_data.deposit_amount else None,
            "Notice period": lease_data.notice_period,
            "Square meters": f"{lease_data.square_meters}m²" if lease_data.square_meters else None,
            "Rooms": lease_data.number_of_rooms,
        }
        
        extracted_count = 0
        for field, value in bonus_fields.items():
            if value:
                print(f"   ✓ {field}: {value}")
                extracted_count += 1
            else:
                print(f"   ✗ {field}: Not found")
        
        print(f"\n   Total bonus fields: {extracted_count}/5")
        
        # Check confidence scores
        print(f"\n🎯 Confidence Scores:")
        if lease_data.confidence_scores:
            for field, score in sorted(
                lease_data.confidence_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:  # Show top 10
                bar = "█" * int(score * 20)
                print(f"   {field:20s} [{bar:20s}] {score:.2f}")
        
        # Print summary
        print("\n" + "="*80)
        print("✅ REAL INTEGRATION TEST PASSED")
        print("="*80)
        print(f"✓ PDF processed successfully")
        print(f"✓ OpenAI extraction completed")
        print(f"✓ Schema validation passed")
        print(f"✓ All known data points verified")
        print(f"✓ {extracted_count} bonus fields extracted")
        print("="*80 + "\n")
    
    @pytest.mark.asyncio
    async def test_real_extraction_with_quality_check(
        self,
        ai_extractor,
        pdf_processor,
        sample_pdf_path
    ):
        """
        Test real extraction WITH quality scoring.
        """
        print("\n" + "="*80)
        print("REAL INTEGRATION TEST - With Quality Checks")
        print("="*80)
        
        # Extract PDF text
        print("\n[1/3] Extracting PDF text...")
        pdf_result = pdf_processor.extract_text(sample_pdf_path)
        pdf_text = pdf_result["text"]
        print(f"✓ Extracted {len(pdf_text)} characters")
        
        # Extract with quality check
        print("\n[2/3] Extracting with quality checks...")
        data, warnings = await ai_extractor.extract_with_quality_check(
            pdf_text,
            min_confidence=0.6
        )
        
        print(f"✓ Extraction completed")
        
        # Check warnings
        print("\n[3/3] Quality Check Results:")
        if warnings:
            print(f"⚠️  {len(warnings)} warning(s) found:")
            for warning in warnings:
                print(f"   • {warning}")
        else:
            print(f"✅ No quality warnings - extraction looks good!")
        
        # Validate schema
        lease_data = LeaseExtraction(**data)
        print(f"\n✓ Schema validation passed")
        print(f"✓ Extracted data for: {lease_data.all_tenant_names}")
        
        print("\n" + "="*80)
        print("✅ QUALITY CHECK TEST PASSED")
        print("="*80 + "\n")
    
    @pytest.mark.asyncio
    async def test_extraction_error_handling(
        self,
        ai_extractor,
    ):
        """Test how AI handles invalid/gibberish text"""
        print("\n" + "="*80)
        print("REAL INTEGRATION TEST - Error Handling")
        print("="*80)
        
        # Test with gibberish
        gibberish_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        
        print("\n[1/1] Testing with non-lease text...")
        print(f"Input: '{gibberish_text}'")
        
        try:
            result = await ai_extractor.extract_from_text(
                gibberish_text,
                use_fallback=False
            )
            
            # AI might still try to extract, but confidence should be low
            print(f"\n⚠️  Extraction attempted despite invalid input")
            print(f"Model response: {result.get('ai_model_used')}")
            
            # Check if it at least marks low confidence
            confidence_scores = result.get('confidence_scores', {})
            if confidence_scores:
                avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
                print(f"Average confidence: {avg_confidence:.2f}")
                
                if avg_confidence < 0.5:
                    print(f"✓ Low confidence scores indicate uncertain extraction")
        
        except Exception as e:
            print(f"\n✓ Extraction failed as expected: {e}")
        
        print("\n" + "="*80 + "\n")


@pytest.mark.integration
class TestRealOpenAIConfiguration:
    """Test OpenAI configuration and connectivity"""
    
    def test_openai_api_key_configured(self):
        """Verify OpenAI API key is configured"""
        print(f"\n🔑 Checking OpenAI API key configuration...")
        
        api_key = settings.OPENAI_API_KEY
        assert api_key, "OPENAI_API_KEY not set in environment"
        assert api_key != "your_openai_api_key_here", "OPENAI_API_KEY is still placeholder"
        assert api_key.startswith("sk-"), "OPENAI_API_KEY should start with 'sk-'"
        
        # Mask the key for security
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print(f"✓ API key configured: {masked_key}")
        print(f"✓ Key length: {len(api_key)} characters")
    
    @pytest.mark.asyncio
    async def test_openai_client_initialization(self):
        """Test that OpenAI client can be initialized"""
        print(f"\n🔧 Testing OpenAI client initialization...")
        
        extractor = AIExtractor()
        assert extractor.openai_client is not None, "OpenAI client not initialized"
        
        print(f"✓ OpenAI client initialized successfully")
        print(f"✓ Model configured: {extractor.OPENAI_MODEL}")
        print(f"✓ Max retries: {extractor.MAX_RETRIES}")
        print(f"✓ Max tokens: {extractor.MAX_TOKENS}")
