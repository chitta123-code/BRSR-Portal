from django.contrib import admin
from django.core.serializers import python
from .models import ESGMetric, ESGData,ESGValidation, ESGEvidence
from .models import ESGImportBatch


@admin.register(ESGMetric)
class ESGMetricAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "unit",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(ESGData)
class ESGDataAdmin(admin.ModelAdmin):

    list_display = (
        "business_unit",
        "financial_year",
        "metric",
        "value",
        "status",
        "created_at",
    )

    list_filter = (
        "financial_year",
        "metric__category",
        "status",
    )

    search_fields = (
        "business_unit__name",
        "metric__name",
        "data_source",
    )



@admin.register(ESGValidation)
class ESGValidationAdmin(admin.ModelAdmin):

    list_display = (
        "esg_data",
        "rule_name",
        "severity",
        "status",
        "created_at",
    )

    list_filter = (
        "severity",
        "status",
    )

    search_fields = (
        "rule_name",
        "message",
        "esg_data__metric__name",
        "esg_data__business_unit__name",
    )



@admin.register(ESGImportBatch)
class ESGImportBatchAdmin(admin.ModelAdmin):

    list_display = (
        "filename",
        "financial_year",
        "total_rows",
        "imported_rows",
        "skipped_rows",
        "error_rows",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "financial_year",
    )

    search_fields = (
        "filename",
        "uploaded_by",
    )

    readonly_fields = (
        "created_at",
        "completed_at",
    )



@admin.register(ESGEvidence)
class ESGEvidenceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "esg_data",
        "evidence_type",
        "verification_status",
        "verified_by",
        "uploaded_at",
    )

    list_filter = (
        "evidence_type",
        "verification_status",
    )

    search_fields = (
        "original_filename",
        "esg_data__metric__name",
        "verified_by",
    )

    readonly_fields = (
        "uploaded_at",
        "verified_at",
    )

