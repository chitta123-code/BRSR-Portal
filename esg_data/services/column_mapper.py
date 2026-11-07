import re


COLUMN_ALIASES = {

    "company": [
        "company",
        "company name",
        "organization",
        "organisation",
    ],

    "business_unit": [
        "business unit",
        "business_unit",
        "unit",
        "plant",
        "facility",
    ],

    "financial_year": [
        "financial year",
        "financial_year",
        "fy",
        "fiscal year",
        "year",
    ],

    "category": [
        "category",
        "pillar",
        "esg category",
    ],

    "metric": [
        "metric",
        "indicator",
        "esg metric",
        "parameter",
        "kpi",
    ],

    "value": [
        "value",
        "amount",
        "quantity",
        "score",
    ],

    "unit": [
        "unit",
        "uom",
        "measurement unit",
    ],

    "data_source": [
        "data source",
        "data_source",
        "source",
        "source system",
    ],

    "remarks": [
        "remarks",
        "remark",
        "comments",
        "comment",
        "notes",
    ],
}


def normalize_column_name(name):

    name = str(name).strip().lower()

    name = re.sub(
        r"[^a-z0-9]+",
        " ",
        name
    )

    return name.strip()


def detect_columns(columns):

    detected = {}

    normalized_columns = {
        column: normalize_column_name(column)
        for column in columns
    }

    for standard_name, aliases in COLUMN_ALIASES.items():

        normalized_aliases = [
            normalize_column_name(alias)
            for alias in aliases
        ]

        for original, normalized in normalized_columns.items():

            if normalized in normalized_aliases:

                detected[standard_name] = original

                break

    return detected