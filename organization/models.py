from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200)
    cin = models.CharField(max_length=50, blank=True)
    year_of_incorporation = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    registered_office = models.TextField(blank=True)
    corporate_address = models.TextField(blank=True)

    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)

    REPORTING_BOUNDARY_CHOICES = [
        ("standalone", "Standalone"),
        ("consolidated", "Consolidated"),
    ]

    reporting_boundary = models.CharField(
        max_length=20,
        choices=REPORTING_BOUNDARY_CHOICES,
        default="standalone"
    )

    assurance_provider = models.CharField(
        max_length=200,
        blank=True
    )

    assurance_type = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Subsidiary(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="subsidiaries"
    )

    name = models.CharField(max_length=200)
    cin = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class BusinessUnit(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="business_units"
    )

    subsidiary = models.ForeignKey(
        Subsidiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business_units"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    head_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Project(models.Model):
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    name = models.CharField(max_length=200)
    project_code = models.CharField(
        max_length=100,
        unique=True
    )

    location = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    def __str__(self):
        return f"{self.project_code} - {self.name}"

