from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse
from decimal import Decimal, InvalidOperation
from datetime import date

from organization.models import Company, BusinessUnit, Project
from reporting.models import ReportingPeriod, BRSRSubmission
from indicators.models import Principle, Indicator, IndicatorResponse
from reporting.services.brsr_pdf_service import generate_brsr_pdf
from esg_data.models import ESGData, ESGEvidence


def is_reviewer(user):
    return (
        user.is_superuser
        or user.groups.filter(name="Reviewer").exists()
    )


def is_data_entry(user):
    return (
        user.is_superuser
        or user.groups.filter(name="Data Entry").exists()
    )


def validate_indicator_response(indicator, value):
    """
    Returns: (is_valid, cleaned_value, numeric_value, error_message)
    """

    value = (value or "").strip()

    # Blank answer
    if not value:
        if indicator.mandatory:
            return False, "", None, "This answer is required."

        return True, "", None, ""

    # TEXT
    if indicator.response_type == "TEXT":
        return True, value, None, ""

    # NUMBER and PERCENTAGE
    if indicator.response_type in ("NUMBER", "PERCENTAGE"):
        try:
            number = Decimal(value)
        except InvalidOperation:
            return False, value, None, "Enter a valid number."

        if not number.is_finite():
            return False, value, None, "Enter a finite number."

        if (
            indicator.response_type == "PERCENTAGE"
            and not Decimal("0") <= number <= Decimal("100")
        ):
            return (
                False,
                value,
                None,
                "Percentage must be between 0 and 100.",
            )

        return True, value, number, ""

    # BOOLEAN
    if indicator.response_type == "BOOLEAN":
        normalized = value.lower()

        if normalized in ("yes", "y", "true", "1"):
            return True, "Yes", None, ""

        if normalized in ("no", "n", "false", "0"):
            return True, "No", None, ""

        return False, value, None, "Enter Yes or No."

    # DATE
    if indicator.response_type == "DATE":
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            return (
                False,
                value,
                None,
                "Enter a valid date in YYYY-MM-DD format.",
            )

        return True, parsed_date.isoformat(), None, ""

    return False, value, None, "Unsupported response type."


@login_required
@user_passes_test(is_data_entry)
def brsr_entry(request):

    companies = Company.objects.all()
    periods = ReportingPeriod.objects.all()
    principles = Principle.objects.all()

    company_id = request.GET.get("company")
    business_unit_id = request.GET.get("business_unit")
    project_id = request.GET.get("project")
    period_id = request.GET.get("period")
    principle_id = request.GET.get("principle")

    selected_company = None
    selected_business_unit = None
    selected_project = None
    selected_period = None
    selected_principle = None

    indicators = []
    submission = None

    # =============================
    # GET COMPANY
    # =============================

    if company_id:
        selected_company = get_object_or_404(
            Company,
            id=company_id
        )

    # =============================
    # GET BUSINESS UNIT
    # =============================

    if business_unit_id and selected_company:
        selected_business_unit = get_object_or_404(
            BusinessUnit,
            id=business_unit_id,
            company=selected_company
        )

    # =============================
    # GET PROJECT
    # =============================

    if project_id and selected_business_unit:
        selected_project = get_object_or_404(
            Project,
            id=project_id,
            business_unit=selected_business_unit
        )

    # =============================
    # GET REPORTING PERIOD
    # =============================

    if period_id:
        selected_period = get_object_or_404(
            ReportingPeriod,
            id=period_id
        )

    # =============================
    # GET PRINCIPLE
    # =============================

    if principle_id:

        selected_principle = get_object_or_404(
            Principle,
            id=principle_id
        )

        indicators = list(
            Indicator.objects.filter(
                principle=selected_principle
            ).order_by("indicator_code")
        )

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        company_id = request.POST.get("company")
        business_unit_id = request.POST.get("business_unit")
        project_id = request.POST.get("project")
        period_id = request.POST.get("period")
        principle_id = request.POST.get("principle")

        action = request.POST.get("action")

        # -----------------------------
        # GET COMPANY
        # -----------------------------

        selected_company = get_object_or_404(
            Company,
            id=company_id
        )

        # -----------------------------
        # GET BUSINESS UNIT
        # -----------------------------

        selected_business_unit = None

        if business_unit_id:

            selected_business_unit = get_object_or_404(
                BusinessUnit,
                company=selected_company,
                id=business_unit_id
            )

        # -----------------------------
        # GET PROJECT
        # -----------------------------

        selected_project = None

        if project_id and selected_business_unit:

            selected_project = get_object_or_404(
                Project,
                business_unit=selected_business_unit,
                id=project_id
            )

        # -----------------------------
        # GET PERIOD
        # -----------------------------

        selected_period = get_object_or_404(
            ReportingPeriod,
            id=period_id
        )

        # -----------------------------
        # GET PRINCIPLE
        # -----------------------------

        selected_principle = get_object_or_404(
            Principle,
            id=principle_id
        )

        
        # =========================================
        # GET EXISTING SUBMISSION
        # =========================================

        submission = BRSRSubmission.objects.filter(
            company=selected_company,
            business_unit=selected_business_unit,
            project=selected_project,
            reporting_period=selected_period,
        ).first()

        # =========================================
        # PREVENT EDITING LOCKED SUBMISSIONS
        # =========================================

        if submission and submission.status in [
            "SUBMITTED",
            "UNDER_REVIEW",
            "APPROVED",
        ]:
            messages.warning(
                request,
                "This submission is locked and cannot be edited in its current status."
            )

            return redirect(
                f"/brsr-entry/?company={selected_company.id}"
                f"&business_unit={selected_business_unit.id if selected_business_unit else ''}"
                f"&project={selected_project.id if selected_project else ''}"
                f"&period={selected_period.id}"
                f"&principle={selected_principle.id}"
            )


        # =================================================
        # CREATE / GET PROJECT-SPECIFIC SUBMISSION
        # =================================================

        submission = BRSRSubmission.objects.get_or_create(
            company=selected_company,
            business_unit=selected_business_unit,
            project=selected_project,
            reporting_period=selected_period,
            defaults={
                "status": "DRAFT",
                "created_by": request.user,
            }
        )[0]

        # =================================================
        # GET INDICATORS
        # =================================================

        indicators = list(
            Indicator.objects.filter(
                principle=selected_principle
            ).order_by("indicator_code")
        )

        # =================================================
        # SAVE RESPONSES
        # =================================================

        validation_errors = []

        for indicator in indicators:
            response_text = request.POST.get(
                f"response_{indicator.id}", ""
            ).strip()

            is_valid, cleaned_value, numeric_value, error_message = (
                validate_indicator_response(indicator, response_text)
            )

            if not is_valid:
                validation_errors.append(
                    f"{indicator.indicator_code}: {error_message}"
                )

            IndicatorResponse.objects.update_or_create(
                indicator=indicator,
                submission=submission,
                defaults={
                    "response_text": cleaned_value,
                    "numeric_value": numeric_value,
                    "is_valid": is_valid,
                }
            )

        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)

            # Do not submit invalid responses.
            if action == "submit":
                return redirect(
                    f"/brsr-entry/?company={selected_company.id}"
                    f"&business_unit={selected_business_unit.id if selected_business_unit else ''}"
                    f"&project={selected_project.id if selected_project else ''}"
                    f"&period={selected_period.id}"
                    f"&principle={selected_principle.id}"
                )


        # =================================================
        # ACTION: SAVE
        # =================================================

        if action == "save":

            messages.success(
                request,
                "BRSR data saved successfully."
            )

        # =================================================
        # ACTION: SUBMIT
        # =================================================

        elif action == "submit":

            if submission.status in [
                "DRAFT",
                "REJECTED",
                "RESUBMITTED"
            ]:

                submission.status = "SUBMITTED"
                submission.submitted_at = timezone.now()
                submission.save()

                messages.success(
                    request,
                    "BRSR submission submitted successfully."
                )

            else:

                messages.warning(
                    request,
                    "This submission cannot be submitted in its current status."
                )

        # =================================================
        # REDIRECT
        # =================================================

        business_unit_param = (
            selected_business_unit.id
            if selected_business_unit is not None
            else ""
        )

        project_param = (
            selected_project.id
            if selected_project is not None
            else ""
        )

        return redirect(
            f"/brsr-entry/"
            f"?company={selected_company.id}"
            f"&business_unit={business_unit_param}"
            f"&project={project_param}"
            f"&period={selected_period.id}"
            f"&principle={selected_principle.id}"
        )

    # =====================================================
    # LOAD EXISTING SUBMISSION
    # =====================================================

    if (
        selected_company
        and selected_business_unit
        and selected_project
        and selected_period
    ):

        submission = BRSRSubmission.objects.filter(
            company=selected_company,
            business_unit=selected_business_unit,
            project=selected_project,
            reporting_period=selected_period
        ).first()

        if submission:

            for indicator in indicators:

                saved = IndicatorResponse.objects.filter(
                    indicator=indicator,
                    submission=submission
                ).first()

                if saved:
                    indicator.saved_response = saved.response_text
                else:
                    indicator.saved_response = ""

        else:

            for indicator in indicators:
                indicator.saved_response = ""

    # =====================================================
    # FILTER BUSINESS UNITS
    # =====================================================

    business_units = []

    if selected_company:

        business_units = BusinessUnit.objects.filter(
            company=selected_company
        )

    # =====================================================
    # FILTER PROJECTS
    # =====================================================

    projects = []

    if selected_business_unit:

        projects = Project.objects.filter(
            business_unit=selected_business_unit
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "companies": companies,
        "business_units": business_units,
        "projects": projects,
        "periods": periods,
        "principles": principles,

        "selected_company": selected_company,
        "selected_business_unit": selected_business_unit,
        "selected_project": selected_project,
        "selected_period": selected_period,
        "selected_principle": selected_principle,

        "indicators": indicators,

        "submission": submission,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "reporting/brsr_entry.html",
        context
    )


@login_required
@user_passes_test(is_reviewer)
def reviewer_dashboard(request):

    submissions = BRSRSubmission.objects.select_related(
        "company",
        "reporting_period",
        "created_by"
    ).order_by("-created_at")

    context = {
        "submissions": submissions,
    }

    return render(
        request,
        "reporting/reviewer_dashboard.html",
        context
    )


@login_required
@user_passes_test(is_reviewer)
def review_submission(request, submission_id):

    submission = get_object_or_404(
        BRSRSubmission,
        id=submission_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        # -----------------------------
        # START REVIEW
        # -----------------------------

        if action == "review":

            if submission.status in [
                "SUBMITTED",
                "RESUBMITTED"
            ]:

                submission.status = "UNDER_REVIEW"
                submission.save()

                messages.success(
                    request,
                    "Submission is now under review."
                )

            else:

                messages.warning(
                    request,
                    "This submission cannot be moved to review."
                )

        # -----------------------------
        # APPROVE
        # -----------------------------

        elif action == "approve":

            if submission.status == "UNDER_REVIEW":

                # =========================================
                # CHECK ESG EVIDENCE
                # =========================================

                evidence_queryset = ESGEvidence.objects.filter(
                    esg_data__project=submission.project,
                    esg_data__financial_year=(
                        submission.reporting_period.financial_year
                    )
                )

                # BLOCK APPROVAL IF NO EVIDENCE EXISTS
                if not evidence_queryset.exists():
                    messages.warning(
                        request,
                        "Approval blocked: no ESG evidence has been uploaded for this project and financial year."
                    )
                    return redirect("reviewer_dashboard")

                pending_evidence = evidence_queryset.filter(
                    verification_status="pending"
                ).exists()

                rejected_evidence = evidence_queryset.filter(
                    verification_status="rejected"
                ).exists()

                # =========================================
                # BLOCK APPROVAL IF EVIDENCE IS PENDING
                # =========================================

                if pending_evidence:

                    messages.warning(
                        request,
                        "Approval blocked: ESG evidence is still pending verification."
                    )

                    return redirect(
                        "reviewer_dashboard"
                    )

                # =========================================
                # BLOCK APPROVAL IF EVIDENCE IS REJECTED
                # =========================================

                if rejected_evidence:

                    messages.warning(
                        request,
                        "Approval blocked: rejected ESG evidence exists."
                    )

                    return redirect(
                        "reviewer_dashboard"
                    )

                # =========================================
                # APPROVE
                # =========================================

                submission.status = "APPROVED"
                submission.approved_at = timezone.now()

                submission.save()

                messages.success(
                    request,
                    "BRSR submission approved successfully."
                )

            else:

                messages.warning(
                    request,
                    "Only submissions under review can be approved."
                )

        # -----------------------------
        # REJECT
        # -----------------------------

        elif action == "reject":

            if submission.status == "UNDER_REVIEW":

                submission.status = "REJECTED"
                submission.save()

                messages.warning(
                    request,
                    "BRSR submission rejected."
                )

            else:

                messages.warning(
                    request,
                    "Only submissions under review can be rejected."
                )

        # -----------------------------
        # RESUBMIT
        # -----------------------------

        elif action == "resubmit":

            if submission.status == "REJECTED":

                submission.status = "RESUBMITTED"
                submission.save()

                messages.success(
                    request,
                    "Submission marked for resubmission."
                )

            else:

                messages.warning(
                    request,
                    "Only rejected submissions can be resubmitted."
                )

        return redirect(
            "reviewer_dashboard"
        )

    return redirect(
        "reviewer_dashboard"
    )


@login_required
@user_passes_test(is_reviewer)
def download_brsr_pdf(request, submission_id):

    submission = get_object_or_404(
        BRSRSubmission,
        id=submission_id
    )

    if submission.status != "APPROVED":

        messages.warning(
            request,
            "Only approved BRSR submissions can generate a PDF report."
        )

        return redirect(
            "reviewer_dashboard"
        )

    pdf_buffer = generate_brsr_pdf(
        submission
    )

    filename = (
        f"BRSR_{submission.company.name}_"
        f"{submission.reporting_period.financial_year}.pdf"
    )

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=filename
    )


@login_required
@user_passes_test(is_reviewer)
def evidence_verification(request):

    evidences = ESGEvidence.objects.select_related(
        "esg_data",
        "esg_data__metric",
        "esg_data__business_unit",
    ).order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "reporting/evidence_verification.html",
        {
            "evidences": evidences,
        }
    )


@login_required
@user_passes_test(is_reviewer)
def verify_evidence(request, evidence_id):

    evidence = get_object_or_404(
        ESGEvidence,
        id=evidence_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        # =========================================
        # VERIFY
        # =========================================

        if action == "verify":

            evidence.verification_status = "verified"

            evidence.verified_by = (
                request.user.username
            )

            evidence.verified_at = timezone.now()

            evidence.rejection_reason = ""

            evidence.save()

            messages.success(
                request,
                "Evidence verified successfully."
            )

        # =========================================
        # REJECT
        # =========================================

        elif action == "reject":

            evidence.verification_status = "rejected"

            evidence.verified_by = (
                request.user.username
            )

            evidence.verified_at = timezone.now()

            evidence.rejection_reason = request.POST.get(
                "rejection_reason",
                ""
            )

            evidence.save()

            messages.warning(
                request,
                "Evidence rejected."
            )

    return redirect(
        "evidence_verification"
    )




@login_required
@user_passes_test(lambda user: user.groups.filter(name="Manager").exists())
def manager_dashboard(request):


    submissions = BRSRSubmission.objects.select_related(
        "company",
        "business_unit",
        "project",
        "reporting_period",
    ).order_by("-created_at")

    context = {
        "submissions": submissions,
        "total_submissions": submissions.count(),
        "submitted_count": submissions.filter(
            status="SUBMITTED"
        ).count(),
        "under_review_count": submissions.filter(
            status="UNDER_REVIEW"
        ).count(),
        "approved_count": submissions.filter(
            status="APPROVED"
        ).count(),
        "rejected_count": submissions.filter(
            status="REJECTED"
        ).count(),
    }

    return render(
        request,
        "reporting/manager_dashboard.html",
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(name="Manager").exists())
def manager_review_submission(request, submission_id):

    submission = get_object_or_404(
        BRSRSubmission.objects.select_related(
            "company",
            "business_unit",
            "project",
            "reporting_period",
        ),
        id=submission_id,
    )

    # ========================================================
    # MANAGER ACTIONS
    # ========================================================

    if request.method == "POST":

        action = request.POST.get("action")

        # ----------------------------------------------------
        # START REVIEW
        # ----------------------------------------------------

        if action == "review":

            if submission.status in [
                "SUBMITTED",
                "RESUBMITTED",
            ]:

                submission.status = "UNDER_REVIEW"

                submission.save(
                    update_fields=["status"]
                )

                messages.success(
                    request,
                    "Submission is now under review."
                )

            else:

                messages.warning(
                    request,
                    "Only submitted or resubmitted submissions can be moved to review."
                )

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        elif action == "approve":

            if submission.status == "UNDER_REVIEW":

                evidence_queryset = ESGEvidence.objects.filter(
                    esg_data__project=submission.project,
                    esg_data__financial_year=(
                        submission.reporting_period.financial_year
                    ),
                )

                if not evidence_queryset.exists():
                    messages.warning(
                        request,
                        "Approval blocked: no ESG evidence has been uploaded for this project and financial year."
                    )

                elif evidence_queryset.filter(
                    verification_status="pending"
                ).exists():
                    messages.warning(
                        request,
                        "Approval blocked: ESG evidence is still pending verification."
                    )

                elif evidence_queryset.filter(
                    verification_status="rejected"
                ).exists():
                    messages.warning(
                        request,
                        "Approval blocked: rejected ESG evidence exists."
                    )

                else:
                    submission.status = "APPROVED"
                    submission.approved_at = timezone.now()

                    submission.save(
                        update_fields=[
                            "status",
                            "approved_at",
                        ]
                    )

                    messages.success(
                        request,
                        "BRSR submission approved successfully."
                    )

            else:

                messages.warning(
                    request,
                    "Only submissions under review can be approved."
                )

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        elif action == "reject":

            if submission.status == "UNDER_REVIEW":

                submission.status = "REJECTED"

                submission.save(
                    update_fields=["status"]
                )

                messages.warning(
                    request,
                    "BRSR submission rejected."
                )

            else:

                messages.warning(
                    request,
                    "Only submissions under review can be rejected."
                )

        # ----------------------------------------------------
        # RESUBMIT
        # ----------------------------------------------------

        elif action == "resubmit":

            if submission.status == "REJECTED":

                submission.status = "RESUBMITTED"

                submission.save(
                    update_fields=["status"]
                )

                messages.success(
                    request,
                    "Submission marked for resubmission."
                )

            else:

                messages.warning(
                    request,
                    "Only rejected submissions can be marked for resubmission."
                )

        return redirect(
            "manager_review_submission",
            submission_id=submission.id,
        )

    # ========================================================
    # ESG DATA
    # ========================================================

    esg_data = ESGData.objects.filter(
        project=submission.project,
        financial_year=submission.reporting_period.financial_year,
    ).select_related(
        "metric",
        "business_unit",
        "project",
    ).prefetch_related(
        "evidence"
    )

    # ========================================================
    # EVIDENCE
    # ========================================================

    evidence = ESGEvidence.objects.filter(
        esg_data__project=submission.project,
        esg_data__financial_year=submission.reporting_period.financial_year,
    ).select_related(
        "esg_data",
        "esg_data__metric",
    ).order_by(
        "-uploaded_at"
    )

    # ========================================================
    # EVIDENCE COUNTS
    # ========================================================

    evidence_total = evidence.count()

    evidence_verified = evidence.filter(
        verification_status="verified"
    ).count()

    evidence_pending = evidence.filter(
        verification_status="pending"
    ).count()

    evidence_rejected = evidence.filter(
        verification_status="rejected"
    ).count()

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "submission":
            submission,

        "esg_data":
            esg_data,

        "evidence":
            evidence,

        "evidence_total":
            evidence_total,

        "evidence_verified":
            evidence_verified,

        "evidence_pending":
            evidence_pending,

        "evidence_rejected":
            evidence_rejected,
    }

    return render(
        request,
        "reporting/manager_review_submission.html",
        context,
    )