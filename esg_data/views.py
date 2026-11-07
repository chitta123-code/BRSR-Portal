from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import ESGDataForm, ESGFileUploadForm, ESGEvidenceForm
from .services.evidence_matcher import match_evidence_to_esg
from .services.smart_validation import validate_esg_record
from django.contrib.auth.decorators import login_required, user_passes_test

from audit_trail.utils import record_audit

from .models import (
    ESGValidation,
    ESGData,
    ESGAnomaly,
    ESGEvidence,
)

from .services.excel_processor import read_esg_file
from .services.column_mapper import detect_columns
from .services.database_matcher import match_all_rows
from .services.import_service import import_esg_data

from .anomaly_detector import detect_anomaly

from .services.consolidation_service import (
    get_company_consolidation,
)




# ============================================================
# ESG MANUAL DATA ENTRY
# ============================================================

def esg_data_entry(request):

    if request.method == "POST":

        form = ESGDataForm(request.POST)

        if form.is_valid():

            esg_data = form.save()

            errors = ESGValidation.objects.filter(
                esg_data=esg_data,
                status="open",
                severity__in=["error", "critical"]
            )

            warnings = ESGValidation.objects.filter(
                esg_data=esg_data,
                status="open",
                severity="warning"
            )

            if errors.exists():

                messages.error(
                    request,
                    "ESG data contains validation errors. Please correct the data."
                )

            elif warnings.exists():

                messages.warning(
                    request,
                    "ESG data saved with warnings. Please review the warnings."
                )

            else:

                messages.success(
                    request,
                    "ESG data saved successfully."
                )

            return redirect("esg_data_entry")

    else:

        form = ESGDataForm()

    return render(
        request,
        "esg_data/data_entry.html",
        {
            "form": form,
        }
    )


# ============================================================
# ESG FILE UPLOAD
# ============================================================

def esg_file_upload(request):

    context = {
        "form": ESGFileUploadForm()
    }

    if request.method == "POST":

        form = ESGFileUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            uploaded_file = request.FILES.get("file")

            company = form.cleaned_data["company"]

            business_unit = form.cleaned_data["business_unit"]

            project = form.cleaned_data["project"]

            financial_year = form.cleaned_data["financial_year"]

            # ------------------------------------------------
            # READ FILE
            # ------------------------------------------------

            df, error = read_esg_file(
                uploaded_file
            )

            if error:

                context["form"] = form

                context["error"] = error

                return render(
                    request,
                    "esg_data/file_upload.html",
                    context
                )

            # ------------------------------------------------
            # DETECT COLUMNS
            # ------------------------------------------------

            detected_columns = detect_columns(
                df.columns
            )

            # ------------------------------------------------
            # DATABASE MATCHING
            # ------------------------------------------------

            match_results = match_all_rows(
                df
            )

            total_rows = len(match_results)

            # ------------------------------------------------
            # MATCHING SUMMARY
            # ------------------------------------------------

            ready_count = sum(
                1
                for result in match_results
                if result.get("business_unit_matched")
                and result.get("metric_matched")
            )

            review_count = total_rows - ready_count

            # ------------------------------------------------
            # IMPORT ACTION
            # ------------------------------------------------

            action = request.POST.get(
                "action"
            )

            print(
                "IMPORT ACTION =",
                action
            )

            if action == "import":

                result = import_esg_data(
                    df=df,
                    column_mapping=detected_columns,
                    match_results=match_results,
                    financial_year=financial_year,
                    filename=uploaded_file.name,
                    company=company,
                    business_unit=business_unit,
                    project=project,
                    uploaded_file=uploaded_file,
                    uploaded_by=(
                        request.user
                        if request.user.is_authenticated
                        else None
                    ),
                )

                context = {

                    "form":
                        ESGFileUploadForm(),

                    "import_complete":
                        True,

                    "imported_count":
                        result["imported_count"],

                    "skipped_count":
                        result["skipped_count"],

                    "error_count":
                        result["error_count"],

                    "batch_id":
                        result["batch"].id,

                    "batch_status":
                        result["batch"].status,
                }

                return render(
                    request,
                    "esg_data/file_upload.html",
                    context
                )

            # ------------------------------------------------
            # PREVIEW
            # ------------------------------------------------

            preview_data = (
                df.head(20)
                .fillna("")
                .to_dict(
                    orient="records"
                )
            )

            context = {

                "form":
                    form,

                "filename":
                    uploaded_file.name,

                "columns":
                    list(df.columns),

                "detected_columns":
                    detected_columns,

                "match_results":
                    match_results,

                "preview_data":
                    preview_data,

                "total_rows":
                    total_rows,

                "ready_count":
                    ready_count,

                "review_count":
                    review_count,

                "financial_year":
                    financial_year,

                "validation_summary":
                    True,

                "success":
                    True,
            }

            return render(
                request,
                "esg_data/file_upload.html",
                context
            )

    return render(
        request,
        "esg_data/file_upload.html",
        context
    )


# ============================================================
# DRAFT ESG DATA
# ============================================================

def draft_esg_data(request):

    draft_data = ESGData.objects.filter(
        status="draft"
    ).select_related(
        "business_unit",
        "metric"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "esg_data/draft_data.html",
        {
            "draft_data": draft_data,
        }
    )


# ============================================================
# SUBMIT ESG DATA FOR REVIEW
# ============================================================

def submit_esg_for_review(request, data_id):

    if request.method != "POST":

        return redirect(
            "esg_data_entry"
        )

    esg_data = get_object_or_404(
        ESGData,
        id=data_id
    )

    # Only draft or rejected records can be submitted

    if esg_data.status not in [
        "draft",
        "rejected"
    ]:

        messages.warning(
            request,
            "This ESG record cannot be submitted in its current status."
        )

        return redirect(
            "esg_review_dashboard"
        )

    esg_data.status = "submitted"

    if request.user.is_authenticated:

        esg_data.entered_by = (
            request.user.username
        )

    esg_data.save()

    messages.success(
        request,
        "ESG data submitted for manager review."
    )

    return redirect(
        "esg_review_dashboard"
    )


# ============================================================
# ESG REVIEW DASHBOARD
# ============================================================

def esg_review_dashboard(request):

    submitted_data = ESGData.objects.filter(
        status__in=[
            "submitted",
            "under_review"
        ]
    ).select_related(
        "business_unit",
        "metric"
    ).order_by(
        "-created_at"
    )

    context = {

        "submitted_data":
            submitted_data,

        "draft_count":
            ESGData.objects.filter(
                status="draft"
            ).count(),

        "submitted_count":
            ESGData.objects.filter(
                status="submitted"
            ).count(),

        "under_review_count":
            ESGData.objects.filter(
                status="under_review"
            ).count(),

        "approved_count":
            ESGData.objects.filter(
                status="approved"
            ).count(),

        "rejected_count":
            ESGData.objects.filter(
                status="rejected"
            ).count(),
    }

    return render(
        request,
        "esg_data/review_dashboard.html",
        context
    )


# ============================================================
# REVIEW INDIVIDUAL ESG DATA
# ============================================================

def review_esg_data(request, data_id):

    esg_data = get_object_or_404(
        ESGData.objects.select_related(
            "business_unit",
            "metric"
        ),
        id=data_id
    )

    validations = esg_data.validations.filter(
        status="open"
    )

    blocking_issues = validations.filter(
        severity__in=[
            "error",
            "critical"
        ]
    )

    # ========================================================
    # POST ACTION
    # ========================================================

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        # ----------------------------------------------------
        # MOVE TO UNDER REVIEW
        # ----------------------------------------------------

        if action == "review":

            if esg_data.status != "submitted":

                messages.warning(
                    request,
                    "Only submitted ESG data can be moved to review."
                )

            else:

                esg_data.status = "under_review"

                esg_data.save()

                record_audit(
                    request=request,
                    action="REVIEW",
                    instance=esg_data,
                    description="ESG data moved to under review by reviewer.",
                    changes={
                        "status": {
                            "before": "submitted",
                            "after": "under_review",
                        }
                    },
                )

                messages.info(
                    request,
                    "ESG data moved to Under Review."
                )

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        elif action == "approve":

            if esg_data.status != "under_review":

                messages.warning(
                    request,
                    "Only ESG data under review can be approved."
                )

            elif blocking_issues.exists():

                messages.error(
                    request,
                    "Approval blocked. This ESG record has unresolved Error or Critical validation issues."
                )

            else:

                # --------------------------------------------
                # APPROVE ESG DATA
                # --------------------------------------------

                esg_data.status = "approved"

                esg_data.save()

                record_audit(
                    request=request,
                    action="APPROVE",
                    instance=esg_data,
                    description="ESG data approved by reviewer.",
                    changes={
                        "status": {
                            "before": "under_review",
                            "after": "approved",
                        }
                    },
                )

                
                # --------------------------------------------
                # RUN ANOMALY DETECTION
                # --------------------------------------------

                anomaly = detect_anomaly(
                    esg_data
                )

                # --------------------------------------------
                # DISPLAY RESULT
                # --------------------------------------------

                if anomaly:

                    messages.warning(
                        request,
                        (
                            "ESG data approved, but an anomaly "
                            "was detected: "
                            f"{anomaly.message}"
                        )
                    )

                else:

                    messages.success(
                        request,
                        (
                            "ESG data approved successfully. "
                            "No anomaly detected."
                        )
                    )

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        elif action == "reject":

            if esg_data.status != "under_review":

                messages.warning(
                    request,
                    "Only ESG data under review can be rejected."
                )

            else:

                esg_data.status = "rejected"

                esg_data.save()

                record_audit(
                    request=request,
                    action="REJECT",
                    instance=esg_data,
                    description="ESG data rejected by reviewer.",
                    changes={
                        "status": {
                            "before": "under_review",
                            "after": "rejected",
                        }
                    },
                )

                messages.warning(
                    request,
                    "ESG data rejected."
                )

        # ----------------------------------------------------
        # REDIRECT
        # ----------------------------------------------------

        return redirect(
            "esg_review_dashboard"
        )

    # ========================================================
    # REVIEW PAGE
    # ========================================================

    return render(
        request,
        "esg_data/review_detail.html",
        {
            "esg_data": esg_data,
            "validations": validations,
            "blocking_issues": blocking_issues,
        }
    )


# ============================================================
# RESOLVE VALIDATION
# ============================================================

def resolve_validation(request, validation_id):

    if request.method != "POST":

        return redirect(
            "esg_review_dashboard"
        )

    validation = get_object_or_404(
        ESGValidation,
        id=validation_id
    )

    validation.status = "resolved"

    validation.resolved_at = (
        timezone.now()
    )

    validation.save(
        update_fields=[
            "status",
            "resolved_at",
        ]
    )

    messages.success(
        request,
        "Validation issue marked as resolved."
    )

    return redirect(
        "review_esg_data",
        data_id=validation.esg_data.id
    )


# ============================================================
# IGNORE VALIDATION
# ============================================================

def ignore_validation(request, validation_id):

    if request.method != "POST":

        return redirect(
            "esg_review_dashboard"
        )

    validation = get_object_or_404(
        ESGValidation,
        id=validation_id
    )

    validation.status = "ignored"

    validation.resolved_at = (
        timezone.now()
    )

    validation.save(
        update_fields=[
            "status",
            "resolved_at",
        ]
    )

    messages.warning(
        request,
        "Validation issue has been ignored."
    )

    return redirect(
        "review_esg_data",
        data_id=validation.esg_data.id
    )


# ============================================================
# ESG DASHBOARD
# ============================================================

def esg_dashboard(request):

    # ========================================================
    # FILTER VALUES
    # ========================================================

    selected_year = request.GET.get(
        "year",
        ""
    )

    selected_category = request.GET.get(
        "category",
        ""
    )

    selected_business_unit = request.GET.get(
        "business_unit",
        ""
    )

    # ========================================================
    # BASE QUERYSET
    # Only approved ESG records are shown
    # ========================================================

    queryset = ESGData.objects.filter(
        status="approved",
        metric__isnull=False
    )

    # ========================================================
    # APPLY YEAR FILTER
    # ========================================================

    if selected_year:

        queryset = queryset.filter(
            financial_year=selected_year
        )

    # ========================================================
    # APPLY CATEGORY FILTER
    # ========================================================

    if selected_category:

        queryset = queryset.filter(
            metric__category=selected_category
        )

    # ========================================================
    # APPLY BUSINESS UNIT FILTER
    # ========================================================

    if selected_business_unit:

        queryset = queryset.filter(
            business_unit_id=selected_business_unit
        )

    # ========================================================
    # STATUS COUNTS
    # ========================================================

    total_data = ESGData.objects.count()

    draft_count = ESGData.objects.filter(
        status="draft"
    ).count()

    submitted_count = ESGData.objects.filter(
        status="submitted"
    ).count()

    under_review_count = ESGData.objects.filter(
        status="under_review"
    ).count()

    approved_count = ESGData.objects.filter(
        status="approved"
    ).count()

    rejected_count = ESGData.objects.filter(
        status="rejected"
    ).count()

    # ========================================================
    # FILTERED KPI VALUES
    # ========================================================

    filtered_count = queryset.count()

    total_value = queryset.aggregate(
        total=Sum("value")
    )["total"] or 0

    average_value = queryset.aggregate(
        average=Avg("value")
    )["average"] or 0

    # ========================================================
    # CATEGORY DATA
    # ========================================================

    category_data = list(

        queryset
        .values(
            "metric__category"
        )
        .annotate(
            total=Count("id"),
            average_value=Avg("value"),
        )
        .order_by(
            "metric__category"
        )

    )

    # ========================================================
    # BUSINESS UNIT DATA
    # ========================================================

    business_unit_data = list(

        queryset
        .values(
            "business_unit__name"
        )
        .annotate(
            total=Count("id"),
            average_value=Avg("value"),
        )
        .order_by(
            "business_unit__name"
        )

    )

    # ========================================================
    # FINANCIAL YEARS
    # ========================================================

    years = list(

        ESGData.objects
        .values_list(
            "financial_year",
            flat=True
        )
        .distinct()
        .order_by(
            "-financial_year"
        )

    )

    # ========================================================
    # BUSINESS UNITS
    # ========================================================

    business_units = list(

        ESGData.objects
        .values(
            "business_unit__id",
            "business_unit__name"
        )
        .distinct()
        .order_by(
            "business_unit__name"
        )

    )

    # ========================================================
    # ESG CATEGORIES
    # ========================================================

    categories = [

        (
            "environmental",
            "Environmental"
        ),

        (
            "social",
            "Social"
        ),

        (
            "governance",
            "Governance"
        ),

    ]

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        # Status counts

        "total_data":
            total_data,

        "draft_count":
            draft_count,

        "submitted_count":
            submitted_count,

        "under_review_count":
            under_review_count,

        "approved_count":
            approved_count,

        "rejected_count":
            rejected_count,

        # Filtered KPI

        "filtered_count":
            filtered_count,

        "total_value":
            total_value,

        "average_value":
            average_value,

        # Chart data

        "category_data":
            category_data,

        "business_unit_data":
            business_unit_data,

        # Filter options

        "years":
            years,

        "business_units":
            business_units,

        "categories":
            categories,

        # Selected filters

        "selected_year":
            selected_year,

        "selected_category":
            selected_category,

        "selected_business_unit":
            selected_business_unit,
    }

    # ========================================================
    # RENDER DASHBOARD
    # ========================================================

    return render(
        request,
        "esg_data/dashboard.html",
        context
    )


# ============================================================
# ESG ANOMALY DASHBOARD
# ============================================================

def esg_anomaly_dashboard(request):

    # --------------------------------------------------------
    # Get all open anomalies
    # --------------------------------------------------------

    anomalies = ESGAnomaly.objects.filter(
        status="open"
    ).select_related(
        "esg_data",
        "esg_data__business_unit",
        "esg_data__metric"
    ).order_by(
        "-score",
        "-created_at"
    )

    # --------------------------------------------------------
    # Severity counts
    # --------------------------------------------------------

    critical_count = anomalies.filter(
        severity="critical"
    ).count()

    high_count = anomalies.filter(
        severity="high"
    ).count()

    medium_count = anomalies.filter(
        severity="medium"
    ).count()

    low_count = anomalies.filter(
        severity="low"
    ).count()

    # --------------------------------------------------------
    # Total anomalies
    # --------------------------------------------------------

    total_anomalies = anomalies.count()

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    context = {

        "anomalies":
            anomalies,

        "total_anomalies":
            total_anomalies,

        "critical_count":
            critical_count,

        "high_count":
            high_count,

        "medium_count":
            medium_count,

        "low_count":
            low_count,
    }

    return render(
        request,
        "esg_data/anomaly_dashboard.html",
        context
    )


# ============================================================
# RUN ANOMALY SCAN
# ============================================================

def run_anomaly_scan(request):

    if request.method != "POST":

        return redirect(
            "esg_anomaly_dashboard"
        )

    # --------------------------------------------------------
    # Get approved ESG records
    # --------------------------------------------------------

    approved_data = ESGData.objects.filter(
        status="approved",
        metric__isnull=False,
        value__isnull=False
    )

    scanned_count = 0

    anomaly_count = 0

    # --------------------------------------------------------
    # Scan each record
    # --------------------------------------------------------

    for esg_data in approved_data:

        scanned_count += 1

        anomaly = detect_anomaly(
            esg_data
        )

        if anomaly:

            anomaly_count += 1

    # --------------------------------------------------------
    # Result message
    # --------------------------------------------------------

    if anomaly_count > 0:

        messages.warning(
            request,
            (
                f"Anomaly scan completed. "
                f"{scanned_count} ESG records scanned and "
                f"{anomaly_count} anomalies detected."
            )
        )

    else:

        messages.success(
            request,
            (
                f"Anomaly scan completed. "
                f"{scanned_count} ESG records scanned. "
                "No new anomalies detected."
            )
        )

    return redirect(
        "esg_anomaly_dashboard"
    )


# ============================================================
# REVIEW ANOMALY
# ============================================================

def review_anomaly(request, anomaly_id):

    if request.method != "POST":

        return redirect(
            "esg_anomaly_dashboard"
        )

    anomaly = get_object_or_404(
        ESGAnomaly,
        id=anomaly_id
    )

    action = request.POST.get(
        "action"
    )

    # --------------------------------------------------------
    # Mark as reviewed
    # --------------------------------------------------------

    if action == "review":

        anomaly.status = "reviewed"

        anomaly.reviewed_at = timezone.now()

        anomaly.save(
            update_fields=[
                "status",
                "reviewed_at",
            ]
        )

        messages.success(
            request,
            "Anomaly marked as reviewed."
        )

    # --------------------------------------------------------
    # Ignore anomaly
    # --------------------------------------------------------

    elif action == "ignore":

        anomaly.status = "ignored"

        anomaly.reviewed_at = timezone.now()

        anomaly.save(
            update_fields=[
                "status",
                "reviewed_at",
            ]
        )

        messages.warning(
            request,
            "Anomaly has been ignored."
        )

    return redirect(
        "esg_anomaly_dashboard"
    )


# ============================================================
# ESG CONSOLIDATION
# ============================================================

def esg_consolidation(request):

    from organization.models import Company

    companies = Company.objects.all().order_by(
        "name"
    )

    company_id = request.GET.get(
        "company"
    )

    financial_year = request.GET.get(
        "financial_year"
    )

    selected_company = None

    consolidation_data = []

    environmental_count = 0

    social_count = 0

    governance_count = 0

    if company_id:

        selected_company = get_object_or_404(
            Company,
            id=company_id
        )

        consolidation_data = get_company_consolidation(
            selected_company,
            financial_year
        )

        for item in consolidation_data:

            category = item[
                "metric__category"
            ]

            if category == "environmental":

                environmental_count += 1

            elif category == "social":

                social_count += 1

            elif category == "governance":

                governance_count += 1

    financial_years = (
        ESGData.objects
        .filter(
            status="approved"
        )
        .values_list(
            "financial_year",
            flat=True
        )
        .distinct()
        .order_by(
            "-financial_year"
        )
    )

    context = {

        "companies":
            companies,

        "financial_years":
            financial_years,

        "selected_company":
            selected_company,

        "selected_company_id":
            company_id,

        "selected_financial_year":
            financial_year,

        "consolidation_data":
            consolidation_data,

        "environmental_count":
            environmental_count,

        "social_count":
            social_count,

        "governance_count":
            governance_count,
    }

    return render(
        request,
        "esg_data/consolidation.html",
        context
    )




# ============================================================
# EVIDENCE ACCESS PERMISSIONS
# ============================================================

def is_reviewer(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Reviewer").exists()
        )
    )


def is_data_entry(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Data Entry").exists()
        )
    )


# ============================================================
# EVIDENCE VERIFICATION DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_reviewer)
def evidence_verification(request):
    evidence = ESGEvidence.objects.select_related(
        "esg_data",
        "esg_data__metric",
        "esg_data__business_unit",
        "esg_data__project",
    ).order_by("-uploaded_at")

    context = {
        "evidence": evidence,
        "total_count": evidence.count(),
        "pending_count": evidence.filter(
            verification_status="pending"
        ).count(),
        "verified_count": evidence.filter(
            verification_status="verified"
        ).count(),
        "rejected_count": evidence.filter(
            verification_status="rejected"
        ).count(),
    }

    return render(
        request,
        "esg_data/evidence_verification.html",
        context,
    )


# ============================================================
# VERIFY OR REJECT EVIDENCE
# ============================================================

@login_required
@user_passes_test(is_reviewer)
def verify_evidence(request, evidence_id):
    if request.method != "POST":
        messages.error(
            request,
            "Evidence can only be verified or rejected using POST.",
        )
        return redirect("evidence_verification")

    evidence = get_object_or_404(
        ESGEvidence,
        id=evidence_id,
    )

    action = request.POST.get("action", "").strip()

    if action == "verify":
        evidence.verification_status = "verified"
        evidence.verified_by = request.user.username
        evidence.verified_at = timezone.now()
        evidence.rejection_reason = ""

        evidence.save(
            update_fields=[
                "verification_status",
                "verified_by",
                "verified_at",
                "rejection_reason",
            ]
        )

        messages.success(
            request,
            "ESG evidence verified successfully.",
        )

    elif action == "reject":
        rejection_reason = request.POST.get(
            "rejection_reason", ""
        ).strip()

        if not rejection_reason:
            messages.error(
                request,
                "A rejection reason is required.",
            )
            return redirect("evidence_verification")

        evidence.verification_status = "rejected"
        evidence.verified_by = request.user.username
        evidence.verified_at = timezone.now()
        evidence.rejection_reason = rejection_reason

        evidence.save(
            update_fields=[
                "verification_status",
                "verified_by",
                "verified_at",
                "rejection_reason",
            ]
        )

        messages.warning(
            request,
            "ESG evidence rejected.",
        )

    else:
        messages.error(
            request,
            "Invalid evidence verification action.",
        )

    return redirect("evidence_verification")


# ============================================================
# UPLOAD EVIDENCE FOR AN ESG DATA RECORD
# ============================================================

@login_required
@user_passes_test(is_data_entry)
def evidence_upload(request, data_id):
    esg_data = get_object_or_404(
        ESGData.objects.select_related(
            "business_unit",
            "metric",
            "project",
        ),
        id=data_id,
    )

    if request.method == "POST":
        form = ESGEvidenceForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.esg_data = esg_data
            evidence.verification_status = "pending"

            uploaded_file = form.cleaned_data.get("file")
            if uploaded_file:
                evidence.original_filename = uploaded_file.name

            evidence.save()

            record_audit(
                request=request,
                action="UPLOAD_EVIDENCE",
                instance=evidence,
                description=(
                    f"Evidence uploaded for ESG record {esg_data.id}."
                ),
                changes={
                    "verification_status": {
                        "before": None,
                        "after": "pending",
                    }
                },
            )

            messages.success(
                request,
                "Evidence uploaded successfully and is awaiting verification.",
            )
            return redirect("evidence_verification")

    else:
        form = ESGEvidenceForm()

    return render(
        request,
        "esg_data/evidence_upload.html",
        {
            "form": form,
            "esg_data": esg_data,
        },
    )


# ============================================================
# MATCH EVIDENCE WITH ESG DATA
# ============================================================

@login_required
@user_passes_test(is_reviewer)
def match_evidence(request, evidence_id):
    evidence = get_object_or_404(
        ESGEvidence.objects.select_related(
            "esg_data",
            "esg_data__metric",
            "esg_data__business_unit",
            "esg_data__project",
        ),
        id=evidence_id,
    )

    result = match_evidence_to_esg(evidence)

    return render(
        request,
        "esg_data/evidence_match_result.html",
        {
            "evidence": evidence,
            "result": result,
        },
    )






def smart_validation_dashboard(request):
    records = ESGData.objects.select_related(
        "metric",
        "business_unit",
        "project",
    ).prefetch_related(
        "validations"
    ).order_by("-id")

    results = []
    total_issues = 0
    error_count = 0
    warning_count = 0

    for record in records:
        issues = list(
            record.validations.filter(
                status="open"
            ).values(
                "rule_name",
                "message",
                "severity",
            )
        )

        results.append({
            "record": record,
            "issues": issues,
            "status": (
                "ERROR"
                if any(
                    issue["severity"] in ["error", "critical"]
                    for issue in issues
                )
                else "WARNING"
                if issues
                else "VALID"
            ),
        })

        total_issues += len(issues)
        error_count += sum(
            1 for issue in issues
            if issue["severity"] in ["error", "critical"]
        )
        warning_count += sum(
            1 for issue in issues
            if issue["severity"] == "warning"
        )

    context = {
        "results": results,
        "record_count": len(results),
        "total_issues": total_issues,
        "error_count": error_count,
        "warning_count": warning_count,
    }

    return render(
        request,
        "esg_data/smart_validation_dashboard.html",
        context,
    )
       