from django.contrib import admin
from .models import ReportingPeriod, BRSRSubmission


@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "financial_year",
        "start_date",
        "end_date",
        "status",
    )

    list_filter = (
        "status",
    )


@admin.register(BRSRSubmission)
class BRSRSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "reporting_period",
        "status",
        "completion_percentage",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "reporting_period",
    )

    search_fields = (
        "company__name",
    )