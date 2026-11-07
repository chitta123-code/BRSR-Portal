from django.contrib import admin
from .models import Company, BusinessUnit, Project,Subsidiary


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cin",
        "reporting_boundary",
        "assurance_provider",
    )

    search_fields = (
        "name",
        "cin",
    )


@admin.register(Subsidiary)
class SubsidiaryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "cin", "created_at")
    search_fields = ("name", "company__name", "cin")


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "location",
        "head_name",
    )

    list_filter = (
        "company",
        "subsidiary",
    )

    search_fields = (
        "name",
        "company__name",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code",
        "name",
        "business_unit",
        "location",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "project_code",
        "name",
        "location",
    )