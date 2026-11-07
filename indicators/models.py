from django.db import models


class Principle(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    def __str__(self):
        return f"Principle {self.number} - {self.name}"


class Indicator(models.Model):

    INDICATOR_TYPE_CHOICES = [
        ("ESSENTIAL", "Essential"),
        ("LEADERSHIP", "Leadership"),
    ]

    RESPONSE_TYPE_CHOICES = [
        ("TEXT", "Text"),
        ("NUMBER", "Number"),
        ("PERCENTAGE", "Percentage"),
        ("BOOLEAN", "Yes/No"),
        ("DATE", "Date"),
    ]

    principle = models.ForeignKey(
        Principle,
        on_delete=models.CASCADE,
        related_name="indicators"
    )

    indicator_code = models.CharField(
        max_length=50,
        unique=True
    )

    indicator_type = models.CharField(
        max_length=20,
        choices=INDICATOR_TYPE_CHOICES
    )

    question = models.TextField()

    mandatory = models.BooleanField(default=True)

    unit = models.CharField(
        max_length=100,
        blank=True
    )

    response_type = models.CharField(
        max_length=20,
        choices=RESPONSE_TYPE_CHOICES,
        default="TEXT"
    )

    def __str__(self):
        return f"{self.indicator_code} - {self.indicator_type}"


class IndicatorResponse(models.Model):

    indicator = models.ForeignKey(
        Indicator,
        on_delete=models.CASCADE,
        related_name="responses"
    )

    submission = models.ForeignKey(
        "reporting.BRSRSubmission",
        on_delete=models.CASCADE,
        related_name="indicator_responses"
    )

    response_text = models.TextField(
        blank=True
    )

    numeric_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True
    )

    unit = models.CharField(
        max_length=100,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    is_valid = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.submission} - {self.indicator.indicator_code}"

class ESGIndicatorMapping(models.Model):

    esg_metric = models.ForeignKey(
        "esg_data.ESGMetric",
        on_delete=models.CASCADE,
        related_name="brsr_mappings"
    )

    indicator = models.ForeignKey(
        Indicator,
        on_delete=models.CASCADE,
        related_name="esg_mappings"
    )

    mapping_type = models.CharField(
        max_length=20,
        choices=[
            ("DIRECT", "Direct"),
            ("SUPPORTING", "Supporting"),
        ],
        default="DIRECT"
    )

    notes = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.esg_metric.name} → "
            f"{self.indicator.indicator_code}"
        )