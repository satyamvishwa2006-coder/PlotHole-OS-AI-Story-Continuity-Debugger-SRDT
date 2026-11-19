# PlotHole OS – Comprehensive Testing & Verification Plan

## 1. Testing Philosophy & Quality Objectives

**PlotHole OS** is designed for mission-critical script analysis where false negatives (missing a fatal plot hole) can lead to expensive production reshoots, and false positives (flagging intentional artistic choices) frustrate screenwriters. 

Our testing strategy enforces **four quality pillars**:
1. **Deterministic Rule Verification**: All 8 continuity detectors must reliably detect known inconsistencies on benchmark scripts.
2. **Type Safety & Data Model Resilience**: Data transfer across database ORM, Pydantic DTOs, and Streamlit visualization layers must never trigger `TypeError` or `AttributeError`.
3. **Graceful Fault Tolerance**: Corrupt uploads, missing API keys, empty scenes, and API timeouts must degrade gracefully with clear user diagnostics.
4. **Sub-second Local Test Execution**: Complete test suite must run locally in under 5 seconds to support rapid test-driven iteration.

---

## 2. Test Architecture & Structure

```
tests/
├── test_parser.py           # Ingestion, validation, screenplay & prose parsing
├── test_database.py         # SQLAlchemy CRUD operations & session lifecycle
├── test_detection.py        # All 8 continuity detectors against benchmark script
├── test_visualizations.py   # Plotly/NetworkX charts with dicts, ORMs, and Pydantic schemas
└── test_reports.py          # PDF generation & JSON export serialization
```

---

## 3. Comprehensive Test Matrix

| Test Suite | Test Case Identifier | Target Module | Description | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Parser** | `test_file_extension_validation` | `DocumentProcessor` | Tests supported vs unsupported file extensions | Accepts `.pdf`, `.docx`, `.txt`; rejects `.exe`, `.mp4` |
| **Parser** | `test_file_size_validation` | `DocumentProcessor` | Uploads exceeding 30MB limit | Rejects with user-friendly file size error |
| **Parser** | `test_text_cleaner` | `TextCleaner` | Cleans `\r\n`, multiple spaces, page break artifacts | Produces clean normalized Unicode text |
| **Parser** | `test_screenplay_parser` | `ScriptParser` | Parses standard screenplay sluglines, dialogue, action | Segments into discrete `Scene` objects with character lists |
| **Parser** | `test_prose_parser` | `ScriptParser` | Parses non-screenplay prose with chapter breaks | Automatically partitions into coherent narrative units |
| **Database** | `test_project_crud` | `operations.py` | Creates project, scenes, characters, queries, and deletes | Full relational persistence without detached instance errors |
| **Detection** | `test_sample_script_parsing` | `ScriptParser` | Ingests benchmark script ("THE CIPHER PROTOCOL") | Accurately extracts 8 scenes, 4 characters, and events |
| **Detection** | `test_continuity_detection_engine` | `DetectorCoordinator` | Runs all 8 detectors against benchmark screenplay | Discovers all 8 planted plot holes with verbatim evidence |
| **Visuals** | `test_timeline_chart_empty` | `timeline_chart.py` | Passes empty scene and issue lists | Returns styled empty-state Plotly figure without crashing |
| **Visuals** | `test_timeline_chart_with_dicts` | `timeline_chart.py` | Passes raw dictionaries | Renders timeline scatter plot |
| **Visuals** | `test_timeline_chart_with_orm_objects` | `timeline_chart.py` | Passes SQLAlchemy `Scene` and `DetectedIssue` objects | Verifies dual-access without `TypeError` |
| **Visuals** | `test_timeline_chart_with_pydantic_models` | `timeline_chart.py` | Passes `SceneModel` and `PlotHoleModel` | Renders cleanly using Pydantic schemas |
| **Visuals** | `test_character_network_graph` | `character_graph.py` | Tests empty, dict, ORM, and Pydantic character networks | Produces NetworkX + Plotly spring-layout graph |
| **Visuals** | `test_all_analytics_visualizations` | `analytics.py` | Tests all 7 charts (donut, bar, gauge, density, path, map) | All charts return valid `go.Figure` instances |
| **Reports** | `test_pdf_generation` | `pdf_generator.py` | Generates ReportLab PDF from analysis summary | Produces non-empty valid PDF byte stream (`%PDF-1.4`) |
| **Reports** | `test_json_export` | `json_exporter.py` | Serializes project, scenes, and issues to JSON string | Produces valid JSON string without recursion errors |

---

## 4. Edge Case Test Catalog

### Edge Case 1: Corrupted or Binary Files
- **Condition**: Upload an arbitrary binary file renamed to `.txt` or a corrupted `.pdf`.
- **Expected Behavior**: `DocumentProcessor.process_file()` catches extraction exceptions, does not crash the server, and returns `{"success": False, "error": "Unable to read document content..."}`.

### Edge Case 2: Zero-Dialogue Screenplay
- **Condition**: Silent or purely action-driven screenplay (e.g., survival film with no spoken lines).
- **Expected Behavior**: `CharacterExtractor` identifies characters from action lines; `CharacterIntelligence` displays `No speaking dialogue recorded` without division-by-zero errors in dialogue frequency metrics.

### Edge Case 3: Split Sluglines Across Linebreaks
- **Condition**: Writer formats headings across multiple lines:
  ```
  SCENE 4
  INT. UNDERGROUND BUNKER - NIGHT
  ```
- **Expected Behavior**: `ScriptParser` automatically collapses adjacent headings within 3 lines into a single scene, preventing empty "ghost" scenes.

### Edge Case 4: Post-Mortem Action vs Dialogue
- **Condition**: Character is confirmed dead in Scene 2, but appears in Scene 4 taking an action (e.g. `ALEX grabs his jacket`) rather than speaking dialogue.
- **Expected Behavior**: `LogicalContradictionDetector` and `CharacterConsistencyDetector` scan both dialogue and action text to identify the post-mortem anomaly.

### Edge Case 5: Missing or Invalid Gemini API Key
- **Condition**: User launches application without `.env` or enters an invalid API key.
- **Expected Behavior**: System operates seamlessly in deterministic rule-based mode. In UI Module 9, a prompt invites the user to enter their API key, but no crash or traceback occurs.

---

## 5. Automated Verification Execution

Run the complete test suite locally with:
```powershell
# 1. Syntax & Bytecode Compilation
python -m compileall .

# 2. Dependency Check
python -m pip install -r requirements.txt

# 3. Fast Pytest Execution
python -m pytest -q

# 4. Verbose Pytest Execution
python -m pytest -v
```

### Verified Baseline Benchmark Output:
```
tests/test_database.py::test_project_crud PASSED                         [  6%]
tests/test_detection.py::test_sample_script_parsing PASSED               [ 12%]
tests/test_detection.py::test_continuity_detection_engine PASSED         [ 18%]
tests/test_parser.py::test_file_extension_validation PASSED              [ 25%]
tests/test_parser.py::test_file_size_validation PASSED                   [ 31%]
tests/test_parser.py::test_text_cleaner PASSED                           [ 37%]
tests/test_parser.py::test_screenplay_parser PASSED                      [ 43%]
tests/test_parser.py::test_prose_parser PASSED                           [ 50%]
tests/test_reports.py::test_pdf_generation PASSED                        [ 56%]
tests/test_reports.py::test_json_export PASSED                           [ 62%]
tests/test_visualizations.py::test_timeline_chart_empty PASSED           [ 68%]
tests/test_visualizations.py::test_timeline_chart_with_dicts PASSED      [ 75%]
tests/test_visualizations.py::test_timeline_chart_with_orm_objects PASSED [ 81%]
tests/test_visualizations.py::test_timeline_chart_with_pydantic_models PASSED [ 87%]
tests/test_visualizations.py::test_character_network_graph PASSED        [ 93%]
tests/test_visualizations.py::test_all_analytics_visualizations PASSED   [100%]

============================= 16 passed in 3.00s ==============================
```

