import re


# ---------------------------------------------------------
# Standard ESG metric dictionary
# ---------------------------------------------------------

ESG_METRIC_ALIASES = {

    # Environmental

    "ENERGY_CONSUMPTION": [
        "energy consumption",
        "electricity consumption",
        "electricity",
        "power consumption",
        "fuel consumption",
        "energy used",
        "total energy",
    ],

    "GHG_EMISSIONS": [
        "co2 emissions",
        "co2",
        "carbon emissions",
        "ghg emissions",
        "greenhouse gas emissions",
        "carbon footprint",
        "scope 1 emissions",
        "scope 2 emissions",
    ],

    "WATER_CONSUMPTION": [
        "water consumption",
        "water usage",
        "water withdrawal",
        "water used",
        "fresh water",
    ],

    "WATER_RECYCLING_RATE": [
        "water recycling rate",
        "water recycled rate",
        "water reuse rate",
        "percentage of water recycled",
        "percentage water recycled",
    ],

    "WASTE_GENERATED": [
        "waste generated",
        "total waste",
        "solid waste",
        "hazardous waste",
        "non hazardous waste",
    ],

    # Social

    "TOTAL_EMPLOYEES": [
        "employees",
        "employee count",
        "total employees",
        "number of employees",
        "workforce",
        "total workforce",
    ],

    "WOMEN_EMPLOYEES": [
        "women employees",
        "female employees",
        "women workforce",
        "female workforce",
        "women employees count",
    ],

    "EMPLOYEE_TURNOVER": [
        "employee turnover",
        "employee turnover rate",
        "staff turnover",
        "employee attrition",
        "employee attrition rate",
    ],

    "TRAINING_HOURS": [
        "training hours",
        "employee training",
        "training hours employees",
        "learning hours",
    ],

    "SAFETY_INCIDENTS": [
        "safety incidents",
        "workplace incidents",
        "accidents",
        "work accidents",
        "occupational incidents",
    ],

    # Governance

    "COMPLAINTS": [
        "complaints",
        "grievances",
        "customer complaints",
        "stakeholder complaints",
        "grievances received",
    ],

    "CSR_EXPENDITURE": [
        "csr expenditure",
        "csr spending",
        "corporate social responsibility",
    ],
}

    


def normalize_metric_name(value):
    """
    Normalize uploaded metric text.
    """

    value = str(value).strip().lower()

    value = re.sub(
        r"[_\-\/]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


def map_metric(metric_name):
    """
    Map uploaded ESG metric name to a standard ESG metric.
    """

    from esg_data.models import ESGMetric

    normalized = normalize_metric_name(metric_name)

    # 1. Exact alias match
    for standard_metric, aliases in ESG_METRIC_ALIASES.items():
        for alias in aliases:
            if normalized == normalize_metric_name(alias):
                return {
                    "standard_metric": standard_metric,
                    "match_type": "EXACT",
                    "confidence": 1.0,
                }

    # 2. Exact database metric match
    db_metric = ESGMetric.objects.filter(
        name__iexact=metric_name.strip()
    ).first()

    if db_metric:
        return {
            "standard_metric": db_metric.name,
            "match_type": "EXACT_DB",
            "confidence": 1.0,
        }

    # 3. Safe partial alias match
    for standard_metric, aliases in ESG_METRIC_ALIASES.items():
        for alias in aliases:

            normalized_alias = normalize_metric_name(alias)

            if len(normalized_alias.split()) < 2:
                continue

            if normalized_alias in normalized:
                return {
                    "standard_metric": standard_metric,
                    "match_type": "PARTIAL",
                    "confidence": 0.85,
                }

    # 4. Unmatched
    return {
        "standard_metric": None,
        "match_type": "UNMATCHED",
        "confidence": 0.0,
    }


def map_rows(valid_rows):
    """
    Map validated ESG rows to standard metrics.
    """

    mapped_rows = []

    for row in valid_rows:

        mapping = map_metric(
            row["metric"]
        )

        mapped_rows.append(
            {
                **row,
                "standard_metric": mapping[
                    "standard_metric"
                ],
                "match_type": mapping[
                    "match_type"
                ],
                "confidence": mapping[
                    "confidence"
                ],
            }
        )

    return mapped_rows