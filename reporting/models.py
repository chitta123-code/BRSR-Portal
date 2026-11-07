from django.db import models
from django.contrib.auth.models import User
from organization.models import Company, BusinessUnit, Project


class ReportingPeriod(models.Model):
    financial_year = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.financial_year


class BRSRSubmission(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("UNDER_REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("RESUBMITTED", "Resubmitted"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="brsr_submissions"
    )

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="brsr_submissions"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="brsr_submissions"
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        on_delete=models.CASCADE,
        related_name="brsr_submissions"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_brsr_submissions"
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.reporting_period.financial_year}"