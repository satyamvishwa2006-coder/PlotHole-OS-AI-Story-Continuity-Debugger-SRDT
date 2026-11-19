import plotly.graph_objects as go
from typing import List, Dict, Any, Union
from utils.helpers import get_val

def create_timeline_chart(
    scenes: List[Any],
    issues: List[Any]
) -> go.Figure:
    """Builds an interactive Plotly timeline chart showing scene flow and continuity error hotspots.
    Seamlessly handles Pydantic models, SQLAlchemy models, dataclasses, and dicts,
    as well as missing fields or empty datasets."""
    
    if not scenes:
        fig = go.Figure()
        fig.add_annotation(
            text="No scene data available for timeline visualization.<br>Upload a script to generate the story timeline.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=300
        )
        return fig

    scene_nums = []
    locations = []
    time_refs = []
    word_counts = []
    hover_texts = []

    for idx, s in enumerate(scenes):
        s_num = get_val(s, "scene_number", idx + 1)
        scene_nums.append(s_num)
        loc = get_val(s, "location_name", "UNKNOWN")
        locations.append(loc)
        time_c = get_val(s, "time_reference") or get_val(s, "time_of_day", "DAY")
        time_refs.append(time_c)
        wc = get_val(s, "word_count", 100) or 100
        word_counts.append(wc)

        chars_raw = get_val(s, "characters_present", []) or []
        chars_str = ", ".join(chars_raw) if isinstance(chars_raw, list) else str(chars_raw)
        heading_str = get_val(s, "heading", f"Scene {s_num}")

        hover_texts.append(
            f"<b>Scene {s_num}</b><br>"
            f"Heading: {heading_str}<br>"
            f"Location: {loc}<br>"
            f"Time: {time_c}<br>"
            f"Characters: {chars_str or 'None'}<br>"
            f"Words: {wc}"
        )

    # Map scenes with issues
    issue_scene_map = {}
    if issues:
        for iss in issues:
            refs = get_val(iss, "scene_references", []) or []
            sev = get_val(iss, "severity", "Medium") or "Medium"
            title = get_val(iss, "title", "Issue") or "Issue"
            for ref in refs:
                if ref not in issue_scene_map:
                    issue_scene_map[ref] = []
                issue_scene_map[ref].append(f"[{sev}] {title}")

    node_colors = []
    for s_num in scene_nums:
        if s_num in issue_scene_map:
            titles = " ".join(issue_scene_map[s_num])
            if "[Critical]" in titles:
                node_colors.append("#FF4B4B")  # Red
            elif "[High]" in titles:
                node_colors.append("#FFA500")  # Orange
            else:
                node_colors.append("#FFD700")  # Yellow
        else:
            node_colors.append("#00E676")  # Green

    fig = go.Figure()

    # Base connecting path
    fig.add_trace(go.Scatter(
        x=scene_nums,
        y=[1] * len(scene_nums),
        mode="lines",
        line=dict(color="#2D3748", width=4),
        hoverinfo="skip",
        name="Narrative Flow"
    ))

    # Scene nodes
    fig.add_trace(go.Scatter(
        x=scene_nums,
        y=[1] * len(scene_nums),
        mode="markers+text",
        marker=dict(
            size=[max(18, min(36, wc // 15)) for wc in word_counts],
            color=node_colors,
            line=dict(color="#FFFFFF", width=1.5)
        ),
        text=[f"Sc.{s}" for s in scene_nums],
        textposition="top center",
        textfont=dict(color="#E2E8F0", size=11),
        hovertext=hover_texts,
        hoverinfo="text",
        name="Scenes"
    ))

    # Highlight continuity issue annotations
    annotations = []
    for s_num, iss_list in issue_scene_map.items():
        if s_num in scene_nums:
            annotations.append(dict(
                x=s_num,
                y=1,
                xref="x",
                yref="y",
                text=f"⚠️ {len(iss_list)} Issue(s)",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#FF4B4B",
                ax=0,
                ay=-45,
                bgcolor="#1A202C",
                bordercolor="#FF4B4B",
                borderwidth=1,
                borderpad=4,
                font=dict(size=10, color="#FFD700")
            ))

    fig.update_layout(
        title=dict(
            text="Screenplay Narrative Timeline & Continuity Hotspots",
            font=dict(color="#F8FAFC", size=16)
        ),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            title="Scene Sequence",
            tickmode="linear",
            tick0=1,
            dtick=1,
            gridcolor="#1E293B",
            zeroline=False,
            color="#94A3B8"
        ),
        yaxis=dict(
            visible=False,
            range=[0.7, 1.4]
        ),
        annotations=annotations
    )

    return fig
