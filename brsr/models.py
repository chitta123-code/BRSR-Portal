
from django.db import models
from organization.models import Company


class EntityDetails(models.Model):
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="entity_details"
    )

    financial_year = models.CharField(
        max_length=20
    )

    stock_exchanges = models.TextField(
        blank=True
    )

    paid_up_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    brsr_contact_name = models.CharField(
        max_length=255,
        blank=True
    )

    brsr_contact_designation = models.CharField(
        max_length=255,
        blank=True
    )

    brsr_contact_phone = models.CharField(
        max_length=30,
        blank=True
    )

    brsr_contact_email = models.EmailField(
        blank=True
    )

    reporting_boundary = models.CharField(
        max_length=20,
        choices=[
            ("STANDALONE", "Standalone"),
            ("CONSOLIDATED", "Consolidated"),
        ]
    )

    assurance_provider = models.CharField(
        max_length=255,
        blank=True
    )

    assurance_type = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.financial_year}"


class BusinessActivity(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="business_activities"
    )

    activity_description = models.CharField(
        max_length=500
    )

    turnover_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.activity_description}"


class ProductService(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products_services"
    )

    product_service_name = models.CharField(
        max_length=500
    )

    nic_code = models.CharField(
        max_length=20,
        blank=True
    )

    turnover_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.product_service_name}"


class OperationLocation(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="operation_locations"
    )

    location_name = models.CharField(
        max_length=255
    )

    location_type = models.CharField(
        max_length=50,
        choices=[
            ("NATIONAL", "National"),
            ("INTERNATIONAL", "International"),
        ]
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.location_name}"


class EmployeeWorkerCount(models.Model):
    CATEGORY_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("WORKER", "Worker"),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ("PERMANENT", "Permanent"),
        ("OTHER_THAN_PERMANENT", "Other than Permanent"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employee_worker_counts"
    )

    financial_year = models.CharField(
        max_length=20
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    employment_type = models.CharField(
        max_length=30,
        choices=EMPLOYMENT_TYPE_CHOICES
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    total = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"{self.category} - "
            f"{self.employment_type} - "
            f"{self.gender}"
        )



class WomenRepresentation(models.Model):
    CATEGORY_CHOICES = [
        ("BOARD_OF_DIRECTORS", "Board of Directors"),
        ("KMP", "Key Management Personnel"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="women_representation"
    )

    financial_year = models.CharField(
        max_length=20
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    total = models.PositiveIntegerField(
        default=0
    )

    female_count = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"{self.category} - {self.financial_year}"
        )

    @property
    def female_percentage(self):
        if self.total == 0:
            return 0
        return (self.female_count / self.total) * 100


class DifferentlyAbledEmployeeWorker(models.Model):
    CATEGORY_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("WORKER", "Worker"),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ("PERMANENT", "Permanent"),
        ("OTHER_THAN_PERMANENT", "Other than Permanent"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="differently_abled_records"
    )

    financial_year = models.CharField(
        max_length=20
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    employment_type = models.CharField(
        max_length=30,
        choices=EMPLOYMENT_TYPE_CHOICES
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    total = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"{self.category} - "
            f"{self.gender}"
        )


class CompanyRelationship(models.Model):
    RELATIONSHIP_CHOICES = [
        ("HOLDING", "Holding Company"),
        ("SUBSIDIARY", "Subsidiary Company"),
        ("ASSOCIATE", "Associate Company"),
        ("JOINT_VENTURE", "Joint Venture"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_relationships"
    )

    related_company_name = models.CharField(
        max_length=255
    )

    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES
    )

    percentage_of_shares_held = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    included_in_consolidation = models.BooleanField(
        default=False
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"{self.related_company_name} - "
            f"{self.relationship_type}"
        )


class CSRDetails(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="csr_details"
    )

    financial_year = models.CharField(
        max_length=20
    )

    csr_applicable = models.BooleanField(
        default=False
    )

    turnover = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    net_worth = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    csr_amount_required = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    csr_amount_spent = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    amount_unspent = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.company.name} - CSR - {self.financial_year}"



class GrievanceDisclosure(models.Model):
    STAKEHOLDER_CHOICES = [
        ("COMMUNITIES", "Communities"),
        ("INVESTORS", "Investors (other than shareholders)"),
        ("SHAREHOLDERS", "Shareholders"),
        ("EMPLOYEES_WORKERS", "Employees and workers"),
        ("CUSTOMERS", "Customers"),
        ("VALUE_CHAIN_PARTNERS", "Value Chain Partners"),
        ("OTHER", "Other"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="grievance_disclosures"
    )

    financial_year = models.CharField(max_length=20)

    stakeholder_group = models.CharField(
        max_length=50,
        choices=STAKEHOLDER_CHOICES
    )

    grievance_mechanism_in_place = models.BooleanField(default=False)

    grievance_policy_link = models.URLField(
        blank=True,
        null=True
    )

    current_complaints_filed = models.PositiveIntegerField(default=0)

    current_complaints_pending = models.PositiveIntegerField(default=0)

    current_remarks = models.TextField(blank=True)

    previous_complaints_filed = models.PositiveIntegerField(default=0)

    previous_complaints_pending = models.PositiveIntegerField(default=0)

    previous_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.stakeholder_group} - {self.financial_year}"


class MaterialResponsibleIssue(models.Model):
    ISSUE_TYPE_CHOICES = [
        ("RISK", "Risk"),
        ("OPPORTUNITY", "Opportunity"),
    ]

    CATEGORY_CHOICES = [
        ("ENVIRONMENTAL", "Environmental"),
        ("SOCIAL", "Social"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="material_responsible_issues"
    )

    financial_year = models.CharField(max_length=20)

    material_issue = models.CharField(max_length=255)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES
    )

    rationale = models.TextField()

    mitigation_approach = models.TextField(
        blank=True,
        null=True
    )

    financial_implication = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.material_issue}"



class PolicyProcess(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="policy_processes"
    )

    financial_year = models.CharField(max_length=20)

    principle = models.ForeignKey(
        "indicators.Principle",
        on_delete=models.CASCADE,
        related_name="policy_processes"
    )

    policy_covers_principle = models.BooleanField(default=False)

    board_approved = models.BooleanField(default=False)

    policy_web_link = models.URLField(
        blank=True,
        null=True
    )

    translated_into_procedures = models.BooleanField(default=False)

    extends_to_value_chain = models.BooleanField(default=False)

    codes_certifications_standards = models.TextField(
        blank=True
    )

    commitments_goals_targets = models.TextField(
        blank=True
    )

    target_timeline = models.CharField(
        max_length=255,
        blank=True
    )

    performance_against_commitments = models.TextField(
        blank=True
    )

    reasons_if_not_met = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"P{self.principle.number} - "
            f"{self.financial_year}"
        )


class GovernanceOversight(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="governance_oversight"
    )

    financial_year = models.CharField(max_length=20)

    director_statement = models.TextField(
        blank=True
    )

    highest_authority = models.CharField(
        max_length=255,
        blank=True
    )

    sustainability_committee_exists = models.BooleanField(
        default=False
    )

    sustainability_committee_details = models.TextField(
        blank=True
    )

    external_agency_assessment = models.BooleanField(
        default=False
    )

    external_agency_name = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.financial_year}"


class NGRBCReview(models.Model):
    REVIEW_SUBJECT_CHOICES = [
        (
            "POLICY_PERFORMANCE",
            "Performance against policies and follow-up action"
        ),
        (
            "STATUTORY_COMPLIANCE",
            "Compliance with statutory requirements and rectification"
        ),
    ]

    REVIEWER_CHOICES = [
        ("DIRECTOR", "Director"),
        ("BOARD_COMMITTEE", "Committee of the Board"),
        ("OTHER_COMMITTEE", "Any other Committee"),
    ]

    FREQUENCY_CHOICES = [
        ("ANNUALLY", "Annually"),
        ("HALF_YEARLY", "Half yearly"),
        ("QUARTERLY", "Quarterly"),
        ("OTHER", "Other"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="ngrbc_reviews"
    )

    financial_year = models.CharField(max_length=20)

    principle = models.ForeignKey(
        "indicators.Principle",
        on_delete=models.CASCADE,
        related_name="ngrbc_reviews"
    )

    review_subject = models.CharField(
        max_length=50,
        choices=REVIEW_SUBJECT_CHOICES
    )

    reviewer = models.CharField(
        max_length=30,
        choices=REVIEWER_CHOICES
    )

    frequency = models.CharField(
        max_length=30,
        choices=FREQUENCY_CHOICES
    )

    other_frequency = models.CharField(
        max_length=100,
        blank=True
    )

    review_details = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"P{self.principle.number} - "
            f"{self.financial_year}"
        )


class PolicyCoverageReason(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="policy_coverage_reasons"
    )

    financial_year = models.CharField(max_length=20)

    principle = models.ForeignKey(
        "indicators.Principle",
        on_delete=models.CASCADE,
        related_name="policy_coverage_reasons"
    )

    not_material = models.BooleanField(default=False)

    not_ready_to_implement = models.BooleanField(default=False)

    insufficient_resources = models.BooleanField(default=False)

    planned_next_financial_year = models.BooleanField(default=False)

    other_reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"P{self.principle.number} - "
            f"{self.financial_year}"
        )


class ExternalPolicyAssessment(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="external_policy_assessments"
    )

    financial_year = models.CharField(max_length=20)

    principle = models.ForeignKey(
        "indicators.Principle",
        on_delete=models.CASCADE,
        related_name="external_policy_assessments"
    )

    assessment_done = models.BooleanField(default=False)

    agency_name = models.CharField(
        max_length=255,
        blank=True
    )

    assessment_details = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"P{self.principle.number} - "
            f"{self.financial_year}"
        )


class PrinciplePerformance(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="principle_performances"
    )

    financial_year = models.CharField(max_length=20)

    principle = models.ForeignKey(
        "indicators.Principle",
        on_delete=models.CASCADE,
        related_name="performances"
    )

    summary = models.TextField(
        blank=True
    )

    key_actions = models.TextField(
        blank=True
    )

    challenges = models.TextField(
        blank=True
    )

    improvement_actions = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.company.name} - "
            f"P{self.principle.number} - "
            f"{self.financial_year}"
        )