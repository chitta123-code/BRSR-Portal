from django.urls import path

from .views import (
    esg_data_entry,
    esg_file_upload,
    match_evidence,
    smart_validation_dashboard,
    submit_esg_for_review,
    esg_review_dashboard,
    review_esg_data,
    draft_esg_data,
    resolve_validation,
    ignore_validation,
    esg_dashboard,
    esg_anomaly_dashboard,
    run_anomaly_scan,
    review_anomaly,
    esg_consolidation,
    evidence_upload,
    evidence_verification,
    verify_evidence,
)


urlpatterns = [
    path("data-entry/", esg_data_entry, name="esg_data_entry"),

    path("upload/", esg_file_upload, name="esg_file_upload"),

    path("draft/", draft_esg_data, name="draft_esg_data"),

    path("review/", esg_review_dashboard, name="esg_review_dashboard"),

    path(
        "review/<int:data_id>/",
        review_esg_data,
        name="review_esg_data"
    ),

    path(
        "submit/<int:data_id>/",
        submit_esg_for_review,
        name="submit_esg_for_review"
    ),

    path(
        "validation/<int:validation_id>/resolve/",
        resolve_validation,
        name="resolve_validation"
    ),

    path(
        "validation/<int:validation_id>/ignore/",
        ignore_validation,
        name="ignore_validation"
    ),

    path(
        "dashboard/",
        esg_dashboard,
        name="esg_dashboard"
    ),

    path(
        "anomalies/",
        esg_anomaly_dashboard,
        name="esg_anomaly_dashboard"
    ),

    path(
    "anomalies/scan/",
    run_anomaly_scan,
    name="run_anomaly_scan"
    ),

   path(
    "anomalies/<int:anomaly_id>/review/",
    review_anomaly,
    name="review_anomaly"
    ),


  path(
    "consolidation/",
    esg_consolidation,
    name="esg_consolidation"
    ),


    
    # Upload evidence for a specific ESG data record
    path(
        "evidence/upload/<int:data_id>/",
        evidence_upload,
        name="evidence_upload",
    ),

    # View all uploaded evidence
    path(
        "evidence-verification/",
        evidence_verification,
        name="evidence_verification",
    ),

    # Verify or reject an uploaded evidence file
    path(
        "evidence/<int:evidence_id>/verify/",
        verify_evidence,
        name="verify_evidence",
    ),

    # Match evidence to ESG data
    path(
        "evidence/<int:evidence_id>/match/",
        match_evidence,
        name="match_evidence",
    ),

    # Smart validation dashboard
    path(
        "validation/dashboard/",
        smart_validation_dashboard,
        name="smart_validation_dashboard",
    ),

]