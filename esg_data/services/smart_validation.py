
import re
from decimal import Decimal, InvalidOperation


# Metrics for which negative values usually need investigation.
# Adjust these names to match your actual ESGMetric records.
NON_NEGATIVE_METRICS = {
    "energy consumption",
    "water consumption",
    "water withdrawal",
    "water discharge",
    "waste generated",
    "total waste generated",
    "scope 1 emissions",
    "scope 2 emissions",
}


def validate_esg_record(record):
    """
    Return validation issues for one ESGData record.
    This function reports issues but does not modify the record.
    """
    issues = []

    # 1. Required fields
    if not record.metric_id:
        issues.append({
            "severity": "error",
            "field": "Metric",
            "message": "ESG metric is missing.",
        })

    if not record.business_unit_id:
        issues.append({
            "severity": "error",
            "field": "Business Unit",
            "message": "Business unit is missing.",
        })

    # 2. Financial year
    financial_year = str(record.financial_year or "").strip()

    if not financial_year:
        issues.append({
            "severity": "error",
            "field": "Financial Year",
            "message": "Financial year is missing.",
        })
    elif not re.fullmatch(r"\d{4}-\d{2}", financial_year):
        issues.append({
            "severity": "warning",
            "field": "Financial Year",
            "message": "Expected format like 2025-26.",
        })
    else:
        start_year, end_year = map(int, financial_year.split("-"))

        if end_year != (start_year + 1) % 100:
            issues.append({
                "severity": "warning",
                "field": "Financial Year",
                "message": "The ending year does not follow the starting year.",
            })

    # 3. Numeric value
    try:
        if record.value is None or str(record.value).strip() == "":
            raise InvalidOperation

        value = Decimal(str(record.value))

    except (InvalidOperation, ValueError, TypeError):
        issues.append({
            "severity": "error",
            "field": "Value",
            "message": "A valid numeric ESG value is required.",
        })
        return issues

    # 4. Negative-value checks for selected metrics
    metric_name = (
        str(record.metric).strip().casefold()
        if record.metric_id
        else ""
    )

    if value < 0 and metric_name in NON_NEGATIVE_METRICS:
        issues.append({
            "severity": "warning",
            "field": "Value",
            "message": (
                "Negative value detected for this metric. "
                "Check the source evidence and unit."
            ),
        })

    return issues