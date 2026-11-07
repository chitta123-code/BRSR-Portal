from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "company": [
        "company",
        "company name",
        "organisation",
        "organization",
        "entity",
    ],
    "business_unit": [
        "business unit",
        "business_unit",
        "bu",
        "unit",
    ],
    "project": [
        "project",
        "project name",
        "project_name",
    ],
    "financial_year": [
        "financial year",
        "financial_year",
        "fy",
        "year",
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
        "result",
        "actual",
    ],
    "unit": [
        "unit",
        "uom",
        "measurement unit",
    ],
}


def normalize_column_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def detect_columns(dataframe):
    """
    Try to identify important ESG columns automatically.
    """

    detected = {}
    normalized_columns = {}

    for column in dataframe.columns:
        normalized = normalize_column_name(column)
        normalized_columns[column] = normalized

    for standard_name, aliases in COLUMN_ALIASES.items():

        for original_column, normalized in normalized_columns.items():

            if normalized in aliases:
                detected[standard_name] = original_column
                break

    return detected


def clean_dataframe(dataframe):

    dataframe = dataframe.dropna(
        how="all"
    )

    dataframe = dataframe.dropna(
        axis=1,
        how="all"
    )

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    for column in dataframe.columns:

        if dataframe[column].dtype == "object":

            dataframe[column] = (
                dataframe[column]
                .astype(str)
                .str.strip()
            )

    return dataframe.reset_index(drop=True)


def extract_excel(path):

    workbook = pd.ExcelFile(path)

    sheets = {}

    for sheet_name in workbook.sheet_names:

        dataframe = pd.read_excel(
            path,
            sheet_name=sheet_name
        )

        dataframe = clean_dataframe(dataframe)

        sheets[sheet_name] = {
            "dataframe": dataframe,
            "columns": detect_columns(dataframe),
            "rows": len(dataframe),
        }

    return sheets


def extract_csv(path):

    dataframe = pd.read_csv(path)

    dataframe = clean_dataframe(dataframe)

    return {
        "CSV": {
            "dataframe": dataframe,
            "columns": detect_columns(dataframe),
            "rows": len(dataframe),
        }
    }


def extract_file_data(file_path):

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension in [".xlsx", ".xls"]:
        return extract_excel(path)

    if extension == ".csv":
        return extract_csv(path)

    raise ValueError(
        "Automatic extraction currently supports "
        "Excel and CSV files."
    )