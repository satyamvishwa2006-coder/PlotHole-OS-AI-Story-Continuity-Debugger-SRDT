import os
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# Core imports
from config.settings import settings
from database.db import init_db
from database.operations import (
    create_project, get_project, list_projects, delete_project,
    save_script, save_scenes, get_scenes, get_scene_by_number,
    save_characters, get_characters, save_relationships, get_relationships,
    save_events, get_events, save_tracked_objects, get_tracked_objects,
    save_issues, get_issues, save_repair_suggestion, update_repair_status,
    save_analysis_history, get_project_summary
)
from core.document_processor import DocumentProcessor
from core.script_parser import ScriptParser
from core.scene_extractor import SceneExtractor
from core.character_extractor import CharacterExtractor
from core.event_extractor import EventExtractor
from core.timeline_engine import TimelineEngine
from core.location_tracker import LocationTracker
from core.knowledge_tracker import KnowledgeTracker
from core.object_tracker import ObjectTracker
from detection.detector_coordinator import DetectorCoordinator
from ai.gemini_service import GeminiService
from ai.reasoning_engine import ReasoningEngine
from ai.repair_assistant import RepairAssistant
from visualization import (
    create_timeline_chart,
    create_character_network_graph,
    create_severity_donut,
    create_issue_type_bar,
    create_continuity_gauge,
    create_character_appearance_chart,
    create_scene_distribution_chart,
    create_knowledge_map,
    create_location_journey_chart
)
from reports.pdf_generator import generate_pdf_report
from reports.json_exporter import export_project_json
from utils.helpers import format_confidence_badge, format_severity_color, get_val

# Page Configuration
st.set_page_config(
    page_title="PlotHole OS – AI Screenplay Analysis & Continuity Debugger",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# Custom Dark Theme CSS
st.markdown("""
<style>
    /* Dark Theme Core Styles */
    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header & Badges */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .main-title {
        color: #F8FAFC;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .main-tagline {
        color: #94A3B8;
        font-size: 13px;
        margin-top: 4px;
        font-weight: 400;
    }
    
    /* Metrics Card */
    .metric-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #9CA3AF;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #F9FAFB;
    }
    
    /* Issue Card */
    .issue-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #38BDF8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .issue-card-critical { border-left-color: #EF4444; }
    .issue-card-high { border-left-color: #F97316; }
    .issue-card-medium { border-left-color: #FBBF24; }
    .issue-card-low { border-left-color: #38BDF8; }
    
    /* Code/Evidence Box */
    .evidence-box {
        background: #030712;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 10px 14px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 12px;
        color: #E2E8F0;
        margin: 6px 0;
    }
    
    /* Diff lines */
    .diff-del {
        background-color: rgba(239, 68, 68, 0.2);
        color: #FCA5A5;
        padding: 2px 4px;
        border-radius: 3px;
        display: block;
        font-family: monospace;
    }
    .diff-add {
        background-color: rgba(34, 197, 94, 0.2);
        color: #86EFAC;
        padding: 2px 4px;
        border-radius: 3px;
        display: block;
        font-family: monospace;
    }
    .diff-eq {
        color: #94A3B8;
        padding: 2px 4px;
        display: block;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_project_id" not in st.session_state:
    st.session_state["current_project_id"] = None
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = settings.GEMINI_API_KEY
if "active_repair_issue" not in st.session_state:
    st.session_state["active_repair_issue"] = None
if "jump_to_scene" not in st.session_state:
    st.session_state["jump_to_scene"] = 1

# Top Header Banner
st.markdown("""
<div class="main-header">
    <div class="main-title">
        <span>🎬 PlotHole OS</span>
        <span style="font-size: 12px; background: #0284C7; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 600;">v1.0 Pro</span>
    </div>
    <div class="main-tagline">Every Story Has a Logic. We Find Where It Breaks.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation (12 sections as specified)
st.sidebar.title("Navigation")
menu_selection = st.sidebar.radio(
    "Modules",
    [
        "1. Overview",
        "2. Upload Script",
        "3. Script Explorer",
        "4. Character Intelligence",
        "5. Story Timeline",
        "6. Location Tracker",
        "7. Knowledge Tracker",
        "8. Plot Hole Detection",
        "9. AI Story Repair",
        "10. Reports",
        "11. Project History",
        "12. Settings"
    ],
    index=0
)

# Helper function to get active project summary
def load_active_project_data():
    pid = st.session_state.get("current_project_id")
    if not pid:
        # Check if there is any project in database
        projs = list_projects()
        if projs:
            pid = projs[0]["id"]
            st.session_state["current_project_id"] = pid
    if pid:
        return get_project_summary(pid)
    return {}

# -------------------------------------------------------------
# 1. OVERVIEW
# -------------------------------------------------------------
if menu_selection == "1. Overview":
    st.subheader("System Overview & Continuity Intelligence")
    summary = load_active_project_data()

    if not summary:
        st.info("No active script analyzed yet. Please go to **Upload Script** or load the sample screenplay.")
        if st.button("🚀 Load Sample Screenplay ('THE CIPHER PROTOCOL')", type="primary"):
            sample_path = settings.SAMPLE_DIR / "sample_screenplay.txt"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                with st.spinner("Analyzing Sample Screenplay..."):
                    # Process and save
                    proj = create_project(title="THE CIPHER PROTOCOL", author="A. Vance", genre="Cyberpunk Espionage Thriller")
                    st.session_state["current_project_id"] = proj.id
                    
                    scenes = ScriptParser.parse_script(content)
                    save_scenes(proj.id, scenes)
                    
                    chars, rels = CharacterExtractor.extract_characters(scenes)
                    save_characters(proj.id, chars)
                    save_relationships(proj.id, rels)
                    
                    events = EventExtractor.extract_events(scenes)
                    save_events(proj.id, events)
                    
                    loc_data = LocationTracker.track_locations(scenes)
                    know_data = KnowledgeTracker.track_knowledge(scenes)
                    objs = ObjectTracker.track_objects(scenes)
                    save_tracked_objects(proj.id, objs)
                    
                    # Detect issues
                    issues = DetectorCoordinator.run_all_detectors(
                        scenes, chars, events, loc_data, know_data, objs
                    )
                    save_issues(proj.id, issues)
                    save_script(proj.id, "sample_screenplay.txt", "TXT", len(content.encode()), content, len(content.split()), len(content), len(scenes))
                    
                    st.success("Sample Screenplay Loaded & Analyzed Successfully!")
                    st.rerun()
    else:
        # Display Key Metrics
        total_scenes = summary.get("total_scenes", 0)
        total_chars = summary.get("total_characters", 0)
        total_issues = summary.get("total_issues", 0)
        sev_counts = summary.get("severity_counts", {})
        critical_count = sev_counts.get("Critical", 0)
        high_count = sev_counts.get("High", 0)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Scenes", total_scenes)
        with c2:
            st.metric("Characters", total_chars)
        with c3:
            st.metric("Detected Inconsistencies", total_issues)
        with c4:
            st.metric("Critical Errors", critical_count, delta=f"{critical_count} critical" if critical_count > 0 else "None", delta_color="inverse")
        with c5:
            st.metric("High-Priority", high_count)

        st.markdown("---")

        # Visual Analytics
        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.plotly_chart(create_timeline_chart(summary.get("scenes", []), summary.get("issues", [])), use_container_width=True)
        with col_right:
            health_score = max(10, 100 - (critical_count * 20 + high_count * 10 + sev_counts.get("Medium", 0) * 5))
            st.plotly_chart(create_continuity_gauge(health_score), use_container_width=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.plotly_chart(create_severity_donut(summary.get("issues", [])), use_container_width=True)
        with col_b2:
            st.plotly_chart(create_issue_type_bar(summary.get("issues", [])), use_container_width=True)


# -------------------------------------------------------------
# 2. UPLOAD SCRIPT
# -------------------------------------------------------------
elif menu_selection == "2. Upload Script":
    st.subheader("Screenplay Ingestion & Analysis Engine")
    
    col_u1, col_u2 = st.columns([2, 1])
    
    with col_u1:
        uploaded_file = st.file_uploader(
            "Upload Screenplay or Story File (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"],
            help="Maximum size: 30MB. Plain text, Fountain, Standard Screenplay, or Prose formats supported."
        )

        with st.expander("Project Metadata & Settings", expanded=True):
            proj_title = st.text_input("Project / Script Title", value="Untitled Screenplay")
            proj_author = st.text_input("Author / Screenwriter", value="Unknown")
            proj_genre = st.selectbox("Genre", ["General", "Action / Thriller", "Sci-Fi / Cyberpunk", "Drama", "Mystery", "Horror", "Comedy"])
            enable_ai_deep_audit = st.checkbox("Enable Gemini Contextual Reasoning (requires API Key)", value=bool(st.session_state.get("gemini_api_key")))

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            proc_res = DocumentProcessor.process_file(uploaded_file.name, file_bytes)

            if not proc_res.get("success"):
                st.error(proc_res.get("error"))
            else:
                st.success(f"File validated successfully: **{uploaded_file.name}**")
                
                # File stats display
                st.markdown(f"""
                - **File Type:** {proc_res['file_type']}
                - **File Size:** {proc_res['file_size_bytes'] / 1024:.1f} KB
                - **Total Words:** {proc_res['word_count']:,}
                - **Total Characters:** {proc_res['char_count']:,}
                - **Estimated Scenes:** {proc_res['estimated_scenes']}
                """)

                if st.button("🚀 Analyze Script", type="primary"):
                    with st.status("Executing Multi-Stage Screenplay Intelligence Pipeline...", expanded=True) as status:
                        # 1. Create DB Project
                        st.write("Creating Project Record...")
                        proj = create_project(title=proj_title, author=proj_author, genre=proj_genre)
                        st.session_state["current_project_id"] = proj.id

                        # 2. Parse Scenes
                        st.write("Parsing scene headings, sluglines, dialogue, and action...")
                        raw_content = proc_res["raw_text"]
                        scenes = ScriptParser.parse_script(raw_content)
                        save_scenes(proj.id, scenes)

                        # 3. Character & Relationship Extraction
                        st.write("Extracting character profiles and co-occurrence network...")
                        chars, rels = CharacterExtractor.extract_characters(scenes)
                        save_characters(proj.id, chars)
                        save_relationships(proj.id, rels)

                        # 4. Chronological Events & Timeline
                        st.write("Constructing chronological timeline and event sequence...")
                        events = EventExtractor.extract_events(scenes)
                        save_events(proj.id, events)

                        # 5. Location & Knowledge Tracking
                        st.write("Tracking character spatial journeys and confidential knowledge leaks...")
                        loc_data = LocationTracker.track_locations(scenes)
                        know_data = KnowledgeTracker.track_knowledge(scenes)
                        objs = ObjectTracker.track_objects(scenes)
                        save_tracked_objects(proj.id, objs)

                        # 6. AI Contextual Deep Audit (if requested)
                        ai_issues = []
                        if enable_ai_deep_audit and st.session_state.get("gemini_api_key"):
                            st.write("Engaging Gemini AI Contextual Reasoning Engine...")
                            reasoning_engine = ReasoningEngine(GeminiService(st.session_state.get("gemini_api_key")))
                            ai_res = reasoning_engine.analyze_script_context(scenes)
                            if ai_res.get("success"):
                                ai_issues = ai_res.get("detected_issues", [])

                        # 7. Unified Plot Hole Detection
                        st.write("Synthesizing rule-based & AI findings with evidence verification...")
                        detected_issues = DetectorCoordinator.run_all_detectors(
                            scenes, chars, events, loc_data, know_data, objs, ai_issues=ai_issues
                        )
                        save_issues(proj.id, detected_issues)

                        # 8. Save script & history
                        save_script(proj.id, uploaded_file.name, proc_res["file_type"], proc_res["file_size_bytes"], raw_content, proc_res["word_count"], proc_res["char_count"], len(scenes), proc_res["file_hash"])
                        save_analysis_history(proj.id, scenes_analyzed=len(scenes), issues_found=len(detected_issues))

                        status.update(label=f"Analysis Complete! {len(detected_issues)} continuity inconsistencies identified.", state="complete")
                    
                    st.rerun()

    with col_u2:
        st.markdown("### Quick Demo")
        st.write("Try our built-in test screenplay **'THE CIPHER PROTOCOL'** containing 8 deliberately planted continuity contradictions.")
        if st.button("Load 'THE CIPHER PROTOCOL' Sample"):
            sample_path = settings.SAMPLE_DIR / "sample_screenplay.txt"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                with st.spinner("Processing sample screenplay..."):
                    proj = create_project(title="THE CIPHER PROTOCOL", author="A. Vance", genre="Cyberpunk Espionage Thriller")
                    st.session_state["current_project_id"] = proj.id
                    scenes = ScriptParser.parse_script(content)
                    save_scenes(proj.id, scenes)
                    chars, rels = CharacterExtractor.extract_characters(scenes)
                    save_characters(proj.id, chars)
                    save_relationships(proj.id, rels)
                    events = EventExtractor.extract_events(scenes)
                    save_events(proj.id, events)
                    loc_data = LocationTracker.track_locations(scenes)
                    know_data = KnowledgeTracker.track_knowledge(scenes)
                    objs = ObjectTracker.track_objects(scenes)
                    save_tracked_objects(proj.id, objs)
                    detected_issues = DetectorCoordinator.run_all_detectors(scenes, chars, events, loc_data, know_data, objs)
                    save_issues(proj.id, detected_issues)
                    save_script(proj.id, "sample_screenplay.txt", "TXT", len(content.encode()), content, len(content.split()), len(content), len(scenes))
                    
                    st.success("Sample Screenplay Loaded!")
                    st.rerun()


# -------------------------------------------------------------
# 3. SCRIPT EXPLORER
# -------------------------------------------------------------
elif menu_selection == "3. Script Explorer":
    st.subheader("Scene-by-Scene Script Explorer")
    summary = load_active_project_data()
    scenes = summary.get("scenes", [])
    issues = summary.get("issues", [])

    if not scenes:
        st.warning("No script loaded yet.")
    else:
        # Search & Filter controls
        c_filter1, c_filter2 = st.columns([2, 1])
        with c_filter1:
            search_query = st.text_input("🔍 Search scene text, character dialogue, or action", "")
        with c_filter2:
            char_list = ["All Characters"] + [get_val(c, "name") for c in summary.get("characters", []) if get_val(c, "name")]
            selected_char_filter = st.selectbox("Filter by Character", char_list)

        # Filtered scene options
        filtered_scenes = scenes
        if search_query:
            filtered_scenes = [s for s in filtered_scenes if search_query.lower() in (get_val(s, "raw_content") or "").lower()]
        if selected_char_filter != "All Characters":
            filtered_scenes = [s for s in filtered_scenes if selected_char_filter in (get_val(s, "characters_present") or [])]

        if not filtered_scenes:
            st.info("No scenes matched your filter criteria.")
        else:
            scene_labels = [f"Scene {get_val(s, 'scene_number')}: {get_val(s, 'heading', '')[:60]}" for s in filtered_scenes]
            selected_idx = st.selectbox("Select Scene to Inspect", range(len(filtered_scenes)), format_func=lambda i: scene_labels[i])
            curr_scene = filtered_scenes[selected_idx]

            # Scene Metadata Strip
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.caption("LOCATION")
                st.write(f"**{get_val(curr_scene, 'location_name', 'Unknown')}** ({get_val(curr_scene, 'int_ext', 'INT')})")
            with col_m2:
                st.caption("TIME OF DAY / CUE")
                st.write(f"**{get_val(curr_scene, 'time_reference') or get_val(curr_scene, 'time_of_day', 'DAY')}**")
            with col_m3:
                st.caption("CHARACTERS PRESENT")
                st.write(f"**{', '.join(get_val(curr_scene, 'characters_present') or ['None'])}**")
            with col_m4:
                st.caption("WORD COUNT")
                st.write(f"**{get_val(curr_scene, 'word_count', 0)} words**")

            # Check if this scene has detected continuity issues
            scene_issues = [
                iss for iss in issues
                if get_val(curr_scene, "scene_number") in (get_val(iss, "scene_references") or [])
            ]
            if scene_issues:
                st.markdown("#### ⚠️ Identified Continuity Hotspots in this Scene")
                for iss in scene_issues:
                    sev = get_val(iss, "severity", "Medium")
                    sev_color = format_severity_color(sev)
                    st.markdown(f"""
                    <div class="issue-card" style="border-left-color: {sev_color};">
                        <strong style="color: {sev_color};">[{sev.upper()}] {get_val(iss, 'title')}</strong> ({get_val(iss, 'issue_type')})<br>
                        <span style="font-size: 13px; color: #CBD5E1;">{get_val(iss, 'description')}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Scene Content Display
            st.markdown("#### Script Text")
            st.code(get_val(curr_scene, "raw_content", ""), language="markdown")

            # Manual Correction Options
            with st.expander("✏️ Manual Scene Correction Override"):
                st.write("If automatic parsing misclassified this scene, adjust metadata below:")
                scene_id = get_val(curr_scene, "id", get_val(curr_scene, "scene_number"))
                edit_heading = st.text_input("Scene Heading", value=get_val(curr_scene, "heading", ""), key=f"hd_{scene_id}")
                edit_loc = st.text_input("Location Name", value=get_val(curr_scene, "location_name", ""), key=f"loc_{scene_id}")
                edit_time = st.text_input("Time / Clock Reference", value=get_val(curr_scene, "time_reference") or get_val(curr_scene, "time_of_day", ""), key=f"tm_{scene_id}")
                
                if st.button("Save Manual Corrections", key=f"btn_save_{scene_id}"):
                    curr_scene.heading = edit_heading
                    curr_scene.location_name = edit_loc
                    curr_scene.time_reference = edit_time
                    if hasattr(curr_scene, "is_customized"):
                        curr_scene.is_customized = True
                    st.success("Scene metadata updated.")
                    st.rerun()


# -------------------------------------------------------------
# 4. CHARACTER INTELLIGENCE
# -------------------------------------------------------------
elif menu_selection == "4. Character Intelligence":
    st.subheader("Character Intelligence & Relationship Network")
    summary = load_active_project_data()
    characters = summary.get("characters", [])
    relationships = summary.get("relationships", [])

    if not characters:
        st.warning("No character data available. Upload a script to generate profiles.")
    else:
        # Visualizations in two balanced columns
        col_cg1, col_cg2 = st.columns([3, 2])
        with col_cg1:
            st.plotly_chart(create_character_network_graph(characters, relationships), use_container_width=True)
        with col_cg2:
            st.plotly_chart(create_character_appearance_chart(characters), use_container_width=True)

        st.markdown("---")
        st.subheader("Character Dossiers")

        # Dossier cards
        for char in characters:
            c_name = get_val(char, "name", "Unknown")
            c_scenes = get_val(char, "total_scenes", 0)
            c_diag = get_val(char, "dialogue_count", 0)
            first_sc = get_val(char, "first_appearance_scene", 1)
            last_sc = get_val(char, "last_appearance_scene", 1)
            exp_traits = get_val(char, "explicit_traits") or []
            inf_traits = get_val(char, "inferred_traits") or []
            motivations = get_val(char, "motivations") or []
            diag_samples = get_val(char, "dialogue_samples") or []

            with st.expander(f"👤 {c_name} (Active in {c_scenes} Scenes, {c_diag} Dialogue Lines)", expanded=False):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown("**Appearance Span:**")
                    st.write(f"First Scene: Scene {first_sc} | Last Scene: Scene {last_sc}")
                    
                    st.markdown("**Explicit Traits (Script Text):**")
                    if exp_traits:
                        for t in exp_traits:
                            st.write(f"- {t}")
                    else:
                        st.caption("No explicit descriptor parentheticals.")

                    st.markdown("**Inferred Behavioral Traits:**")
                    if inf_traits:
                        for t in inf_traits:
                            st.write(f"- {t}")
                    else:
                        st.caption("Standard secondary character.")

                with col_d2:
                    st.markdown("**Core Motivations & Goals:**")
                    st.write(", ".join(motivations or ["Unstated in dialogue"]))

                    st.markdown("**Dialogue Samples:**")
                    if diag_samples:
                        for sample in diag_samples:
                            st.caption(sample)
                    else:
                        st.caption("No speaking dialogue recorded.")


# -------------------------------------------------------------
# 5. STORY TIMELINE
# -------------------------------------------------------------
elif menu_selection == "5. Story Timeline":
    st.subheader("Story Timeline & Chronological Engine")
    summary = load_active_project_data()
    scenes = summary.get("scenes", [])
    events = summary.get("events", [])
    issues = summary.get("issues", [])

    if not scenes:
        st.warning("No script loaded yet.")
    else:
        # Timeline and Scene Density Charts
        st.plotly_chart(create_timeline_chart(scenes, issues), use_container_width=True)
        st.plotly_chart(create_scene_distribution_chart(scenes), use_container_width=True)

        # Chronological Event Flow Table
        st.markdown("#### Chronological Narrative Event Sequence")
        if events:
            event_rows = []
            for e in events:
                event_rows.append({
                    "Event ID": get_val(e, "event_id", ""),
                    "Scene": f"Scene {get_val(e, 'scene_number', 1)}",
                    "Time Reference": get_val(e, "time_reference") or "Unspecified",
                    "Location": get_val(e, "location") or "Unknown",
                    "Characters Involved": ", ".join(get_val(e, "characters_involved") or []),
                    "Description": get_val(e, "description", "")
                })
            st.dataframe(pd.DataFrame(event_rows), use_container_width=True)
        else:
            st.info("No explicit narrative events extracted.")


# -------------------------------------------------------------
# 6. LOCATION TRACKER
# -------------------------------------------------------------
elif menu_selection == "6. Location Tracker":
    st.subheader("Spatial & Location Continuity Tracker")
    summary = load_active_project_data()
    scenes = summary.get("scenes", [])

    if not scenes:
        st.warning("No script loaded yet.")
    else:
        loc_data = LocationTracker.track_locations(scenes)
        unique_locs = loc_data.get("unique_locations", [])
        journeys = loc_data.get("character_journeys", {})

        st.plotly_chart(create_location_journey_chart(scenes), use_container_width=True)

        col_l1, col_l2 = st.columns([1, 2])
        with col_l1:
            st.markdown("#### Unique Story Locations")
            for loc in unique_locs:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 8px;">
                    <strong>{loc['location_name']}</strong><br>
                    <span style="font-size: 12px; color: #94A3B8;">Appears in {loc['scene_count']} scene(s): {', '.join(map(str, loc['scenes']))}</span>
                </div>
                """, unsafe_allow_html=True)

        with col_l2:
            st.markdown("#### Character Movement Paths Across Scenes")
            if journeys:
                selected_char = st.selectbox("Inspect Character Journey", list(journeys.keys()))
                if selected_char:
                    char_path = journeys[selected_char]
                    journey_rows = []
                    for step in char_path:
                        journey_rows.append({
                            "Scene": f"Scene {step['scene_number']}",
                            "Location": step['location'],
                            "Environment": step['int_ext'],
                            "Time Cue": step['time_reference']
                        })
                    st.table(pd.DataFrame(journey_rows))
            else:
                st.info("No character movement journeys detected.")


# -------------------------------------------------------------
# 7. KNOWLEDGE TRACKER
# -------------------------------------------------------------
elif menu_selection == "7. Knowledge Tracker":
    st.subheader("Character Knowledge State Tracker")
    summary = load_active_project_data()
    scenes = summary.get("scenes", [])

    if not scenes:
        st.warning("No script loaded yet.")
    else:
        know_data = KnowledgeTracker.track_knowledge(scenes)
        facts = know_data.get("disclosed_facts", {})
        char_know = know_data.get("character_knowledge", {})

        st.plotly_chart(create_knowledge_map(know_data), use_container_width=True)

        st.markdown("#### Stated Secrets, Ciphers & Confidential Disclosures")
        if facts:
            for fact_k, fact_info in facts.items():
                with st.expander(f"🔑 Secret: '{fact_k}' (Disclosed in Scene {fact_info['first_scene']})", expanded=True):
                    st.write(f"- **First Established:** Scene {fact_info['first_scene']}")
                    st.write(f"- **Source / Revealer:** {fact_info['discloser']}")
                    st.write(f"- **Witnesses Present:** {', '.join(fact_info['witnesses']) if fact_info['witnesses'] else 'None (Private)'}")
                    st.code(fact_info['evidence'])
        else:
            st.info("No classified codes or stated confidential secrets identified in this script.")


# -------------------------------------------------------------
# 8. PLOT HOLE DETECTION
# -------------------------------------------------------------
elif menu_selection == "8. Plot Hole Detection":
    st.subheader("Continuity Breakdown & Plot Hole Registry")
    summary = load_active_project_data()
    issues = summary.get("issues", [])

    if not issues:
        st.success("✅ No continuity plot holes identified in the current script.")
    else:
        # Filter controls
        c_sev, c_typ = st.columns(2)
        with c_sev:
            sev_filter = st.multiselect("Filter by Severity", ["Critical", "High", "Medium", "Low", "Informational"], default=["Critical", "High", "Medium"])
        with c_typ:
            types = sorted(list(set(get_val(i, "issue_type", "Other") for i in issues)))
            type_filter = st.multiselect("Filter by Category", types, default=types)

        filtered_issues = [
            i for i in issues
            if get_val(i, "severity", "Medium") in sev_filter and get_val(i, "issue_type", "Other") in type_filter
        ]

        st.write(f"Showing **{len(filtered_issues)}** of **{len(issues)}** identified inconsistencies:")

        for idx, iss in enumerate(filtered_issues):
            iss_sev = get_val(iss, "severity", "Medium")
            iss_title = get_val(iss, "title", "Continuity Issue")
            iss_id_str = get_val(iss, "issue_id", f"ISS_{idx+1}")
            iss_conf = get_val(iss, "confidence", 1.0)
            iss_type = get_val(iss, "issue_type", "General")
            iss_desc = get_val(iss, "description", "")
            iss_sc_refs = get_val(iss, "scene_references") or []
            iss_ev = get_val(iss, "evidence") or []
            iss_reason = get_val(iss, "reasoning", "")
            iss_fix = get_val(iss, "suggested_fix", "")
            iss_pk = get_val(iss, "id", idx)

            sev_class = f"issue-card-{iss_sev.lower()}"
            sev_color = format_severity_color(iss_sev)
            
            with st.container():
                st.markdown(f"""
                <div class="issue-card {sev_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; font-size: 16px; color: #F8FAFC;">[{iss_id_str}] {iss_title}</span>
                        <span style="background: {sev_color}; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">
                            {iss_sev.upper()} • {int(iss_conf * 100)}% Confidence
                        </span>
                    </div>
                    <div style="color: #94A3B8; font-size: 13px; margin-bottom: 8px;">
                        <strong>Category:</strong> {iss_type} | <strong>Scenes:</strong> {', '.join(map(str, iss_sc_refs))}
                    </div>
                    <div style="color: #E2E8F0; margin-bottom: 10px;">
                        {iss_desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Supporting evidence box
                with st.expander(f"View Supporting Script Evidence & Causality Reasoning ({iss_id_str})", expanded=False):
                    st.markdown("**Verbatim Script Evidence:**")
                    for ev in iss_ev:
                        ev_sc = get_val(ev, "scene_number", "?")
                        ev_tx = get_val(ev, "text", "")
                        st.markdown(f"""
                        <div class="evidence-box">
                            <strong>Scene {ev_sc}:</strong> "{ev_tx}"
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("**Logical Causality Analysis:**")
                    st.write(iss_reason)

                    st.markdown("**Recommended Solution:**")
                    st.info(iss_fix)

                    if st.button(f"🛠️ Open in AI Story Repair ({iss_id_str})", key=f"rep_btn_{iss_pk}"):
                        st.session_state["active_repair_issue"] = iss
                        st.session_state["menu_selection"] = "9. AI Story Repair"
                        st.info("Loaded into AI Story Repair. Click '9. AI Story Repair' in sidebar.")


# -------------------------------------------------------------
# 9. AI STORY REPAIR
# -------------------------------------------------------------
elif menu_selection == "9. AI Story Repair":
    st.subheader("AI Story Repair & Scene Rewriting Workbench")
    summary = load_active_project_data()
    issues = summary.get("issues", [])
    scenes = summary.get("scenes", [])

    if not issues:
        st.info("No open issues to repair. Analyze a script first.")
    else:
        issue_options = {f"[{get_val(i, 'issue_id', 'ISS')}] {get_val(i, 'title')} ({get_val(i, 'severity', 'Medium')})": i for i in issues}
        selected_key = st.selectbox("Select Continuity Issue to Resolve", list(issue_options.keys()))
        target_issue = issue_options[selected_key]

        target_scene_refs = get_val(target_issue, "scene_references") or [1]
        target_scene_num = target_scene_refs[-1] if target_scene_refs else 1
        target_scene = next((s for s in scenes if get_val(s, "scene_number") == target_scene_num), None)

        iss_sev = get_val(target_issue, "severity", "medium").lower()
        iss_title = get_val(target_issue, "title", "Continuity Issue")
        iss_desc = get_val(target_issue, "description", "")
        sc_heading = get_val(target_scene, "heading", "Unknown") if target_scene else "Unknown"

        st.markdown(f"""
        <div class="issue-card issue-card-{iss_sev}">
            <h4>{iss_title}</h4>
            <p>{iss_desc}</p>
            <strong>Target Scene for Revision:</strong> Scene {target_scene_num} ({sc_heading})
        </div>
        """, unsafe_allow_html=True)

        if st.button("✨ Generate Continuity Repair Proposal", type="primary"):
            with st.spinner("Generating narrative solutions and diff revision..."):
                repair_assistant = RepairAssistant(GeminiService(st.session_state.get("gemini_api_key")))
                original_text = get_val(target_scene, "raw_content", "") if target_scene else ""
                repair_res = repair_assistant.generate_repair(target_issue, original_text, target_scene_num)

                st.session_state["current_repair_proposal"] = repair_res

        proposal = st.session_state.get("current_repair_proposal")
        if proposal:
            st.markdown("---")
            st.markdown("### Continuity Analysis & Solutions")
            st.write(f"**Impact on Story:** {proposal['continuity_impact']}")
            
            c_fix1, c_fix2 = st.columns(2)
            with c_fix1:
                st.markdown("**Primary Recommended Fix:**")
                st.success(proposal['primary_fix'])
            with c_fix2:
                st.markdown("**Alternative Narrative Solution:**")
                st.info(proposal['alternative_fix'])

            st.markdown("### Scene Side-by-Side Comparison")
            col_orig, col_rev = st.columns(2)
            with col_orig:
                st.markdown(f"**Original Scene {proposal['target_scene_number']}**")
                st.code(proposal['original_scene_text'], language="markdown")
            with col_rev:
                st.markdown(f"**Revised Scene {proposal['target_scene_number']} (Continuity Preserved)**")
                st.code(proposal['revised_scene_text'], language="markdown")

            st.markdown("### Line-by-Line Narrative Diff")
            diff_container = st.container()
            with diff_container:
                for d in proposal.get("diff", []):
                    if d["type"] == "deleted":
                        st.markdown(f"<span class='diff-del'>- {d['text']}</span>", unsafe_allow_html=True)
                    elif d["type"] == "added":
                        st.markdown(f"<span class='diff-add'>+ {d['text']}</span>", unsafe_allow_html=True)

            # Accept / Reject / Feedback
            st.markdown("### Writer Decision")
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                if st.button("✅ Accept Proposal"):
                    save_repair_suggestion(
                        issue_id=get_val(target_issue, "id"),
                        explanation=proposal["explanation"],
                        continuity_impact=proposal["continuity_impact"],
                        primary_fix=proposal["primary_fix"],
                        alternative_fix=proposal["alternative_fix"],
                        original_scene_text=proposal["original_scene_text"],
                        revised_scene_text=proposal["revised_scene_text"],
                        scene_number=proposal["target_scene_number"],
                        user_status="Accepted"
                    )
                    st.success("Proposal marked as ACCEPTED and stored in project archive.")
            with col_act2:
                if st.button("❌ Reject Proposal"):
                    save_repair_suggestion(
                        issue_id=get_val(target_issue, "id"),
                        explanation=proposal["explanation"],
                        continuity_impact=proposal["continuity_impact"],
                        primary_fix=proposal["primary_fix"],
                        user_status="Rejected"
                    )
                    st.info("Proposal rejected.")
            with col_act3:
                feedback = st.text_input("Feedback / Writer Notes")
                if st.button("💾 Save to Project Notes"):
                    save_repair_suggestion(
                        issue_id=get_val(target_issue, "id"),
                        explanation=proposal["explanation"],
                        continuity_impact=proposal["continuity_impact"],
                        primary_fix=proposal["primary_fix"],
                        user_status="Saved",
                        user_feedback=feedback
                    )
                    st.success("Saved with notes.")


# -------------------------------------------------------------
# 10. REPORTS
# -------------------------------------------------------------
elif menu_selection == "10. Reports":
    st.subheader("Screenplay Continuity Reports & Documentation Export")
    summary = load_active_project_data()

    # 1. Project-Specific Reports
    if not summary:
        st.info("No screenplay analysis loaded yet. You can still download the system implementation plan below or upload a script under '2. Upload Script'.")
    else:
        st.markdown(f"### Export Dossier for '{summary.get('title', 'Project')}'")
        st.write(f"- Total Scenes: {summary.get('total_scenes')}")
        st.write(f"- Total Detected Continuity Breaches: {summary.get('total_issues')}")

        col_rep1, col_rep2 = st.columns(2)

        with col_rep1:
            st.markdown("#### 📄 Executive PDF Continuity Report")
            st.write("Generate a formal, publication-ready PDF analysis report with executive metrics, character dossiers, scene breakdown, and evidence cards.")
            
            pdf_bytes = generate_pdf_report(summary)
            st.download_button(
                label="📥 Download Comprehensive PDF Report",
                data=pdf_bytes,
                file_name=f"PlotHole_OS_Report_{summary.get('title', 'Script').replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary"
            )

        with col_rep2:
            st.markdown("#### 🗄️ Structured JSON Data Export")
            st.write("Export complete structured screenplay data, scene objects, knowledge graphs, and continuity audit results for external pipelines.")
            
            json_data = export_project_json(summary)
            st.download_button(
                label="📥 Download Analysis JSON",
                data=json_data,
                file_name=f"PlotHole_OS_{summary.get('title', 'Script').replace(' ', '_')}.json",
                mime="application/json"
            )

    # 2. System Architecture & Master Implementation Plan PDF
    st.markdown("---")
    st.markdown("### 📋 System Architecture & Implementation Plan")
    st.write("Download the comprehensive architectural specifications, database schemas, 7-phase roadmap, and the v2.0 Advanced Feature Upgrade Blueprint.")

    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
        plan_pdf_path = os.path.join(os.path.dirname(__file__), "PlotHole_OS_Implementation_Plan.pdf")
        if os.path.exists(plan_pdf_path):
            with open(plan_pdf_path, "rb") as f:
                plan_pdf_bytes = f.read()
            st.download_button(
                label="📥 Download Master Plan (PDF)",
                data=plan_pdf_bytes,
                file_name="PlotHole_OS_Implementation_Plan.pdf",
                mime="application/pdf",
                type="primary" if not summary else "secondary"
            )

    with col_doc2:
        upgrade_pdf_path = os.path.join(os.path.dirname(__file__), "PlotHole_OS_Advanced_Enhancement_Plan.pdf")
        if os.path.exists(upgrade_pdf_path):
            with open(upgrade_pdf_path, "rb") as f:
                upgrade_pdf_bytes = f.read()
            st.download_button(
                label="🚀 Download Upgrade Blueprint (PDF)",
                data=upgrade_pdf_bytes,
                file_name="PlotHole_OS_Advanced_Enhancement_Plan.pdf",
                mime="application/pdf",
                type="primary" if not summary else "secondary"
            )


# -------------------------------------------------------------
# 11. PROJECT HISTORY
# -------------------------------------------------------------
elif menu_selection == "11. Project History":
    st.subheader("Archived Screenplay Projects & History")
    projects = list_projects()

    if not projects:
        st.info("No saved projects found in local SQLite database.")
    else:
        for p in projects:
            col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
            with col_p1:
                st.markdown(f"### {p['title']}")
                st.caption(f"Author: {p['author']} | Genre: {p['genre']} | Last Modified: {p['updated_at']}")
                st.write(f"Scenes: **{p['scene_count']}** | Characters: **{p['character_count']}** | Inconsistencies: **{p['issue_count']}**")
            with col_p2:
                if st.button("📂 Open Project", key=f"open_{p['id']}"):
                    st.session_state["current_project_id"] = p["id"]
                    st.success(f"Loaded '{p['title']}'.")
                    st.rerun()
            with col_p3:
                if st.button("🗑️ Delete", key=f"del_{p['id']}"):
                    delete_project(p["id"])
                    if st.session_state.get("current_project_id") == p["id"]:
                        st.session_state["current_project_id"] = None
                    st.warning("Project deleted.")
                    st.rerun()
            st.markdown("---")


# -------------------------------------------------------------
# 12. SETTINGS
# -------------------------------------------------------------
elif menu_selection == "12. Settings":
    st.subheader("PlotHole OS Configuration & Environment")

    st.markdown("#### 🤖 Google Gemini AI Configuration")
    current_key = st.session_state.get("gemini_api_key", "")
    masked_key = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) > 10 else ""
    
    new_api_key = st.text_input(
        "Gemini API Key",
        value=current_key,
        type="password",
        help="Enter your Google Gemini API Key to enable deep reasoning, long-script contextual analysis, and scene rewriting."
    )

    if new_api_key != current_key:
        st.session_state["gemini_api_key"] = new_api_key
        st.success("API Key updated in session.")

    c_t1, c_t2 = st.columns(2)
    with c_t1:
        if st.button("⚡ Test Gemini API Connection"):
            service = GeminiService(new_api_key)
            test_res = service.test_connection()
            if test_res.get("success"):
                st.success(f"Connection Successful! Model responded: '{test_res.get('message')}'")
            else:
                st.error(test_res.get("error"))

    st.markdown("---")
    st.markdown("#### ⚙️ Analysis & Model Preferences")
    sel_model = st.selectbox(
        "Default Gemini Model",
        ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-3.8-flash"],
        index=0
    )
    settings.DEFAULT_GEMINI_MODEL = sel_model

    conf_thresh = st.slider(
        "Minimum Confidence Threshold for Findings",
        min_value=0.50,
        max_value=0.95,
        value=settings.MIN_CONFIDENCE_THRESHOLD,
        step=0.05
    )
    settings.MIN_CONFIDENCE_THRESHOLD = conf_thresh

    st.markdown("---")
    st.markdown("#### 💾 Database & Local Storage")
    st.write(f"- Database URL: `{settings.DATABASE_URL}`")
    st.write(f"- Max Upload Size: `{settings.MAX_UPLOAD_SIZE_MB} MB`")
    st.write(f"- Supported Formats: `{', '.join(settings.ALLOWED_EXTENSIONS)}`")

