from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.widgets.streak_calendar import StreakCalendar
from ui.widgets.progress_rings import ProgressRings
from database import Database
from exercises import get_all_exercises


class Dashboard(QWidget):
    """Dashboard view with today's session, streak calendar, and progress rings."""
    
    # Signals
    start_exercise = pyqtSignal(str, str)  # exercise_id, tier
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Welcome section
        welcome_label = QLabel("Welcome to Bespoke")
        welcome_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2DD4BF;")
        
        subtitle_label = QLabel("Your local voice practice gym")
        subtitle_label.setFont(QFont("Arial", 16))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #94A3B8;")
        
        # Today's session card
        session_card = self.create_session_card()
        
        # Stats row (streak calendar + progress rings)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # Streak calendar
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)
        self.streak_calendar = StreakCalendar()
        calendar_layout.addWidget(self.streak_calendar)
        
        # Current streak display
        self.streak_label = QLabel("Current Streak: 0 days")
        self.streak_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.streak_label.setStyleSheet("color: #F59E0B;")
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendar_layout.addWidget(self.streak_label)
        
        # Progress rings
        rings_frame = QFrame()
        rings_frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        rings_layout = QVBoxLayout(rings_frame)
        self.progress_rings = ProgressRings()
        rings_layout.addWidget(self.progress_rings)
        
        stats_layout.addWidget(calendar_frame)
        stats_layout.addWidget(rings_frame)
        
        # Baseline comparison card (if baseline exists)
        self.baseline_card = self.create_baseline_card()
        
        # Assemble layout
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(session_card)
        main_layout.addLayout(stats_layout)
        main_layout.addWidget(self.baseline_card)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def create_session_card(self):
        """Create today's session recommendation card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = QLabel("Today's Session")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        
        # Recommended exercises
        rec_label = QLabel("Recommended exercises:")
        rec_label.setFont(QFont("Arial", 12))
        rec_label.setStyleSheet("color: #94A3B8;")
        
        # Exercise buttons
        exercises_layout = QHBoxLayout()
        exercises_layout.setSpacing(15)
        
        # Default recommendations (Module 1 exercises)
        recommended = ["1a", "1b", "1c"]
        
        for ex_id in recommended:
            btn = QPushButton(f"Exercise {ex_id}")
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A3444;
                    color: #E2E8F0;
                    border: 1px solid #374151;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
            """)
            btn.clicked.connect(lambda checked, e=ex_id: self.start_exercise.emit(e, "foundation"))
            exercises_layout.addWidget(btn)
        
        # Big start button
        start_btn = QPushButton("Start Practice Session")
        start_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2DD4BF;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #26B5A3;
            }
        """)
        start_btn.clicked.connect(lambda: self.start_exercise.emit("1a", "foundation"))
        
        layout.addWidget(title)
        layout.addWidget(rec_label)
        layout.addLayout(exercises_layout)
        layout.addWidget(start_btn)
        
        return card
        
    def create_baseline_card(self):
        """Create baseline comparison card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = QLabel("Baseline Comparison")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        
        # Baseline info
        self.baseline_info = QLabel("No baseline recorded yet. Complete a baseline assessment to track your progress.")
        self.baseline_info.setWordWrap(True)
        self.baseline_info.setStyleSheet("color: #94A3B8;")
        
        # Baseline button
        baseline_btn = QPushButton("Take Baseline Assessment")
        baseline_btn.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(self.baseline_info)
        layout.addWidget(baseline_btn)
        
        return card
        
    def load_data(self):
        """Load dashboard data from database."""
        # Load practice days for streak calendar
        stats = self.database.get_session_stats(days=30)
        practice_days = stats.get('practice_days', [])
        self.streak_calendar.set_practice_days(practice_days)
        
        # Update streak label
        current_streak = self.streak_calendar.get_current_streak()
        self.streak_label.setText(f"Current Streak: {current_streak} days")
        
        # Calculate module progress
        sessions = self.database.get_sessions(limit=100)
        module_scores = {1: [], 2: [], 3: [], 4: []}
        
        for session in sessions:
            module = session.get('module')
            scores = session.get('scores', {})
            main_score = scores.get('score', 0)
            if module in module_scores:
                module_scores[module].append(main_score)
        
        # Set progress rings (average of recent scores)
        for module in range(1, 5):
            if module_scores[module]:
                avg_score = sum(module_scores[module]) / len(module_scores[module])
                self.progress_rings.set_module_progress(module, avg_score)
            else:
                self.progress_rings.set_module_progress(module, 0)
        
        # Load baseline if exists
        baseline = self.database.get_latest_baseline()
        if baseline:
            baseline_text = f"Baseline recorded on {baseline['date']}\n"
            baseline_text += f"Pitch Range: {baseline.get('pitch_min', 0):.0f} - {baseline.get('pitch_max', 0):.0f} Hz\n"
            baseline_text += f"Sustain: {baseline.get('sustain_duration', 0):.1f}s\n"
            baseline_text += f"Dynamic Range: {baseline.get('dynamic_range', 0):.1f} dB"
            self.baseline_info.setText(baseline_text)
            
    def refresh(self):
        """Refresh dashboard data."""
        self.load_data()
