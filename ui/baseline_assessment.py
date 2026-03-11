from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from ui.practice_session import PracticeSession
from database import Database
import datetime


class BaselineAssessment(QWidget):
    """First-run baseline assessment flow for new users."""
    
    assessment_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_exercise = 0
        self.baseline_data = {}
        self.practice_session = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Voice Baseline Assessment")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Welcome text
        welcome = QLabel(
            "Welcome to Bespoke! Let's establish your voice baseline.\n\n"
            "You'll complete 4 short exercises to measure:\n"
            "• Pitch range • Breath control • Speaking pace • Vocal dynamics\n\n"
            "This helps us personalize your practice plan and track progress."
        )
        welcome.setWordWrap(True)
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 4)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Exercise %v of 4")
        layout.addWidget(self.progress_bar)
        
        # Exercise info
        self.exercise_frame = QFrame()
        self.exercise_frame.setFrameStyle(QFrame.Shape.Box)
        self.exercise_layout = QVBoxLayout(self.exercise_frame)
        
        self.exercise_title = QLabel("")
        self.exercise_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.exercise_layout.addWidget(self.exercise_title)
        
        self.exercise_description = QLabel("")
        self.exercise_description.setWordWrap(True)
        self.exercise_layout.addWidget(self.exercise_description)
        
        self.exercise_target = QLabel("")
        self.exercise_target.setFont(QFont("Arial", 12))
        self.exercise_layout.addWidget(self.exercise_target)
        
        layout.addWidget(self.exercise_frame)
        
        # Practice session container
        self.session_container = QWidget()
        self.session_layout = QVBoxLayout(self.session_container)
        layout.addWidget(self.session_container)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setMaximumHeight(150)
        self.results_area.hide()
        layout.addWidget(self.results_area)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Assessment")
        self.start_button.clicked.connect(self.start_assessment)
        self.button_layout.addWidget(self.start_button)
        
        self.skip_button = QPushButton("Skip for Now")
        self.skip_button.clicked.connect(self.skip_assessment)
        self.button_layout.addWidget(self.skip_button)
        
        layout.addLayout(self.button_layout)
        
        self.setLayout(layout)
        
    def start_assessment(self):
        """Begin the baseline assessment sequence."""
        self.start_button.hide()
        self.skip_button.hide()
        self.current_exercise = 1
        self.baseline_data = {}
        self.progress_bar.setValue(0)
        self.load_exercise()
        
    def load_exercise(self):
        """Load the current baseline exercise."""
        # Clear previous session
        if self.practice_session:
            self.practice_session.deleteLater()
            self.practice_session = None
            
        # Clear session container
        while self.session_layout.count():
            child = self.session_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        exercises = {
            1: {"id": "1a", "tier": "foundation", 
                "title": "Pitch Range Assessment",
                "desc": "Hold a steady pitch in your comfortable range",
                "target": "Target: 150 Hz ± 15 Hz",
                "metric": "pitch_range"},
            2: {"id": "2a", "tier": "foundation",
                "title": "Breath Control Assessment", 
                "desc": "Sustain a steady 'ah' sound for as long as possible",
                "target": "Target: Hold for 8+ seconds",
                "metric": "sustain_duration"},
            3: {"id": "3a", "tier": "foundation",
                "title": "Speaking Pace Assessment",
                "desc": "Read at a comfortable, steady pace",
                "target": "Target: 120-150 WPM",
                "metric": "avg_wpm"},
            4: {"id": "4a", "tier": "foundation", 
                "title": "Vocal Dynamics Assessment",
                "desc": "Speak with normal volume, then gradually increase",
                "target": "Target: Show dynamic range of 10+ dB",
                "metric": "dynamic_range"}
        }
        
        exercise = exercises[self.current_exercise]
        self.exercise_title.setText(exercise["title"])
        self.exercise_description.setText(exercise["desc"])
        self.exercise_target.setText(exercise["target"])
        self.progress_bar.setValue(self.current_exercise)
        
        # Create practice session
        self.practice_session = PracticeSession(exercise["id"], exercise["tier"])
        self.practice_session.session_completed.connect(self.on_exercise_completed)
        self.session_layout.addWidget(self.practice_session)
        
    def on_exercise_completed(self, scores):
        """Handle completion of current exercise."""
        # Store the relevant metric
        exercises = {
            1: "pitch_range",
            2: "sustain_duration", 
            3: "avg_wpm",
            4: "dynamic_range"
        }
        
        metric = exercises[self.current_exercise]
        
        # Extract the relevant score
        if metric == "pitch_range":
            self.baseline_data[metric] = scores.get("range", 0)
        elif metric == "sustain_duration":
            self.baseline_data[metric] = scores.get("duration", 0)
        elif metric == "avg_wpm":
            self.baseline_data[metric] = scores.get("wpm", 0)
        elif metric == "dynamic_range":
            self.baseline_data[metric] = scores.get("dynamic_range", 0)
        
        # Show brief result
        self.show_exercise_result(metric, scores)
        
        # Move to next exercise or complete
        if self.current_exercise < 4:
            self.current_exercise += 1
            QTimer.singleShot(2000, self.load_exercise)  # 2 second delay
        else:
            QTimer.singleShot(2000, self.complete_assessment)
            
    def show_exercise_result(self, metric, scores):
        """Display brief result for completed exercise."""
        result_text = f"Exercise {self.current_exercise} completed!\n"
        
        if metric == "pitch_range":
            result_text += f"Pitch range: {scores.get('range', 0):.1f} Hz"
        elif metric == "sustain_duration":
            result_text += f"Sustain duration: {scores.get('duration', 0):.1f} seconds"
        elif metric == "avg_wpm":
            result_text += f"Speaking pace: {scores.get('wpm', 0):.1f} WPM"
        elif metric == "dynamic_range":
            result_text += f"Dynamic range: {scores.get('dynamic_range', 0):.1f} dB"
            
        self.results_area.append(result_text)
        self.results_area.show()
        
    def complete_assessment(self):
        """Complete the baseline assessment and save results."""
        # Clear session container
        while self.session_layout.count():
            child = self.session_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Save to database
        self.save_baselines()
        
        # Show completion message
        self.exercise_title.setText("Assessment Complete!")
        self.exercise_description.setText(
            "Your voice baseline has been established.\n"
            "This will help us track your progress and personalize your practice.\n\n"
            "You can now access all exercises and see your progress."
        )
        self.exercise_target.setText("")
        
        # Show summary
        summary = "Your Baseline Results:\n\n"
        summary += f"Pitch Range: {self.baseline_data.get('pitch_range', 0):.1f} Hz\n"
        summary += f"Breath Control: {self.baseline_data.get('sustain_duration', 0):.1f} seconds\n"
        summary += f"Speaking Pace: {self.baseline_data.get('avg_wpm', 0):.1f} WPM\n"
        summary += f"Vocal Dynamics: {self.baseline_data.get('dynamic_range', 0):.1f} dB\n\n"
        summary += "Great job! You're ready to start your voice practice journey."
        
        self.results_area.setText(summary)
        
        # Show continue button
        self.continue_button = QPushButton("Continue to Dashboard")
        self.continue_button.clicked.connect(self.finish_assessment)
        self.button_layout.addWidget(self.continue_button)
        
    def save_baselines(self):
        """Save baseline measurements to database."""
        try:
            self.db.save_baselines(
                pitch_min=self.baseline_data.get('pitch_range', 0) * 0.8,  # Estimate
                pitch_max=self.baseline_data.get('pitch_range', 0) * 1.2,  # Estimate
                sustain_duration=self.baseline_data.get('sustain_duration', 0),
                dynamic_range=self.baseline_data.get('dynamic_range', 0),
                avg_wpm=self.baseline_data.get('avg_wpm', 0)
            )
        except Exception as e:
            print(f"Error saving baselines: {e}")
            
    def skip_assessment(self):
        """Skip baseline assessment and go to main app."""
        self.assessment_completed.emit({})
        
    def finish_assessment(self):
        """Complete assessment and emit signal."""
        self.assessment_completed.emit(self.baseline_data)
