import re
from pathlib import Path
from decimal import Decimal, InvalidOperation

from pypdf import PdfReader


def extract_pdf_text(file_path):
    """Extract selectable text from a PDF."""
    reader = PdfReader(str(file_path))

    return "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).strip()


def normalize_text(value):
    """Normalize text for basic comparisons."""
    return re.sub(
        r"\s+",
        " ",
        str(value or "")
    ).strip().casefold()


def number_exists(number, text):
    """Check whether a complete numeric value exists in text."""
    try:
        expected = Decimal(str(number))
    except (InvalidOperation, TypeError, ValueError):
        return False

    # Find numeric tokens, including optional comma separators.
    tokens = re.findall(
        r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?"
        r"(?![\w.])",
        text
    )

    for token in tokens:
        try:
            actual = Decimal(token.replace(",", ""))
            if actual == expected:
                return True
        except InvalidOperation:
            continue

    return False


def match_evidence_to_esg(evidence):
    """
    Compare extracted PDF text with the linked ESG record.

    This is a basic consistency check, not proof of authenticity.
    Human verification is still required.
    """
    esg_data = evidence.esg_data

    try:
        filename = (
            getattr(evidence, "original_filename", "")
            or Path(evidence.file.name).name
        )
    except Exception:
        filename = getattr(evidence, "original_filename", "")

    result = {
        "filename": filename,
        "checks": [],
        "overall_status": "needs_review",
        "extracted_text": "",
        "message": "",
    }

    try:
        if not evidence.file:
            result["message"] = "No evidence file is attached."
            return result

        text = extract_pdf_text(evidence.file.path)

    except Exception as exc:
        result["message"] = f"Could not read PDF: {exc}"
        return result

    result["extracted_text"] = text[:10000]

    if not text:
        result["message"] = (
            "No selectable text found. The PDF may be scanned "
            "and require OCR or manual review."
        )
        return result

    normalized_text = normalize_text(text)

    # 1. Metric name
    metric_name = (
        str(esg_data.metric)
        if esg_data.metric_id
        else ""
    )

    metric_match = (
        bool(metric_name)
        and normalize_text(metric_name) in normalized_text
    )

    result["checks"].append({
        "name": "Metric name",
        "expected": metric_name or "Not specified",
        "matched": metric_match,
    })

    # 2. Financial year
    year = str(esg_data.financial_year or "").strip()

    year_variants = {
        normalize_text(year),
        normalize_text(year.replace("-", "–")),
        normalize_text(year.replace("-", "/")),
    }

    year_match = (
        bool(year)
        and any(
            variant in normalized_text
            for variant in year_variants
            if variant
        )
    )

    result["checks"].append({
        "name": "Financial year",
        "expected": year or "Not specified",
        "matched": year_match,
    })

    # 3. Numeric value
    value = esg_data.value

    number_match = (
        value is not None
        and number_exists(value, text)
    )

    result["checks"].append({
        "name": "Reported value",
        "expected": str(value),
        "matched": number_match,
    })

    # 4. Unit
    unit = (
        str(esg_data.metric.unit or "").strip()
        if esg_data.metric_id
        else ""
    )

    unit_match = (
        bool(unit)
        and normalize_text(unit) in normalized_text
    )

    result["checks"].append({
        "name": "Unit",
        "expected": unit or "Not specified",
        "matched": unit_match,
    })

    # A missing unit must not be counted as a successful match.
    matched_count = sum(
        1
        for check in result["checks"]
        if check["matched"]
    )

    if matched_count == len(result["checks"]):
        result["overall_status"] = "matched"
        result["message"] = (
            "All basic text checks matched. Human verification "
            "is still required."
        )

    elif matched_count == 0:
        result["overall_status"] = "mismatched"
        result["message"] = (
            "No basic checks matched. Review the PDF and ESG record."
        )

    else:
        result["overall_status"] = "needs_review"
        result["message"] = (
            "Some checks matched and others did not. "
            "Manual review is required."
        )

    return result

