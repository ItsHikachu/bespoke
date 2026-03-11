from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QFrame, QProgressBar)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_engine import AudioEngine
from exercises import get_exercise, Exercise
from scoring import ScoringEngine
from database import Database
from ui.widgets.pitch_graph import PitchGraph
from ui.widgets.amplitude_bar import AmplitudeBar
from ui.widgets.amplitude_envelope import AmplitudeEnvelope
from ui.widgets.wpm_gauge import WPMGauge
from ui.widgets.db_meter import DBMeter
from ui.widgets.centroid_bar import CentroidBar
from exercise_instructions import ExerciseInstructions, ExerciseContent
from datetime import datetime


class PracticeSession(QWidget):
    """Core exercise practice view with real-time visualizers."""
    
    # Signals
    session_completed = pyqtSignal(dict)  # Emits session data when completed
    back_requested = pyqtSignal()  # Emits when user wants to go back
    
    def __init__(self, exercise_id: str, tier: str = "foundation"):
        super().__init__()
        self.exercise_id = exercise_id
        self.tier = tier
        self.exercise = get_exercise(exercise_id)
        
        # Audio and scoring
        self.audio_engine = AudioEngine()
        self.scoring_engine = ScoringEngine()
        self.database = Database()
        self._load_audio_settings()
        
        # Session state
        self.is_recording = False
        self.session_start_time = None
        self.exercise_data = {
            "pitch_history": [],
            "amplitude_history": [],
            "time_stamps": [],
            "duration": 0.0
        }
        
        # UI update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_visualizer)
        self.ui_timer.start(16)  # ~60fps
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self._handle_back_request)
        self.back_button.setMaximumWidth(80)
        
        # Exercise info
        title_label = QLabel(f"{self.exercise.name} - {self.tier.title()}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        desc_label = QLabel(self.exercise.description)
        desc_label.setWordWrap(True)
        
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Instructions area
        initial_instructions = ExerciseInstructions.get_instructions(self.exercise_id, self.tier, "ready")
        self.instructions_label = QLabel(initial_instructions)
        self.instructions_label.setFont(QFont("Arial", 12))
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setStyleSheet("""
            QLabel {
                background-color: #1A2332;
                color: #E2E8F0;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #2A3444;
            }
        """)
        
        # Reading passage area (for exercises that need it)
        self.reading_text = ExerciseContent.get_reading_text(self.exercise_id, self.tier)
        self.reading_display = QTextEdit()
        self.reading_display.setReadOnly(True)
        self.reading_display.setPlainText(self.reading_text)
        self.reading_display.setFont(QFont("Arial", 14))
        self.reading_display.setStyleSheet("""
            QTextEdit {
                background-color: #1A2332;
                color: #E2E8F0;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        # Only show reading display if there's text
        if not self.reading_text:
            self.reading_display.setVisible(False)
        
        # Visualizer area (TOP HALF - 40%+ viewport)
        self.visualizer_frame = QFrame()
        self.visualizer_frame.setStyleSheet("""
            QFrame {
                background-color: #0F1419;
                border: 1px solid #2A3444;
                border-radius: 8px;
            }
        """)
        self.visualizer_layout = QVBoxLayout(self.visualizer_frame)
        
        # Create appropriate visualizer based on exercise
        self._create_visualizer()
        
        # Control area (CENTER)
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Exercise")
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2DD4BF;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #26B5A3;
            }
        """)
        self.start_button.clicked.connect(self.toggle_exercise)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.stop_button.clicked.connect(self.stop_exercise)
        self.stop_button.setEnabled(False)
        
        # Timer display
        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(QFont("Monospace", 16))
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #2DD4BF;
                background-color: #1A2332;
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #2A3444;
            }
        """)
        
        # Progress bar for exercise duration
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.exercise.duration)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2A3444;
                border-radius: 6px;
                text-align: center;
                background-color: #1A2332;
                color: #E2E8F0;
            }
            QProgressBar::chunk {
                background-color: #2DD4BF;
                border-radius: 5px;
            }
        """)
        
        control_layout.addStretch()
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.timer_label)
        control_layout.addStretch()
        
        # Results area (BOTTOM) - initially hidden
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        self.results_frame.setVisible(False)
        
        self.results_layout = QVBoxLayout(self.results_frame)
        
        self.score_label = QLabel()
        self.score_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #0F1419;
                color: #E2E8F0;
                border: 1px solid #2A3444;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        self.save_button = QPushButton("Save Session")
        self.save_button.clicked.connect(self.save_session)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2DD4BF;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #26B5A3;
            }
        """)
        
        self.results_layout.addWidget(self.score_label)
        self.results_layout.addWidget(self.details_text)
        self.results_layout.addWidget(self.save_button)
        
        # Assemble main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(desc_label)
        main_layout.addWidget(self.instructions_label)
        main_layout.addWidget(self.reading_display)  # Reading passage (if applicable)
        main_layout.addWidget(self.visualizer_frame, 2)  # Takes 2/3 of space
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.results_frame)
        
        self.setLayout(main_layout)
        
        # Set up audio callback
        self.audio_engine.on_analysis = self._on_audio_analysis
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1419;
                color: #E2E8F0;
            }
            QPushButton {
                background-color: #1A2332;
                color: #E2E8F0;
                border: 1px solid #2A3444;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2A3444;
            }
            QLabel {
                color: #E2E8F0;
            }
        """)
        
    def _create_visualizer(self):
        """Create the appropriate visualizer for this exercise."""
        tier_params = self.exercise.get_tier(self.tier).params
        
        if self.exercise.visualizer == "pitch_graph":
            self.visualizer = PitchGraph()
            if "target_pitch" in tier_params and "tolerance" in tier_params:
                self.visualizer.set_target(tier_params["target_pitch"], tier_params["tolerance"])
                
        elif self.exercise.visualizer == "amplitude_bar":
            # Module 2: Single amplitude bar
            self.visualizer = AmplitudeBar()
            
        elif self.exercise.visualizer == "amplitude_envelope":
            # Module 2: Amplitude envelope trace
            self.visualizer = AmplitudeEnvelope()
            if "target_amplitude" in tier_params:
                self.visualizer.set_target(tier_params["target_amplitude"])
                
        elif self.exercise.visualizer == "wpm_gauge":
            # Module 3: WPM gauge
            self.visualizer = WPMGauge()
            if "target_wpm" in tier_params:
                self.visualizer.set_target(tier_params["target_wpm"])
                
        elif self.exercise.visualizer == "db_meter":
            # Module 4: dB meter
            self.visualizer = DBMeter()
            
        elif self.exercise.visualizer == "centroid_bar":
            # Module 4: Spectral centroid bar
            self.visualizer = CentroidBar()
            
        else:
            # Fallback placeholder
            placeholder = QLabel(f"Visualizer: {self.exercise.visualizer}")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #94A3B8;")
            self.visualizer = placeholder
            
        self.visualizer_layout.addWidget(self.visualizer)
        
    def toggle_exercise(self):
        """Start or stop the exercise."""
        if not self.is_recording:
            self.start_exercise()
        else:
            self.stop_exercise()

    def _load_audio_settings(self):
        """Apply persisted audio settings."""
        saved_device_id = self.database.get_setting("microphone_device_id")
        if saved_device_id not in (None, ""):
            try:
                self.audio_engine.device = int(saved_device_id)
            except ValueError:
                self.audio_engine.device = None

        saved_threshold = self.database.get_setting("voice_threshold")
        if saved_threshold not in (None, ""):
            try:
                self.audio_engine.voice_threshold = float(saved_threshold)
            except ValueError:
                pass
            
    def start_exercise(self):
        """Start the exercise recording."""
        self._load_audio_settings()
        self.is_recording = True
        self.session_start_time = datetime.now()
        
        # Clear previous data
        self.exercise_data = {
            "pitch_history": [],
            "amplitude_history": [],
            "time_stamps": [],
            "duration": 0.0
        }
        
        # Start audio
        try:
            self.audio_engine.start()
            self.audio_engine.start_recording()
        except Exception as exc:
            self.is_recording = False
            self.instructions_label.setText(f"Unable to start audio input: {exc}")
            self.start_button.setText("Start Exercise")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        if hasattr(self.visualizer, "clear"):
            self.visualizer.clear()
        if hasattr(self.visualizer, "reset_peak"):
            self.visualizer.reset_peak()
        if hasattr(self.visualizer, "reset_range"):
            self.visualizer.reset_range()
        
        # Update UI
        self.start_button.setText("Recording...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.results_frame.setVisible(False)
        
        # Start exercise timer
        self.exercise_timer = QTimer()
        self.exercise_timer.timeout.connect(self.update_exercise_timer)
        self.exercise_seconds = 0
        self.exercise_timer.start(1000)  # Update every second
        
        # Update instructions to recording phase
        recording_instructions = ExerciseInstructions.get_instructions(self.exercise_id, self.tier, "recording")
        self.instructions_label.setText(recording_instructions)
        
    def stop_exercise(self):
        """Stop the exercise and show results."""
        if not self.is_recording:
            return

        self.is_recording = False
        
        # Stop audio
        self.audio_engine.stop()
        
        # Stop timer
        if hasattr(self, 'exercise_timer'):
            self.exercise_timer.stop()
            
        # Calculate final duration
        if self.session_start_time:
            self.exercise_data["duration"] = (datetime.now() - self.session_start_time).total_seconds()
            
        # Score the exercise
        scores = self.scoring_engine.score_exercise(self.exercise, self.exercise_data, self.tier)
        
        # Update UI with results
        self.show_results(scores)
        
        # Update buttons
        self.start_button.setText("Start Exercise")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Update instructions to completed phase
        completed_instructions = ExerciseInstructions.get_instructions(self.exercise_id, self.tier, "completed")
        self.instructions_label.setText(completed_instructions)
        
    def update_exercise_timer(self):
        """Update the exercise timer display."""
        self.exercise_seconds += 1
        remaining = max(0, self.exercise.duration - self.exercise_seconds)
        
        # Update timer display
        minutes = self.exercise_seconds // 60
        seconds = self.exercise_seconds % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        # Update progress bar
        self.progress_bar.setValue(self.exercise_seconds)
        
        # Keep exercise-specific instructions while showing remaining time
        recording_instructions = ExerciseInstructions.get_instructions(self.exercise_id, self.tier, "recording")
        self.instructions_label.setText(f"{recording_instructions}\n\n{remaining}s remaining")
        
        # Auto-stop when duration reached
        if self.exercise_seconds >= self.exercise.duration:
            self.stop_exercise()
            
    def show_results(self, scores: dict):
        """Display exercise results."""
        self.results_frame.setVisible(True)
        
        # Main score
        main_score = scores.get("score", 0)
        self.score_label.setText(f"Score: {main_score:.1f}%")
        
        # Color code the score
        if main_score >= 80:
            color = "#2DD4BF"  # Teal
        elif main_score >= 60:
            color = "#F59E0B"  # Amber
        else:
            color = "#EF4444"  # Red
            
        self.score_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: #1A2332;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #2A3444;
            }}
        """)
        
        # Detailed results
        details = []
        for key, value in scores.items():
            if key != "score" and not key.endswith("_threshold"):
                if isinstance(value, float):
                    details.append(f"{key.replace('_', ' ').title()}: {value:.1f}")
                else:
                    details.append(f"{key.replace('_', ' ').title()}: {value}")
                    
        self.details_text.setText("\n".join(details))
        
        # Store scores for saving
        self.current_scores = scores
        
    def save_session(self):
        """Save the completed session to database."""
        session_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "module": self.exercise.module,
            "exercise": self.exercise_id,
            "duration": self.exercise_data["duration"],
            "scores": self.current_scores,
            "timestamp": datetime.now().isoformat()
        }
        
        self.database.save_session(session_data)
        
        # Emit signal for navigation
        self.session_completed.emit(session_data)
        
        # Show confirmation
        self.instructions_label.setText("Session saved successfully!")

    def _handle_back_request(self):
        """Stop active session and request navigation back."""
        if self.is_recording:
            self.stop_exercise()
        self.back_requested.emit()
        
    def _on_audio_analysis(self, pitch: float, amplitude_db: float, centroid: float, is_voice: bool):
        """Handle audio analysis updates from audio engine."""
        # This is called from audio thread, just store data
        # UI updates happen in _update_visualizer (main thread)
        if self.is_recording:
            timestamp = len(self.exercise_data["pitch_history"]) * 0.023  # ~43Hz update rate
            self.exercise_data["pitch_history"].append(pitch)
            self.exercise_data["amplitude_history"].append(amplitude_db)
            self.exercise_data["time_stamps"].append(timestamp)
            
    def _update_visualizer(self):
        """Update visualizer with latest data (runs in main thread)."""
        if not self.is_recording:
            return
            
        # Get latest data
        latest_pitch = self.exercise_data["pitch_history"][-1] if self.exercise_data["pitch_history"] else 0
        latest_amplitude = self.exercise_data["amplitude_history"][-1] if self.exercise_data["amplitude_history"] else -60
        
        # Update based on visualizer type
        if isinstance(self.visualizer, PitchGraph):
            self.visualizer.add_data_point(latest_pitch)
            
        elif isinstance(self.visualizer, AmplitudeBar):
            self.visualizer.set_amplitude(latest_amplitude)
            
        elif isinstance(self.visualizer, AmplitudeEnvelope):
            self.visualizer.add_data_point(latest_amplitude)
            
        elif isinstance(self.visualizer, WPMGauge):
            # WPM is calculated post-exercise with transcription
            # During recording, just show speaking status
            is_speaking = self.audio_engine.is_voice_active if self.audio_engine else False
            self.visualizer.set_speaking(is_speaking)
            
        elif isinstance(self.visualizer, DBMeter):
            # Calculate peak from recent history
            if self.exercise_data["amplitude_history"]:
                recent = self.exercise_data["amplitude_history"][-10:]
                peak_db = max(recent)
                rms_db = latest_amplitude
                self.visualizer.set_levels(peak_db, rms_db)
                
        elif isinstance(self.visualizer, CentroidBar):
            # Get spectral centroid from audio engine
            centroid = self.audio_engine.spectral_centroid if self.audio_engine else 0
            self.visualizer.set_centroid(centroid)
            
    def closeEvent(self, event):
        """Clean up when widget is closed."""
        if self.is_recording:
            self.stop_exercise()
        self.audio_engine.stop()
        event.accept()
