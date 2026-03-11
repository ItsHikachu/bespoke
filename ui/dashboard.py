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
from curriculum_manager import CurriculumManager


class Dashboard(QWidget):
    """Dashboard view with today's session, streak calendar, and progress rings."""
    
    # Signals
    start_exercise = pyqtSignal(str, str)  # exercise_id, tier
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.curriculum_mgr = CurriculumManager()
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
        
        # Weekly plan card
        self.weekly_plan_card = self.create_weekly_plan_card()
        
        # Baseline comparison card (if baseline exists)
        self.baseline_card = self.create_baseline_card()
        
        # Assemble layout
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(session_card)
        main_layout.addWidget(self.weekly_plan_card)
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
        
        # Focus module & rationale
        self.focus_label = QLabel("")
        self.focus_label.setFont(QFont("Arial", 11))
        self.focus_label.setStyleSheet("color: #F59E0B;")
        self.focus_label.setWordWrap(True)
        
        # Recommended exercises
        rec_label = QLabel("Recommended exercises:")
        rec_label.setFont(QFont("Arial", 12))
        rec_label.setStyleSheet("color: #94A3B8;")
        
        # Exercise buttons container
        self.exercises_layout = QHBoxLayout()
        self.exercises_layout.setSpacing(15)
        
        # Big start button (starts first recommended exercise)
        self.start_btn = QPushButton("Start Practice Session")
        self.start_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_btn.setStyleSheet("""
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
        self.start_btn.clicked.connect(lambda: self.start_exercise.emit("1a", "foundation"))
        
        layout.addWidget(title)
        layout.addWidget(self.focus_label)
        layout.addWidget(rec_label)
        layout.addLayout(self.exercises_layout)
        layout.addWidget(self.start_btn)
        
        return card
    
    def create_weekly_plan_card(self):
        """Create the weekly curriculum plan card."""
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
        
        # Header row
        header_layout = QHBoxLayout()
        
        title = QLabel("Weekly Plan")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        regen_btn = QPushButton("Regenerate Plan")
        regen_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #E2E8F0;
                border: 1px solid #4B5563;
                padding: 6px 14px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        regen_btn.clicked.connect(self._regenerate_curriculum)
        header_layout.addWidget(regen_btn)
        
        layout.addLayout(header_layout)
        
        # Day grid
        self.day_grid = QGridLayout()
        self.day_grid.setSpacing(8)
        layout.addLayout(self.day_grid)
        
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
        
        # Load curriculum
        self._load_curriculum()
        
    def _load_curriculum(self):
        """Load and display curriculum data."""
        from datetime import datetime
        
        # Get today's exercises
        today_exercises = self.curriculum_mgr.get_today_exercises()
        focus_module = self.curriculum_mgr.get_focus_module()
        rationale = self.curriculum_mgr.get_rationale()
        
        module_names = {1: "Pitch Control", 2: "Breath & Sustain",
                       3: "Pace & Rhythm", 4: "Dynamics & Projection"}
        focus_name = module_names.get(focus_module, "Pitch Control")
        self.focus_label.setText(f"Focus: Module {focus_module} ({focus_name}) — {rationale}")
        
        # Clear old exercise buttons
        while self.exercises_layout.count():
            child = self.exercises_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Add curriculum-driven exercise buttons
        for ex_id in today_exercises:
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
            self.exercises_layout.addWidget(btn)
            
        # Update start button to launch first recommended exercise
        if today_exercises:
            first_ex = today_exercises[0]
            try:
                self.start_btn.clicked.disconnect()
            except TypeError:
                pass
            self.start_btn.clicked.connect(lambda: self.start_exercise.emit(first_ex, "foundation"))
        
        # Populate weekly plan grid
        self._populate_weekly_grid()
        
    def _populate_weekly_grid(self):
        """Fill the weekly plan grid with day columns."""
        from datetime import datetime
        
        # Clear existing grid
        while self.day_grid.count():
            child = self.day_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        weekly_plan = self.curriculum_mgr.get_full_weekly_plan()
        today_index = datetime.now().weekday()
        
        for col, day_entry in enumerate(weekly_plan):
            day_name = day_entry.get('day', '')
            exercises = day_entry.get('exercises', [])
            is_today = (col == today_index)
            
            # Day header
            header = QLabel(day_name)
            header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_today:
                header.setStyleSheet("color: #2DD4BF; background-color: #1E3A3A; border-radius: 4px; padding: 4px;")
            else:
                header.setStyleSheet("color: #94A3B8; padding: 4px;")
            self.day_grid.addWidget(header, 0, col)
            
            # Exercise labels
            if exercises:
                ex_text = "\n".join(exercises)
            else:
                ex_text = "Rest"
            
            ex_label = QLabel(ex_text)
            ex_label.setFont(QFont("Arial", 10))
            ex_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_today:
                ex_label.setStyleSheet("color: #E2E8F0; background-color: #1E3A3A; border-radius: 4px; padding: 6px;")
            else:
                ex_label.setStyleSheet("color: #6B7280; padding: 6px;")
            self.day_grid.addWidget(ex_label, 1, col)
            
    def _regenerate_curriculum(self):
        """Force regenerate the weekly curriculum."""
        self.curriculum_mgr.generate_curriculum()
        self._load_curriculum()
            
    def refresh(self):
        """Refresh dashboard data."""
        self.curriculum_mgr.invalidate_cache()
        self.load_data()
