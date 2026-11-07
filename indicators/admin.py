from django.contrib import admin
from .models import Principle, Indicator, IndicatorResponse
from .models import ESGIndicatorMapping


@admin.register(Principle)
class PrincipleAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "name",
    )

    ordering = (
        "number",
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "indicator_code",
        "principle",
        "indicator_type",
        "mandatory",
        "response_type",
    )

    list_filter = (
        "indicator_type",
        "mandatory",
        "principle",
    )

    search_fields = (
        "indicator_code",
        "question",
    )


@admin.register(IndicatorResponse)
class IndicatorResponseAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "indicator",
        "numeric_value",
        "unit",
        "is_valid",
        "updated_at",
    )

    list_filter = (
        "is_valid",
    )


@admin.register(ESGIndicatorMapping)
class ESGIndicatorMappingAdmin(admin.ModelAdmin):

    list_display = (
        "esg_metric",
        "indicator",
        "mapping_type",
        "is_active",
        "created_at",
    )

    list_filter = (
        "mapping_type",
        "is_active",
        "indicator__indicator_type",
    )

    search_fields = (
        "esg_metric__name",
        "indicator__indicator_code",
        "indicator__question",
    )

    autocomplete_fields = (
        "esg_metric",
        "indicator",
    )

    ordering = (
        "esg_metric__category",
        "esg_metric__name",
    )

