"""
AI-Powered Lease Extraction Service

Production-grade service for extracting structured lease data from German contracts
using OpenAI GPT-4. Implements retry logic, structured output,
and comprehensive error handling.
"""

import json
from typing import Dict
from datetime import datetime
import asyncio

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from app.config import settings
from app.schemas import LeaseExtraction
from app.logging_config import logger


class ExtractionError(Exception):
    """Custom exception for extraction failures"""
    pass


class AIExtractor:
    """
    AI-powered extraction service with retry logic.
    
    Architecture:
    - OpenAI GPT-4 with JSON mode
    - Retry strategy: 3 attempts with exponential backoff
    - Structured output validation using Pydantic
    """
    
    # Model configuration
    OPENAI_MODEL = "gpt-4-turbo-preview"
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1  # seconds
    
    # Token limits
    MAX_TOKENS = 4000
    
    def __init__(self):
        """Initialize AI client"""
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._extraction_prompt = self._build_extraction_prompt()
    
    def _build_extraction_prompt(self) -> str:
        """
        Build comprehensive extraction prompt with clear instructions.
        
        Returns:
            Formatted system prompt for extraction
        """
        return """You are an expert AI assistant specialized in extracting structured data from German lease agreements (Mietverträge).

Your task is to extract the following information from the provided lease document text:

**REQUIRED FIELDS (must always be extracted):**
1. Tenant Information: All tenant names (first_name, last_name), birth dates if available
2. Property Address: street, house_number, zip_code, city, apartment_unit (e.g., "3.OG links")
3. Rent Details: warm_rent (Warmmiete), cold_rent (Kaltmiete)
4. Contract Dates: contract_start_date (Mietbeginn)
5. Rent Increase Type: "index-linked", "percentage", "fixed_step", "none", or "unknown"

**OPTIONAL FIELDS (extract if available, otherwise use null):**
- utilities_cost: Monthly utilities (Betriebskosten/Nebenkosten)
- parking_rent: Separate parking fees
- contract_end_date: End date if fixed-term
- landlord_name: Landlord's full name (Vermieter)
- landlord_address: Landlord's address
- deposit_amount: Security deposit (Kaution)
- notice_period: Termination notice period (Kündigungsfrist)
- special_clauses: Notable clauses or conditions (as array)
- utilities_included: List of included utilities (as array)
- square_meters: Property size in m²
- number_of_rooms: Number of rooms (e.g., 2.5)
- rent_increase_schedule: Array of rent increases for Staffelmiete

**IMPORTANT EXTRACTION RULES:**
1. For tenants: Create separate entries for each tenant. If multiple tenants listed, extract all.
2. For dates: Use YYYY-MM-DD format only
3. For amounts: Extract numbers only (no currency symbols)
4. For rent_increase_type:
   - Use "fixed_step" for Staffelmiete (fixed increases at specific dates)
   - Use "index-linked" for index-based increases (Indexmiete)
   - Use "percentage" for percentage-based increases
   - Use "none" if explicitly no increases
   - Use "unknown" if unclear
5. For rent_increase_schedule: Extract all scheduled increases with dates and amounts
6. For special_clauses: Include important clauses like pet policies, renovation restrictions, etc.
7. For is_active: Set to true if contract_end_date is null or in future, false otherwise

**CONFIDENCE SCORING:**
For each field extracted, provide a confidence score (0.0-1.0):
- 1.0: Explicitly stated with clear value
- 0.8-0.9: Clearly implied or calculated from other fields
- 0.5-0.7: Inferred from context or partial information
- 0.0-0.4: Uncertain or guessed

**OUTPUT FORMAT:**
Return a valid JSON object matching this structure:
{
  "tenants": [
    {"first_name": "string", "last_name": "string", "birth_date": "YYYY-MM-DD or null"}
  ],
  "address": {
    "street": "string",
    "house_number": "string",
    "zip_code": "string",
    "city": "string",
    "apartment_unit": "string or null"
  },
  "warm_rent": "decimal as string",
  "cold_rent": "decimal as string",
  "utilities_cost": "decimal as string or null",
  "parking_rent": "decimal as string or null",
  "rent_increase_type": "fixed_step|index-linked|percentage|none|unknown",
  "rent_increase_schedule": [{"date": "YYYY-MM-DD", "increase": "amount", "new_cold_rent": "amount"}] or null,
  "contract_start_date": "YYYY-MM-DD",
  "contract_end_date": "YYYY-MM-DD or null",
  "is_active": true or false,
  "landlord_name": "string or null",
  "landlord_address": "string or null",
  "deposit_amount": "decimal as string or null",
  "notice_period": "string or null",
  "special_clauses": ["string"] or null,
  "utilities_included": ["string"] or null,
  "square_meters": "decimal as string or null",
  "number_of_rooms": "decimal as string or null",
  "confidence_scores": {
    "field_name": confidence_value
  }
}

**CRITICAL:** Return ONLY valid JSON. No markdown, no explanations, no additional text."""

    async def extract(
        self,
        pdf_text: str
    ) -> Dict:
        """
        Extract lease data from PDF text using AI.
        
        Args:
            pdf_text: Extracted text from PDF document
            
        Returns:
            Extracted lease data as dictionary
            
        Raises:
            ExtractionError: If extraction fails after all retries
        """
        logger.info(f"Starting AI extraction | Text length: {len(pdf_text)} chars")
        
        result = await self._extract_with_openai(pdf_text)
        logger.info(f"✓ Extraction successful with OpenAI | Model: {self.OPENAI_MODEL}")
        return result
    
    async def _extract_with_openai(self, text: str) -> Dict:
        """
        Extract data using OpenAI GPT-4 with JSON mode.
        
        Args:
            text: PDF text to extract from
            
        Returns:
            Extracted data as dictionary
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"OpenAI extraction attempt {attempt + 1}/{self.MAX_RETRIES} | Model: {self.OPENAI_MODEL}")
                
                response = await self.openai_client.chat.completions.create(
                    model=self.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": self._extraction_prompt},
                        {"role": "user", "content": f"Extract lease data from this German contract:\n\n{text}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,  # Low temperature for consistency
                    max_tokens=self.MAX_TOKENS
                )
                
                # Parse JSON response
                result = json.loads(response.choices[0].message.content)
                logger.info(f"OpenAI response parsed successfully | Keys extracted: {list(result.keys())}")
                
                # Add metadata
                result["ai_model_used"] = self.OPENAI_MODEL
                result["extraction_timestamp"] = datetime.utcnow().isoformat()
                
                # Validate against schema
                await self._validate_extraction(result)
                logger.info("OpenAI extraction validated against schema successfully")
                
                return result
                
            except OpenAIError as e:
                logger.warning(f"OpenAI API error on attempt {attempt + 1}/{self.MAX_RETRIES}: {str(e)[:200]}")
                if attempt < self.MAX_RETRIES - 1:
                    delay = await self._exponential_backoff(attempt)
                    logger.info(f"Retrying after {delay:.2f}s backoff...")
                else:
                    logger.error(f"OpenAI extraction failed after {self.MAX_RETRIES} attempts")
                    raise
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await self._exponential_backoff(attempt)
                else:
                    raise ExtractionError(f"Invalid JSON from OpenAI: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in OpenAI extraction on attempt {attempt + 1}: {e}", exc_info=True)
                raise
    
    async def _validate_extraction(self, data: Dict) -> None:
        """
        Validate extracted data against Pydantic schema.
        
        Args:
            data: Extracted data dictionary
            
        Raises:
            ExtractionError: If validation fails
        """
        try:
            # Validate using Pydantic schema
            LeaseExtraction(**data)
            logger.info("✓ Extraction data validated against Pydantic schema")
        except ValidationError as e:
            logger.error(f"✗ Schema validation failed: {e.error_count()} errors | {e.errors()[:3]}")
            raise ExtractionError(f"Extracted data doesn't match schema: {e}")
    
    async def _exponential_backoff(self, attempt: int) -> float:
        """
        Implement exponential backoff between retries.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay duration in seconds
        """
        delay = self.BASE_RETRY_DELAY * (2 ** attempt)
        logger.info(f"⏱ Exponential backoff: waiting {delay}s before retry (attempt {attempt + 1})")
        await asyncio.sleep(delay)
        return delay


# Singleton instance
ai_extractor = AIExtractor()
