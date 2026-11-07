from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from audit_trail.models import AuditLog
from esg_data.models import ESGData, ESGMetric
from organization.models import BusinessUnit, Company


class ESGReviewAuditTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="secret123",
        )

        self.company = Company.objects.create(
            name="Test Company",
        )

        self.business_unit = BusinessUnit.objects.create(
            company=self.company,
            name="Operations",
        )

        self.metric = ESGMetric.objects.create(
            name="Energy Consumption",
            category="environmental",
            unit="kWh",
        )

        self.esg_data = ESGData.objects.create(
            business_unit=self.business_unit,
            metric=self.metric,
            financial_year="2024",
            value=100.5,
            status="under_review",
        )

    def test_reject_action_records_audit_log(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("review_esg_data", args=[self.esg_data.pk]),
            {"action": "reject"},
        )

        self.esg_data.refresh_from_db()

        self.assertRedirects(response, reverse("esg_review_dashboard"))
        self.assertEqual(self.esg_data.status, "rejected")
        self.assertTrue(
            AuditLog.objects.filter(
                action="REJECT",
                actor=self.user,
                object_pk=str(self.esg_data.pk),
            ).exists()
        )
