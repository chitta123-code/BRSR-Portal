from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from reporting.services.brsr_report_service import get_brsr_report_data


def generate_brsr_pdf(submission):

    report = get_brsr_report_data(submission)

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "BRSRTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "BRSRHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=10,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "BRSRNormal",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
    )

    small_style = ParagraphStyle(
        "BRSRSmall",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=10,
    )

    story = []

    # -------------------------------------------------
    # TITLE
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Business Responsibility and Sustainability Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Financial Year:</b> {report['financial_year']}",
            normal_style,
        )
    )

    story.append(Spacer(1, 8))

    # -------------------------------------------------
    # COMPANY INFORMATION
    # -------------------------------------------------

    story.append(
        Paragraph(
            "1. Company Information",
            heading_style,
        )
    )

    company_name = report["company"].name

    business_unit = (
        report["business_unit"].name
        if report["business_unit"]
        else "Not specified"
    )

    project = (
        report["project"].name
        if report["project"]
        else "Not specified"
    )

    company_data = [
        ["Company", company_name],
        ["Financial Year", report["financial_year"]],
        ["Business Unit", business_unit],
        ["Project", project],
        ["Submission Status", report["status"]],
        [
            "Completion",
            f"{report['completion_percentage']}%",
        ],
        [
            "Total Responses",
            str(report["total_responses"]),
        ],
    ]

    company_table = Table(
        company_data,
        colWidths=[45 * mm, 125 * mm],
    )

    company_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(company_table)

    story.append(Spacer(1, 15))

    # -------------------------------------------------
    # PRINCIPLES
    # -------------------------------------------------

    story.append(
        Paragraph(
            "2. BRSR Principle-wise Responses",
            heading_style,
        )
    )

    for principle_number, principle_data in report["principles"].items():

        story.append(
            Paragraph(
                f"Principle {principle_number}: "
                f"{principle_data['name']}",
                heading_style,
            )
        )

        if principle_data["description"]:
            story.append(
                Paragraph(
                    principle_data["description"],
                    normal_style,
                )
            )

            story.append(Spacer(1, 6))

        table_data = [
            [
                "Code",
                "Type",
                "Question",
                "Response",
                "Unit",
                "Valid",
            ]
        ]

        for indicator in principle_data["indicators"]:

            response = indicator["response"]

            if not response and indicator["numeric_value"] is not None:
                response = str(indicator["numeric_value"])

            if not response:
                response = "No response"

            valid_text = (
                "Yes"
                if indicator["is_valid"]
                else "No"
            )

            table_data.append(
                [
                    Paragraph(
                        str(indicator["code"]),
                        small_style,
                    ),
                    Paragraph(
                        str(indicator["type"]),
                        small_style,
                    ),
                    Paragraph(
                        str(indicator["question"]),
                        small_style,
                    ),
                    Paragraph(
                        str(response),
                        small_style,
                    ),
                    Paragraph(
                        str(indicator["unit"] or "-"),
                        small_style,
                    ),
                    Paragraph(
                        valid_text,
                        small_style,
                    ),
                ]
            )

        response_table = Table(
            table_data,
            colWidths=[
                18 * mm,
                23 * mm,
                57 * mm,
                40 * mm,
                17 * mm,
                15 * mm,
            ],
            repeatRows=1,
        )

        response_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.grey,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(response_table)
        story.append(Spacer(1, 12))

    # -------------------------------------------------
    # FOOTER / END
    # -------------------------------------------------

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Generated from the approved BRSR submission "
            "in the ESG/BRSR Management Portal.",
            normal_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer