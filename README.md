# PlotHole OS – AI-Powered Story Continuity & Logic Debugger

> **Tagline:** *"Every Story Has a Logic. We Find Where It Breaks."*

---

## 1. Project Introduction & Overview

**PlotHole OS** is an intelligent, professional-grade screenplay analysis and narrative continuity debugging platform. Designed for screenwriters, script doctors, showrunners, development executives, and story analysts, PlotHole OS ingests written screenplays (PDF, DOCX, TXT), reconstructs their underlying narrative ontology (characters, locations, timelines, knowledge distribution, and physical props), and identifies continuity errors, plot holes, and logical breakdowns.

Unlike generic chatbots or surface-level summarizers, PlotHole OS uses a **hybrid architecture** combining deterministic rule-based verification with Google Gemini AI contextual reasoning. Every identified inconsistency is grounded in verbatim script excerpts, exact scene references, formal causality reasoning, confidence scores, and actionable rewrite recommendations.

---

## 2. Problem Statement & Objectives

Screenplays are complex multi-dimensional systems where events unfold non-linearly across hundreds of scenes. Human writers and script supervisors frequently encounter continuity breaks:
- A character killed in Scene 4 casually walks onto the set in Scene 6.
- A critical flash drive incinerated in Scene 3 reappears intact in Scene 5.
- A character trapped inside a subterranean bunker in Berlin appears 10 minutes later in a Parisian bistro with zero transit or escape sequence.
- A character cites a top-secret cipher they were never told and never witnessed.
- A protagonist vows mortal vengeance against an antagonist, only to cheerfully accept a mission from them without narrative explanation.

### Core Objectives:
1. **Automated Structural Understanding:** Ingest industry-standard screenplays (INT/EXT headers, character cues, dialogue, action) and prose fiction.
2. **Entity & State Tracking:** Maintain real-time tracking of characters, locations, timelines, knowledge, and objects across scenes.
3. **Multi-Dimensional Plot Hole Detection:** Detect continuity breaks across 8 core dimensions.
4. **Verifiable Evidence Chain:** Provide exact scene numbers and verbatim quotes for every finding without hallucination.
5. **AI Story Repair:** Suggest non-destructive narrative solutions and line-by-line scene rewrites with visual diffs.
6. **Executive Reporting:** Generate downloadable ReportLab PDF dossiers and structured JSON exports.

---

## 3. Technology Stack

- **Application & Dashboard:** Python 3.11+, Streamlit
- **Generative AI:** Google Gemini API (`google-genai` SDK)
- **Natural Language Processing:** Regular Expressions, spaCy NER tokenization, text normalization
- **Document Processing:** PyPDF (`pypdf`), python-docx (`docx`), multi-encoding TXT parser
- **Data & Relational Storage:** SQLite, SQLAlchemy ORM, Pydantic v2
- **Visualizations:** Plotly Graph Objects, NetworkX graph algorithms
- **Reporting:** ReportLab (vector PDF generation), JSON
- **Testing:** Pytest

---

## 4. The 8 Continuity Detection Engines

| Engine | Description | Sample Detected Error |
|---|---|---|
| **1. Timeline Consistency** | Clock regressions, impossible day/night shifts, missing flashback indicators | Scene 4 set at 9:00 PM Tuesday follows Scene 3 set at 10:00 PM Tuesday without flashback tag. |
| **2. Character Consistency** | Physical state violations, radical behavioral reversals | Severely shattered shoulder in Scene 2, but effortlessly hangs from helicopter with that arm in Scene 4. |
| **3. Location Continuity** | Impossible spatial teleportation, unaddressed confinement | Trapped in locked Berlin bunker in Scene 2; sipping coffee in Paris in Scene 3 without transit. |
| **4. Knowledge Consistency** | Premature omniscience, speaking of unwitnessed secrets | Character inputs classified password "CHRONOS-9" when it was concealed from them in Scene 1. |
| **5. Object Continuity** | Conservation of physical props, destroyed items resurfacing | Cracked titanium flash drive destroyed in incinerator in Scene 3 is handed intact to director in Scene 5. |
| **6. Motivation Consistency** | Unearned goal reversals, unprompted alliance shifts | Protagonist vows mortal revenge against director in Scene 2, but cheerfully pledges loyalty in Scene 6. |
| **7. Missing Transitions** | Abrupt tonal jumps, abandoned mortal peril | Scene ends with 20 guns pointed at character's head; next scene casually opens in peaceful archive library. |
| **8. Logical Contradictions** | Causality violations, post-mortem appearances | Mercenary shot in the heart and killed in Scene 4 stands at attention alive in Scene 6. |

---

## 5. System Architecture & Folder Structure

```
PlotHole-OS/
│
├── app.py                      # Main Streamlit Dashboard (12 Modules)
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation & user guide
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Central application configuration & thresholds
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLAlchemy engine, session maker, init_db
│   ├── models.py               # Database schemas (Project, Scene, Character, Issue, etc.)
│   └── operations.py           # CRUD operations & project summary aggregators
│
├── utils/
│   ├── __init__.py
│   ├── validators.py           # File extension, size, hash, and content validation
│   ├── text_cleaner.py         # Script text normalization, artifact stripping
│   └── helpers.py              # Diff generator, token estimator, badge formatters
│
├── core/
│   ├── __init__.py
│   ├── document_processor.py   # Multi-format document parser (PDF, DOCX, TXT)
│   ├── script_parser.py        # Screenplay heading, character, dialogue & prose parser
│   ├── scene_extractor.py      # Scene segmentation & manual override manager
│   ├── character_extractor.py  # Character profiling, traits (explicit vs inferred)
│   ├── event_extractor.py      # Chronological narrative event extractor
│   ├── timeline_engine.py      # Chronological ordering & temporal constraint engine
│   ├── location_tracker.py     # Spatial journeys & scene occupancy tracking
│   ├── knowledge_tracker.py    # Confidential fact disclosure & witness matrix
│   └── object_tracker.py       # Prop lifecycle & physical status tracking
│
├── detection/
│   ├── __init__.py
│   ├── timeline_detector.py    # Timeline contradiction detector
│   ├── character_detector.py   # Character physical & personality consistency detector
│   ├── location_detector.py    # Location continuity & teleportation detector
│   ├── knowledge_detector.py   # Knowledge leak & omniscience detector
│   ├── object_detector.py      # Object continuity & destruction detector
│   ├── motivation_detector.py  # Motivation contradiction detector
│   ├── missing_transition_detector.py # Missing transition detector
│   ├── logical_detector.py     # Logical causality & death contradiction detector
│   └── detector_coordinator.py # Coordinator for unified evidence-backed issue registry
│
├── ai/
│   ├── __init__.py
│   ├── gemini_service.py       # Google GenAI API client with retries & validation
│   ├── prompts.py              # Structured prompts for continuity auditing & repair
│   ├── reasoning_engine.py     # Multi-chunk script analysis with context memory
│   └── repair_assistant.py     # Scene rewrite generator & side-by-side diff engine
│
├── visualization/
│   ├── __init__.py
│   ├── timeline_chart.py       # Interactive Plotly narrative timeline
│   ├── character_graph.py      # NetworkX + Plotly character interaction network
│   └── analytics.py            # Severity donut, category bar, continuity health gauge
│
├── reports/
│   ├── __init__.py
│   ├── pdf_generator.py        # ReportLab vector PDF continuity report generator
│   └── json_exporter.py        # Comprehensive JSON data exporter
│
├── sample_data/
│   ├── sample_screenplay.txt   # Built-in test script ("THE CIPHER PROTOCOL")
│   └── expected_findings.json  # Reference guide to all 8 planted continuity errors
│
└── tests/
    ├── test_parser.py          # Unit tests for document extraction & script parser
    ├── test_detection.py       # Unit tests verifying all 8 detectors against sample data
    ├── test_database.py        # Unit tests for database CRUD operations
    └── test_reports.py         # Unit tests for PDF & JSON generation
```

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.11, 3.12, or 3.13 installed
- Git installed (optional)
- A Google Gemini API Key (get one free at [Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone or Navigate to the Workspace
```bash
cd "c:\Users\moolc\OneDrive\Desktop\Generative ID"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the example configuration:
```bash
copy .env.example .env
```
Open `.env` and paste your Gemini API Key:
```ini
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-2.5-flash
```

*(Note: PlotHole OS functions 100% locally with deterministic rule-based engines even without an API key. Supplying an API key unlocks deep contextual reasoning and AI scene rewrites).*

### Step 4: Run the Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 7. Beginner Setup Guide for VS Code

If you are using Visual Studio Code:
1. Open VS Code.
2. Select **File > Open Folder...** and select `Generative ID`.
3. Open the integrated terminal (`Ctrl + ~`).
4. Select your Python interpreter: Press `Ctrl + Shift + P`, type `Python: Select Interpreter`, and select your Python 3.11+ executable.
5. In the terminal, run:
   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```
6. VS Code will display a notification: *"Your application running on port 8501 is available. Open in Browser."* Click **Open in Browser**.

---

## 8. Step-by-Step Usage Walkthrough

1. **Dashboard Overview:** Launching the app opens the Overview dashboard showing script stats, timeline hotspots, and continuity health index.
2. **Load Built-In Sample:** On the Overview or Upload Script page, click **"🚀 Load Sample Screenplay ('THE CIPHER PROTOCOL')"**.
3. **Explore Scenes:** Go to **Script Explorer** to browse scenes, search dialogue, view character presence, and inspect flags.
4. **Analyze Characters:** Open **Character Intelligence** to interact with the NetworkX relationship graph and read character dossiers.
5. **Inspect Timeline:** View chronological event sequences and temporal regressions in **Story Timeline**.
6. **Examine Plot Holes:** Go to **Plot Hole Detection** to review categorized continuity breaks with verbatim quotes.
7. **Generate AI Repairs:** In **AI Story Repair**, click **"Generate Continuity Repair Proposal"** to compare original vs revised scenes with line-by-line diffs.
8. **Export Reports:** Navigate to **Reports** to download the professional ReportLab PDF dossier or raw JSON dataset.
9. **Project History:** Reopen previously analyzed screenplays anytime from **Project History**.

---

## 9. Running the Test Suite

Run all unit tests using pytest:
```bash
python -m pytest -v
```
All 10 test suites covering parsing, rule-based detection, database operations, and PDF/JSON generation will execute and report status.

---

## 10. Sample Test Screenplay ("THE CIPHER PROTOCOL")

The project includes an original, fictional test screenplay located at `sample_data/sample_screenplay.txt`. It features 6 scenes and deliberately introduced continuity errors:
1. **Scene 1:** Marcus decrypts password `CHRONOS-9` and conceals it from Sarah.
2. **Scene 2:** Sarah mysteriously knows `CHRONOS-9` without being told. Marcus's left shoulder is shattered by gunfire. Marcus vows mortal revenge on Director Vance.
3. **Scene 3:** Marcus drops the cracked titanium flash drive into an incinerator; it burns to ash. Marcus is in Paris 45 minutes after being locked in a Berlin bunker.
4. **Scene 4:** Set backwards at 9:00 PM without flashback cue. Marcus effortlessly hangs from a helicopter with his shattered left arm. Korda is shot in the heart and killed.
5. **Scene 5:** Sarah produces the intact cracked titanium flash drive from her pocket.
6. **Scene 6:** Marcus cheerfully pledges loyalty to Director Vance. Korda is alive and well.

---

## 11. System Limitations & Future Enhancements

### Current Scope & Limitations:
- **Script-Only:** Focuses strictly on written text (PDF, DOCX, TXT). Does not process video or audio footage.
- **Stylistic Intent:** In experimental avant-garde or dream-logic scripts (e.g. David Lynch style), surrealist scene jumps may be flagged as continuity breaks; writers can dismiss these via manual overrides.

### Planned Enhancements:
- Direct Final Draft (.fdx) file ingestion.
- Multi-user collaborative screenplay editing.
- Automatic beat-sheet / three-act structure adherence scoring.
- Audio table-read generation via Gemini Text-to-Speech.

