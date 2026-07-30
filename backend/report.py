from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_report(
    output_path: Path,
    filename: str,
    score: int,
    matched_skills: list[str],
    missing_skills: list[str],
    suggestions: list[str],
) -> str:
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=27,
        textColor=colors.HexColor("#1F3A5F"),
        spaceAfter=14,
    )

    section_style = ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1F3A5F"),
        spaceBefore=12,
        spaceAfter=7,
    )

    normal_style = ParagraphStyle(
        name="BodyTextCustom",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=4,
    )

    score_color = (
        "#15803D" if score >= 70
        else "#D97706" if score >= 40
        else "#B91C1C"
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="ATS Resume Report",
        author="ATS Resume Analyzer",
    )

    elements = []

    elements.append(
        Paragraph("ATS Resume Analysis Report", title_style)
    )

    information = [
        [
            Paragraph("<b>Resume</b>", normal_style),
            Paragraph(escape(filename), normal_style),
        ],
        [
            Paragraph("<b>Generated On</b>", normal_style),
            Paragraph(
                datetime.now().strftime("%d %B %Y, %I:%M %p"),
                normal_style,
            ),
        ],
    ]

    info_table = Table(
        information,
        colWidths=[40 * mm, 105 * mm]
    )

    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8EEF7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2E2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    elements.append(info_table)
    elements.append(Spacer(1, 14))

    score_table = Table(
        [
            [
                Paragraph(
                    f"<b>ATS Match Score</b><br/>"
                    f"<font size='24' color='{score_color}'>{score}%</font>",
                    ParagraphStyle(
                        name="Score",
                        parent=normal_style,
                        alignment=TA_CENTER,
                        leading=28,
                    ),
                )
            ]
        ],
        colWidths=[145 * mm],
    )

    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F7FB")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#C7D2E2")),
                ("TOPPADDING", (0, 0), (-1, -1), 15),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
            ]
        )
    )

    elements.append(score_table)

    elements.append(
        Paragraph("Matched Skills", section_style)
    )

    if matched_skills:
        for skill in matched_skills:
            elements.append(
                Paragraph(
                    f"&#10003; {escape(skill)}",
                    normal_style
                )
            )
    else:
        elements.append(
            Paragraph("No matched skills detected.", normal_style)
        )

    elements.append(
        Paragraph("Missing Skills", section_style)
    )

    if missing_skills:
        for skill in missing_skills:
            elements.append(
                Paragraph(
                    f"&#8226; {escape(skill)}",
                    normal_style
                )
            )
    else:
        elements.append(
            Paragraph(
                "No important skills are missing.",
                normal_style
            )
        )

    elements.append(
        Paragraph("Recommendations", section_style)
    )

    for suggestion in suggestions:
        elements.append(
            Paragraph(
                f"&#8226; {escape(suggestion)}",
                normal_style
            )
        )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Note: This score is based on detected skills and keyword "
            "matching. It is not an official score from any employer's ATS.",
            ParagraphStyle(
                name="Disclaimer",
                parent=normal_style,
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#64748B"),
            ),
        )
    )

    doc.build(elements)

    return str(output_path)
