import os
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)

def build_upgrade_plan_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Typography & Color Palette
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0284C7'),
        fontName="Helvetica-Bold",
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading3'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        fontName="Helvetica-Bold",
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=10,
        spaceAfter=3
    )
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )
    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=7,
        leading=9.5,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor('#0F172A')
    )
    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontSize=7,
        leading=9.5,
        fontName="Courier",
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # -------------------------------------------------------------
    # 1. Header Banner
    # -------------------------------------------------------------
    story.append(Paragraph("PlotHole OS – Advanced Feature Enhancement & Quality Upgrade Plan", title_style))
    story.append(Paragraph("ARCHITECTURAL BLUEPRINT: DEPENDABILITY, TRACEABILITY, REPAIR & SECURITY", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceAfter=8))

    meta_info = [
        [
            Paragraph("<b>Document Version:</b> 2.0.0 Architecture Blueprint", body_style),
            Paragraph("<b>Role:</b> Senior AI Architect & Product Lead", body_style),
            Paragraph(f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%b %d, %Y %H:%M UTC')}", body_style)
        ],
        [
            Paragraph("<b>Target System:</b> PlotHole OS (Script Continuity Debugger)", body_style),
            Paragraph("<b>Enhancement Scope:</b> 8 Advanced Modules & QA Suite", body_style),
            Paragraph("<b>Current Status:</b> Awaiting Implementation Approval", body_style)
        ]
    ]
    t_meta = Table(meta_info, colWidths=[180, 180, 180])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 2. Executive Vision & Objectives
    # -------------------------------------------------------------
    story.append(Paragraph("1. Executive Vision & Problem Statement", h1_style))
    story.append(Paragraph(
        "While PlotHole OS currently has a functional end-to-end pipeline (parsing, 8 continuity detectors, Gemini AI repair, and visualizations), "
        "professional-grade screenplay adoption requires moving beyond basic contradiction alerts to a <b>dependable, trustworthy intelligence platform</b>. "
        "Writers and script supervisors reject systems that produce hallucinated dialogue, flag legitimate non-linear narrative devices (dreams, flashbacks) as errors, "
        "or propose rewrites that destroy the screenplay's voice. This enhancement plan elevates PlotHole OS into an indispensable production tool.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 3. Eight Advanced Enhancement Modules
    # -------------------------------------------------------------
    story.append(Paragraph("2. Detailed Technical Specifications: 8 Advanced Enhancement Areas", h1_style))

    modules_data = [
        [
            Paragraph("Area", th_style),
            Paragraph("Core Objective", th_style),
            Paragraph("Current Status", th_style),
            Paragraph("Proposed Technical Architecture & Deliverables", th_style)
        ],
        [
            Paragraph("<b>1. False Positive Management</b>", td_bold),
            Paragraph("Distinguish confirmed plot holes from artistic choices with writer triage controls.", td_style),
            Paragraph("Partially Implemented (<code>status='Open'</code>)", td_style),
            Paragraph("• Add <code>triage_status</code>: <code>Confirmed Valid</code>, <code>False Positive / Artistic Choice</code>, <code>Unresolved</code>.<br/>• Add <code>certainty_tier</code>: Confirmed Contradiction, Probable Inconsistency, Insufficient Info.<br/>• Interactive triage pills in Streamlit Module 8 allowing writers to categorize issues.", td_style)
        ],
        [
            Paragraph("<b>2. Evidence-Based Detection</b>", td_bold),
            Paragraph("Exact line numbers, estimated pages, and deterministic anti-hallucination guard.", td_style),
            Paragraph("Partially Implemented (Quotes & Scene #)", td_style),
            Paragraph("• Screenplay line indexer and industry-standard page calculator (~55 lines = 1 page).<br/>• <code>anti_hallucination.py</code>: Fuzzy & substring validator that checks all findings against source script. Discards or flags any invented quotes.", td_style)
        ],
        [
            Paragraph("<b>3. Character Knowledge Graph</b>", td_bold),
            Paragraph("Track character epistemic state and detect inquiry/assertion paradoxes.", td_style),
            Paragraph("Partially Implemented (Regex tracker)", td_style),
            Paragraph("• Populate <code>CharacterKnowledge</code> database records.<br/>• Bipartite directed graph (Character $\\to$ Fact) with disclosure classification (Witnessed, Told, Leaked).<br/>• Catch inquiry paradoxes (asking about known facts) and assertion contradictions.", td_style)
        ],
        [
            Paragraph("<b>4. Advanced Repair Assistant</b>", td_bold),
            Paragraph("Multi-path solutions preserving author voice; side-by-side non-destructive diffs.", td_style),
            Paragraph("Partially Implemented (2 fixes + diff)", td_style),
            Paragraph("• <code>style_profiler.py</code>: Extracts dialogue rhythm, sentence length, and vocabulary constraints.<br/>• 3 Repair Strategies: Minimally Invasive Edit, Narrative Deep-Fix, Alternative Staging.<br/>• Non-destructive versioning: Writer accepts/rejects; original script is never mutated.", td_style)
        ],
        [
            Paragraph("<b>5. Script Version Comparison</b>", td_bold),
            Paragraph("Compare Draft A vs Draft B to detect regression and track resolved issues.", td_style),
            Paragraph("Not Implemented (Single script only)", td_style),
            Paragraph("• <code>version_comparator.py</code>: Scene alignment matching by slugline, location, and index.<br/>• Continuity Regression Matrix: Resolved Plot Holes, Persisting Issues, and Newly Introduced Errors.<br/>• Dedicated Streamlit diffing UI comparing two project drafts.", td_style)
        ],
        [
            Paragraph("<b>6. Advanced Severity Scoring</b>", td_bold),
            Paragraph("De-couple mathematical certainty from dramatic narrative impact.", td_style),
            Paragraph("Partially Implemented (Single category)", td_style),
            Paragraph("• Tri-factor scoring formula: Logical Certainty (0.0 to 1.0) $\\times$ Narrative Impact (Critical=10, High=7, Medium=4, Low=1).<br/>• Dynamic Continuity Health Score: $\\max(10, 100 - \\sum (\\text{Impact}_i \\times \\text{Certainty}_i))$.", td_style)
        ],
        [
            Paragraph("<b>7. Advanced Testing Suite</b>", td_bold),
            Paragraph("Stress-test edge cases, flashbacks, long scripts, and API failure modes.", td_style),
            Paragraph("Baseline (16 unit tests passing)", td_style),
            Paragraph("• <code>test_advanced_scenarios.py</code>: 120-scene script ingestion, non-linear flashback/dream handling, twins/metaphor ambiguity, API timeout & rate-limit fallback testing.", td_style)
        ],
        [
            Paragraph("<b>8. Security, Privacy & Air-Gap</b>", td_bold),
            Paragraph("Protect script IP, sanitize prompt injection, and allow 100% local operation.", td_style),
            Paragraph("Baseline (.env key storage)", td_style),
            Paragraph("• <code>prompt_sanitizer.py</code>: Encapsulates screenplay dialogue in escaped XML tags to block prompt injection.<br/>• Air-Gapped Privacy Mode: Disables external API calls entirely.<br/>• Complete cascade project deletion.", td_style)
        ]
    ]

    t_modules = Table(modules_data, colWidths=[90, 115, 85, 250])
    t_modules.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t_modules)
    story.append(Spacer(1, 8))

    # Page Break for Roadmap & Implementation Details
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 4. Four-Sprint Implementation Phasing
    # -------------------------------------------------------------
    story.append(Paragraph("3. Four-Sprint Implementation Execution Roadmap", h1_style))
    story.append(Paragraph(
        "To ensure zero disruption to current working capabilities, enhancements are scheduled into four focused sprints:",
        body_style
    ))

    sprint_data = [
        [
            Paragraph("Sprint / Phase", th_style),
            Paragraph("Primary Deliverables", th_style),
            Paragraph("Affected Modules", th_style),
            Paragraph("Target Milestone / Outcome", th_style)
        ],
        [
            Paragraph("<b>Sprint 1: Integrity & Security</b>", td_bold),
            Paragraph("• User Triage controls (Confirm / False Positive / Unresolved)<br/>• Line & page number indexing in parser<br/>• Anti-hallucination evidence verifier<br/>• Prompt injection sanitizer & Air-Gapped toggle", td_style),
            Paragraph("<code>database/</code><br/><code>core/script_parser.py</code><br/><code>core/anti_hallucination.py</code><br/><code>app.py</code>", td_style),
            Paragraph("Writers can categorize issues; evidence displays exact line & page numbers; hallucinated quotes rejected.", td_style)
        ],
        [
            Paragraph("<b>Sprint 2: Narrative Intelligence</b>", td_bold),
            Paragraph("• Character Knowledge Graph DB persistence<br/>• Interactive Bipartite Knowledge Graph visualization<br/>• Epistemic contradiction detector (inquiry paradoxes)<br/>• Tri-factor severity scoring formula", td_style),
            Paragraph("<code>core/knowledge_tracker.py</code><br/><code>detection/knowledge_detector.py</code><br/><code>visualization/analytics.py</code>", td_style),
            Paragraph("Visual knowledge state map; catching characters who inquire about secrets they already know.", td_style)
        ],
        [
            Paragraph("<b>Sprint 3: Repair & Version Diffing</b>", td_bold),
            Paragraph("• Script Version Comparator (Draft A vs Draft B)<br/>• Continuity regression breakdown (Fixed vs New errors)<br/>• Style & voice profiler (dialogue rhythm & constraints)<br/>• 3-strategy narrative repair workbench", td_style),
            Paragraph("<code>core/version_comparator.py</code><br/><code>ai/style_profiler.py</code><br/><code>ai/repair_assistant.py</code><br/><code>app.py</code>", td_style),
            Paragraph("Draft comparison view with regression matrix; author-voice-preserving scene rewrites.", td_style)
        ],
        [
            Paragraph("<b>Sprint 4: Verification & Docs</b>", td_bold),
            Paragraph("• <code>tests/test_advanced_scenarios.py</code> (120 scenes, flashbacks, fault-injection)<br/>• Full regression suite run (all 20+ tests passing)<br/>• Update master architecture documentation", td_style),
            Paragraph("<code>tests/</code><br/><code>README.md</code><br/><code>IMPLEMENTATION_PLAN.md</code>", td_style),
            Paragraph("100% test pass rate across extreme edge cases; fully updated documentation.", td_style)
        ]
    ]

    t_sprint = Table(sprint_data, colWidths=[90, 210, 110, 130])
    t_sprint.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t_sprint)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 5. Prioritization Matrix & Acceptance Criteria
    # -------------------------------------------------------------
    story.append(Paragraph("4. Prioritization Matrix & Quality Acceptance Criteria", h1_style))

    prio_data = [
        [Paragraph("Enhancement Task", th_style), Paragraph("Priority", th_style), Paragraph("Complexity", th_style), Paragraph("Acceptance Criteria", th_style)],
        [Paragraph("Anti-Hallucination Guard", td_bold), Paragraph("CRITICAL", td_bold), Paragraph("Medium", td_style), Paragraph("100% of reported evidence quotes exist verbatim in script text.", td_style)],
        [Paragraph("User Triage Status Manager", td_bold), Paragraph("CRITICAL", td_bold), Paragraph("Low", td_style), Paragraph("User can mark issue as False Positive; status persists across restarts.", td_style)],
        [Paragraph("Script Version Comparator", td_bold), Paragraph("HIGH", td_bold), Paragraph("High", td_style), Paragraph("Correctly aligns scenes between Drafts and identifies newly introduced plot holes.", td_style)],
        [Paragraph("Prompt Injection Defense", td_bold), Paragraph("HIGH", td_bold), Paragraph("Low", td_style), Paragraph("Malicious screenplay dialogue cannot alter Gemini system instructions.", td_style)],
        [Paragraph("Voice-Preserving Repair", td_bold), Paragraph("HIGH", td_bold), Paragraph("Medium", td_style), Paragraph("Rewritten dialogue matches original scene sentence length and tone.", td_style)],
        [Paragraph("Bipartite Knowledge Graph", td_bold), Paragraph("MEDIUM", td_bold), Paragraph("Medium", td_style), Paragraph("Renders directed NetworkX graph of character $\\to$ secret connections.", td_style)],
        [Paragraph("Tri-Factor Severity Scoring", td_bold), Paragraph("MEDIUM", td_bold), Paragraph("Low", td_style), Paragraph("Separates mathematical certainty from dramatic narrative impact.", td_style)],
        [Paragraph("Air-Gapped Privacy Mode", td_bold), Paragraph("MEDIUM", td_bold), Paragraph("Low", td_style), Paragraph("Blocks all outbound network requests; runs 100% locally.", td_style)]
    ]

    t_prio = Table(prio_data, colWidths=[120, 65, 65, 290])
    t_prio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t_prio)
    story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94A3B8'), spaceAfter=6))
    story.append(Paragraph("<b>Next Step:</b> Upon user approval of this blueprint, Sprint 1 implementation will commence without disruption to existing features.", subtitle_style))

    doc.build(story)
    print(f"Upgrade Plan PDF built successfully at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "PlotHole_OS_Advanced_Enhancement_Plan.pdf")
    build_upgrade_plan_pdf(out_file)

