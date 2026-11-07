from decimal import Decimal

from django.core.management.base import BaseCommand

from organization.models import BusinessUnit
from esg_data.models import ESGMetric, ESGData


class Command(BaseCommand):

    help = "Create multi-year ESG data for anomaly detection testing"

    def handle(self, *args, **kwargs):

        # ----------------------------------------------------
        # Find Business Unit
        # ----------------------------------------------------

        business_unit = BusinessUnit.objects.filter(
            name="Main Plant"
        ).first()

        if not business_unit:

            business_unit = BusinessUnit.objects.first()

        if not business_unit:

            self.stdout.write(
                self.style.ERROR(
                    "No Business Unit found."
                )
            )

            return


        # ----------------------------------------------------
        # Find metrics
        # ----------------------------------------------------

        test_metrics = {
            "Electricity Consumption": [
                ("2023-24", "125000"),
                ("2024-25", "128000"),
                ("2025-26", "250000"),
            ],

            "Water Consumption": [
                ("2023-24", "9000"),
                ("2024-25", "9400"),
                ("2025-26", "18000"),
            ],

            "Employee Turnover": [
                ("2023-24", "7"),
                ("2024-25", "8"),
                ("2025-26", "45"),
            ],

            "CO2 Emissions": [
                ("2023-24", "4700"),
                ("2024-25", "4850"),
                ("2025-26", "15000"),
            ],
        }


        created_count = 0


        # ----------------------------------------------------
        # Create records
        # ----------------------------------------------------

        for metric_name, yearly_values in test_metrics.items():

            metric = ESGMetric.objects.filter(
                name=metric_name
            ).first()

            if not metric:

                self.stdout.write(
                    self.style.WARNING(
                        f"Metric not found: {metric_name}"
                    )
                )

                continue


            for financial_year, value in yearly_values:

                obj, created = ESGData.objects.update_or_create(

                    business_unit=business_unit,

                    metric=metric,

                    financial_year=financial_year,

                    defaults={
                        "value": Decimal(value),
                        "data_source": "Synthetic Historical Test Data",
                        "remarks": "Created for anomaly detection testing",
                        "status": "approved",
                        "entered_by": "system",
                    }

                )

                if created:

                    created_count += 1


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} historical ESG records."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Anomaly test data is ready."
            )
        )