from django.contrib import admin
from .models import ( EntityDetails,
                     BusinessActivity, 
                     ProductService,
                     OperationLocation,
                     EmployeeWorkerCount,
                     WomenRepresentation,
                     DifferentlyAbledEmployeeWorker, 
                     CompanyRelationship,
                     CSRDetails,
                     GrievanceDisclosure,
                     MaterialResponsibleIssue,
                     PolicyProcess,
                     GovernanceOversight,
                     NGRBCReview,
                     PolicyCoverageReason,
                     ExternalPolicyAssessment,
                     PrinciplePerformance,)


@admin.register(EntityDetails)
class EntityDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "financial_year",
        "reporting_boundary",
        "assurance_provider",
        "assurance_type",
    )

    list_filter = (
        "financial_year",
        "reporting_boundary",
    )

    search_fields = (
        "company__name",
        "financial_year",
        "brsr_contact_name",
    )


@admin.register(BusinessActivity)
class BusinessActivityAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "activity_description",
        "turnover_percentage",
    )

    search_fields = (
        "company__name",
        "activity_description",
    )


@admin.register(ProductService)
class ProductServiceAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "product_service_name",
        "nic_code",
        "turnover_percentage",
    )

    search_fields = (
        "company__name",
        "product_service_name",
        "nic_code",
    )


@admin.register(OperationLocation)
class OperationLocationAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "location_name",
        "location_type",
    )

    list_filter = (
        "location_type",
    )

    search_fields = (
        "company__name",
        "location_name",
    )


@admin.register(EmployeeWorkerCount)
class EmployeeWorkerCountAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "financial_year",
        "category",
        "employment_type",
        "gender",
        "total",
    )

    list_filter = (
        "financial_year",
        "category",
        "employment_type",
        "gender",
    )

    search_fields = (
        "company__name",
    )


@admin.register(WomenRepresentation)
class WomenRepresentationAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "financial_year",
        "category",
        "total",
        "female_count",
        "female_percentage",
    )

    list_filter = (
        "financial_year",
        "category",
    )


@admin.register(DifferentlyAbledEmployeeWorker)
class DifferentlyAbledEmployeeWorkerAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "financial_year",
        "category",
        "employment_type",
        "gender",
        "total",
    )

    list_filter = (
        "financial_year",
        "category",
        "employment_type",
        "gender",
    )

    search_fields = (
        "company__name",
    )


@admin.register(CompanyRelationship)
class CompanyRelationshipAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "related_company_name",
        "relationship_type",
        "percentage_of_shares_held",
        "included_in_consolidation",
    )

    list_filter = (
        "relationship_type",
        "included_in_consolidation",
    )

    search_fields = (
        "company__name",
        "related_company_name",
    )



@admin.register(CSRDetails)
class CSRDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "financial_year",
        "csr_applicable",
        "csr_amount_required",
        "csr_amount_spent",
        "amount_unspent",
    )

    list_filter = (
        "financial_year",
        "csr_applicable",
    )

    search_fields = (
        "company__name",
        "financial_year",
    )



@admin.register(GrievanceDisclosure)
class GrievanceDisclosureAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "stakeholder_group",
        "grievance_mechanism_in_place",
        "current_complaints_filed",
        "current_complaints_pending",
    )

    list_filter = (
        "financial_year",
        "stakeholder_group",
        "grievance_mechanism_in_place",
    )

    search_fields = (
        "company__name",
        "stakeholder_group",
    )


@admin.register(MaterialResponsibleIssue)
class MaterialResponsibleIssueAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "material_issue",
        "category",
        "issue_type",
    )

    list_filter = (
        "financial_year",
        "category",
        "issue_type",
    )

    search_fields = (
        "company__name",
        "material_issue",
    )



@admin.register(PolicyProcess)
class PolicyProcessAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "principle",
        "policy_covers_principle",
        "board_approved",
        "translated_into_procedures",
        "extends_to_value_chain",
    )

    list_filter = (
        "financial_year",
        "policy_covers_principle",
        "board_approved",
        "translated_into_procedures",
        "extends_to_value_chain",
    )

    search_fields = (
        "company__name",
        "principle__name",
    )


@admin.register(GovernanceOversight)
class GovernanceOversightAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "highest_authority",
        "sustainability_committee_exists",
        "external_agency_assessment",
    )

    list_filter = (
        "financial_year",
        "sustainability_committee_exists",
        "external_agency_assessment",
    )

    search_fields = (
        "company__name",
        "highest_authority",
        "external_agency_name",
    )


@admin.register(NGRBCReview)
class NGRBCReviewAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "principle",
        "review_subject",
        "reviewer",
        "frequency",
    )

    list_filter = (
        "financial_year",
        "review_subject",
        "reviewer",
        "frequency",
    )

    search_fields = (
        "company__name",
        "principle__name",
    )


@admin.register(PolicyCoverageReason)
class PolicyCoverageReasonAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "principle",
        "not_material",
        "not_ready_to_implement",
        "insufficient_resources",
        "planned_next_financial_year",
    )

    list_filter = (
        "financial_year",
        "not_material",
        "not_ready_to_implement",
        "insufficient_resources",
        "planned_next_financial_year",
    )

    search_fields = (
        "company__name",
        "principle__name",
    )



@admin.register(ExternalPolicyAssessment)
class ExternalPolicyAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "principle",
        "assessment_done",
        "agency_name",
    )

    list_filter = (
        "financial_year",
        "assessment_done",
        "principle",
    )

    search_fields = (
        "company__name",
        "principle__name",
        "agency_name",
    )


@admin.register(PrinciplePerformance)
class PrinciplePerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "financial_year",
        "principle",
    )

    list_filter = (
        "financial_year",
        "principle",
    )

    search_fields = (
        "company__name",
        "principle__name",
    )