import pandas as pd
from pathlib import Path


SUPPORTED_EXCEL = [".xlsx", ".xls", ".xlsm"]
SUPPORTED_CSV = [".csv"]
SUPPORTED_PDF = [".pdf"]


def read_esg_file(uploaded_file):
    """
    Read an uploaded Excel, CSV, or text-based PDF file.

    Returns:
    
        dataframe, error_message
    """

    filename = uploaded_file.name
    extension = Path(filename).suffix.lower()

    try:
        if extension in SUPPORTED_EXCEL:
            df = pd.read_excel(
                uploaded_file,
                sheet_name=0
            )

        elif extension in SUPPORTED_CSV:
            df = pd.read_csv(uploaded_file)

        elif extension in SUPPORTED_PDF:
            return None, (
                "PDF upload is not yet supported for automatic "
                "data extraction. Please convert the PDF table "
                "to Excel or CSV first. PDF evidence can be "
                "uploaded separately for verification."
            )

        else:
            return None, (
                "Unsupported file type. "
                "Please upload XLSX, XLS, XLSM or CSV."
            )

        # Remove completely empty rows and columns
        df = df.dropna(how="all")
        df = df.dropna(axis=1, how="all")

        # Clean column names
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # Reject files with no usable data
        if df.empty or len(df.columns) == 0:
            return None, (
                "The uploaded file contains no usable data."
            )

        return df, None

    except Exception as e:
        return None, (
            f"Could not read the uploaded file: {e}"
        )

