from reporting.models import BRSRSubmission


def get_brsr_report_data(submission):

    if submission.status != "APPROVED":
        raise ValueError(
            "Only approved BRSR submissions can generate a report."
        )

    responses = (
        submission.indicator_responses
        .select_related("indicator", "indicator__principle")
        .order_by(
            "indicator__principle__number",
            "indicator__indicator_code"
        )
    )

    principles = {}

    for response in responses:

        principle = response.indicator.principle
        principle_number = principle.number

        if principle_number not in principles:
            principles[principle_number] = {
                "number": principle.number,
                "name": principle.name,
                "description": principle.description,
                "indicators": [],
            }

        principles[principle_number]["indicators"].append({
            "code": response.indicator.indicator_code,
            "type": response.indicator.indicator_type,
            "question": response.indicator.question,
            "mandatory": response.indicator.mandatory,
            "response_type": response.indicator.response_type,
            "unit": response.unit or response.indicator.unit,
            "response": response.response_text,
            "numeric_value": response.numeric_value,
            "remarks": response.remarks,
            "is_valid": response.is_valid,
        })

    return {
        "submission": submission,
        "company": submission.company,
        "business_unit": submission.business_unit,
        "project": submission.project,
        "reporting_period": submission.reporting_period,
        "financial_year": submission.reporting_period.financial_year,
        "status": submission.status,
        "completion_percentage": submission.completion_percentage,
        "principles": principles,
        "total_responses": responses.count(),
    }