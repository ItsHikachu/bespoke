# Bespoke: Local Voice Practice Gym

## IMPORTANT: Build Order

**Build Phase 1 FIRST. Do not scaffold other phases until Phase 1 is working.**

### Phase 1: Audio Engine + One Exercise + Basic UI
- `audio_engine.py` with sounddevice streaming, pitch detection, amplitude
- `ui/widgets/pitch_graph.py` (pyqtgraph scrolling plot)
- `ui/practice_session.py` with exercise 1a (Pitch Hold) end to end
- `database.py` with session saving
- `ui/main_window.py` with minimal navigation
- **Test:** user can run Pitch Hold, see real-time pitch graph, get a score, save it

### Phase 2: All Module 1 + Dashboard
- Remaining pitch exercises (1b-1e)
- Dashboard with streak calendar and progress rings
- Module view for Module 1
- Baseline assessment flow (first-run experience)
- Settings view with mic selection and voice threshold calibration

### Phase 3: Modules 2-4
- Amplitude visualizer widgets for Module 2
- WPM gauge and speech/silence display for Module 3
- `faster-whisper` integration for Module 3 post-exercise
- dB meter and centroid bar for Module 4
- All remaining exercises

### Phase 4: Ollama + Progress + Polish
- `ollama_coach.py` with graceful degradation
- Weekly curriculum generation
- Progress view with matplotlib charts
- Tier gating logic
- Dark theme QSS
- Error handling (no mic, Ollama down, Whisper model missing)
- Packaging with PyInstaller

---

## Overview

Build a Python desktop application called **"Bespoke"** -- a fully local voice practice gym with real-time audio biofeedback. The app runs entirely offline. No cloud APIs. Voice data never leaves the machine.

**Critical design principle:** Every exercise must produce measurable audio data displayed to the user in real time. If the microphone can't measure it, don't build it.

**Graceful degradation:** The app MUST work without Ollama and without faster-whisper installed. Those features show "not available" states. The core value (real-time audio biofeedback during exercises) is pure Python with no external services.

---

## Tech Stack

### requirements.txt

```
PyQt6>=6.6
sounddevice>=0.4.6
numpy>=1.24
scipy>=1.10
librosa>=0.10
pyqtgraph>=0.13
faster-whisper>=1.0
ollama>=0.3
matplotlib>=3.7
soundfile>=0.12
```

### Optional (user installs separately)
- Ollama server: https://ollama.com (required for AI coaching only)
- Model: `ollama pull llama3.2:3b` (or any model, configurable in settings)

---

## Project Structure

```
bespoke/
  main.py                  # Entry point. Launch PyQt6 app.
  audio_engine.py          # AudioEngine class: sounddevice stream, real-time analysis
  pitch_detector.py        # Autocorrelation and pYIN pitch detection
  exercises.py             # Exercise database: all 20 exercises with metadata
  scoring.py               # Score computation for each exercise type
  ollama_coach.py          # Ollama integration: coaching and curriculum
  whisper_transcriber.py   # faster-whisper integration for Module 3
  database.py              # SQLite wrapper: sessions, baselines, settings, curriculum
  ui/
    main_window.py         # QMainWindow with navigation
    dashboard.py           # Dashboard view widget
    module_view.py         # Module browser widget
    practice_session.py    # Core exercise view with visualizers
    progress_view.py       # Charts and stats view
    settings_view.py       # Settings and baseline management
    widgets/
      pitch_graph.py       # pyqtgraph scrolling pitch line
      amplitude_bar.py     # Vertical amplitude meter
      amplitude_envelope.py # Scrolling amplitude trace
      wpm_gauge.py         # Large WPM display with ring
      db_meter.py          # Peak/RMS dB meter
      centroid_bar.py      # Spectral centroid horizontal bar
      streak_calendar.py   # 30-day practice calendar
      progress_rings.py    # Module progress circular indicators
  resources/
    passages.json          # Reading passages for exercises (varied difficulty)
    topics.json            # Random impromptu speaking topics
    style.qss              # Qt stylesheet for dark theme
```

---

## Audio Engine

**File: `audio_engine.py`**

Implement this class. The `_audio_callback` and `_autocorrelation_pitch` methods are provided as reference implementations -- use them directly.

```python
from collections import deque
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioEngine:
    """Real-time audio capture and analysis via sounddevice."""

    def __init__(self, sample_rate=44100, buffer_size=1024, device=None):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.device = device
        self.voice_threshold = -40  # dB, adjustable in settings
        self.stream = None
        self.recording_buffer = []
        self.is_recording = False

        # Analysis outputs (updated every buffer callback):
        self.pitch = 0.0             # Hz, 0 if unvoiced
        self.pitch_confidence = 0.0  # 0-1
        self.amplitude_rms = 0.0     # Linear RMS
        self.amplitude_db = -60.0    # dB
        self.spectral_centroid = 0.0 # Hz
        self.is_voice_active = False

        # Histories (ring buffers, last 5 seconds = ~215 frames at 44100/1024):
        self.pitch_history = deque(maxlen=215)
        self.amplitude_history = deque(maxlen=215)
        self.centroid_history = deque(maxlen=215)

        # Callback for UI updates (set by practice_session.py)
        self.on_analysis = None  # callback(pitch, amplitude_db, centroid, is_voice)

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio buffer. Runs in a separate thread."""
        audio = indata[:, 0].copy()  # Mono

        # Accumulate recording if active
        if self.is_recording:
            self.recording_buffer.append(audio.copy())

        # RMS amplitude
        rms = np.sqrt(np.mean(audio ** 2))
        self.amplitude_rms = rms
        self.amplitude_db = 20 * np.log10(max(rms, 1e-10))

        # Voice activity detection
        self.is_voice_active = self.amplitude_db > self.voice_threshold

        # Pitch detection (autocorrelation method for low latency)
        if self.is_voice_active:
            self.pitch, self.pitch_confidence = self._autocorrelation_pitch(audio)
        else:
            self.pitch, self.pitch_confidence = 0.0, 0.0

        # Spectral centroid
        fft = np.abs(np.fft.rfft(audio * np.hanning(len(audio))))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
        self.spectral_centroid = np.sum(freqs * fft) / max(np.sum(fft), 1e-10)

        # Update histories
        self.pitch_history.append(self.pitch)
        self.amplitude_history.append(self.amplitude_db)
        self.centroid_history.append(self.spectral_centroid)

        # Notify UI (must be thread-safe -- use QTimer or signal in practice)
        if self.on_analysis:
            self.on_analysis(self.pitch, self.amplitude_db, self.spectral_centroid, self.is_voice_active)

    def _autocorrelation_pitch(self, audio, fmin=60, fmax=600):
        """Autocorrelation pitch detection. Returns (freq_hz, confidence)."""
        audio = audio - np.mean(audio)
        if np.max(np.abs(audio)) < 1e-6:
            return 0.0, 0.0
        audio = audio / np.max(np.abs(audio))

        n = len(audio)
        fft = np.fft.rfft(audio, n=2*n)
        acf = np.fft.irfft(fft * np.conj(fft))[:n]
        acf = acf / acf[0]

        lag_min = int(self.sample_rate / fmax)
        lag_max = int(self.sample_rate / fmin)
        lag_max = min(lag_max, n - 1)
        if lag_min >= lag_max:
            return 0.0, 0.0

        segment = acf[lag_min:lag_max]
        peak_idx = np.argmax(segment)
        confidence = segment[peak_idx]
        if confidence < 0.8:
            return 0.0, 0.0

        lag = peak_idx + lag_min
        freq = self.sample_rate / lag
        return freq, confidence

    def start(self):
        """Open sounddevice InputStream with callback."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            device=self.device,
            channels=1,
            dtype='float32',
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """Close stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def start_recording(self):
        self.recording_buffer = []
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False
        if self.recording_buffer:
            return np.concatenate(self.recording_buffer)
        return np.array([])

    def save_recording(self, filepath):
        """Save accumulated recording to .wav."""
        audio = self.stop_recording()
        if len(audio) > 0:
            sf.write(filepath, audio, self.sample_rate)
        return filepath
```

**IMPORTANT threading note:** The `_audio_callback` runs in sounddevice's audio thread, NOT the Qt main thread. Do NOT call any Qt widget methods directly from `on_analysis`. Instead, use a `QTimer` polling pattern in the practice session view:

```python
# In practice_session.py:
self.ui_timer = QTimer()
self.ui_timer.timeout.connect(self._update_visualizer)
self.ui_timer.start(16)  # ~60fps

def _update_visualizer(self):
    # Read latest values from audio_engine (thread-safe reads of simple floats)
    pitch = self.audio_engine.pitch
    amplitude_db = self.audio_engine.amplitude_db
    # Update pyqtgraph widgets here (safe, we're in the main thread)
    self.pitch_graph.add_data_point(pitch)
```

---

## Ollama Coaching

**File: `ollama_coach.py`**

Graceful degradation is the key behavior: if Ollama is not running, every method returns a useful fallback instead of crashing.

```python
import json

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaCoach:
    """Local LLM coaching via Ollama. Gracefully degrades if unavailable."""

    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.available = self._check_availability()

    def _check_availability(self):
        if not OLLAMA_AVAILABLE:
            return False
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def post_session_feedback(self, exercise_name, module, tier, scores: dict) -> str:
        if not self.available:
            return self._fallback_feedback(scores)
        prompt = f"""Exercise completed: {exercise_name} (Module {module}, Tier: {tier})
Scores: {json.dumps(scores, indent=2)}

Provide exactly 2-3 sentences of specific coaching feedback:
1. What was strongest in this attempt
2. One specific adjustment for the next attempt
Be direct and precise. No filler phrases. No pleasantries."""
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "system", "content": "You are a concise voice coach. Respond in 2-3 sentences only. Be specific and actionable."},
                {"role": "user", "content": prompt}
            ])
            return response['message']['content']
        except Exception:
            return self._fallback_feedback(scores)

    def weekly_curriculum(self, progress: dict) -> dict:
        if not self.available:
            return self._default_curriculum()
        prompt = f"""Weekly progress data:
{json.dumps(progress, indent=2)}

Output ONLY a JSON object with these exact keys:
- focusModule: number 1-4 (weakest module)
- tierAdjustments: object mapping module number to "up", "stay", or "down"
- dailyPlan: array of 7 objects, each with "day" and "exercises" (array of exercise IDs like "1a", "2c")
- rationale: one sentence explaining the focus choice

Prioritize the weakest module. Maintain all modules at least twice per week. 3-4 exercises per day."""
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "system", "content": "You are a training program designer. Output valid JSON only. No markdown. No preamble."},
                {"role": "user", "content": prompt}
            ], format='json')
            return json.loads(response['message']['content'])
        except Exception:
            return self._default_curriculum()

    def _fallback_feedback(self, scores: dict) -> str:
        parts = []
        for key, value in scores.items():
            if isinstance(value, (int, float)):
                if value > 80:
                    parts.append(f"Strong {key} score at {value:.0f}%.")
                elif value < 50:
                    parts.append(f"Focus on improving {key} (currently {value:.0f}%).")
        if not parts:
            return "Session completed. Keep practicing for consistent improvement."
        return " ".join(parts[:2])

    def _default_curriculum(self) -> dict:
        return {
            "focusModule": 1,
            "tierAdjustments": {"1": "stay", "2": "stay", "3": "stay", "4": "stay"},
            "dailyPlan": [
                {"day": "Mon", "exercises": ["1a", "2a", "3a"]},
                {"day": "Tue", "exercises": ["1b", "2b", "4a"]},
                {"day": "Wed", "exercises": ["1c", "2c", "3b"]},
                {"day": "Thu", "exercises": ["1d", "2d", "4b"]},
                {"day": "Fri", "exercises": ["1e", "2e", "3c"]},
                {"day": "Sat", "exercises": ["1a", "3d", "4c"]},
                {"day": "Sun", "exercises": []}
            ],
            "rationale": "Default balanced plan. Install Ollama for personalized curriculum."
        }
```

---

## Whisper Transcription

**File: `whisper_transcriber.py`**

Used only for Module 3 (Pace & Rhythm) exercises. Must gracefully handle missing faster-whisper.

```python
import numpy as np

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class WhisperTranscriber:
    """Local speech-to-text via faster-whisper. Used for Module 3 only."""

    def __init__(self, model_size="base.en"):
        self.available = WHISPER_AVAILABLE
        self.model = None
        self.model_size = model_size
        self.filler_words = {
            "um", "uh", "like", "you know", "basically",
            "actually", "so", "right", "kind of", "sort of",
            "i mean", "literally", "honestly"
        }

    def ensure_loaded(self):
        if not self.available:
            return False
        if self.model is None:
            try:
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            except Exception:
                self.available = False
                return False
        return True

    def transcribe(self, audio_path: str) -> dict:
        if not self.ensure_loaded():
            return {"error": "faster-whisper not available", "wpm": 0, "filler_count": 0}

        segments, info = self.model.transcribe(audio_path, word_timestamps=True)
        words = []
        full_text = []
        for segment in segments:
            if segment.words:
                for word in segment.words:
                    words.append({"text": word.word.strip(), "start": word.start, "end": word.end})
                    full_text.append(word.word.strip())

        if not words:
            return {"transcript": "", "word_count": 0, "duration": 0, "wpm": 0,
                    "filler_count": 0, "pauses": [], "avg_pause_duration": 0, "words": []}

        duration = words[-1]["end"]
        word_count = len([w for w in words if len(w["text"]) > 0])
        wpm = (word_count / duration * 60) if duration > 0 else 0

        text_lower = " ".join(full_text).lower()
        filler_count = sum(text_lower.count(f) for f in self.filler_words)

        pauses = []
        for i in range(1, len(words)):
            gap = words[i]["start"] - words[i-1]["end"]
            if gap > 0.3:
                pauses.append({"start": words[i-1]["end"], "duration": round(gap, 2)})

        return {
            "transcript": " ".join(full_text),
            "word_count": word_count,
            "duration": round(duration, 2),
            "wpm": round(wpm, 1),
            "filler_count": filler_count,
            "pauses": pauses,
            "avg_pause_duration": round(np.mean([p["duration"] for p in pauses]), 2) if pauses else 0,
            "words": words
        }
```

---

## Exercise Database

**File: `exercises.py`**

Generate the complete database for all 20 exercises. **Implement every exercise with complete params for all 3 tiers.**

### Module 1: Pitch Control (visualizer: `pitch_graph`)

| ID | Name | Duration | Scoring | Foundation | Intermediate | Advanced |
|----|------|----------|---------|------------|--------------|----------|
| 1a | Pitch Hold | 60s | % time within tolerance band | +/-30 Hz | +/-15 Hz | +/-8 Hz |
| 1b | Pitch Glide | 45s | Mean deviation from target line (Hz) | Slow linear rise 5s | Faster + descend | Zigzag patterns |
| 1c | Variation Reading | 60s | Pitch std dev (higher=better, ceiling ~80 Hz SD) | Short sentences | Paragraphs | Passages with emotional shifts |
| 1d | Emotional Contrast | 60s | Shape correlation to target pitch envelope | 2 emotions | 4 emotions | 6 emotions |
| 1e | Range Expansion | 45s | Range in Hz and semitones | Measure current range | Expand by 2 semitones | Expand by 4+ semitones |

### Module 2: Breath & Sustain (visualizer: `amplitude_bar` + `amplitude_envelope`)

| ID | Name | Duration | Scoring | Foundation | Intermediate | Advanced |
|----|------|----------|---------|------------|--------------|----------|
| 2a | Sustained Tone | 45s | Duration + amplitude stability (1/variance) | 10s target | 20s target | 30s target |
| 2b | S/Z Ratio | 30s | Ratio (healthy: 0.8-1.2) | Measure ratio | Track consistency | Maintain across 3 trials |
| 2c | Breath Ladder | 60s | Count reached + volume consistency | Reach 15 | Reach 25 | Reach 35 |
| 2d | Volume Sustain | 60s | Amplitude coeff of variation (lower=better) | Short sentence | Paragraph | 60s passage |
| 2e | Crescendo/Decrescendo | 45s | Correlation of amplitude to target shape | Linear ramp | Steep ramp | Complex curves |

### Module 3: Pace & Rhythm (visualizer: `wpm_gauge`, post-exercise: `uses_whisper: true`)

| ID | Name | Duration | Scoring | Foundation | Intermediate | Advanced |
|----|------|----------|---------|------------|--------------|----------|
| 3a | Metronome Pace | 60s | WPM deviation from target | 130 WPM | 150 WPM | Alternating fast/slow |
| 3b | Pause Training | 60s | % target pauses hit + penalty for unplanned | 3 pause points | 6 pause points | 10+ pause points |
| 3c | Rate Shifting | 60s | Accuracy per tempo segment | 2 speeds | 3 speeds | Rapid alternation |
| 3d | Silence Ratio | 60s | Composite: talk%, pause count, avg, longest | Target 70-80% talk | Tighter targets | + filler word penalty |
| 3e | Cadence Lock | 45s | Rhythm correlation (syllable vs tap intervals) | Steady beat | 2-beat pattern | 3-beat syncopated |

### Module 4: Dynamics & Projection (visualizer: `db_meter` + `centroid_bar`)

| ID | Name | Duration | Scoring | Foundation | Intermediate | Advanced |
|----|------|----------|---------|------------|--------------|----------|
| 4a | Dynamic Range Finder | 30s | Range in dB | 15 dB target | 20 dB target | 25 dB+ target |
| 4b | Emphasis Drill | 60s | % correct emphasis alignment | Obvious words | Subtle emphasis | Multi-word + deemphasis |
| 4c | Projection Scaling | 45s | dB step separation + spectral quality | 3ft/15ft | 3ft/15ft/50ft | + centroid check |
| 4d | Volume Contouring | 60s | Amplitude correlation to target shape | Simple ramp | Two peaks | Complex emotional arc |
| 4e | Brightness Tracker | 45s | Avg spectral centroid vs baseline | Measure baseline | Maintain above baseline | 10%+ improvement |

---

## Application Views

### 1. Dashboard (`ui/dashboard.py`)
- "Today's Session" card: 3-4 recommended exercises, big "Start Session" button
- 30-day streak calendar: custom QWidget, colored dots (teal=practiced, empty=missed, pulsing=today)
- 4 module progress rings: circular arc indicators
- Baseline comparison card: current vs first baseline for each metric
- If Ollama unavailable: info banner at top, all exercises still work

### 2. Module View (`ui/module_view.py`)
- Module name and icon header
- Collapsible "Why This Matters" theory panel (2-3 sentences)
- Exercise cards in grid grouped by tier (Foundation / Intermediate / Advanced)
- **Tier gating:** Intermediate unlocks when 3/5 Foundation exercises score above threshold. Show lock icons with progress.
- Each card: name, duration, tier badge, best score, one-line description

### 3. Practice Session (`ui/practice_session.py`) -- THE CORE SCREEN
- **TOP HALF (>=40% viewport):** Real-time visualizer (pyqtgraph). Which one depends on exercise:
  - Pitch exercises: ScrollingPitchGraph (Y=Hz 80-400, X=last 5s, target overlay)
  - Amplitude exercises: AmplitudeBar (left) + AmplitudeEnvelope (right, scrolling)
  - Pace exercises: Large WPM number + speech/silence waveform
  - Dynamics exercises: dBMeter (left) + CentroidBar (right)
- **CENTER:** Phase-aware instructions (text changes as exercise progresses). Reading exercises: passage with word highlighting.
- **BOTTOM:** Start/Stop, timer, post-exercise score card + Ollama coaching if available.

### 4. Progress (`ui/progress_view.py`)
- Matplotlib radar chart: 4 axes, normalized 0-100
- Per-module line chart: scores over last 30 sessions
- Stats cards: total minutes, current streak, longest streak
- "Retake Baseline" button

---

## Design & Theming (`resources/style.qss`)

Dark theme. Instrument-like aesthetic. Audio workstation, not toy app.

```
Palette:
  Background:       #0F1419
  Surface:          #1A2332
  Primary accent:   #2DD4BF  (teal)
  Secondary accent: #F59E0B  (amber)
  Error:            #EF4444
  Text primary:     #E2E8F0
  Text secondary:   #94A3B8
  Visualizer grid:  #2A3444
```

```python
# pyqtgraph config (set in main.py before creating widgets):
import pyqtgraph as pg
pg.setConfigOptions(background='#0F1419', foreground='#94A3B8', antialias=True)

# Plot pens:
user_pen = pg.mkPen('#2DD4BF', width=2)
target_pen = pg.mkPen('#F59E0B', width=1.5, style=Qt.DashLine)
```

Font: system sans-serif for UI, monospace for metrics/scores.

---

## Database (`database.py`)

SQLite. Single file: `~/.bespoke/bespoke.db`

```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    pitch_min REAL,
    pitch_max REAL,
    sustain_duration REAL,
    dynamic_range REAL,
    avg_wpm REAL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    module INTEGER NOT NULL,
    exercise TEXT NOT NULL,
    duration REAL,
    scores TEXT,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS curriculum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_of TEXT NOT NULL,
    focus_module INTEGER,
    daily_plan TEXT,
    tier_adjustments TEXT
);

CREATE TABLE IF NOT EXISTS recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    filepath TEXT,
    transcript TEXT,
    wpm REAL,
    filler_count INTEGER
);
```

---

## Prerequisites

1. Python 3.10+
2. `pip install -r requirements.txt`
3. (Optional) Ollama from https://ollama.com + `ollama pull llama3.2:3b`
4. (Optional) faster-whisper model downloads on first run (~150MB)
5. `python main.py`
