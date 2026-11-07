from django.core.management.base import BaseCommand

from organization.models import Company, BusinessUnit
from esg_data.models import ESGMetric


class Command(BaseCommand):

    help = "Create synthetic ESG master data for testing"

    def handle(self, *args, **options):

        # -------------------------------------------------
        # COMPANY
        # -------------------------------------------------

        company, created = Company.objects.get_or_create(
            name="Megha Engineering & Infrastructures Limited (Synthetic)",
            defaults={
                "reporting_boundary": "consolidated",
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("Created synthetic company")
            )
        else:
            self.stdout.write(
                "Synthetic company already exists"
            )

        # -------------------------------------------------
        # BUSINESS UNITS
        # -------------------------------------------------

        business_units = [
            "Main Manufacturing Plant",
            "Infrastructure Projects Division",
            "Renewable Energy Unit",
            "Water Infrastructure Unit",
        ]

        for name in business_units:

            obj, created = BusinessUnit.objects.get_or_create(
                company=company,
                name=name,
                defaults={
                    "location": "India",
                    "description": "Synthetic ESG demonstration business unit",
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created Business Unit: {name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Business Unit already exists: {name}"
                )

        # -------------------------------------------------
        # ESG METRICS
        # -------------------------------------------------

        metrics = [

            # ENVIRONMENTAL
            ("Electricity Consumption", "environmental", "MWh"),
            ("Renewable Electricity Consumption", "environmental", "MWh"),
            ("Grid Electricity Consumption", "environmental", "MWh"),
            ("Diesel Consumption", "environmental", "KL"),
            ("Petrol Consumption", "environmental", "KL"),
            ("Natural Gas Consumption", "environmental", "MSCM"),
            ("LPG Consumption", "environmental", "MT"),
            ("Coal Consumption", "environmental", "MT"),
            ("Total Energy Consumption", "environmental", "GJ"),
            ("Energy Intensity", "environmental", "GJ/crore INR"),
            ("Renewable Energy Share", "environmental", "%"),
            ("Scope 1 GHG Emissions", "environmental", "tCO2e"),
            ("Scope 2 GHG Emissions", "environmental", "tCO2e"),
            ("Scope 1 and 2 GHG Emissions", "environmental", "tCO2e"),
            ("GHG Emission Intensity", "environmental", "tCO2e/crore INR"),
            ("Scope 3 GHG Emissions", "environmental", "tCO2e"),
            ("Total GHG Emissions", "environmental", "tCO2e"),
            ("CO2 Emissions from Stationary Combustion", "environmental", "tCO2e"),
            ("CO2 Emissions from Mobile Combustion", "environmental", "tCO2e"),
            ("Fugitive Emissions", "environmental", "tCO2e"),
            ("Purchased Electricity Emissions", "environmental", "tCO2e"),
            ("Business Travel Emissions", "environmental", "tCO2e"),
            ("Employee Commuting Emissions", "environmental", "tCO2e"),
            ("Upstream Transportation Emissions", "environmental", "tCO2e"),
            ("Downstream Transportation Emissions", "environmental", "tCO2e"),
            ("Water Withdrawal", "environmental", "KL"),
            ("Water Consumption", "environmental", "KL"),
            ("Water Discharge", "environmental", "KL"),
            ("Water Recycled or Reused", "environmental", "KL"),
            ("Water Recycling Rate", "environmental", "%"),
            ("Freshwater Withdrawal", "environmental", "KL"),
            ("Groundwater Withdrawal", "environmental", "KL"),
            ("Municipal Water Withdrawal", "environmental", "KL"),
            ("Rainwater Harvested", "environmental", "KL"),
            ("Wastewater Treated", "environmental", "KL"),
            ("Hazardous Waste Generated", "environmental", "MT"),
            ("Non-Hazardous Waste Generated", "environmental", "MT"),
            ("Total Waste Generated", "environmental", "MT"),
            ("Waste Recycled", "environmental", "MT"),
            ("Waste Reused", "environmental", "MT"),
            ("Waste Sent to Landfill", "environmental", "MT"),
            ("Waste Incinerated", "environmental", "MT"),
            ("Hazardous Waste Recycled", "environmental", "MT"),
            ("E-Waste Generated", "environmental", "MT"),
            ("E-Waste Recycled", "environmental", "MT"),
            ("Plastic Waste Generated", "environmental", "MT"),
            ("Plastic Waste Recycled", "environmental", "MT"),
            ("Construction and Demolition Waste", "environmental", "MT"),
            ("Fly Ash Generated", "environmental", "MT"),
            ("Fly Ash Utilized", "environmental", "MT"),
            ("Waste Diversion Rate", "environmental", "%"),
            ("Air Emission Monitoring Points", "environmental", "count"),
            ("Environmental Incidents", "environmental", "count"),
            ("Environmental Fines and Penalties", "environmental", "INR lakh"),
            ("Environmental Compliance Rate", "environmental", "%"),
            ("ISO 14001 Certified Sites", "environmental", "count"),

            # SOCIAL
            ("Total Employees", "social", "persons"),
            ("Permanent Employees", "social", "persons"),
            ("Temporary Employees", "social", "persons"),
            ("Male Employees", "social", "persons"),
            ("Female Employees", "social", "persons"),
            ("Women in Workforce", "social", "%"),
            ("Employees Under 30", "social", "persons"),
            ("Employees Aged 30-50", "social", "persons"),
            ("Employees Above 50", "social", "persons"),
            ("Employees with Disabilities", "social", "persons"),
            ("New Hires", "social", "persons"),
            ("Employee Turnover", "social", "%"),
            ("Voluntary Turnover", "social", "%"),
            ("Involuntary Turnover", "social", "%"),
            ("Average Training Hours per Employee", "social", "hours/person"),
            ("Total Training Hours", "social", "hours"),
            ("Technical Training Hours", "social", "hours"),
            ("Safety Training Hours", "social", "hours"),
            ("Ethics Training Hours", "social", "hours"),
            ("Leadership Training Hours", "social", "hours"),
            ("Employees Trained in Human Rights", "social", "persons"),
            ("Employees Covered by Performance Reviews", "social", "%"),
            ("Employee Engagement Score", "social", "%"),
            ("Workplace Injuries", "social", "cases"),
            ("Lost Time Injuries", "social", "cases"),
            ("Lost Time Injury Frequency Rate", "social", "per million hours"),
            ("Total Recordable Injury Rate", "social", "per million hours"),
            ("Fatalities - Employees", "social", "cases"),
            ("Fatalities - Workers", "social", "cases"),
            ("Lost Workdays", "social", "days"),
            ("Near Miss Incidents", "social", "cases"),
            ("Safety Inspections", "social", "count"),
            ("Safety Training Completion", "social", "%"),
            ("Occupational Health Checkups", "social", "persons"),
            ("Health and Safety Committees", "social", "count"),
            ("Grievances Received", "social", "cases"),
            ("Grievances Resolved", "social", "cases"),
            ("Grievance Resolution Rate", "social", "%"),
            ("Human Rights Assessments", "social", "count"),
            ("Human Rights Incidents", "social", "cases"),
            ("Community Investment", "social", "INR crore"),
            ("CSR Expenditure", "social", "INR crore"),
            ("CSR Projects", "social", "count"),
            ("Beneficiaries of CSR Programs", "social", "persons"),
            ("Schools Supported", "social", "count"),
            ("Healthcare Beneficiaries", "social", "persons"),
            ("Skill Development Beneficiaries", "social", "persons"),
            ("Local Community Complaints", "social", "cases"),
            ("Local Hiring Rate", "social", "%"),
            ("Women in Management", "social", "%"),
            ("Women in Senior Management", "social", "%"),
            ("Women in Board", "social", "%"),

            # GOVERNANCE
            ("Board Meetings", "governance", "meetings"),
            ("Board Attendance Rate", "governance", "%"),
            ("Independent Directors", "governance", "persons"),
            ("Total Directors", "governance", "persons"),
            ("Women Directors", "governance", "persons"),
            ("Board Diversity Rate", "governance", "%"),
            ("Audit Committee Meetings", "governance", "meetings"),
            ("Nomination and Remuneration Committee Meetings", "governance", "meetings"),
            ("CSR Committee Meetings", "governance", "meetings"),
            ("Risk Management Committee Meetings", "governance", "meetings"),
            ("Ethics Committee Meetings", "governance", "meetings"),
            ("Compliance Training Completion", "governance", "%"),
            ("Employees Covered by Code of Conduct", "governance", "%"),
            ("Board Members Covered by Code of Conduct", "governance", "%"),
            ("Whistleblower Complaints", "governance", "cases"),
            ("Whistleblower Complaints Resolved", "governance", "cases"),
            ("Confirmed Corruption Incidents", "governance", "cases"),
            ("Confirmed Ethics Violations", "governance", "cases"),
            ("Data Privacy Incidents", "governance", "cases"),
            ("Cybersecurity Incidents", "governance", "cases"),
            ("Regulatory Non-Compliance Cases", "governance", "cases"),
            ("Regulatory Fines and Penalties", "governance", "INR lakh"),
            ("Supplier Assessments", "governance", "count"),
            ("Suppliers Screened for ESG", "governance", "count"),
            ("Suppliers with ESG Corrective Actions", "governance", "count"),
            ("Suppliers Audited", "governance", "count"),
            ("Responsible Procurement Spend", "governance", "INR crore"),
            ("ESG Supplier Coverage", "governance", "%"),
            ("Internal Audits Completed", "governance", "count"),
            ("External Audits Completed", "governance", "count"),
            ("Audit Findings", "governance", "count"),
            ("Audit Findings Closed", "governance", "count"),
            ("Risk Assessments Completed", "governance", "count"),
            ("Material ESG Issues", "governance", "count"),
            ("Material ESG Issues Resolved", "governance", "count"),
            ("Policy Reviews Completed", "governance", "count"),
            ("ESG Policies in Force", "governance", "count"),
            ("BRSR Indicators Reported", "governance", "count"),
            ("BRSR Data Points Collected", "governance", "count"),
            ("Assurance Coverage", "governance", "%"),
        ]

        created_count = 0
        existing_count = 0

        for name, category, unit in metrics:

            obj, created = ESGMetric.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "unit": unit,
                    "description": f"Synthetic {category} ESG metric for demonstration",
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"ESG metrics created: {created_count}"
            )
        )

        self.stdout.write(
            f"ESG metrics already existing: {existing_count}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Synthetic ESG master data setup completed."
            )
        )