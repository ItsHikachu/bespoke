# Bespoke - AI Agent Development Guide

**Last Updated**: 2026-03-11  
**Current Phase**: Phase 4 Implementation In Progress  
**Project Path**: `/home/nova/.local/projects/bespoke`

---

## Project Overview

**Bespoke** is a fully local desktop voice practice application built with PyQt6. It provides real-time audio biofeedback for 20 voice exercises across 4 modules: Pitch Control, Breath & Sustain, Pace & Rhythm, and Dynamics & Projection.

**Core Principle**: Every exercise produces measurable audio data displayed in real-time. No cloud APIs. Voice data never leaves the machine.

**Tech Stack**:
- UI: PyQt6
- Audio: sounddevice, librosa, scipy
- Visualization: pyqtgraph
- Database: SQLite (~/.bespoke/bespoke.db)
- Optional: Ollama (coaching), faster-whisper (Module 3 transcription)

---

## Critical Build Discipline

### ⚠️ PHASE ORDER IS SACRED

**DO NOT scaffold future phases until current phase is working.**

The build order from `Bespoke_Windsurf_Prompt.md` is:
1. **Phase 1**: Audio engine + Pitch Hold (1a) + basic UI ✅ COMPLETE
2. **Phase 2**: All Module 1 exercises + Dashboard + Settings ✅ COMPLETE
3. **Phase 3**: All visualizers + Modules 2-4 exercises ✅ COMPLETE
4. **Phase 4**: Baseline assessment + tier gating + Ollama curriculum + polish 🔄 IN PROGRESS

**Why this matters**: Each phase validates core functionality before adding complexity. Skipping ahead creates untestable, broken code.

### Testing Requirements

Before marking any phase complete:
- Run `python main.py` - must launch without errors
- Test the specific deliverables for that phase
- Verify no regressions in previous phases
- Check `TESTING_GUIDE.md` for comprehensive test cases

---

## Architecture & Key Files

### Audio Pipeline
```
sounddevice stream (44100 Hz, 1024 buffer)
  ↓
audio_engine.py (_audio_callback in separate thread)
  ↓
Real-time analysis: pitch, amplitude_db, spectral_centroid
  ↓
QTimer polling (60fps) in practice_session.py
  ↓
Visualizer widgets (pyqtgraph + custom QPainter)
```

**CRITICAL**: Audio callback runs in a separate thread. NEVER call Qt widget methods directly from `on_analysis` callback. Use QTimer polling pattern.

### File Structure
```
bespoke/
├── main.py                      # Entry point, pyqtgraph config
├── audio_engine.py              # Real-time audio capture & analysis
├── exercises.py                 # 20 exercises × 3 tiers = 60 configurations
├── scoring.py                   # Score computation for all exercise types
├── exercise_instructions.py     # Phase-aware instructions for all exercises
├── database.py                  # SQLite wrapper
├── ollama_coach.py              # Ollama integration (graceful degradation)
├── whisper_transcriber.py       # faster-whisper for Module 3
├── ui/
│   ├── main_window.py           # Navigation shell
│   ├── dashboard.py             # Streak calendar, progress rings
│   ├── practice_session.py      # Core exercise view (THE MAIN SCREEN)
│   ├── settings_view.py         # Mic selection, threshold calibration
│   └── widgets/
│       ├── pitch_graph.py       # Module 1 visualizer
│       ├── amplitude_bar.py     # Module 2 vertical meter
│       ├── amplitude_envelope.py # Module 2 scrolling trace
│       ├── wpm_gauge.py         # Module 3 circular gauge
│       ├── db_meter.py          # Module 4 peak/RMS meters
│       ├── centroid_bar.py      # Module 4 brightness bar
│       ├── streak_calendar.py   # Dashboard calendar
│       └── progress_rings.py    # Dashboard module rings
└── resources/
    ├── passages.json            # Reading passages (not yet implemented)
    ├── topics.json              # Speaking topics (not yet implemented)
    └── style.qss                # Dark theme (not yet implemented)
```

---

## Common Pitfalls & Gotchas

### 1. Thread Safety with Audio Engine

**WRONG**:
```python
def _audio_callback(self, indata, frames, time_info, status):
    # This runs in audio thread!
    self.pitch_graph.add_data_point(pitch)  # ❌ CRASH
```

**RIGHT**:
```python
# In practice_session.py:
self.ui_timer = QTimer()
self.ui_timer.timeout.connect(self._update_visualizer)
self.ui_timer.start(16)  # ~60fps

def _update_visualizer(self):
    # Safe - we're in main thread
    pitch = self.audio_engine.pitch
    self.pitch_graph.add_data_point(pitch)
```

### 2. Widget Initialization Order

**WRONG**:
```python
def __init__(self):
    super().__init__()
    self.init_ui()  # ❌ UI tries to access self.data before it exists
    self.data = []
```

**RIGHT**:
```python
def __init__(self):
    super().__init__()
    self.data = []  # ✅ Data attributes first
    self.init_ui()  # Then UI setup
```

### 3. Duplicate Code in Classes

**Watch for**: Methods accidentally placed in wrong class. Example from recent fix:
- `ExerciseInstructions._get_2a_instructions()` ✅ Correct
- `ExerciseContent._get_2a_instructions()` ❌ Duplicate (removed)

Always verify method belongs to the correct class based on its purpose.

### 4. Pyqtgraph Pen Styles

**WRONG**:
```python
pen = pg.mkPen('#F59E0B', width=2, style=Qt.DashLine)  # ❌ Doesn't work
```

**RIGHT**:
```python
pen = pg.mkPen('#F59E0B', width=2, style=QtCore.Qt.DashLine)  # ✅ Use QtCore
# OR use dash pattern:
pen = pg.mkPen('#F59E0B', width=2)
pen.setDashPattern([5, 5])  # ✅ Works reliably
```

### 5. Exercise ID Mapping

Exercise IDs are strings: `"1a"`, `"2c"`, `"4e"`, etc.
- Module 1: `1a-1e` (Pitch Control)
- Module 2: `2a-2e` (Breath & Sustain)
- Module 3: `3a-3e` (Pace & Rhythm)
- Module 4: `4a-4e` (Dynamics & Projection)

Each exercise has 3 tiers: `foundation`, `intermediate`, `advanced`

### 6. Graceful Degradation Pattern

**ALWAYS** check availability before using optional dependencies:

```python
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class OllamaCoach:
    def post_session_feedback(self, ...):
        if not self.available:
            return self._fallback_feedback(scores)  # ✅ Graceful
        # ... actual Ollama call
```

Never crash if Ollama or Whisper is missing. Core exercises must work without them.

---

## Exercise-Visualizer Mapping

| Module | Exercises | Visualizer Widget |
|--------|-----------|-------------------|
| 1: Pitch Control | 1a-1e | `pitch_graph` |
| 2: Breath & Sustain | 2a-2e | `amplitude_bar` or `amplitude_envelope` |
| 3: Pace & Rhythm | 3a-3e | `wpm_gauge` |
| 4: Dynamics & Projection | 4a-4e | `db_meter` or `centroid_bar` |

Check `exercises.py` for exact visualizer per exercise.

---

## Phase 4 Roadmap (Next Work)

### Must Implement:

1. **Baseline Assessment Flow**
   - First-run experience: guide user through baseline exercises
   - Measure: pitch range, sustain duration, dynamic range, avg WPM
   - Store in `baselines` table
   - UI: `ui/baseline_assessment.py` (new file)

2. **Tier Gating Logic**
   - Intermediate unlocks when 3/5 Foundation exercises score >70%
   - Advanced unlocks when 3/5 Intermediate exercises score >70%
   - Show lock icons in module view
   - Update `ui/module_view.py` (not yet created)

3. **Weekly Curriculum Generation**
   - Use Ollama to analyze progress and generate weekly plan
   - Fallback to default balanced plan if Ollama unavailable
   - Store in `curriculum` table
   - Display on Dashboard

4. **Progress View**
   - Matplotlib radar chart (4 axes, normalized 0-100)
   - Per-module line charts (last 30 sessions)
   - Stats cards: total minutes, streaks
   - File: `ui/progress_view.py` (exists but minimal)

5. **Polish**
   - Load `resources/style.qss` for dark theme
   - Error handling: no mic, Ollama down, Whisper missing
   - PyInstaller packaging script
   - Final testing pass

### Files to Create:
- `ui/baseline_assessment.py`
- `ui/module_view.py` (currently exercises launched from dashboard)
- `resources/style.qss` (dark theme stylesheet)
- `build_installer.py` (PyInstaller script)

---

## Testing Strategy

### Quick Smoke Test
```bash
cd /home/nova/.local/projects/bespoke
source venv/bin/activate
python main.py
# Should launch without errors, show dashboard
```

### Comprehensive Testing
See `TESTING_GUIDE.md` for 14 test categories covering:
- All 20 exercises launch
- All visualizers render and update
- Audio engine integration
- Database persistence
- Graceful degradation
- Performance (CPU, memory)

### Before Committing
1. Run smoke test
2. Test modified exercises/visualizers
3. Check for regressions
4. Verify no duplicate code
5. Ensure imports are correct

---

## Git Workflow

### Current State
- Branch: `master`
- Remote: Check with `git remote -v`
- Last commit: "Add comprehensive testing guide for Phase 3 checkpoint"

### Committing Changes
```bash
# Check status
git status

# Stage changes
git add -A

# Commit with descriptive message
git commit -m "Phase X: Brief description of changes"

# Push to GitHub
git push origin master
```

### Commit Message Format
- **Phase 1-4**: `Phase N: Description`
- **Bug fixes**: `Fix: Description of bug`
- **Refactor**: `Refactor: What was refactored`
- **Docs**: `Docs: What documentation changed`

---

## Database Schema Quick Reference

```sql
-- Settings (key-value pairs)
settings(key TEXT PRIMARY KEY, value TEXT)

-- Baselines (vocal measurements)
baselines(id, date, pitch_min, pitch_max, sustain_duration, dynamic_range, avg_wpm)

-- Sessions (practice history)
sessions(id, date, module, exercise, duration, scores TEXT, timestamp)

-- Curriculum (weekly plans)
curriculum(id, week_of, focus_module, daily_plan TEXT, tier_adjustments TEXT)

-- Recordings (audio files + transcripts)
recordings(id, session_id, filepath, transcript, wpm, filler_count)
```

JSON fields: `scores`, `daily_plan`, `tier_adjustments`

---

## Debugging Tips

### Audio Issues
```python
# List available devices
import sounddevice as sd
print(sd.query_devices())

# Check if audio engine is running
print(f"Stream active: {audio_engine.stream.active if audio_engine.stream else False}")
```

### Visualizer Not Updating
- Check QTimer is running: `self.ui_timer.isActive()`
- Verify audio engine has data: `len(audio_engine.pitch_history)`
- Check for exceptions in `_update_visualizer()` method

### Database Issues
```bash
# Inspect database
sqlite3 ~/.bespoke/bespoke.db
.tables
SELECT * FROM sessions ORDER BY id DESC LIMIT 5;
.quit
```

### Import Errors
- Ensure virtual environment is activated
- Check `requirements.txt` is installed
- Verify file paths are absolute, not relative

---

## Code Style & Conventions

### Naming
- Classes: `PascalCase` (e.g., `AudioEngine`, `PitchGraph`)
- Methods: `snake_case` (e.g., `get_exercise`, `_audio_callback`)
- Private methods: `_leading_underscore`
- Constants: `UPPER_SNAKE_CASE` (e.g., `OLLAMA_AVAILABLE`)

### Imports
```python
# Standard library
import sys
import os

# Third-party
import numpy as np
from PyQt6.QtWidgets import QWidget

# Local
from audio_engine import AudioEngine
from exercises import get_exercise
```

### Docstrings
Use for public methods:
```python
def score_exercise(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
    """Score an exercise based on collected data.
    
    Args:
        exercise: Exercise definition
        data: Collected audio data (pitch_history, amplitude_history, etc.)
        tier: Tier name ("foundation", "intermediate", "advanced")
        
    Returns:
        Dictionary with score and metrics
    """
```

---

## When You Get Stuck

### Check These First:
1. Read `Bespoke_Windsurf_Prompt.md` - the source of truth
2. Review `PROGRESS.md` - what's been completed
3. Check `TESTING_GUIDE.md` - how to verify it works
4. Look at similar working code (e.g., if adding Module 4 exercise, check Module 1)

### Common Questions:

**Q: Should I create a new visualizer widget?**  
A: Only if the spec requires it. Reuse existing widgets when possible.

**Q: Exercise not launching?**  
A: Check `exercises.py` has the exercise ID, `exercise_instructions.py` has instructions, and visualizer widget exists.

**Q: How do I test without a microphone?**  
A: You can't fully test audio features, but UI should still render. Add mock data for testing.

**Q: Should I refactor existing code?**  
A: Only if it's broken or blocking progress. Don't refactor working code unnecessarily.

---

## Success Criteria for Phase 4

Phase 4 is complete when:
- ✅ User can complete baseline assessment on first run
- ✅ Tier gating works (locked exercises show lock icons)
- ✅ Weekly curriculum generates and displays on dashboard
- ✅ Progress view shows charts and stats
- ✅ Dark theme QSS loads and looks good
- ✅ Error handling for missing mic/Ollama/Whisper
- ✅ PyInstaller builds working executable
- ✅ All Phase 1-3 features still work (no regressions)

---

## Final Notes

### What Makes This Project Different
- **Local-first**: No cloud dependencies
- **Real-time feedback**: Audio analysis at 60fps
- **Graceful degradation**: Core features work without optional dependencies
- **Phased development**: Each phase must work before next begins

### Avoid These Mistakes
- ❌ Scaffolding future phases too early
- ❌ Breaking thread safety with audio callbacks
- ❌ Adding features not in the spec
- ❌ Skipping testing before moving on
- ❌ Creating duplicate code across classes
- ❌ Hardcoding values that should be tier-specific

### Remember
This is a voice practice tool for real users. Every exercise must:
1. Provide clear instructions
2. Show real-time visual feedback
3. Calculate meaningful scores
4. Save progress to database
5. Work reliably without crashes

**Build with discipline. Test thoroughly. Ship quality.**

---

*For questions or clarifications, refer to the original spec: `Bespoke_Windsurf_Prompt.md`*
