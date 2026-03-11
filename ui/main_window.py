from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.practice_session import PracticeSession
from ui.dashboard import Dashboard
from ui.settings_view import SettingsView
from exercises import get_module_exercises, Exercise


class MainWindow(QMainWindow):
    """Main application window with navigation."""
    
    def __init__(self):
        super().__init__()
        self.current_session = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Bespoke - Voice Practice Gym")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area (stacked widget)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create views
        self.create_views()
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F1419;
            }
            QWidget {
                background-color: #0F1419;
                color: #E2E8F0;
            }
            QPushButton {
                background-color: #1A2332;
                color: #E2E8F0;
                border: 1px solid #2A3444;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2A3444;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
            QLabel {
                color: #E2E8F0;
            }
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
            }
        """)
        
    def create_header(self):
        """Create the application header."""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border-bottom: 2px solid #2DD4BF;
                border-radius: 0px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App title
        title_label = QLabel("Bespoke")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2DD4BF;")
        
        subtitle_label = QLabel("Voice Practice Gym")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #94A3B8;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(0)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.clicked.connect(lambda: self.switch_view("dashboard"))
        
        self.modules_btn = QPushButton("Modules")
        self.modules_btn.clicked.connect(lambda: self.switch_view("modules"))
        
        self.progress_btn = QPushButton("Progress")
        self.progress_btn.clicked.connect(lambda: self.switch_view("progress"))
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(lambda: self.switch_view("settings"))
        
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.modules_btn)
        nav_layout.addWidget(self.progress_btn)
        nav_layout.addWidget(self.settings_btn)
        
        # Assemble header
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(nav_layout)
        
        return header
        
    def create_views(self):
        """Create all application views."""
        # Dashboard view (index 0)
        self.dashboard_view = Dashboard()
        self.dashboard_view.start_exercise.connect(self.start_exercise)
        self.stacked_widget.addWidget(self.dashboard_view)
        
        # Modules view (index 1)
        self.modules_view = self.create_modules_view()
        self.stacked_widget.addWidget(self.modules_view)
        
        # Progress view (index 2) - placeholder
        progress_placeholder = QLabel("Progress View - Coming Soon")
        progress_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_placeholder.setStyleSheet("color: #94A3B8; font-size: 18px;")
        self.stacked_widget.addWidget(progress_placeholder)
        
        # Settings view (index 3)
        self.settings_view = SettingsView()
        self.stacked_widget.addWidget(self.settings_view)
        
        # Practice session view (index 4) - initially hidden
        self.practice_session_view = None
        
    def create_dashboard_view(self):
        """Create the dashboard view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Bespoke")
        welcome_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2DD4BF;")
        
        subtitle_label = QLabel("Your local voice practice gym")
        subtitle_label.setFont(QFont("Arial", 16))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #94A3B8;")
        
        # Quick start section
        quick_start_frame = QFrame()
        quick_start_layout = QVBoxLayout(quick_start_frame)
        quick_start_layout.setSpacing(20)
        
        quick_start_title = QLabel("Quick Start")
        quick_start_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        # Exercise 1a quick start button
        start_1a_btn = QPushButton("Start Pitch Hold (Exercise 1a)")
        start_1a_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        start_1a_btn.setStyleSheet("""
            QPushButton {
                background-color: #2DD4BF;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #26B5A3;
            }
        """)
        start_1a_btn.clicked.connect(lambda: self.start_exercise("1a", "foundation"))
        
        # Module overview
        modules_frame = QFrame()
        modules_layout = QVBoxLayout(modules_frame)
        
        modules_title = QLabel("Modules")
        modules_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        modules_info = QLabel("""
Module 1: Pitch Control - Foundation exercises for pitch accuracy
Module 2: Breath & Sustain - Develop breath control and volume stability  
Module 3: Pace & Rhythm - Master speaking rate and timing
Module 4: Dynamics & Projection - Control volume and vocal quality
        """)
        modules_info.setWordWrap(True)
        modules_info.setStyleSheet("color: #94A3B8;")
        
        modules_layout.addWidget(modules_title)
        modules_layout.addWidget(modules_info)
        
        # Assemble dashboard
        quick_start_layout.addWidget(quick_start_title)
        quick_start_layout.addWidget(start_1a_btn)
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        layout.addWidget(quick_start_frame)
        layout.addWidget(modules_frame)
        layout.addStretch()
        
        return widget
        
    def create_modules_view(self):
        """Create the modules browser view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("Training Modules")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2DD4BF;")
        
        # Module cards container
        modules_container = QWidget()
        modules_layout = QVBoxLayout(modules_container)
        modules_layout.setSpacing(20)
        
        # Create module cards
        for module_num in range(1, 5):
            module_frame = self.create_module_card(module_num)
            modules_layout.addWidget(module_frame)
            
        layout.addWidget(title_label)
        layout.addWidget(modules_container)
        
        return widget
        
    def create_module_card(self, module_num: int):
        """Create a card for a specific module."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Module title
        module_titles = {
            1: "Module 1: Pitch Control",
            2: "Module 2: Breath & Sustain", 
            3: "Module 3: Pace & Rhythm",
            4: "Module 4: Dynamics & Projection"
        }
        
        module_descriptions = {
            1: "Master pitch accuracy and control with real-time visual feedback",
            2: "Develop breath support, sustain, and volume control",
            3: "Improve speaking pace, rhythm, and timing patterns",
            4: "Enhance dynamic range, projection, and vocal quality"
        }
        
        title_label = QLabel(module_titles[module_num])
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2DD4BF;")
        
        desc_label = QLabel(module_descriptions[module_num])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #94A3B8;")
        
        # Exercise list
        exercises = get_module_exercises(module_num)
        exercise_layout = QVBoxLayout()
        
        for exercise in exercises:
            exercise_btn = QPushButton(f"{exercise.id}: {exercise.name}")
            exercise_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0F1419;
                    color: #E2E8F0;
                    border: 1px solid #2A3444;
                    padding: 8px 16px;
                    border-radius: 4px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2A3444;
                }
            """)
            exercise_btn.clicked.connect(lambda e, ex=exercise: self.start_exercise(ex.id, "foundation"))
            exercise_layout.addWidget(exercise_btn)
            
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addLayout(exercise_layout)
        
        return frame
        
    @pyqtSlot(str, str)
    def start_exercise(self, exercise_id: str, tier: str):
        """Start a practice session."""
        if self.practice_session_view is not None:
            self.stacked_widget.removeWidget(self.practice_session_view)
            self.practice_session_view.deleteLater()
            self.practice_session_view = None

        self.practice_session_view = PracticeSession(exercise_id, tier)
        self.practice_session_view.session_completed.connect(self.on_session_completed)
        self.practice_session_view.back_requested.connect(self.on_back_to_dashboard)
        self.stacked_widget.insertWidget(4, self.practice_session_view)
            
        # Switch to practice session view
        self.stacked_widget.setCurrentIndex(4)
        
    @pyqtSlot(dict)
    def on_session_completed(self, session_data):
        """Handle completed practice session."""
        self.dashboard_view.refresh()
        # Return to dashboard after session
        self.switch_view("dashboard")
        
    @pyqtSlot()
    def on_back_to_dashboard(self):
        """Handle back button from practice session."""
        self.dashboard_view.refresh()
        self.switch_view("dashboard")
        
    def switch_view(self, view_name: str):
        """Switch between main views."""
        view_map = {
            "dashboard": 0,
            "modules": 1, 
            "progress": 2,
            "settings": 3
        }
        
        if view_name in view_map:
            self.stacked_widget.setCurrentIndex(view_map[view_name])
            
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_Escape:
            # ESC key returns to dashboard
            if self.stacked_widget.currentIndex() == 4:  # Practice session
                self.on_back_to_dashboard()
