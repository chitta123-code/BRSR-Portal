import re

from organization.models import BusinessUnit
from esg_data.models import ESGMetric


def normalize_text(value):
    if value is None:
        return ""

    text = str(value).strip().lower()

    # Standardize company-name variations
    text = text.replace("&", " and ")
    text = text.replace(" ltd.", " limited")
    text = text.replace(" ltd", " limited")

    # Remove extra spaces
    text = " ".join(text.split())

    return text


def normalize_business_unit(value):
    if value is None:
        return ""

    text = normalize_text(value)

    # Excel/demo name -> database name
    aliases = {
        "main plant": "main manufacturing plant",
    }

    return aliases.get(text, text)


def match_business_unit(company_name, business_unit_name):

    if not company_name or not business_unit_name:
        return None

    company_normalized = normalize_text(company_name)
    bu_normalized = normalize_business_unit(business_unit_name)

    for business_unit in BusinessUnit.objects.select_related("company").all():

        if not business_unit.company:
            continue

        db_company = normalize_text(
            business_unit.company.name
        )

        db_bu = normalize_business_unit(
            business_unit.name
        )

        if (
            db_company == company_normalized
            and db_bu == bu_normalized
        ):
            return business_unit

    return None


def match_esg_metric(metric_name):

    if not metric_name:
        return None

    metric_normalized = normalize_text(metric_name)

    for metric in ESGMetric.objects.all():

        db_metric = normalize_text(metric.name)

        if db_metric == metric_normalized:
            return metric

    return None


def match_row(row):

    company_name = row.get("company")
    business_unit_name = row.get("business_unit")
    metric_name = row.get("metric")

    business_unit = match_business_unit(
        company_name,
        business_unit_name
    )

    metric = match_esg_metric(
        metric_name
    )

    return {
        "business_unit": business_unit,
        "metric": metric,
        "business_unit_matched": business_unit is not None,
        "metric_matched": metric is not None,
    }


def match_all_rows(df, company_name=None):

    results = []

    for _, row in df.iterrows():

        row_dict = {}

        for key, value in row.to_dict().items():

            normalized_key = (
                str(key)
                .strip()
                .lower()
                .replace(" ", "_")
            )

            row_dict[normalized_key] = value

        row_company = row_dict.get("company")

        if not row_company and company_name:
            row_company = company_name

        result = match_row({
            **row_dict,
            "company": row_company,
        })

        results.append({
            **row_dict,
            **result,
        })

    return results