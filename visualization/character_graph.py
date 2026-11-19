import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict, Any
from utils.helpers import get_val

def create_character_network_graph(
    characters: List[Any],
    relationships: List[Any]
) -> go.Figure:
    """Creates an interactive NetworkX + Plotly character interaction and co-occurrence graph.
    Seamlessly handles Pydantic models, SQLAlchemy models, dataclasses, and dicts,
    as well as empty or single-character screenplays."""
    
    if not characters:
        fig = go.Figure()
        fig.add_annotation(
            text="No character data available for network graph.<br>Analyze a script to view character interactions.",
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
            height=400
        )
        return fig

    G = nx.Graph()

    # Add character nodes
    top_chars = characters[:16]
    for c in top_chars:
        name = get_val(c, "name", "Unknown")
        scenes_c = get_val(c, "total_scenes", 1) or 1
        diags_c = get_val(c, "dialogue_count", 0) or 0
        traits_raw = get_val(c, "personality_traits", []) or []
        traits_str = ", ".join(traits_raw[:3]) if isinstance(traits_raw, list) else str(traits_raw)

        G.add_node(
            name,
            scenes=scenes_c,
            dialogues=diags_c,
            traits=traits_str
        )

    # Add edges
    if relationships:
        for r in relationships:
            src = get_val(r, "source_character") or get_val(r, "character1", "")
            tgt = get_val(r, "target_character") or get_val(r, "character2", "")
            weight = get_val(r, "interaction_count") or get_val(r, "co_occurrences", 1) or 1
            rel_type = get_val(r, "relationship_type", "Co-occurrence") or "Co-occurrence"
            if src and tgt and G.has_node(src) and G.has_node(tgt):
                G.add_edge(src, tgt, weight=weight, rel_type=rel_type)

    # Compute layout (fallback safely if isolated or single node)
    if len(G.nodes) == 1:
        single_node = list(G.nodes)[0]
        pos = {single_node: (0.0, 0.0)}
    else:
        pos = nx.spring_layout(G, k=0.6, seed=42)

    # Edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#475569"),
        hoverinfo="none",
        mode="lines"
    )

    # Node traces
    node_x = []
    node_y = []
    node_sizes = []
    node_texts = []
    hover_texts = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        data = G.nodes[node]
        node_sizes.append(max(20, min(55, data["scenes"] * 7 + 15)))
        node_texts.append(node)
        hover_texts.append(
            f"<b>{node}</b><br>"
            f"Scenes: {data['scenes']}<br>"
            f"Dialogue Count: {data['dialogues']}<br>"
            f"Traits: {data['traits'] or 'Undisclosed'}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=hover_texts,
        text=node_texts,
        textposition="bottom center",
        textfont=dict(color="#F1F5F9", size=11, family="Inter, sans-serif"),
        marker=dict(
            showscale=True,
            colorscale="Viridis",
            reversescale=True,
            color=[G.nodes[n]["dialogues"] for n in G.nodes()],
            size=node_sizes,
            colorbar=dict(
                thickness=12,
                title=dict(text="Dialogue", font=dict(color="#94A3B8", size=10)),
                xanchor="left",
                tickfont=dict(color="#94A3B8", size=9)
            ),
            line=dict(color="#0F172A", width=2)
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=dict(text="Character Relationship & Interaction Network", font=dict(color="#F8FAFC", size=16)),
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=50),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=420
    )

    return fig
