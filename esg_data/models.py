from django.core.serializers import python
from django.db import models
from organization.models import BusinessUnit, Project


class ESGMetric(models.Model):

    CATEGORY_CHOICES = [
        ("environmental", "Environmental"),
        ("social", "Social"),
        ("governance", "Governance"),
    ]

    name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    unit = models.CharField(max_length=50)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"



class ESGData(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name="esg_data"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="esg_data"
    )

    financial_year = models.CharField(
        max_length=9
    )

    metric = models.ForeignKey(
        ESGMetric,
        on_delete=models.PROTECT,
        related_name="data_entries",
        null=True,
        blank=True
    )

    value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True
    )

    data_source = models.CharField(
        max_length=200,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    entered_by = models.CharField(
        max_length=150,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from .validators import run_validation
        run_validation(self)

    def __str__(self):
        metric_name = self.metric.name if self.metric else "Unmapped Metric"

        return (
            f"{self.business_unit.name} - "
            f"{metric_name} - "
            f"{self.financial_year}"
        )

    

class ESGEvidence(models.Model):

    EVIDENCE_TYPE_CHOICES = [
        ("electricity_bill", "Electricity Bill"),
        ("fuel_invoice", "Fuel Invoice"),
        ("water_bill", "Water Bill"),
        ("travel_document", "Travel Document"),
        ("waste_document", "Waste Document"),
        ("employee_record", "Employee Record"),
        ("audit_report", "Audit Report"),
        ("other", "Other"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    esg_data = models.ForeignKey(
        ESGData,
        on_delete=models.CASCADE,
        related_name="evidence"
    )

    evidence_type = models.CharField(
        max_length=50,
        choices=EVIDENCE_TYPE_CHOICES,
        default="other"
    )

    file = models.FileField(
        upload_to="esg_evidence/%Y/%m/"
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="pending"
    )

    verified_by = models.CharField(
        max_length=150,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    rejection_reason = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.original_filename or self.file.name} - "
            f"{self.esg_data}"
        )

  


class ESGValidation(models.Model):

    SEVERITY_CHOICES = [
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("ignored", "Ignored"),
    ]

    esg_data = models.ForeignKey(
        ESGData,
        on_delete=models.CASCADE,
        related_name="validations"
    )

    rule_name = models.CharField(
        max_length=200
    )

    message = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.esg_data} - {self.rule_name}"



class ESGImportBatch(models.Model):

    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("completed_with_errors", "Completed with Errors"),
        ("failed", "Failed"),
    ]

    filename = models.CharField(
        max_length=255
    )

    financial_year = models.CharField(
        max_length=9
    )

    total_rows = models.PositiveIntegerField(
        default=0
    )

    imported_rows = models.PositiveIntegerField(
        default=0
    )

    skipped_rows = models.PositiveIntegerField(
        default=0
    )

    error_rows = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="uploaded"
    )

    uploaded_by = models.CharField(
        max_length=150,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.filename} - "
            f"{self.financial_year}"
        )



class ESGAnomaly(models.Model):

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("reviewed", "Reviewed"),
        ("ignored", "Ignored"),
    ]

    esg_data = models.ForeignKey(
        ESGData,
        on_delete=models.CASCADE,
        related_name="anomalies"
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    message = models.TextField()

    expected_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True
    )

    difference_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.esg_data} - "
            f"{self.severity} anomaly"
        )