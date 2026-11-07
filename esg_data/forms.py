from django import forms
from .models import ESGData, ESGMetric
from .models import ESGEvidence
from pathlib import Path
from organization.models import Company, BusinessUnit, Project


class ESGDataForm(forms.ModelForm):
    class Meta:
        model = ESGData
        fields = [
            "business_unit",
            "financial_year",
            "metric",
            "value",
            "data_source",
            "remarks",
        ]
        widgets = {
            "business_unit": forms.Select(attrs={"class": "form-select"}),
            "financial_year": forms.TextInput(attrs={"class": "form-control", "placeholder": "2025-26"}),
            "metric": forms.Select(attrs={"class": "form-select"}),
            "value": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001"}),
            "data_source": forms.TextInput(attrs={"class": "form-control"}),
            "remarks": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["business_unit"].queryset = BusinessUnit.objects.order_by("name")
        self.fields["metric"].queryset = ESGMetric.objects.filter(is_active=True).order_by("name")


class ESGFileUploadForm(forms.Form):

    company = forms.ModelChoiceField(
        queryset=Company.objects.all().order_by("name"),
        label="Company",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_company",
            }
        )
    )

    business_unit = forms.ModelChoiceField(
        queryset=BusinessUnit.objects.none(),
        label="Business Unit",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_business_unit",
            }
        )
    )

    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        label="Project",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_project",
            }
        )
    )

    financial_year = forms.CharField(
        max_length=9,
        label="Financial Year",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "2025-26",
            }
        )
    )

    file = forms.FileField(
        label="Upload ESG File",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx,.xls,.xlsm,.csv,.pdf",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        company_id = self.data.get("company")

        if company_id:
            try:
                company_id = int(company_id)

                self.fields["business_unit"].queryset = (
                    BusinessUnit.objects
                    .filter(company_id=company_id)
                    .order_by("name")
                )

            except (TypeError, ValueError):
                pass

        business_unit_id = self.data.get("business_unit")

        if business_unit_id:
            try:
                business_unit_id = int(business_unit_id)

                self.fields["project"].queryset = (
                    Project.objects
                    .filter(business_unit_id=business_unit_id)
                    .order_by("name")
                )

            except (TypeError, ValueError):
                pass



class ESGEvidenceForm(forms.ModelForm):
    class Meta:
        model = ESGEvidence
        fields = [
            "evidence_type",
            "file",
            "description",
        ]

        widgets = {
            "evidence_type": forms.Select(
                attrs={"class": "form-select"}
            ),
            "file": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Explain how this document supports "
                        "the reported ESG value."
                    ),
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            raise forms.ValidationError(
                "Please select an evidence document."
            )

        allowed_extensions = {
            ".pdf", ".xlsx", ".xls", ".csv",
            ".doc", ".docx", ".jpg", ".jpeg", ".png"
        }

        extension = Path(uploaded_file.name).suffix.lower()

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Upload a PDF, Excel, CSV, Word or image file."
            )

        max_size = 10 * 1024 * 1024

        if uploaded_file.size > max_size:
            raise forms.ValidationError(
                "The evidence file must not exceed 10 MB."
            )

        return uploaded_file