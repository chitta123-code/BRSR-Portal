
from django.db import models
from django.contrib.auth.models import User

from organization.models import Company, BusinessUnit, Project
from reporting.models import ReportingPeriod


class UploadedESGFile(models.Model):

    FILE_TYPE_CHOICES = [
        ("EXCEL", "Excel"),
        ("CSV", "CSV"),
        ("PDF", "PDF"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("UPLOADED", "Uploaded"),
        ("PROCESSING", "Processing"),
        ("PROCESSED", "Processed"),
        ("VALIDATION_ERROR", "Validation Error"),
        ("IMPORTED", "Imported"),
        ("FAILED", "Failed"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="uploaded_esg_files"
    )

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_esg_files"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_esg_files"
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_esg_files"
    )

    file = models.FileField(
        upload_to="esg_uploads/%Y/%m/"
    )

    original_filename = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default="OTHER"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="UPLOADED"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_esg_files"
    )

    extracted_rows = models.PositiveIntegerField(
        default=0
    )

    validation_errors = models.PositiveIntegerField(
        default=0
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.original_filename



class ImportedESGRecord(models.Model):
    uploaded_file = models.ForeignKey(
        UploadedESGFile,
        on_delete=models.CASCADE,
        related_name="imported_records"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="imported_esg_records"
    )

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_esg_records"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_esg_records"
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_esg_records"
    )

    row_number = models.PositiveIntegerField()

    original_metric = models.CharField(max_length=255)

    standard_metric = models.CharField(max_length=100)

    value = models.FloatField()

    unit = models.CharField(
        max_length=100,
        blank=True
    )

    confidence = models.FloatField(default=0)

    match_type = models.CharField(
        max_length=30,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.standard_metric} - "
            f"{self.value} {self.unit}"
        )