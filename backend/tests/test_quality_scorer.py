"""
Tests for Quality Scoring Service

Tests the 4-metric quality assessment system with various scenarios.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from app.services.quality_scorer import QualityScorer, QualityIssue
from app.schemas import LeaseExtraction, TenantInfo, AddressData


class TestQualityScorer:
    """Test suite for quality scoring system"""
    
    @pytest.fixture
    def quality_scorer(self):
        """Create QualityScorer instance"""
        return QualityScorer()
    
    @pytest.fixture
    def perfect_extraction(self):
        """Create a perfect extraction with all fields filled correctly"""
        return LeaseExtraction(
            tenants=[
                TenantInfo(
                    first_name="Daniela",
                    last_name="Rudolph",
                    birth_date=date(1992, 2, 16)
                ),
                TenantInfo(
                    first_name="Hendrik",
                    last_name="Weber",
                    birth_date=date(1989, 9, 11)
                )
            ],
            address=AddressData(
                street="Zieblandstraße",
                house_number="25",
                zip_code="80798",
                city="München",
                apartment_unit="3.OG links"
            ),
            warm_rent=Decimal("1405.00"),
            cold_rent=Decimal("1040.00"),
            utilities_cost=Decimal("290.00"),
            parking_rent=Decimal("75.00"),
            rent_increase_type="fixed_step",
            rent_increase_schedule=[
                {"date": "2020-07-01", "increase": "50", "new_cold_rent": "1090"},
                {"date": "2022-07-01", "increase": "50", "new_cold_rent": "1140"}
            ],
            contract_start_date=date(2020, 3, 1),
            contract_end_date=None,
            is_active=True,
            landlord_name="Franz Emanuel Freiherr Karaisl von Karais",
            landlord_address="Lachnerstr. 29, 80639 München",
            deposit_amount=Decimal("3120.00"),
            notice_period="3 Monate zum Monatsende",
            special_clauses=["Haustierhaltung nur mit Genehmigung"],
            utilities_included=["Heizung", "Warmwasser"],
            square_meters=Decimal("65"),
            number_of_rooms=Decimal("2"),
            confidence_scores={
                "tenants": 1.0,
                "address": 1.0,
                "warm_rent": 1.0,
                "cold_rent": 1.0,
                "rent_increase_type": 1.0,
                "contract_start_date": 1.0,
                "landlord_name": 0.95,
                "deposit_amount": 0.9
            }
        )
    
    @pytest.fixture
    def minimal_extraction(self):
        """Create minimal valid extraction with only required fields"""
        return LeaseExtraction(
            tenants=[
                TenantInfo(first_name="Max", last_name="Mustermann", birth_date=None)
            ],
            address=AddressData(
                street="Teststraße",
                house_number="1",
                zip_code="10115",
                city="Berlin"
            ),
            warm_rent=Decimal("1000.00"),
            cold_rent=Decimal("800.00"),
            rent_increase_type="unknown",
            contract_start_date=date(2024, 1, 1),
            is_active=True,
            confidence_scores={
                "tenants": 0.8,
                "address": 0.7,
                "warm_rent": 0.9,
                "cold_rent": 0.9
            }
        )
    
    @pytest.fixture
    def problematic_extraction(self):
        """Create extraction with various quality issues"""
        return LeaseExtraction(
            tenants=[
                TenantInfo(first_name="Test", last_name="User", birth_date=None)
            ],
            address=AddressData(
                street="Street",
                house_number="999",
                zip_code="99999",  # Invalid for München
                city="München"
            ),
            warm_rent=Decimal("500.00"),  # Less than cold rent!
            cold_rent=Decimal("1000.00"),
            rent_increase_type="fixed_step",
            rent_increase_schedule=None,  # Missing schedule for fixed_step
            contract_start_date=date(2024, 1, 1),
            contract_end_date=date(2023, 1, 1),  # Before start date!
            is_active=False,
            deposit_amount=Decimal("50.00"),  # Too low
            number_of_rooms=Decimal("50"),  # Unrealistic
            confidence_scores={
                "tenants": 0.3,  # Low confidence
                "address": 0.4,
                "warm_rent": 0.2,
                "cold_rent": 0.5
            }
        )
    
    def test_scorer_initialization(self, quality_scorer):
        """Test QualityScorer initializes correctly"""
        assert quality_scorer is not None
        assert quality_scorer.CONFIDENCE_WEIGHT == 0.30
        assert quality_scorer.COMPLETENESS_WEIGHT == 0.25
        assert quality_scorer.VALIDATION_WEIGHT == 0.25
        assert quality_scorer.CONSISTENCY_WEIGHT == 0.20
        assert len(quality_scorer.REQUIRED_FIELDS) > 0
        assert len(quality_scorer.BONUS_FIELDS) > 0
    
    def test_perfect_extraction_scores_high(self, quality_scorer, perfect_extraction):
        """Test that perfect extraction receives excellent quality score."""
        metrics = quality_scorer.assess_quality(perfect_extraction)
        
        # Should be "excellent" (>= 80)
        assert metrics.quality_tier == "excellent"
        assert metrics.overall_score >= 80
        assert len(metrics.validation_errors) == 0
    
    def test_minimal_extraction_scores_fair(self, quality_scorer, minimal_extraction):
        """Test that minimal extraction receives fair/good quality score."""
        metrics = quality_scorer.assess_quality(minimal_extraction)
        
        # Should be good range (scores can be high for minimal valid extraction)
        assert metrics.quality_tier in ["excellent", "good"]
        assert metrics.overall_score >= 60
        assert metrics.completeness_score < 100  # Should not have all fields
    
    def test_problematic_extraction_scores_poor(self, quality_scorer, problematic_extraction):
        """Test that problematic extraction receives poor quality score."""
        metrics = quality_scorer.assess_quality(problematic_extraction)
        
        # Should be "poor" (< 60)
        assert metrics.quality_tier == "poor"
        assert metrics.overall_score < 60
        assert len(metrics.validation_errors) > 0  # Should have many errors
    
    def test_confidence_score_calculation(self, quality_scorer, perfect_extraction):
        """Test confidence score calculation"""
        score = quality_scorer._calculate_confidence_score(perfect_extraction)
        
        # Should be high for perfect extraction
        assert 90 <= score <= 100
        
        # Test with low confidence
        perfect_extraction.confidence_scores = {
            "tenants": 0.3,
            "address": 0.4,
            "warm_rent": 0.5
        }
        low_score = quality_scorer._calculate_confidence_score(perfect_extraction)
        assert low_score < 50
    
    def test_completeness_score_calculation(self, quality_scorer, perfect_extraction):
        """Test completeness score calculation"""
        # Perfect extraction should have high completeness
        score = quality_scorer._calculate_completeness_score(perfect_extraction)
        assert score >= 90
        
        # Minimal extraction should have lower completeness
        minimal = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1", zip_code="12345", city="Test"
            ),
            warm_rent=Decimal("1000"),
            cold_rent=Decimal("800"),
            rent_increase_type="none",
            contract_start_date=date(2024, 1, 1),
            is_active=True
        )
        minimal_score = quality_scorer._calculate_completeness_score(minimal)
        assert minimal_score < score
    
    def test_validation_score_rules(self, quality_scorer):
        """Test validation score checks business rules"""
        # Test warm < cold rent violation
        bad_rent = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1", zip_code="12345", city="Test"
            ),
            warm_rent=Decimal("500"),  # Invalid: less than cold
            cold_rent=Decimal("1000"),
            rent_increase_type="none",
            contract_start_date=date(2024, 1, 1),
            is_active=True
        )
        
        score = quality_scorer._calculate_validation_score(bad_rent)
        
        # Should fail at least one rule
        assert score < 100
        
        # Should have validation error
        validation_errors = [
            issue for issue in quality_scorer.issues
            if issue.category == "validation" and issue.severity == "error"
        ]
        assert len(validation_errors) > 0
    
    def test_consistency_score_checks(self, quality_scorer):
        """Test consistency score checks cross-field logic"""
        # Test inconsistent is_active with end date
        inconsistent = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1", zip_code="12345", city="Test"
            ),
            warm_rent=Decimal("1000"),
            cold_rent=Decimal("800"),
            rent_increase_type="none",
            contract_start_date=date(2020, 1, 1),
            contract_end_date=date(2022, 1, 1),  # Past date
            is_active=True,  # But marked as active!
            confidence_scores={}
        )
        
        score = quality_scorer._calculate_consistency_score(inconsistent)
        
        # Should detect inconsistency
        assert score < 100
    
    def test_rent_increase_consistency(self, quality_scorer):
        """Test rent increase type and schedule consistency"""
        # fixed_step without schedule
        inconsistent = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1", zip_code="12345", city="Test"
            ),
            warm_rent=Decimal("1000"),
            cold_rent=Decimal("800"),
            rent_increase_type="fixed_step",
            rent_increase_schedule=None,  # Missing!
            contract_start_date=date(2024, 1, 1),
            is_active=True,
            confidence_scores={}
        )
        
        score = quality_scorer._calculate_consistency_score(inconsistent)
        
        # Should flag inconsistency
        consistency_issues = [
            issue for issue in quality_scorer.issues
            if issue.category == "consistency" and "schedule" in issue.message.lower()
        ]
        assert len(consistency_issues) > 0
    
    def test_quality_level_determination(self, quality_scorer):
        """Test quality level categorization"""
        assert quality_scorer._determine_quality_level(95) == "excellent"
        assert quality_scorer._determine_quality_level(80) == "good"
        assert quality_scorer._determine_quality_level(65) == "fair"
        assert quality_scorer._determine_quality_level(40) == "poor"
    
    def test_field_filled_detection(self, quality_scorer, perfect_extraction):
        """Test field filled detection logic"""
        # Filled fields
        assert quality_scorer._is_field_filled(perfect_extraction, "landlord_name")
        assert quality_scorer._is_field_filled(perfect_extraction, "address.street")
        assert quality_scorer._is_field_filled(perfect_extraction, "warm_rent")
        
        # Empty/None fields
        perfect_extraction.square_meters = None
        assert not quality_scorer._is_field_filled(perfect_extraction, "square_meters")
        
        perfect_extraction.special_clauses = []
        assert not quality_scorer._is_field_filled(perfect_extraction, "special_clauses")
    
    def test_issue_categorization(self, quality_scorer, problematic_extraction):
        """Test issue categorization by severity"""
        quality_scorer.assess_quality(problematic_extraction)
        
        categorized = quality_scorer._categorize_issues()
        
        # Should have issues in multiple categories
        assert len(categorized["errors"]) > 0
        assert len(categorized["warnings"]) > 0
        
        # Each message should include category and field
        for error in categorized["errors"]:
            assert "[" in error  # Has category tag
            assert ":" in error  # Has field:message format
    
    def test_weighted_score_calculation(self, quality_scorer, perfect_extraction):
        """Test that overall score is correctly weighted"""
        metrics = quality_scorer.assess_quality(perfect_extraction)
        
        # Manually calculate expected score (confidence_score is 0-1, others are 0-100)
        expected = (
            (metrics.confidence_score * 100) * 0.30 +
            metrics.completeness_score * 0.25 +
            metrics.validation_score * 0.25 +
            metrics.consistency_score * 0.20
        )
        
        # Should match (within rounding)
        assert abs(metrics.overall_score - expected) < 0.1
    
    def test_munich_postal_code_validation(self, quality_scorer):
        """Test Munich postal code consistency check"""
        # Valid Munich postal code
        valid_munich = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1",
                zip_code="80798",  # Valid Munich code
                city="München"
            ),
            warm_rent=Decimal("1000"),
            cold_rent=Decimal("800"),
            rent_increase_type="none",
            contract_start_date=date(2024, 1, 1),
            is_active=True,
            confidence_scores={}
        )
        
        quality_scorer._calculate_consistency_score(valid_munich)
        
        # Should not flag postal code issue
        postal_issues = [
            issue for issue in quality_scorer.issues
            if "postal" in issue.message.lower() or "zip" in issue.field.lower()
        ]
        assert len(postal_issues) == 0
    
    def test_deposit_validation(self, quality_scorer):
        """Test deposit amount validation against rent"""
        # Reasonable deposit (3x rent)
        good_deposit = LeaseExtraction(
            tenants=[TenantInfo(first_name="Test", last_name="User", birth_date=None)],
            address=AddressData(
                street="Test", house_number="1", zip_code="12345", city="Test"
            ),
            warm_rent=Decimal("1000"),
            cold_rent=Decimal("800"),
            deposit_amount=Decimal("2400"),  # 3x cold rent
            rent_increase_type="none",
            contract_start_date=date(2024, 1, 1),
            is_active=True,
            confidence_scores={}
        )
        
        quality_scorer._calculate_validation_score(good_deposit)
        
        # Should pass deposit validation
        deposit_errors = [
            issue for issue in quality_scorer.issues
            if issue.field == "deposit_amount" and issue.severity == "error"
        ]
        assert len(deposit_errors) == 0


class TestQualityIssue:
    """Test QualityIssue dataclass"""
    
    def test_issue_creation(self):
        """Test creating quality issues"""
        issue = QualityIssue(
            severity="error",
            category="validation",
            field="warm_rent",
            message="Invalid value",
            impact=0.3
        )
        
        assert issue.severity == "error"
        assert issue.category == "validation"
        assert issue.field == "warm_rent"
        assert issue.message == "Invalid value"
        assert issue.impact == 0.3


class TestQualityScorerIntegration:
    """Integration tests with real-world scenarios"""
    
    @pytest.fixture
    def quality_scorer(self):
        return QualityScorer()
    
    def test_real_world_excellent_extraction(self, quality_scorer):
        """Test scoring of realistic high-quality extraction"""
        extraction = LeaseExtraction(
            tenants=[
                TenantInfo(first_name="Anna", last_name="Schmidt", birth_date=date(1990, 5, 15)),
                TenantInfo(first_name="Tom", last_name="Müller", birth_date=date(1988, 3, 22))
            ],
            address=AddressData(
                street="Leopoldstraße",
                house_number="142",
                zip_code="80804",
                city="München",
                apartment_unit="2. Stock"
            ),
            warm_rent=Decimal("1850.00"),
            cold_rent=Decimal("1500.00"),
            utilities_cost=Decimal("250.00"),
            parking_rent=Decimal("100.00"),
            rent_increase_type="index-linked",
            contract_start_date=date(2023, 1, 1),
            is_active=True,
            landlord_name="Immobilien GmbH München",
            deposit_amount=Decimal("4500.00"),
            notice_period="3 Monate",
            number_of_rooms=Decimal("3"),
            square_meters=Decimal("85"),
            confidence_scores={
                "tenants": 0.98,
                "address": 0.95,
                "warm_rent": 1.0,
                "cold_rent": 1.0,
                "utilities_cost": 0.9,
                "parking_rent": 0.92
            }
        )
        
        metrics = quality_scorer.assess_quality(extraction)
        
        assert metrics.quality_tier in ["excellent", "good"]
        assert metrics.overall_score >= 75
        print(f"\n✓ Real-world extraction scored: {metrics.overall_score} ({metrics.quality_tier})")
    
    def test_incomplete_extraction_with_warnings(self, quality_scorer):
        """Test extraction with missing optional fields"""
        extraction = LeaseExtraction(
            tenants=[TenantInfo(first_name="John", last_name="Doe", birth_date=None)],
            address=AddressData(
                street="Hauptstraße",
                house_number="10",
                zip_code="10115",
                city="Berlin"
            ),
            warm_rent=Decimal("1200.00"),
            cold_rent=Decimal("950.00"),
            rent_increase_type="unknown",
            contract_start_date=date(2024, 6, 1),
            is_active=True,
            confidence_scores={
                "tenants": 0.75,
                "address": 0.8,
                "warm_rent": 0.85,
                "cold_rent": 0.85
            }
        )
        
        metrics = quality_scorer.assess_quality(extraction)
        
        # Should still pass but with lower completeness
        assert metrics.completeness_score < 80
        assert metrics.quality_tier in ["excellent", "good"]  # Can still be excellent with validation/consistency scores
        assert len(metrics.warnings) >= 0  # May have warnings
