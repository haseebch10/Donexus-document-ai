from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal, List, Dict
from datetime import date, datetime
from decimal import Decimal
import re


class AddressData(BaseModel):
    """Address information for tenant or property"""
    street: str = Field(..., min_length=1, description="Street name only")
    house_number: str = Field(..., description="House number, may include letters (e.g., '25a')")
    zip_code: str = Field(..., description="German 5-digit postal code")
    city: str = Field(..., min_length=1, description="City or municipality name")
    apartment_unit: Optional[str] = Field(None, description="Apartment/unit number (e.g., '3.OG links')")
    
    @field_validator('zip_code')
    @classmethod
    def validate_german_postal_code(cls, v: str) -> str:
        """Validate German postal code format (5 digits)"""
        if not re.match(r'^\d{5}$', v):
            raise ValueError(f"Invalid German postal code: {v}. Must be 5 digits.")
        return v
    
    @field_validator('house_number')
    @classmethod
    def validate_house_number(cls, v: str) -> str:
        """Validate house number format"""
        if not re.match(r'^[0-9]+[a-zA-Z]?$', v):
            raise ValueError(f"Invalid house number format: {v}")
        return v


class TenantInfo(BaseModel):
    """Individual tenant information"""
    first_name: str = Field(..., min_length=1, description="Tenant's first name")
    last_name: str = Field(..., min_length=1, description="Tenant's last name")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    
    @property
    def full_name(self) -> str:
        """Get full name of tenant"""
        return f"{self.first_name} {self.last_name}"


class LeaseExtraction(BaseModel):
    """Complete lease extraction result with all fields"""
    
    # Tenant Information - Now supports multiple tenants!
    tenants: List[TenantInfo] = Field(
        ..., 
        min_length=1,
        description="List of all tenants (can be 1 or more). Primary tenant first."
    )
    
    # Legacy fields for backward compatibility (auto-populated from first tenant)
    name: Optional[str] = Field(None, description="Primary tenant's first name (auto-filled from tenants[0])")
    surname: Optional[str] = Field(None, description="Primary tenant's last name (auto-filled from tenants[0])")
    
    # Property Address
    address: AddressData
    
    # Rent Details
    warm_rent: Decimal = Field(..., gt=0, description="Total monthly rent including utilities (Warmmiete)")
    cold_rent: Decimal = Field(..., gt=0, description="Base rent excluding utilities (Kaltmiete)")
    utilities_cost: Optional[Decimal] = Field(None, ge=0, description="Monthly utilities/operating costs (Betriebskosten)")
    parking_rent: Optional[Decimal] = Field(None, ge=0, description="Additional parking space rent if separate")
    
    # Rent Increase
    rent_increase_type: Literal["index-linked", "percentage", "fixed_step", "none", "unknown"] = Field(
        ..., description="Type of rent increase mechanism"
    )
    rent_increase_schedule: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Detailed rent increase schedule if available (for Staffelmiete)"
    )
    
    # Contract Dates
    contract_start_date: date = Field(..., description="Contract effective/start date (Mietbeginn)")
    contract_end_date: Optional[date] = Field(None, description="Contract end date if fixed-term")
    is_active: bool = Field(..., description="Whether the lease is currently active")
    # Contract Dates
    contract_start_date: date = Field(..., description="Contract effective/start date (Mietbeginn)")
    contract_end_date: Optional[date] = Field(None, description="Contract end date if fixed-term")
    is_active: bool = Field(..., description="Whether the lease is currently active")
    
    # Bonus fields (optional)
    landlord_name: Optional[str] = Field(None, description="Landlord or property owner name (Vermieter)")
    landlord_address: Optional[str] = Field(None, description="Landlord's address")
    deposit_amount: Optional[Decimal] = Field(None, gt=0, description="Security deposit (Kaution)")
    notice_period: Optional[str] = Field(None, description="Termination notice period (Kündigungsfrist)")
    special_clauses: Optional[List[str]] = Field(None, description="Notable contract clauses or special conditions")
    utilities_included: Optional[List[str]] = Field(None, description="List of included utilities")
    square_meters: Optional[Decimal] = Field(None, gt=0, description="Property size in square meters")
    number_of_rooms: Optional[Decimal] = Field(None, gt=0, description="Number of rooms (e.g., 2.5 for 2.5 rooms)")
    
    # AI metadata
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="AI confidence score for each field (0.0-1.0)"
    )
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    ai_model_used: str = Field(default="unknown", description="AI model used for extraction")
    
    model_config = ConfigDict(
        protected_namespaces=(),  # Allow model_* field names
        json_schema_extra={
            "example": {
                "tenants": [
                    {"first_name": "Daniela", "last_name": "Rudolph", "birth_date": "1992-02-16"},
                    {"first_name": "Hendrik", "last_name": "Weber", "birth_date": "1989-09-11"}
                ],
                "address": {
                    "street": "Zieblandstraße",
                    "house_number": "25",
                    "zip_code": "80798",
                    "city": "München",
                    "apartment_unit": "3.OG links"
                },
                "warm_rent": "1405.00",
                "cold_rent": "1040.00",
                "parking_rent": "75.00",
                "utilities_cost": "290.00",
                "rent_increase_type": "fixed_step",
                "rent_increase_schedule": [
                    {"date": "2020-07-01", "increase": "50", "new_cold_rent": "1090"},
                    {"date": "2022-07-01", "increase": "50", "new_cold_rent": "1140"}
                ],
                "contract_start_date": "2020-03-01",
                "is_active": True,
                "landlord_name": "Franz Emanuel Freiherr Karaisl von Karais",
                "number_of_rooms": "2"
            }
        }
    )
    
    def model_post_init(self, __context) -> None:
        """Auto-populate legacy name/surname fields from first tenant"""
        if self.tenants and len(self.tenants) > 0:
            if not self.name:
                self.name = self.tenants[0].first_name
            if not self.surname:
                self.surname = self.tenants[0].last_name
    
    @property
    def primary_tenant(self) -> TenantInfo:
        """Get the primary (first) tenant"""
        return self.tenants[0] if self.tenants else None
    
    @property
    def tenant_count(self) -> int:
        """Get number of tenants"""
        return len(self.tenants) if self.tenants else 0
    
    @property
    def all_tenant_names(self) -> str:
        """Get comma-separated list of all tenant names"""
        if not self.tenants:
            return ""
        return ", ".join([t.full_name for t in self.tenants])
    
    @field_validator('warm_rent')
    @classmethod
    def validate_warm_rent_vs_cold_rent(cls, v: Decimal, info) -> Decimal:
        """Ensure warm rent is not less than cold rent"""
        if 'cold_rent' in info.data and v < info.data['cold_rent']:
            raise ValueError("Warm rent must be greater than or equal to cold rent")
        return v
    
    @field_validator('contract_start_date')
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        """Warn if contract date is in the future (but don't fail)"""
        if v > date.today():
            # Could add to warnings list if we had context
            pass
        return v
    
    @field_validator('utilities_cost')
    @classmethod
    def validate_utilities_calculation(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Check if utilities_cost matches warm_rent - cold_rent (with tolerance for parking)"""
        if v is None:
            return v
        
        if 'warm_rent' in info.data and 'cold_rent' in info.data:
            expected_utilities = info.data['warm_rent'] - info.data['cold_rent']
            # Allow for parking rent to be included
            if 'parking_rent' in info.data and info.data['parking_rent']:
                expected_utilities -= info.data['parking_rent']
            
            # Check with small tolerance (±10 EUR)
            if abs(v - expected_utilities) > 10:
                # This is a warning, not an error - could be parking included differently
                pass
        
        return v


class QualityMetrics(BaseModel):
    """Quality assessment metrics for extraction"""
    
    overall_score: float = Field(..., ge=0, le=100, description="Overall quality score (0-100)")
    confidence_score: float = Field(..., ge=0, le=1, description="Average AI confidence (0.0-1.0)")
    completeness_score: float = Field(..., ge=0, le=100, description="Percentage of required fields filled")
    validation_score: float = Field(..., ge=0, le=100, description="Data validation score")
    consistency_score: float = Field(..., ge=0, le=100, description="Cross-field consistency score")
    
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    
    # Detailed breakdown
    field_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual confidence scores per field"
    )
    
    @property
    def quality_tier(self) -> str:
        """Get quality tier based on overall score"""
        if self.overall_score >= 80:
            return "excellent"
        elif self.overall_score >= 60:
            return "good"
        else:
            return "poor"
    
    @property
    def color_code(self) -> str:
        """Get color code for UI display"""
        if self.overall_score >= 80:
            return "green"
        elif self.overall_score >= 60:
            return "yellow"
        else:
            return "red"


class ExtractionResult(BaseModel):
    """Complete API response for extraction"""
    
    id: str = Field(..., description="Unique extraction ID")
    filename: str = Field(..., description="Original PDF filename")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction: Optional[LeaseExtraction] = Field(None, description="Extracted lease data")
    quality: Optional[QualityMetrics] = Field(None, description="Quality metrics")
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")
    status: Literal["processing", "success", "partial", "failed"] = Field(
        default="processing",
        description="Extraction status"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "Mietvertrag-Zieblandstr_25.pdf",
                "status": "success",
                "processing_time_ms": 2847
            }
        }
    )


class UploadResponse(BaseModel):
    """Response for file upload"""
    
    id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field(default="uploaded", description="Upload status")
    message: str = Field(default="File uploaded successfully")


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
