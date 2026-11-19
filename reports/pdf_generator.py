import io
from datetime import datetime, timezone
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

def generate_pdf_report(project_summary: Dict[str, Any]) -> bytes:
    """Generates a professional, comprehensive PDF report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    evidence_style = ParagraphStyle(
        'EvidenceText',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        fontName="Courier",
        textColor=colors.HexColor('#0F172A')
    )
    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    story = []

    # 1. Header & Title Banner
    story.append(Paragraph("PlotHole OS – Screenplay Analysis Report", title_style))
    story.append(Paragraph("Every Story Has a Logic. We Find Where It Breaks.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#38BDF8'), spaceAfter=15))

    # 2. Project Metadata Table
    title = project_summary.get("title", "Untitled Project")
    author = project_summary.get("author", "Unknown")
    genre = project_summary.get("genre", "General")
    total_scenes = project_summary.get("total_scenes", 0)
    total_chars = project_summary.get("total_characters", 0)
    total_issues = project_summary.get("total_issues", 0)
    sev_counts = project_summary.get("severity_counts", {})

    meta_data = [
        [
            Paragraph("<b>Project Title:</b>", body_style), Paragraph(str(title), body_style),
            Paragraph("<b>Analysis Date:</b>", body_style), Paragraph(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), body_style)
        ],
        [
            Paragraph("<b>Author:</b>", body_style), Paragraph(str(author), body_style),
            Paragraph("<b>Genre:</b>", body_style), Paragraph(str(genre), body_style)
        ],
        [
            Paragraph("<b>Total Scenes:</b>", body_style), Paragraph(str(total_scenes), body_style),
            Paragraph("<b>Detected Issues:</b>", body_style), Paragraph(f"<b>{total_issues}</b>", body_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[100, 170, 100, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 3. Severity Distribution Summary
    story.append(Paragraph("Executive Severity Overview", section_style))
    sev_data = [
        [
            Paragraph(f"<b>Critical:</b> {sev_counts.get('Critical', 0)}", body_style),
            Paragraph(f"<b>High:</b> {sev_counts.get('High', 0)}", body_style),
            Paragraph(f"<b>Medium:</b> {sev_counts.get('Medium', 0)}", body_style),
            Paragraph(f"<b>Low:</b> {sev_counts.get('Low', 0)}", body_style),
            Paragraph(f"<b>Informational:</b> {sev_counts.get('Informational', 0)}", body_style)
        ]
    ]
    sev_table = Table(sev_data, colWidths=[108, 108, 108, 108, 108])
    sev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#FEE2E2')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#FFEDD5')),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#FEF9C3')),
        ('BACKGROUND', (3, 0), (3, 0), colors.HexColor('#E0F2FE')),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(sev_table)
    story.append(Spacer(1, 15))

    # 4. Characters Summary
    characters = project_summary.get("characters", [])
    if characters:
        story.append(Paragraph("Key Character Intelligence", section_style))
        char_rows = [[
            Paragraph("<b>Character</b>", body_style),
            Paragraph("<b>Scenes Active</b>", body_style),
            Paragraph("<b>Dialogue Lines</b>", body_style),
            Paragraph("<b>Primary Traits & Notes</b>", body_style)
        ]]
        for c in characters[:8]:
            c_name = getattr(c, "name", c.get("name", "Unknown") if isinstance(c, dict) else "Unknown")
            c_scenes = getattr(c, "total_scenes", c.get("total_scenes", 0) if isinstance(c, dict) else 0)
            c_diag = getattr(c, "dialogue_count", c.get("dialogue_count", 0) if isinstance(c, dict) else 0)
            c_traits = getattr(c, "personality_traits", c.get("personality_traits", []) if isinstance(c, dict) else [])
            traits_str = ", ".join(c_traits[:3]) if c_traits else "Unspecified"

            char_rows.append([
                Paragraph(f"<b>{c_name}</b>", body_style),
                Paragraph(str(c_scenes), body_style),
                Paragraph(str(c_diag), body_style),
                Paragraph(traits_str, body_style)
            ])

        char_table = Table(char_rows, colWidths=[120, 80, 90, 250])
        char_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))
        story.append(char_table)
        story.append(Spacer(1, 15))

    # 5. Detected Continuity Plot Holes & Evidence
    issues = project_summary.get("issues", [])
    story.append(Paragraph("Detailed Continuity Audit & Evidence Log", section_style))

    if not issues:
        story.append(Paragraph("No continuity plot holes detected. All story logic verified intact.", body_style))
    else:
        for idx, iss in enumerate(issues):
            iss_id = getattr(iss, "issue_id", iss.get("issue_id", f"PH{idx+1:03d}") if isinstance(iss, dict) else f"PH{idx+1:03d}")
            iss_type = getattr(iss, "issue_type", iss.get("issue_type", "Plot Hole") if isinstance(iss, dict) else "Plot Hole")
            iss_title = getattr(iss, "title", iss.get("title", "") if isinstance(iss, dict) else "")
            iss_desc = getattr(iss, "description", iss.get("description", "") if isinstance(iss, dict) else "")
            iss_sev = getattr(iss, "severity", iss.get("severity", "Medium") if isinstance(iss, dict) else "Medium")
            iss_conf = getattr(iss, "confidence", iss.get("confidence", 0.85) if isinstance(iss, dict) else 0.85)
            iss_scenes = getattr(iss, "scene_references", iss.get("scene_references", []) if isinstance(iss, dict) else [])
            iss_evidence = getattr(iss, "evidence", iss.get("evidence", []) if isinstance(iss, dict) else [])
            iss_reason = getattr(iss, "reasoning", iss.get("reasoning", "") if isinstance(iss, dict) else "")
            iss_fix = getattr(iss, "suggested_fix", iss.get("suggested_fix", "") if isinstance(iss, dict) else "")

            # Color for severity badge
            sev_color_map = {
                "Critical": colors.HexColor("#DC2626"),
                "High": colors.HexColor("#EA580C"),
                "Medium": colors.HexColor("#CA8A04"),
                "Low": colors.HexColor("#0284C7"),
                "Informational": colors.HexColor("#64748B")
            }
            badge_color = sev_color_map.get(iss_sev, colors.HexColor("#0284C7"))

            evidence_items = []
            if iss_evidence:
                for ev in iss_evidence:
                    s_ref = ev.get("scene_number", "?") if isinstance(ev, dict) else "?"
                    ev_txt = ev.get("text", "") if isinstance(ev, dict) else str(ev)
                    evidence_items.append(Paragraph(f"• <b>Scene {s_ref}:</b> \"{ev_txt}\"", evidence_style))
            else:
                evidence_items.append(Paragraph("No direct quote excerpt available.", evidence_style))

            issue_table_data = [
                [
                    Paragraph(f"<b>[{iss_id}] {iss_title}</b>", ParagraphStyle('IH', parent=body_style, fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor('#0F172A'))),
                    Paragraph(f"<b>{iss_sev.upper()} ({int(iss_conf*100)}%)</b>", ParagraphStyle('SevBadge', parent=badge_style, textColor=badge_color, alignment=2))
                ],
                [
                    Paragraph(f"<b>Category:</b> {iss_type} | <b>Scenes:</b> {', '.join(map(str, iss_scenes))}", body_style),
                    Paragraph("", body_style)
                ],
                [
                    Paragraph(f"<b>Contradiction:</b> {iss_desc}", body_style),
                    Paragraph("", body_style)
                ],
                [
                    Paragraph("<b>Verified Script Evidence:</b>", body_style),
                    Paragraph("", body_style)
                ],
                [
                    evidence_items,
                    Paragraph("", body_style)
                ],
                [
                    Paragraph(f"<b>Reasoning:</b> {iss_reason}", body_style),
                    Paragraph("", body_style)
                ],
                [
                    Paragraph(f"<b>Suggested Fix:</b> {iss_fix}", ParagraphStyle('FixText', parent=body_style, textColor=colors.HexColor('#0284C7'))),
                    Paragraph("", body_style)
                ]
            ]

            card = Table(issue_table_data, colWidths=[420, 120])
            card.setStyle(TableStyle([
                ('SPAN', (0, 1), (1, 1)),
                ('SPAN', (0, 2), (1, 2)),
                ('SPAN', (0, 3), (1, 3)),
                ('SPAN', (0, 4), (1, 4)),
                ('SPAN', (0, 5), (1, 5)),
                ('SPAN', (0, 6), (1, 6)),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8)
            ]))

            story.append(KeepTogether([card, Spacer(1, 10)]))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
