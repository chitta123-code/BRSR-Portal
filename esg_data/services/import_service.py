from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

from django.db import transaction
from django.utils import timezone

from esg_data.models import ESGData, ESGImportBatch
from esg_data.validators import run_validation

from ingestion.models import UploadedESGFile, ImportedESGRecord
from reporting.models import ReportingPeriod


def normalize_column_name(value):
    """
    Convert Excel column names into a standard format.

    Example:
    Business Unit -> business_unit
    Financial Year -> financial_year
    Data Source -> data_source
    """
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
    )


def get_row_value(row, column_mapping, field_name, default=None):
    """
    Get a value from an Excel/CSV row using the detected column mapping.
    """

    column_name = column_mapping.get(field_name)

    if column_name:
        if column_name in row:
            return row.get(column_name)

        normalized_column = normalize_column_name(column_name)

        for key, value in row.items():
            if normalize_column_name(key) == normalized_column:
                return value

    normalized_field = normalize_column_name(field_name)

    for key, value in row.items():
        if normalize_column_name(key) == normalized_field:
            return value

    return default


def clean_value(value):
    """
    Convert an Excel/CSV value into Decimal.
    """

    if value is None:
        return None

    try:

        # Check for NaN
        try:
            if value != value:
                return None
        except Exception:
            pass

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return None

            value = value.replace(",", "")

        return Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):

        return None


def detect_file_type(filename):
    """
    Detect uploaded file type from extension.
    """

    extension = Path(filename).suffix.lower()

    if extension in [".xlsx", ".xls", ".xlsm"]:
        return "EXCEL"

    if extension == ".csv":
        return "CSV"

    if extension == ".pdf":
        return "PDF"

    return "OTHER"


@transaction.atomic
def import_esg_data(
    df,
    column_mapping,
    match_results,
    financial_year,
    filename,
    uploaded_by="",
    company=None,
    business_unit=None,
    project=None,
    uploaded_file=None,
):
    """
    Import ESG data while preserving:

    Company
    Business Unit
    Project
    Reporting Period
    Uploaded File
    Imported ESG Record
    ESG Data
    Validation
    """

    # ---------------------------------------------------------
    # 1. FIND REPORTING PERIOD
    # ---------------------------------------------------------

    try:

        reporting_period = ReportingPeriod.objects.get(
            financial_year=financial_year
        )

    except ReportingPeriod.DoesNotExist:

        raise ValueError(
            f"Reporting Period '{financial_year}' does not exist. "
            f"Please create it first."
        )

    # ---------------------------------------------------------
    # 2. CREATE UPLOADED ESG FILE
    # ---------------------------------------------------------

    if uploaded_file is None:
        raise ValueError(
            "Uploaded file is required."
        )

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    file_type = detect_file_type(
        uploaded_file.name
    )

    uploaded_esg_file = UploadedESGFile.objects.create(

        company=company,

        business_unit=business_unit,

        project=project,

        reporting_period=reporting_period,

        file=uploaded_file,

        original_filename=filename,

        file_type=file_type,

        status="PROCESSING",

        uploaded_by=(
            uploaded_by
            if hasattr(uploaded_by, "pk")
            else None
        ),
    )

    # ---------------------------------------------------------
    # 3. CREATE IMPORT BATCH
    # ---------------------------------------------------------

    batch = ESGImportBatch.objects.create(

        filename=filename,

        financial_year=financial_year,

        total_rows=len(match_results),

        uploaded_by=(
            uploaded_by.username
            if hasattr(uploaded_by, "username")
            else str(uploaded_by or "")
        ),

        status="processing",
    )

    imported_count = 0
    skipped_count = 0
    error_count = 0

    # ---------------------------------------------------------
    # 4. PROCESS EACH ROW
    # ---------------------------------------------------------

    try:

        for index, match_result in enumerate(match_results):

            # -------------------------------------------------
            # CHECK MATCHING
            # -------------------------------------------------

            business_unit_matched = match_result.get(
                "business_unit_matched",
                False
            )

            metric_matched = match_result.get(
                "metric_matched",
                False
            )

            if not business_unit_matched or not metric_matched:

                skipped_count += 1

                continue

            matched_business_unit = (
                match_result.get("business_unit")
            )

            metric = match_result.get("metric")

            if (
                matched_business_unit is None
                or metric is None
            ):

                skipped_count += 1

                continue

            # -------------------------------------------------
            # CHECK DATAFRAME ROW
            # -------------------------------------------------

            if index >= len(df):

                error_count += 1

                continue

            row = df.iloc[index].to_dict()

            # -------------------------------------------------
            # FINANCIAL YEAR
            # -------------------------------------------------

            row_financial_year = get_row_value(
                row,
                column_mapping,
                "financial_year",
                financial_year
            )

            if row_financial_year is None:

                row_financial_year = financial_year

            row_financial_year = str(
                row_financial_year
            ).strip()

            if not row_financial_year:

                row_financial_year = financial_year

            # Check financial-year format, for example 2025-26
            year_match = re.fullmatch(
                r"(\d{4})-(\d{2})",
                row_financial_year
            )

            if not year_match:
                error_count += 1
                skipped_count += 1
                continue

            start_year = int(year_match.group(1))
            end_year = int(year_match.group(2))

            if end_year != (start_year + 1) % 100:
                error_count += 1
                skipped_count += 1
                continue

            # -------------------------------------------------
            # ORIGINAL METRIC
            # -------------------------------------------------

            original_metric = get_row_value(
                row,
                column_mapping,
                "metric",
                ""
            )

            if original_metric is None:

                original_metric = ""

            original_metric = str(
                original_metric
            ).strip()

            # -------------------------------------------------
            # ESG VALUE
            # -------------------------------------------------

            raw_value = get_row_value(
                row,
                column_mapping,
                "value"
            )

            value = clean_value(
                raw_value
            )

            # Do not silently convert invalid or missing values to zero
            if value is None:
                error_count += 1
                skipped_count += 1
                continue

            # -------------------------------------------------
            # UNIT
            # -------------------------------------------------

            unit = get_row_value(
                row,
                column_mapping,
                "unit",
                ""
            )

            if unit is None:

                unit = ""

            unit = str(unit).strip()

            # -------------------------------------------------
            # CONFIDENCE
            # -------------------------------------------------

            confidence = match_result.get(
                "confidence",
                0
            )

            try:

                confidence = float(
                    confidence or 0
                )

            except (TypeError, ValueError):

                confidence = 0

            # -------------------------------------------------
            # MATCH TYPE
            # -------------------------------------------------

            match_type = match_result.get(
                "match_type",
                ""
            )

            if match_type is None:

                match_type = ""

            match_type = str(
                match_type
            ).strip()

            # -------------------------------------------------
            # 5. CREATE IMPORTED ESG RECORD
            # -------------------------------------------------

            ImportedESGRecord.objects.create(

                uploaded_file=uploaded_esg_file,

                company=company,

                business_unit=business_unit,

                project=project,

                reporting_period=reporting_period,

                row_number=index + 2,

                original_metric=original_metric,

                standard_metric=metric.name,

                value=float(value) if value is not None else 0,

                unit=unit,

                confidence=confidence,

                match_type=match_type,
            )

            # -------------------------------------------------
            # DATA SOURCE
            # -------------------------------------------------

            data_source = get_row_value(
                row,
                column_mapping,
                "data_source",
                ""
            )

            if data_source is None:

                data_source = ""

            data_source = str(
                data_source
            ).strip()

            # -------------------------------------------------
            # REMARKS
            # -------------------------------------------------

            remarks = get_row_value(
                row,
                column_mapping,
                "remarks",
                ""
            )

            if remarks is None:

                remarks = ""

            remarks = str(
                remarks
            ).strip()

            # -------------------------------------------------
            # 6. CREATE ESG DATA
            # -------------------------------------------------

            esg_data = ESGData.objects.create(

                business_unit=(
                    matched_business_unit
                ),

                financial_year=row_financial_year,

                metric=metric,

                value=value,

                data_source=data_source,

                remarks=remarks,

                status="draft",

                entered_by=(
                    uploaded_by.username
                    if hasattr(
                        uploaded_by,
                        "username"
                    )
                    else str(
                        uploaded_by or ""
                    )
                ),
            )

            imported_count += 1

            # -------------------------------------------------
            # 7. RUN VALIDATION
            # -------------------------------------------------

            try:

                run_validation(
                    esg_data
                )

            except Exception as validation_error:

                error_count += 1

                esg_data.remarks = (
                    f"{remarks}\n"
                    f"Validation processing error: "
                    f"{validation_error}"
                ).strip()

                esg_data.save(
                    update_fields=[
                        "remarks",
                        "updated_at",
                    ]
                )

        # -----------------------------------------------------
        # 8. UPDATE UPLOADED FILE
        # -----------------------------------------------------

        uploaded_esg_file.extracted_rows = (
            len(match_results)
        )

        uploaded_esg_file.validation_errors = (
            error_count
        )

        uploaded_esg_file.processed_at = (
            timezone.now()
        )

        if error_count > 0:

            uploaded_esg_file.status = (
                "VALIDATION_ERROR"
            )

        else:

            uploaded_esg_file.status = (
                "PROCESSED"
            )

        uploaded_esg_file.save(
            update_fields=[
                "extracted_rows",
                "validation_errors",
                "processed_at",
                "status",
            ]
        )

        # -----------------------------------------------------
        # 9. UPDATE IMPORT BATCH
        # -----------------------------------------------------

        batch.imported_rows = (
            imported_count
        )

        batch.skipped_rows = (
            skipped_count
        )

        batch.error_rows = (
            error_count
        )

        if error_count > 0:

            batch.status = (
                "completed_with_errors"
            )

        else:

            batch.status = (
                "completed"
            )

        batch.completed_at = (
            timezone.now()
        )

        batch.save(
            update_fields=[
                "imported_rows",
                "skipped_rows",
                "error_rows",
                "status",
                "completed_at",
            ]
        )

        # -----------------------------------------------------
        # 10. RETURN RESULT
        # -----------------------------------------------------

        return {

            "batch": batch,

            "uploaded_file": (
                uploaded_esg_file
            ),

            "imported_count": (
                imported_count
            ),

            "skipped_count": (
                skipped_count
            ),

            "error_count": (
                error_count
            ),
        }

    except Exception:

        uploaded_esg_file.status = (
            "FAILED"
        )

        uploaded_esg_file.processed_at = (
            timezone.now()
        )

        uploaded_esg_file.save(
            update_fields=[
                "status",
                "processed_at",
            ]
        )

        batch.imported_rows = (
            imported_count
        )

        batch.skipped_rows = (
            skipped_count
        )

        batch.error_rows = (
            error_count + 1
        )

        batch.status = "failed"

        batch.completed_at = (
            timezone.now()
        )

        batch.save(
            update_fields=[
                "imported_rows",
                "skipped_rows",
                "error_rows",
                "status",
                "completed_at",
            ]
        )

        raise