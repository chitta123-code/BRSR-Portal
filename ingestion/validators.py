import math


REQUIRED_COLUMNS = [
    "metric",
    "value",
]


def validate_dataframe(dataframe, detected_columns):
    """
    Validate extracted ESG data before database import.

    Returns:
        errors
        warnings
        valid_rows
    """

    errors = []
    warnings = []
    valid_rows = []

    # -------------------------------------------------
    # 1. Required columns
    # -------------------------------------------------

    for required_column in REQUIRED_COLUMNS:

        if required_column not in detected_columns:

            errors.append(
                f"Required column '{required_column}' "
                f"could not be detected."
            )

    if errors:
        return errors, warnings, valid_rows

    metric_column = detected_columns["metric"]
    value_column = detected_columns["value"]

    # -------------------------------------------------
    # 2. Validate every row
    # -------------------------------------------------

    for index, row in dataframe.iterrows():

        excel_row = index + 2

        metric = row.get(metric_column)
        value = row.get(value_column)

        # ---------------------------------------------
        # Missing metric
        # ---------------------------------------------

        if (
            metric is None
            or str(metric).strip() == ""
            or str(metric).lower() == "nan"
        ):

            errors.append(
                f"Row {excel_row}: ESG metric is missing."
            )

            continue

        # ---------------------------------------------
        # Missing value
        # ---------------------------------------------

        if (
            value is None
            or str(value).strip() == ""
            or str(value).lower() == "nan"
        ):

            errors.append(
                f"Row {excel_row}: value is missing "
                f"for metric '{metric}'."
            )

            continue

        # ---------------------------------------------
        # Numeric value
        # ---------------------------------------------

        try:

            numeric_value = float(value)

            if not math.isfinite(numeric_value):

                errors.append(
                    f"Row {excel_row}: invalid numeric "
                    f"value for '{metric}'."
                )

                continue

        except (ValueError, TypeError):

            errors.append(
                f"Row {excel_row}: value '{value}' "
                f"for '{metric}' is not numeric."
            )

            continue

        # ---------------------------------------------
        # Negative values
        # ---------------------------------------------

        if numeric_value < 0:

            warnings.append(
                f"Row {excel_row}: '{metric}' has a "
                f"negative value ({numeric_value}). "
                f"Please verify the source data."
            )

        # ---------------------------------------------
        # Valid row
        # ---------------------------------------------

        valid_rows.append(
            {
                "row_number": excel_row,
                "metric": str(metric).strip(),
                "value": numeric_value,
                "unit": (
                    str(
                        row.get(
                            detected_columns.get("unit"),
                            ""
                        )
                    ).strip()
                    if detected_columns.get("unit")
                    else ""
                ),
            }
        )

    return errors, warnings, valid_rows