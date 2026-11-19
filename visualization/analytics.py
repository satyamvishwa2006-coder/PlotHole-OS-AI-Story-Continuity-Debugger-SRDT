import plotly.graph_objects as go
from typing import List, Dict, Any
from utils.helpers import format_severity_color, get_val

def create_severity_donut(issues: List[Any]) -> go.Figure:
    """Creates a donut chart displaying issue count grouped by severity.
    Handles empty data, objects, and dictionaries gracefully."""
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    
    if issues:
        for iss in issues:
            sev = get_val(iss, "severity", "Medium") or "Medium"
            if sev in severity_counts:
                severity_counts[sev] += 1
            else:
                severity_counts["Medium"] += 1

    labels = [k for k, v in severity_counts.items() if v > 0]
    values = [v for k, v in severity_counts.items() if v > 0]
    colors = [format_severity_color(k) for k in labels]

    if not values:
        labels = ["No Issues Detected"]
        values = [1]
        colors = ["#00E676"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#0F172A", width=2)),
        textinfo="label+value",
        textfont=dict(color="#F8FAFC", size=12)
    )])

    fig.update_layout(
        title=dict(text="Issue Severity Breakdown", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        showlegend=True,
        legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.2),
        height=300,
        margin=dict(t=50, b=30, l=20, r=20)
    )
    return fig

def create_issue_type_bar(issues: List[Any]) -> go.Figure:
    """Creates a horizontal bar chart displaying issues categorized by type."""
    if not issues:
        fig = go.Figure()
        fig.add_annotation(
            text="No continuity issues to categorize.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            height=300
        )
        return fig

    type_counts = {}
    for iss in issues:
        itype = get_val(iss, "issue_type", "Other") or "Other"
        type_counts[itype] = type_counts.get(itype, 0) + 1

    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    types = [x[0] for x in sorted_types]
    counts = [x[1] for x in sorted_types]

    fig = go.Figure(go.Bar(
        x=counts,
        y=types,
        orientation="h",
        marker=dict(
            color="#38BDF8",
            line=dict(color="#0284C7", width=1.5)
        ),
        text=counts,
        textposition="auto",
        textfont=dict(color="#FFFFFF")
    ))

    fig.update_layout(
        title=dict(text="Continuity Breaches by Category", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        height=300,
        margin=dict(t=50, b=30, l=140, r=20),
        xaxis=dict(title="Count", gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(autorange="reversed", color="#94A3B8")
    )
    return fig

def create_continuity_gauge(score: int) -> go.Figure:
    """Creates a radial gauge representing the Screenplay Continuity Health Score."""
    clamped_score = max(0, min(100, score))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=clamped_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Continuity Health Index", 'font': {'size': 16, 'color': "#F8FAFC"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#38BDF8"},
            'bgcolor': "#1E293B",
            'borderwidth': 2,
            'bordercolor': "#0F172A",
            'steps': [
                {'range': [0, 50], 'color': '#7F1D1D'},
                {'range': [50, 75], 'color': '#78350F'},
                {'range': [75, 90], 'color': '#14532D'},
                {'range': [90, 100], 'color': '#065F46'}
            ],
            'threshold': {
                'line': {'color': "#00E676", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        height=260,
        margin=dict(t=40, b=20, l=30, r=30),
        font=dict(color="#F8FAFC")
    )
    return fig

def create_character_appearance_chart(characters: List[Any]) -> go.Figure:
    """Creates a comparative bar chart showing character scene appearances vs dialogue lines."""
    if not characters:
        fig = go.Figure()
        fig.add_annotation(
            text="No character data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            height=320
        )
        return fig

    top_chars = characters[:12]
    names = [get_val(c, "name", "Unknown") for c in top_chars]
    scenes_counts = [get_val(c, "total_scenes", 0) for c in top_chars]
    diag_counts = [get_val(c, "dialogue_count", 0) for c in top_chars]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=scenes_counts,
        name="Scenes Active",
        marker_color="#38BDF8"
    ))
    fig.add_trace(go.Bar(
        x=names,
        y=diag_counts,
        name="Dialogue Lines",
        marker_color="#818CF8"
    ))

    fig.update_layout(
        title=dict(text="Character Screenplay Presence & Dialogue Volume", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        barmode="group",
        height=320,
        margin=dict(t=50, b=40, l=40, r=20),
        legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.25),
        xaxis=dict(color="#94A3B8"),
        yaxis=dict(gridcolor="#1E293B", color="#94A3B8")
    )
    return fig

def create_scene_distribution_chart(scenes: List[Any]) -> go.Figure:
    """Creates a chart showing word count pacing across scenes."""
    if not scenes:
        fig = go.Figure()
        fig.add_annotation(
            text="No scenes available for distribution analysis.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            height=300
        )
        return fig

    scene_nums = [get_val(s, "scene_number", idx + 1) for idx, s in enumerate(scenes)]
    words = [get_val(s, "word_count", 0) for s in scenes]
    locations = [get_val(s, "location_name", "") for s in scenes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Sc.{n}" for n in scene_nums],
        y=words,
        marker_color="#0284C7",
        hovertext=[f"Scene {n}: {loc} ({w} words)" for n, loc, w in zip(scene_nums, locations, words)],
        name="Scene Length"
    ))

    # Add trend line
    fig.add_trace(go.Scatter(
        x=[f"Sc.{n}" for n in scene_nums],
        y=words,
        mode="lines+markers",
        line=dict(color="#F43F5E", width=2),
        name="Pacing Curve"
    ))

    fig.update_layout(
        title=dict(text="Screenplay Scene Pacing & Length Distribution", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        height=300,
        margin=dict(t=50, b=40, l=40, r=20),
        legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.25),
        xaxis=dict(color="#94A3B8"),
        yaxis=dict(title="Words per Scene", gridcolor="#1E293B", color="#94A3B8")
    )
    return fig

def create_knowledge_map(knowledge_timeline: List[Any]) -> go.Figure:
    """Creates a timeline map of character knowledge disclosures."""
    if not knowledge_timeline:
        fig = go.Figure()
        fig.add_annotation(
            text="No confidential disclosures or knowledge records extracted.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            height=280
        )
        return fig

    scenes = [get_val(k, "scene_number", 1) for k in knowledge_timeline]
    facts = [get_val(k, "fact", "Secret")[:24] for k in knowledge_timeline]
    speakers = [get_val(k, "speaker", "Action") or "Action" for k in knowledge_timeline]

    fig = go.Figure(go.Scatter(
        x=scenes,
        y=facts,
        mode="markers+text",
        marker=dict(size=14, color="#A855F7", symbol="diamond"),
        text=speakers,
        textposition="top right",
        textfont=dict(color="#E2E8F0", size=10),
        hovertext=[f"Scene {s}: {f} (Discloser: {sp})" for s, f, sp in zip(scenes, facts, speakers)]
    ))

    fig.update_layout(
        title=dict(text="Character Knowledge Revelation Points", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        height=280,
        margin=dict(t=50, b=40, l=140, r=20),
        xaxis=dict(title="Scene", tickmode="linear", dtick=1, gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(color="#94A3B8")
    )
    return fig

def create_location_journey_chart(unique_locations: List[Any]) -> go.Figure:
    """Visualizes location usage and scene counts across the narrative."""
    if not unique_locations:
        fig = go.Figure()
        fig.add_annotation(
            text="No location history available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            height=280
        )
        return fig

    loc_names = [get_val(l, "location_name", "Unknown")[:25] for l in unique_locations[:10]]
    counts = [get_val(l, "scene_count", 1) for l in unique_locations[:10]]

    fig = go.Figure(go.Bar(
        x=counts,
        y=loc_names,
        orientation="h",
        marker=dict(color="#10B981", line=dict(color="#059669", width=1.5)),
        text=counts,
        textposition="auto"
    ))

    fig.update_layout(
        title=dict(text="Top Locations by Scene Frequency", font=dict(color="#F8FAFC", size=15)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        height=280,
        margin=dict(t=50, b=30, l=150, r=20),
        xaxis=dict(title="Number of Scenes", gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(autorange="reversed", color="#94A3B8")
    )
    return fig
