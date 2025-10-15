"""
Quality Scoring Service

Production-grade quality assessment system for lease extraction results.
Implements 4-metric scoring: Confidence, Completeness, Validation, and Consistency.

Scoring Formula:
EQS = (Confidence × 0.30) + (Completeness × 0.25) + (Validation × 0.25) + (Consistency × 0.20)

Quality Levels:
- Excellent: 90-100
- Good: 75-89
- Fair: 60-74
- Poor: 0-59
"""

from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from datetime import date
from dataclasses import dataclass

from app.schemas import LeaseExtraction, QualityMetrics
from app.logging_config import logger


@dataclass
class QualityIssue:
    """Represents a quality issue found during assessment"""
    severity: str  # "error", "warning", "info"
    category: str  # "confidence", "completeness", "validation", "consistency"
    field: str
    message: str
    impact: float  # Impact on score (0.0-1.0)


class QualityScorer:
    """
    Advanced quality scoring system for lease extraction results.
    
    Metrics:
    1. Confidence Score (30%): AI's confidence in extracted values
    2. Completeness Score (25%): Percentage of required fields filled
    3. Validation Score (25%): Business rule compliance
    4. Consistency Score (20%): Cross-field logical consistency
    """
    
    # Required fields that MUST be present
    REQUIRED_FIELDS = [
        "tenants",
        "address.street",
        "address.house_number",
        "address.zip_code",
        "address.city",
        "warm_rent",
        "cold_rent",
        "contract_start_date",
        "rent_increase_type",
    ]
    
    # Bonus fields that are nice to have
    BONUS_FIELDS = [
        "landlord_name",
        "landlord_address",
        "deposit_amount",
        "notice_period",
        "special_clauses",
        "utilities_included",
        "square_meters",
        "number_of_rooms",
        "parking_rent",
        "utilities_cost",
    ]
    
    # Weight distribution
    CONFIDENCE_WEIGHT = 0.30
    COMPLETENESS_WEIGHT = 0.25
    VALIDATION_WEIGHT = 0.25
    CONSISTENCY_WEIGHT = 0.20
    
    def __init__(self):
        """Initialize quality scorer"""
        self.issues: List[QualityIssue] = []
    
    def assess_quality(self, extraction: LeaseExtraction) -> QualityMetrics:
        """
        Perform comprehensive quality assessment.
        
        Args:
            extraction: Lease extraction result to assess
            
        Returns:
            QualityMetrics with scores and details
        """
        logger.info("━━━ Starting Quality Assessment ━━━")
        self.issues = []  # Reset issues
        
        # Calculate individual scores
        logger.info("Calculating confidence score...")
        confidence_score = self._calculate_confidence_score(extraction)
        logger.info(f"  → Confidence: {confidence_score:.2f}/100")
        
        logger.info("Calculating completeness score...")
        completeness_score = self._calculate_completeness_score(extraction)
        logger.info(f"  → Completeness: {completeness_score:.2f}/100")
        
        logger.info("Calculating validation score...")
        validation_score = self._calculate_validation_score(extraction)
        logger.info(f"  → Validation: {validation_score:.2f}/100")
        
        logger.info("Calculating consistency score...")
        consistency_score = self._calculate_consistency_score(extraction)
        logger.info(f"  → Consistency: {consistency_score:.2f}/100")
        
        # Calculate weighted overall score
        overall_score = (
            confidence_score * self.CONFIDENCE_WEIGHT +
            completeness_score * self.COMPLETENESS_WEIGHT +
            validation_score * self.VALIDATION_WEIGHT +
            consistency_score * self.CONSISTENCY_WEIGHT
        )
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        # Count issues
        errors = len([i for i in self.issues if i.severity == "error"])
        warnings = len([i for i in self.issues if i.severity == "warning"])
        
        logger.info(
            f"━━━ Quality Assessment Complete ━━━\n"
            f"  Overall Score: {overall_score:.2f}/100 ({quality_level})\n"
            f"  Confidence: {confidence_score:.2f} | Completeness: {completeness_score:.2f} | "
            f"Validation: {validation_score:.2f} | Consistency: {consistency_score:.2f}\n"
            f"  Issues: {errors} errors, {warnings} warnings"
        )
        
        # Return metrics - overall_score remains 0-100, confidence_score is 0-1
        return QualityMetrics(
            overall_score=overall_score,
            confidence_score=confidence_score / 100,  # Convert to 0-1
            completeness_score=completeness_score,
            validation_score=validation_score,
            consistency_score=consistency_score,
            validation_errors=[issue.message for issue in self.issues if issue.severity == "error"],
            warnings=[issue.message for issue in self.issues if issue.severity == "warning"],
            field_scores={}  # Can be populated later if needed
        )
    
    def _calculate_confidence_score(self, extraction: LeaseExtraction) -> float:
        """
        Calculate confidence score based on AI's confidence values.
        
        Score: Average of confidence scores for required fields.
        Bonus fields contribute but with lower weight.
        
        Args:
            extraction: Lease extraction result
            
        Returns:
            Confidence score (0-100)
        """
        if not extraction.confidence_scores:
            self.issues.append(QualityIssue(
                severity="warning",
                category="confidence",
                field="confidence_scores",
                message="No confidence scores provided by AI",
                impact=0.3
            ))
            return 50.0  # Default middle score if no confidence data
        
        # Calculate average for required fields
        required_confidences = []
        for field in self.REQUIRED_FIELDS:
            # Handle nested fields like "address.street"
            if "." in field:
                # For nested fields, use the parent field confidence (e.g., "address")
                parent_field = field.split(".")[0]
                field_key = parent_field
            else:
                field_key = field
            
            if field_key in extraction.confidence_scores:
                score = extraction.confidence_scores[field_key]
                required_confidences.append(score)
                
                # Flag low confidence fields (only once per parent field)
                if score < 0.6 and field_key == field:  # Only flag for non-nested or first occurrence
                    self.issues.append(QualityIssue(
                        severity="warning",
                        category="confidence",
                        field=field_key,
                        message=f"Low confidence score: {score:.2f}",
                        impact=0.1
                    ))
            else:
                # Missing confidence for required field
                required_confidences.append(0.5)  # Assume medium confidence
        
        # Calculate average
        if required_confidences:
            avg_confidence = sum(required_confidences) / len(required_confidences)
            score = avg_confidence * 100
            logger.debug(f"Confidence: {len(required_confidences)} fields averaged to {score:.2f}/100")
            return score
        
        logger.debug("Confidence: No confidence data, returning default 50.0")
        return 50.0
    
    def _calculate_completeness_score(self, extraction: LeaseExtraction) -> float:
        """
        Calculate completeness score based on filled fields.
        
        Score: (Required fields filled × 0.7) + (Bonus fields filled × 0.3)
        
        Args:
            extraction: Lease extraction result
            
        Returns:
            Completeness score (0-100)
        """
        # Check required fields
        required_filled = 0
        required_total = len(self.REQUIRED_FIELDS)
        
        for field in self.REQUIRED_FIELDS:
            if self._is_field_filled(extraction, field):
                required_filled += 1
            else:
                self.issues.append(QualityIssue(
                    severity="error",
                    category="completeness",
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    impact=0.2
                ))
        
        # Check bonus fields
        bonus_filled = 0
        bonus_total = len(self.BONUS_FIELDS)
        
        for field in self.BONUS_FIELDS:
            if self._is_field_filled(extraction, field):
                bonus_filled += 1
        
        # Calculate weighted score
        required_percentage = (required_filled / required_total) if required_total > 0 else 0
        bonus_percentage = (bonus_filled / bonus_total) if bonus_total > 0 else 0
        
        score = (required_percentage * 0.7 + bonus_percentage * 0.3) * 100
        
        logger.debug(
            f"Completeness: {required_filled}/{required_total} required ({required_percentage*100:.1f}%), "
            f"{bonus_filled}/{bonus_total} bonus ({bonus_percentage*100:.1f}%) = {score:.2f}/100"
        )
        
        return score
    
    def _calculate_validation_score(self, extraction: LeaseExtraction) -> float:
        """
        Calculate validation score based on business rule compliance.
        
        Rules checked:
        - Rent relationships (warm >= cold)
        - Date logic (start before end if exists)
        - Postal code format
        - Reasonable value ranges
        
        Args:
            extraction: Lease extraction result
            
        Returns:
            Validation score (0-100)
        """
        total_rules = 0
        passed_rules = 0
        
        # Rule 1: Warm rent >= Cold rent
        total_rules += 1
        if extraction.warm_rent >= extraction.cold_rent:
            passed_rules += 1
        else:
            self.issues.append(QualityIssue(
                severity="error",
                category="validation",
                field="rent",
                message=f"Warm rent (€{extraction.warm_rent}) < Cold rent (€{extraction.cold_rent})",
                impact=0.3
            ))
        
        # Rule 2: Utilities calculation check (if available)
        if extraction.utilities_cost:
            total_rules += 1
            expected_utilities = extraction.warm_rent - extraction.cold_rent
            
            # Allow for parking rent to be included in cold rent
            if extraction.parking_rent:
                expected_utilities -= extraction.parking_rent
            
            # Allow ±10% tolerance
            tolerance = expected_utilities * Decimal("0.10")
            if abs(extraction.utilities_cost - expected_utilities) <= tolerance:
                passed_rules += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="validation",
                    field="utilities_cost",
                    message=f"Utilities (€{extraction.utilities_cost}) don't match warm-cold difference",
                    impact=0.1
                ))
        
        # Rule 3: Contract dates logic
        if extraction.contract_end_date:
            total_rules += 1
            if extraction.contract_end_date > extraction.contract_start_date:
                passed_rules += 1
            else:
                self.issues.append(QualityIssue(
                    severity="error",
                    category="validation",
                    field="contract_dates",
                    message="Contract end date is before start date",
                    impact=0.2
                ))
        
        # Rule 4: Reasonable rent values (€100-€10,000)
        total_rules += 1
        if Decimal("100") <= extraction.cold_rent <= Decimal("10000"):
            passed_rules += 1
        else:
            self.issues.append(QualityIssue(
                severity="warning",
                category="validation",
                field="cold_rent",
                message=f"Unusual cold rent amount: €{extraction.cold_rent}",
                impact=0.1
            ))
        
        # Rule 5: Deposit typically 2-3 months rent
        if extraction.deposit_amount:
            total_rules += 1
            expected_deposit_min = extraction.cold_rent * 2
            expected_deposit_max = extraction.cold_rent * 3 * Decimal("1.2")  # +20% tolerance
            
            if expected_deposit_min <= extraction.deposit_amount <= expected_deposit_max:
                passed_rules += 1
            else:
                self.issues.append(QualityIssue(
                    severity="info",
                    category="validation",
                    field="deposit_amount",
                    message=f"Deposit (€{extraction.deposit_amount}) unusual for rent (€{extraction.cold_rent})",
                    impact=0.05
                ))
        
        # Rule 6: At least one tenant
        total_rules += 1
        if extraction.tenants and len(extraction.tenants) > 0:
            passed_rules += 1
        else:
            self.issues.append(QualityIssue(
                severity="error",
                category="validation",
                field="tenants",
                message="No tenants found",
                impact=0.3
            ))
        
        # Rule 7: Reasonable number of rooms (0.5-10)
        if extraction.number_of_rooms:
            total_rules += 1
            if Decimal("0.5") <= extraction.number_of_rooms <= Decimal("10"):
                passed_rules += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="validation",
                    field="number_of_rooms",
                    message=f"Unusual number of rooms: {extraction.number_of_rooms}",
                    impact=0.05
                ))
        
        # Rule 8: Reasonable square meters (10-500)
        if extraction.square_meters:
            total_rules += 1
            if Decimal("10") <= extraction.square_meters <= Decimal("500"):
                passed_rules += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="validation",
                    field="square_meters",
                    message=f"Unusual square meters: {extraction.square_meters}m²",
                    impact=0.05
                ))
        
        score = (passed_rules / total_rules * 100) if total_rules > 0 else 100
        
        logger.debug(f"Validation: {passed_rules}/{total_rules} rules passed ({score:.2f}/100)")
        
        return score
    
    def _calculate_consistency_score(self, extraction: LeaseExtraction) -> float:
        """
        Calculate consistency score based on cross-field logic.
        
        Checks:
        - is_active matches contract end date
        - Rent increase schedule matches type
        - Address components are consistent
        - Legacy name fields match tenant data
        
        Args:
            extraction: Lease extraction result
            
        Returns:
            Consistency score (0-100)
        """
        total_checks = 0
        passed_checks = 0
        
        # Check 1: is_active consistency with end date
        total_checks += 1
        today = date.today()
        
        if extraction.contract_end_date:
            expected_active = extraction.contract_end_date >= today
            if extraction.is_active == expected_active:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="consistency",
                    field="is_active",
                    message=f"is_active={extraction.is_active} inconsistent with end_date={extraction.contract_end_date}",
                    impact=0.1
                ))
        else:
            # No end date means unlimited = should be active
            if extraction.is_active:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="info",
                    category="consistency",
                    field="is_active",
                    message="Unlimited contract marked as inactive",
                    impact=0.05
                ))
        
        # Check 2: Rent increase schedule matches type
        total_checks += 1
        if extraction.rent_increase_type == "fixed_step":
            if extraction.rent_increase_schedule and len(extraction.rent_increase_schedule) > 0:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="consistency",
                    field="rent_increase_schedule",
                    message="Rent type is 'fixed_step' but no schedule provided",
                    impact=0.15
                ))
        elif extraction.rent_increase_type == "none":
            if not extraction.rent_increase_schedule or len(extraction.rent_increase_schedule) == 0:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="consistency",
                    field="rent_increase_schedule",
                    message="Rent type is 'none' but schedule exists",
                    impact=0.1
                ))
        else:
            # For index-linked, percentage, or unknown - schedule is optional
            passed_checks += 1
        
        # Check 3: Legacy name fields match first tenant
        if extraction.tenants and len(extraction.tenants) > 0:
            total_checks += 1
            first_tenant = extraction.tenants[0]
            
            # These should auto-populate, but let's verify
            if (extraction.name == first_tenant.first_name and 
                extraction.surname == first_tenant.last_name):
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="info",
                    category="consistency",
                    field="name/surname",
                    message="Legacy name fields don't match first tenant",
                    impact=0.05
                ))
        
        # Check 4: Postal code matches city (basic check)
        total_checks += 1
        munich_zip_ranges = [(80000, 81999)]  # Munich postal codes
        
        if "münchen" in extraction.address.city.lower() or "munich" in extraction.address.city.lower():
            zip_int = int(extraction.address.zip_code)
            is_munich_zip = any(start <= zip_int <= end for start, end in munich_zip_ranges)
            
            if is_munich_zip:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="info",
                    category="consistency",
                    field="address",
                    message=f"Postal code {extraction.address.zip_code} unusual for München",
                    impact=0.05
                ))
        else:
            # Can't verify other cities, assume correct
            passed_checks += 1
        
        # Check 5: Parking rent should be less than cold rent
        if extraction.parking_rent:
            total_checks += 1
            if extraction.parking_rent < extraction.cold_rent:
                passed_checks += 1
            else:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="consistency",
                    field="parking_rent",
                    message=f"Parking (€{extraction.parking_rent}) >= Cold rent (€{extraction.cold_rent})",
                    impact=0.1
                ))
        
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        
        logger.debug(f"Consistency: {passed_checks}/{total_checks} checks passed ({score:.2f}/100)")
        
        return score
    
    def _is_field_filled(self, extraction: LeaseExtraction, field: str) -> bool:
        """
        Check if a field is filled with valid data.
        
        Args:
            extraction: Lease extraction result
            field: Field name (supports nested like "address.street")
            
        Returns:
            True if field has valid data
        """
        try:
            # Handle nested fields
            if "." in field:
                parts = field.split(".")
                value = extraction
                for part in parts:
                    value = getattr(value, part, None)
                    if value is None:
                        return False
            else:
                value = getattr(extraction, field, None)
            
            # Check if value is meaningful
            if value is None:
                return False
            
            if isinstance(value, str):
                return len(value.strip()) > 0
            
            if isinstance(value, list):
                return len(value) > 0
            
            if isinstance(value, (int, float, Decimal)):
                return value > 0
            
            return True
            
        except AttributeError:
            return False
    
    def _determine_quality_level(self, score: float) -> str:
        """
        Determine quality level from score.
        
        Args:
            score: Overall quality score (0-100)
            
        Returns:
            Quality level string
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "poor"
    
    def _categorize_issues(self) -> Dict[str, List[str]]:
        """
        Categorize issues by severity for reporting.
        
        Returns:
            Dictionary mapping severity to list of issue messages
        """
        categorized = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        for issue in self.issues:
            message = f"[{issue.category}] {issue.field}: {issue.message}"
            
            if issue.severity == "error":
                categorized["errors"].append(message)
            elif issue.severity == "warning":
                categorized["warnings"].append(message)
            else:
                categorized["info"].append(message)
        
        return categorized


# Singleton instance
quality_scorer = QualityScorer()
