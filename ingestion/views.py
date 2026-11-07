from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from organization.models import Company, BusinessUnit, Project
from reporting.models import ReportingPeriod

from .models import UploadedESGFile,ImportedESGRecord

from django.core.files.storage import default_storage
from django.db import transaction

from .services import extract_file_data

from .validators import validate_dataframe
from .mapping import map_rows


@login_required
def upload_esg_file(request):

    companies = Company.objects.all().order_by("name")
    periods = ReportingPeriod.objects.all().order_by("-financial_year")

    selected_company = None
    business_units = []
    projects = []

    if request.method == "POST":

        company_id = request.POST.get("company")
        business_unit_id = request.POST.get("business_unit")
        project_id = request.POST.get("project")
        period_id = request.POST.get("period")
        uploaded_file = request.FILES.get("file")

        if not company_id:
            messages.error(request, "Please select a company.")
            return redirect("upload_esg_file")

        if not period_id:
            messages.error(request, "Please select a financial year.")
            return redirect("upload_esg_file")

        if not uploaded_file:
            messages.error(request, "Please select a file.")
            return redirect("upload_esg_file")

        selected_company = Company.objects.filter(
            id=company_id
        ).first()

        if not selected_company:
            messages.error(request, "Invalid company selected.")
            return redirect("upload_esg_file")

        business_unit = None
        if business_unit_id:
            business_unit = BusinessUnit.objects.filter(
                id=business_unit_id,
                company=selected_company
            ).first()

        project = None
        if project_id and business_unit:
            project = Project.objects.filter(
                id=project_id,
                business_unit=business_unit
            ).first()

        reporting_period = ReportingPeriod.objects.filter(
            id=period_id
        ).first()

        if not reporting_period:
            messages.error(request, "Invalid financial year.")
            return redirect("upload_esg_file")

        extension = Path(uploaded_file.name).suffix.lower()

        if extension in [".xlsx", ".xls"]:
            file_type = "EXCEL"

        elif extension == ".csv":
            file_type = "CSV"

        elif extension == ".pdf":
            file_type = "PDF"

        else:
            file_type = "OTHER"

        allowed_extensions = [
            ".xlsx",
            ".xls",
            ".csv",
            ".pdf",
        ]

        if extension not in allowed_extensions:
            messages.error(
                request,
                "Unsupported file format. Please upload Excel, CSV or PDF."
            )
            return redirect("upload_esg_file")

        max_size = 20 * 1024 * 1024

        if uploaded_file.size > max_size:
            messages.error(
                request,
                "File size must be less than 20 MB."
            )
            return redirect("upload_esg_file")

        uploaded = UploadedESGFile.objects.create(
            company=selected_company,
            business_unit=business_unit,
            project=project,
            reporting_period=reporting_period,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_type=file_type,
            status="UPLOADED",
            uploaded_by=request.user,
        )

        messages.success(
            request,
            f"{uploaded.original_filename} uploaded successfully."
        )

        return redirect("preview_esg_file",file_id=uploaded.id)

    return render(
        request,
        "ingestion/upload_esg_file.html",
        {
            "companies": companies,
            "periods": periods,
            "business_units": business_units,
            "projects": projects,
        }
    )


@login_required
def preview_esg_file(request, file_id):
    uploaded_file = UploadedESGFile.objects.filter(
        id=file_id,
        uploaded_by=request.user
    ).first()

    if not uploaded_file:
        messages.error(request, "Uploaded ESG file was not found.")
        return redirect("upload_esg_file")

    try:
        file_path = uploaded_file.file.path
        extracted_data = extract_file_data(file_path)

        preview_sheets = []
        all_mapped_rows = []
        total_errors = 0
        total_warnings = 0

        for sheet_name, sheet_data in extracted_data.items():
            dataframe = sheet_data["dataframe"]
            columns = list(dataframe.columns)

            if sheet_name.strip().lower() == "metric_master":
                continue

            errors, warnings, valid_rows = validate_dataframe(
                dataframe,
                sheet_data["columns"]
            )

            mapped_rows = map_rows(valid_rows)

            all_mapped_rows.extend(mapped_rows)
            total_errors += len(errors)
            total_warnings += len(warnings)

            rows = (
                dataframe
                .head(20)
                .fillna("")
                .to_dict(orient="records")
            )

            preview_sheets.append({
                "name": sheet_name,
                "columns": columns,
                "rows": rows,
                "total_rows": len(dataframe),
                "detected_columns": sheet_data["columns"],
                "errors": errors,
                "warnings": warnings,
                "mapped_rows": mapped_rows,
            })

        uploaded_file.extracted_rows = sum(
            sheet["total_rows"]
            for sheet in preview_sheets
        )
        uploaded_file.validation_errors = total_errors

        if total_errors > 0:
            uploaded_file.status = "VALIDATION_ERROR"
        else:
            uploaded_file.status = "PROCESSED"

        uploaded_file.notes = (
            f"Validation errors: {total_errors}; "
            f"Warnings: {total_warnings}"
        )

        uploaded_file.save(
            update_fields=[
                "extracted_rows",
                "validation_errors",
                "status",
                "notes",
            ]
        )

    except Exception as error:
        uploaded_file.status = "FAILED"
        uploaded_file.notes = str(error)

        uploaded_file.save(
            update_fields=["status", "notes"]
        )

        messages.error(
            request,
            f"File processing failed: {error}"
        )

        return redirect("upload_esg_file")

    return render(
        request,
        "ingestion/preview_esg_file.html",
        {
            "uploaded_file": uploaded_file,
            "preview_sheets": preview_sheets,
            "mapped_rows": all_mapped_rows,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
        }
    )

@login_required
def import_esg_file(request, file_id):

    if request.method != "POST":
        return redirect(
            "preview_esg_file",
            file_id=file_id
        )

    uploaded_file = UploadedESGFile.objects.filter(
        id=file_id,
        uploaded_by=request.user
    ).first()

    if not uploaded_file:
        messages.error(
            request,
            "Uploaded ESG file was not found."
        )
        return redirect("upload_esg_file")

    # -------------------------------------------------
    # Prevent accidental duplicate import
    # -------------------------------------------------

    if uploaded_file.status == "IMPORTED":

        messages.warning(
            request,
            "This file has already been imported."
        )

        return redirect(
            "preview_esg_file",
            file_id=file_id
        )

    try:

        # -------------------------------------------------
        # Extract file
        # -------------------------------------------------

        file_path = uploaded_file.file.path

        extracted_data = extract_file_data(file_path)

        total_imported = 0
        total_errors = 0

        # -------------------------------------------------
        # Process every sheet
        # -------------------------------------------------

        with transaction.atomic():

            for sheet_name, sheet_data in extracted_data.items():

                # Skip reference/master sheet
                if sheet_name.strip().lower() == "metric_master":
                    continue

                dataframe = sheet_data["dataframe"]

                errors, warnings, valid_rows = validate_dataframe(
                    dataframe,
                    sheet_data["columns"]
                )

                total_errors += len(errors)

                if errors:
                    continue

                # -------------------------------------------------
                # Map validated rows to standard ESG metrics
                # -------------------------------------------------

                mapped_rows = map_rows(valid_rows)

                for row in mapped_rows:

                    # Skip unmatched ESG metrics
                    if not row["standard_metric"]:
                        continue

                    # -------------------------------------------------
                    # Prevent duplicate rows
                    # -------------------------------------------------

                    existing_record = ImportedESGRecord.objects.filter(
                        uploaded_file=uploaded_file,
                        row_number=row["row_number"],
                    ).first()

                    if existing_record:
                        continue

                    # -------------------------------------------------
                    # Create imported ESG record
                    # -------------------------------------------------

                    ImportedESGRecord.objects.create(
                        uploaded_file=uploaded_file,
                        company=uploaded_file.company,
                        business_unit=uploaded_file.business_unit,
                        project=uploaded_file.project,
                        reporting_period=uploaded_file.reporting_period,
                        row_number=row["row_number"],
                        original_metric=row["metric"],
                        standard_metric=row["standard_metric"],
                        value=row["value"],
                        unit=row["unit"],
                        confidence=row["confidence"],
                        match_type=row["match_type"],
                    )

                    total_imported += 1

            # -------------------------------------------------
            # Validation error
            # -------------------------------------------------

            if total_errors > 0:

                uploaded_file.status = "VALIDATION_ERROR"

                uploaded_file.validation_errors = total_errors

                uploaded_file.notes = (
                    f"Import blocked. "
                    f"{total_errors} validation error(s) found."
                )

                uploaded_file.save(
                    update_fields=[
                        "status",
                        "validation_errors",
                        "notes",
                    ]
                )

                messages.error(
                    request,
                    "Import was blocked because validation errors exist."
                )

                return redirect(
                    "preview_esg_file",
                    file_id=file_id
                )

            # -------------------------------------------------
            # Successful import
            # -------------------------------------------------

            uploaded_file.status = "IMPORTED"

            uploaded_file.notes = (
                f"Successfully imported "
                f"{total_imported} ESG record(s)."
            )

            uploaded_file.save(
                update_fields=[
                    "status",
                    "notes",
                ]
            )

        messages.success(
            request,
            f"Successfully imported {total_imported} ESG record(s)."
        )

        return redirect(
            "preview_esg_file",
            file_id=file_id
        )

    except Exception as error:

        messages.error(
            request,
            f"Import failed: {error}"
        )

        uploaded_file.status = "FAILED"

        uploaded_file.notes = str(error)

        uploaded_file.save(
            update_fields=[
                "status",
                "notes",
            ]
        )

        return redirect(
            "preview_esg_file",
            file_id=file_id
        )