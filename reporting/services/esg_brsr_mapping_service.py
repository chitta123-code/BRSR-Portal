from esg_data.models import ESGData
from indicators.models import ESGIndicatorMapping, IndicatorResponse


def populate_brsr_from_esg(submission):
    """
    Populate BRSR indicator responses using approved ESG data.

    The function:
    - Uses only approved ESG data.
    - Updates existing IndicatorResponse records.
    - Keeps DIRECT and SUPPORTING mapping information.
    - Reports indicator-level population status.
    - Does not assume that every mapped ESG metric is mandatory.
    """

    if submission.status == "APPROVED":
        raise ValueError(
            "Approved BRSR submissions cannot be modified automatically."
        )

    if submission.business_unit is None:
        raise ValueError(
            "The BRSR submission must have a business unit."
        )

    financial_year = submission.reporting_period.financial_year

    esg_data = ESGData.objects.filter(
        business_unit=submission.business_unit,
        financial_year=financial_year,
        status="approved",
        metric__isnull=False,
    ).select_related("metric")

    updated_count = 0
    skipped_count = 0
    details = []
    indicator_summary = {}

    for data in esg_data:
        mappings = ESGIndicatorMapping.objects.filter(
            esg_metric=data.metric,
            is_active=True,
        ).select_related("indicator")

        if not mappings.exists():
            skipped_count += 1
            details.append({
                "metric": data.metric.name,
                "status": "No mapping found",
            })
            continue

        for mapping in mappings:
            response_text = str(data.value) if data.value is not None else ""

            _, created = IndicatorResponse.objects.update_or_create(
                submission=submission,
                indicator=mapping.indicator,
                defaults={
                    "response_text": response_text,
                    "numeric_value": data.value,
                    "unit": data.metric.unit,
                    "remarks": (
                        f"Automatically populated from ESG metric "
                        f"'{data.metric.name}' "
                        f"({mapping.mapping_type})."
                    ),
                    "is_valid": True,
                },
            )

            updated_count += 1

            indicator_code = mapping.indicator.indicator_code
            summary = indicator_summary.setdefault(
                indicator_code,
                {
                    "indicator": indicator_code,
                    "indicator_question": mapping.indicator.question,
                    "metrics": [],
                    "populated_count": 0,
                },
            )

            summary["metrics"].append({
                "metric": data.metric.name,
                "mapping_type": mapping.mapping_type,
                "value": data.value,
                "unit": data.metric.unit,
            })
            summary["populated_count"] += 1

            details.append({
                "metric": data.metric.name,
                "indicator": indicator_code,
                "mapping_type": mapping.mapping_type,
                "created": created,
                "value": data.value,
                "status": "Populated",
            })

    for indicator_code, summary in indicator_summary.items():
        direct_count = sum(
            1
            for metric in summary["metrics"]
            if metric["mapping_type"] == "DIRECT"
        )

        supporting_count = sum(
            1
            for metric in summary["metrics"]
            if metric["mapping_type"] == "SUPPORTING"
        )

        total_direct_mappings = ESGIndicatorMapping.objects.filter(
            indicator__indicator_code=indicator_code,
            is_active=True,
            mapping_type="DIRECT",
        ).count()

        if direct_count < total_direct_mappings:
            status = "PARTIALLY_POPULATED"
        elif direct_count == total_direct_mappings and total_direct_mappings > 0:
            status = "POPULATED"
        elif supporting_count > 0:
            status = "PARTIALLY_POPULATED"
        else:
            status = "NOT_POPULATED"

        summary["direct_count"] = direct_count
        summary["supporting_count"] = supporting_count
        summary["total_direct_mappings"] = total_direct_mappings
        summary["status"] = status

    return {
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "details": details,
        "indicator_summary": list(indicator_summary.values()),
    }