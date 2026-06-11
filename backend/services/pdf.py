from __future__ import annotations

from io import BytesIO
from textwrap import wrap

from shared.schemas import ValidationReport


def build_report_pdf(report: ValidationReport) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        return _plain_text_report(report).encode("utf-8")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 54

    def line(text: str, *, size: int = 10, leading: int = 14) -> None:
        nonlocal y
        if y < 60:
            pdf.showPage()
            y = height - 54
        pdf.setFont("Helvetica", size)
        pdf.drawString(54, y, text)
        y -= leading

    line("VenturePilot AI Validation Report", size=16, leading=24)
    line(f"Overall Grade: {report.scores.overall_grade}", size=12, leading=18)
    line(f"Idea: {report.idea_summary}", size=10, leading=18)
    for paragraph in report.executive_summary.splitlines():
        for chunk in wrap(paragraph, 92):
            line(chunk)
        y -= 6

    line("Recommendations", size=13, leading=20)
    for index, item in enumerate(report.recommendations, start=1):
        for chunk in wrap(f"{index}. {item}", 92):
            line(chunk)

    line("Key Risks", size=13, leading=20)
    for item in report.key_risks:
        for chunk in wrap(f"- {item}", 92):
            line(chunk)

    pdf.save()
    return buffer.getvalue()


def _plain_text_report(report: ValidationReport) -> str:
    return "\n".join(
        [
            "VenturePilot AI Validation Report",
            f"Overall Grade: {report.scores.overall_grade}",
            f"Idea: {report.idea_summary}",
            "",
            report.executive_summary,
            "",
            "Recommendations:",
            *[f"{index}. {item}" for index, item in enumerate(report.recommendations, start=1)],
        ]
    )

