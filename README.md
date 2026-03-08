# Bespoke - Local Voice Practice Gym

A fully local desktop application for voice practice with real-time audio biofeedback. No cloud APIs. Voice data never leaves your machine.

## Project Status

**Phase 1 (In Progress)**: Building core audio engine + Pitch Hold exercise + basic UI

### Completed
- ✅ Project structure created
- ✅ Audio engine with real-time pitch detection
- ✅ Exercise database (20 exercises across 4 modules)
- ✅ Scoring engine for all exercise types
- ✅ SQLite database for session tracking
- ✅ Pitch graph visualizer widget
- ✅ Practice session UI
- ✅ Main window with navigation
- ✅ Resource files (passages, topics, dark theme)

### In Progress
- 🔄 Testing Phase 1 end-to-end
- 🔄 Bug fixes and refinements

## Tech Stack

- **UI**: PyQt6
- **Audio**: sounddevice, librosa, scipy
- **Visualization**: pyqtgraph
- **Database**: SQLite
- **Optional AI**: Ollama (for coaching)
- **Optional STT**: faster-whisper (for Module 3)

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Project Structure

```
bespoke/
  main.py                  # Entry point
  audio_engine.py          # Real-time audio capture and analysis
  exercises.py             # 20 exercises with 3 tiers each
  scoring.py               # Scoring logic for all exercise types
  database.py              # SQLite wrapper
  ui/
    main_window.py         # Main navigation
    practice_session.py    # Core exercise view
    widgets/
      pitch_graph.py       # Real-time pitch visualization
  resources/
    passages.json          # Reading passages
    topics.json            # Speaking topics
    style.qss              # Dark theme stylesheet
```

## Modules

1. **Pitch Control** - Pitch accuracy, variation, range
2. **Breath & Sustain** - Breath support, volume control
3. **Pace & Rhythm** - Speaking rate, timing, pauses
4. **Dynamics & Projection** - Volume range, emphasis, vocal quality

## Build Phases

- **Phase 1**: Audio engine + Pitch Hold (1a) + basic UI ← CURRENT
- **Phase 2**: All Module 1 exercises + dashboard + settings
- **Phase 3**: Modules 2-4 with all visualizers
- **Phase 4**: Ollama integration + progress tracking + polish

## Development Notes

- Build order is critical: Phase 1 must work before scaffolding Phase 2
- Every exercise produces measurable audio data displayed in real-time
- Graceful degradation: core features work without Ollama/Whisper
- Dark theme with instrument-like aesthetic

## License

MIT
