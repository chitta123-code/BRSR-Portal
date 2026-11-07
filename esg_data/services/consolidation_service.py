from django.db.models import Sum, Avg, Count

from esg_data.models import ESGData


def get_business_unit_consolidation(
    business_unit,
    financial_year=None
):
    """
    Calculate ESG summary for one Business Unit.
    Only approved ESG data is included.
    """

    queryset = ESGData.objects.filter(
        business_unit=business_unit,
        status="approved"
    )

    if financial_year:
        queryset = queryset.filter(
            financial_year=financial_year
        )

    summary = queryset.values(
        "metric__id",
        "metric__name",
        "metric__category",
        "metric__unit"
    ).annotate(
        total_value=Sum("value"),
        average_value=Avg("value"),
        record_count=Count("id")
    ).order_by(
        "metric__category",
        "metric__name"
    )

    return summary


def get_company_consolidation(
    company,
    financial_year=None
):
    """
    Calculate consolidated ESG summary
    for all Business Units belonging to a Company.
    """

    queryset = ESGData.objects.filter(
        business_unit__company=company,
        status="approved"
    )

    if financial_year:
        queryset = queryset.filter(
            financial_year=financial_year
        )

    summary = queryset.values(
        "metric__id",
        "metric__name",
        "metric__category",
        "metric__unit"
    ).annotate(
        total_value=Sum("value"),
        average_value=Avg("value"),
        record_count=Count("id")
    ).order_by(
        "metric__category",
        "metric__name"
    )

    return summary