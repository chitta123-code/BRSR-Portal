
from decimal import Decimal, InvalidOperation

from .models import ESGData, ESGValidation


# Metrics that are expected to be non-negative in ordinary reporting.
# Match these names against the metric names stored in your database.
NON_NEGATIVE_METRICS = {
    "energy consumption",
    "water consumption",
    "water withdrawal",
    "water discharge",
    "waste generated",
    "total waste generated",
    "co2 emissions",
    "co2 emissions (environmental)",
    "scope 1 emissions",
    "scope 2 emissions",
    "scope 3 emissions",
}


def validate_esg_data(esg_data):
    """
    Validate one ESGData record.
    Returns a list of validation issues.
    """

    issues = []

    # 1. Missing value
    if esg_data.value is None:
        issues.append({
            "rule_name": "Missing Value Check",
            "message": "ESG value is missing.",
            "severity": "error",
        })
        return issues

    # 2. Numeric value check
    try:
        value = Decimal(str(esg_data.value))
    except (InvalidOperation, ValueError, TypeError):
        issues.append({
            "rule_name": "Invalid Numeric Value Check",
            "message": "ESG value must be a valid number.",
            "severity": "error",
        })
        return issues

    metric_name = (
        str(esg_data.metric.name).strip().casefold()
        if esg_data.metric_id
        else ""
    )

    # 3. Negative value check for configured metrics
    if value < 0 and metric_name in NON_NEGATIVE_METRICS:
        issues.append({
            "rule_name": "Negative Value Check",
            "message": (
                f"{esg_data.metric.name} has a negative value "
                "that needs investigation. Check the source "
                "evidence, unit and reporting methodology."
            ),
            "severity": "warning",
        })

    # 4. Extremely large value
    if value > Decimal("1000000000"):
        issues.append({
            "rule_name": "Extreme Value Check",
            "message": (
                f"The entered value {value} is extremely large. "
                "Please verify the data and unit."
            ),
            "severity": "warning",
        })

    # 5. Percentage validation
    if esg_data.metric_id and esg_data.metric.unit == "%":
        if value < 0 or value > 100:
            issues.append({
                "rule_name": "Percentage Range Check",
                "message": (
                    "Percentage value must be between 0 and 100."
                ),
                "severity": "error",
            })

    return issues


def run_validation(esg_data):
    """
    Replace previous open validation results
    with the latest validation findings.
    """

    ESGValidation.objects.filter(
        esg_data=esg_data,
        status="open"
    ).delete()

    issues = validate_esg_data(esg_data)

    for issue in issues:
        ESGValidation.objects.create(
            esg_data=esg_data,
            rule_name=issue["rule_name"],
            message=issue["message"],
            severity=issue["severity"],
        )

    return issues