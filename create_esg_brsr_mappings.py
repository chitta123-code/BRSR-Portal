import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from indicators.models import ESGIndicatorMapping, Indicator
from esg_data.models import ESGMetric


mapping_data = [
    # P3 - Employee / Worker
    ("Employee Training Hours", "P3-E8", "SUPPORTING"),
    ("Employees Covered by Performance Reviews", "P3-E9", "DIRECT"),
    ("Workplace Injuries", "P3-E11", "SUPPORTING"),
    ("Lost Time Injuries", "P3-E11", "SUPPORTING"),
    ("Fatalities - Employees", "P3-E11", "SUPPORTING"),
    ("Fatalities - Workers", "P3-E11", "SUPPORTING"),
    ("Lost Workdays", "P3-E11", "SUPPORTING"),
    ("Safety Inspections", "P3-E14", "SUPPORTING"),
    ("Employees with Disabilities", "P3-E3", "SUPPORTING"),

    # P5 - Human Rights
    ("Employees Trained in Human Rights", "P5-E1", "DIRECT"),
    ("Human Rights Assessments", "P5-L2", "SUPPORTING"),

    # P6 - Environment
    ("Total Energy Consumption", "P6-E1", "DIRECT"),
    ("Electricity Consumption", "P6-E1", "SUPPORTING"),
    ("Grid Electricity Consumption", "P6-E1", "SUPPORTING"),
    ("Fuel Consumption", "P6-E1", "SUPPORTING"),
    ("Coal Consumption", "P6-E1", "SUPPORTING"),
    ("Diesel Consumption", "P6-E1", "SUPPORTING"),
    ("LPG Consumption", "P6-E1", "SUPPORTING"),
    ("Natural Gas Consumption", "P6-E1", "SUPPORTING"),
    ("Petrol Consumption", "P6-E1", "SUPPORTING"),
    ("Energy Intensity", "P6-E1", "DIRECT"),

    ("Water Withdrawal", "P6-E3", "DIRECT"),
    ("Freshwater Withdrawal", "P6-E3", "SUPPORTING"),
    ("Groundwater Withdrawal", "P6-E3", "SUPPORTING"),
    ("Municipal Water Withdrawal", "P6-E3", "SUPPORTING"),
    ("Water Consumption", "P6-E3", "DIRECT"),
    ("Water Discharge", "P6-E4", "DIRECT"),

    ("Scope 1 GHG Emissions", "P6-E7", "DIRECT"),
    ("Scope 2 GHG Emissions", "P6-E7", "DIRECT"),
    ("Scope 1 and 2 GHG Emissions", "P6-E7", "SUPPORTING"),
    ("GHG Emission Intensity", "P6-E7", "DIRECT"),

    ("Scope 3 GHG Emissions", "P6-L2", "DIRECT"),

    ("Plastic Waste Generated", "P6-E9", "DIRECT"),
    ("E-Waste Generated", "P6-E9", "DIRECT"),
    ("Construction and Demolition Waste", "P6-E9", "DIRECT"),
    ("Hazardous Waste Generated", "P6-E9", "DIRECT"),
    ("Non-Hazardous Waste Generated", "P6-E9", "DIRECT"),
    ("Total Waste Generated", "P6-E9", "DIRECT"),
    ("Waste Recycled", "P6-E9", "DIRECT"),
    ("Waste Reused", "P6-E9", "DIRECT"),
    ("Waste Incinerated", "P6-E9", "DIRECT"),
    ("Waste Sent to Landfill", "P6-E9", "DIRECT"),

    ("Environmental Compliance Rate", "P6-E13", "SUPPORTING"),
    ("Environmental Fines and Penalties", "P6-E13", "SUPPORTING"),
    ("Environmental Incidents", "P6-E13", "SUPPORTING"),

    # P8 - Community / CSR
    ("Beneficiaries of CSR Programs", "P8-L6", "SUPPORTING"),
    ("Schools Supported", "P8-L6", "SUPPORTING"),
    ("Skill Development Beneficiaries", "P8-L6", "SUPPORTING"),
    ("Healthcare Beneficiaries", "P8-L6", "SUPPORTING"),
    ("Local Community Complaints", "P8-E3", "SUPPORTING"),
]


created = 0
existing = 0
skipped = 0


for metric_name, indicator_code, mapping_type in mapping_data:

    metric = ESGMetric.objects.filter(
        name=metric_name
    ).first()

    indicator = Indicator.objects.filter(
        indicator_code=indicator_code
    ).first()

    if metric is None:
        print(f"SKIPPED - ESG metric not found: {metric_name}")
        skipped += 1
        continue

    if indicator is None:
        print(f"SKIPPED - Indicator not found: {indicator_code}")
        skipped += 1
        continue

    mapping, was_created = ESGIndicatorMapping.objects.get_or_create(
        esg_metric=metric,
        indicator=indicator,
        defaults={
            "mapping_type": mapping_type,
            "is_active": True,
        }
    )

    if was_created:
        created += 1
        print(
            f"CREATED: {metric_name} -> "
            f"{indicator_code} [{mapping_type}]"
        )
    else:
        existing += 1
        print(
            f"EXISTS: {metric_name} -> "
            f"{indicator_code} [{mapping.mapping_type}]"
        )


print()
print("================================")
print("ESG → BRSR MAPPING RESULT")
print("================================")
print("Created :", created)
print("Existing:", existing)
print("Skipped :", skipped)
print("Total   :", ESGIndicatorMapping.objects.count())
print("================================")