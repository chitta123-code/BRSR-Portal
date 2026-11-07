from decimal import Decimal

from django.db.models import Avg

from .models import ESGData, ESGAnomaly


def detect_anomaly(esg_data):

    # --------------------------------------------------------
    # Basic checks
    # --------------------------------------------------------

    if esg_data.value is None:
        return None

    if esg_data.metric is None:
        return None


    # --------------------------------------------------------
    # Get historical approved records
    # --------------------------------------------------------

    historical_data = (
        ESGData.objects
        .filter(
            business_unit=esg_data.business_unit,
            metric=esg_data.metric,
            status="approved",
            value__isnull=False
        )
        .exclude(
            id=esg_data.id
        )
        .order_by(
            "-created_at"
        )
    )


    # --------------------------------------------------------
    # Need historical data
    # --------------------------------------------------------

    if not historical_data.exists():
        return None


    # --------------------------------------------------------
    # Calculate historical average
    # --------------------------------------------------------

    average_value = historical_data.aggregate(
        average=Avg("value")
    )["average"]


    if average_value is None:
        return None


    average_value = Decimal(
        str(average_value)
    )

    current_value = Decimal(
        str(esg_data.value)
    )


    # --------------------------------------------------------
    # Avoid division by zero
    # --------------------------------------------------------

    if average_value == 0:

        return None


    # --------------------------------------------------------
    # Percentage difference
    # --------------------------------------------------------

    difference_percentage = (

        abs(
            current_value - average_value
        )

        / abs(
            average_value
        )

    ) * Decimal("100")


    # --------------------------------------------------------
    # Determine anomaly
    # --------------------------------------------------------

    if difference_percentage < Decimal("20"):

        score = Decimal("0")
        severity = "low"


    elif difference_percentage < Decimal("40"):

        score = Decimal("40")
        severity = "medium"


    elif difference_percentage < Decimal("70"):

        score = Decimal("70")
        severity = "high"


    else:

        score = Decimal("95")
        severity = "critical"


    # --------------------------------------------------------
    # No anomaly
    # --------------------------------------------------------

    if score == 0:

        return None


    # --------------------------------------------------------
    # Avoid duplicate open anomalies
    # --------------------------------------------------------

    existing_anomaly = ESGAnomaly.objects.filter(
        esg_data=esg_data,
        status="open"
    ).first()


    if existing_anomaly:

        return existing_anomaly


    # --------------------------------------------------------
    # Create anomaly
    # --------------------------------------------------------

    anomaly = ESGAnomaly.objects.create(

        esg_data=esg_data,

        score=score,

        severity=severity,

        message=(
            f"{esg_data.metric.name} value is "
            f"{difference_percentage:.2f}% different "
            f"from the historical average."
        ),

        expected_value=average_value,

        difference_percentage=difference_percentage,

        status="open"
    )


    return anomaly