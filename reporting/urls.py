from django.urls import path

from reporting.views import (
    brsr_entry,
    manager_dashboard,
    reviewer_dashboard,
    review_submission,
    download_brsr_pdf,
    evidence_verification,
    verify_evidence,
    manager_review_submission,

)


urlpatterns = [

    path(
        "brsr-entry/",
        brsr_entry,
        name="brsr_entry",
    ),

    path(
        "reviewer-dashboard/",
        reviewer_dashboard,
        name="reviewer_dashboard",
    ),

    path(
        "review-submission/<int:submission_id>/",
        review_submission,
        name="review_submission",
    ),

    path(
        "download-brsr-pdf/<int:submission_id>/",
        download_brsr_pdf,
        name="download_brsr_pdf",
    ),


    path(
    "evidence-verification/",
    evidence_verification,
    name="reporting_evidence_verification",
),

path(
    "verify-evidence/<int:evidence_id>/",
    verify_evidence,
    name="reporting_verify_evidence",
),


    path(
    "manager-dashboard/",
    manager_dashboard,
    name="manager_dashboard",
  ),


   path(
    "manager-review/<int:submission_id>/",
    manager_review_submission,
    name="manager_review_submission",
    ),
]

