from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPixmap
from tier_gating import TierGating
from exercises import get_module_exercises
import exercises


class ModuleView(QWidget):
    """Module browser with tier gating and lock indicators."""
    
    start_exercise = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.tier_gating = TierGating()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Practice Modules")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Complete exercises to unlock higher tiers. "
            "Foundation tier is always available.\n"
            "Intermediate: Complete 3/5 foundation exercises with 70%+ score\n"
            "Advanced: Complete 3/5 intermediate exercises with 70%+ score"
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(instructions)
        
        # Scrollable area for modules
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        modules_widget = QWidget()
        modules_layout = QVBoxLayout(modules_widget)
        modules_layout.setSpacing(20)
        
        # Create module sections
        for module_num in range(1, 5):
            module_widget = self.create_module_section(module_num)
            modules_layout.addWidget(module_widget)
            
        scroll.setWidget(modules_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
    def create_module_section(self, module_num: int) -> QWidget:
        """Create a section for one module."""
        module_names = {
            1: "Pitch Control",
            2: "Breath & Sustain", 
            3: "Pace & Rhythm",
            4: "Dynamics & Projection"
        }
        
        module_descriptions = {
            1: "Master pitch accuracy and control",
            2: "Develop breath support and sustain",
            3: "Improve speaking pace and rhythm",
            4: "Enhance volume and dynamics"
        }
        
        # Get tier status
        tier_status = self.tier_gating.get_module_tier_status(module_num)
        
        # Module frame
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Module header
        header_layout = QHBoxLayout()
        
        title = QLabel(f"Module {module_num}: {module_names[module_num]}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Tier status indicators
        tier_indicators = self.create_tier_indicators(tier_status)
        header_layout.addLayout(tier_indicators)
        
        layout.addLayout(header_layout)
        
        # Module description
        desc = QLabel(module_descriptions[module_num])
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94A3B8; font-size: 12px; margin: 5px 0;")
        layout.addWidget(desc)
        
        # Exercise grid
        exercise_grid_widget = QWidget()
        exercise_grid_layout = self.create_exercise_grid(module_num, tier_status)
        exercise_grid_widget.setLayout(exercise_grid_layout)
        layout.addWidget(exercise_grid_widget)
        
        return frame
        
    def create_tier_indicators(self, tier_status: dict) -> QHBoxLayout:
        """Create tier lock/unlock indicators."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        tiers = [
            ("Foundation", tier_status['foundation_unlocked'], "#10B981"),
            ("Intermediate", tier_status['intermediate_unlocked'], "#F59E0B"),
            ("Advanced", tier_status['advanced_unlocked'], "#EF4444")
        ]
        
        for tier_name, is_unlocked, color in tiers:
            indicator = QLabel()
            indicator.setFixedSize(20, 20)
            
            if is_unlocked:
                # Unlocked - show checkmark
                indicator.setStyleSheet(f"""
                    QLabel {{
                        background-color: {color};
                        border-radius: 10px;
                        color: white;
                        font-weight: bold;
                    }}
                """)
                indicator.setText("✓")
                indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                # Locked - show lock
                indicator.setStyleSheet("""
                    QLabel {
                        background-color: #374151;
                        border-radius: 10px;
                        color: #9CA3AF;
                        font-weight: bold;
                    }
                """)
                indicator.setText("🔒")
                indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
            indicator.setToolTip(tier_name)
            layout.addWidget(indicator)
            
        return layout
        
    def create_exercise_grid(self, module_num: int, tier_status: dict) -> QGridLayout:
        """Create grid of exercises for a module."""
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Headers
        headers = ["Exercise", "Foundation", "Intermediate", "Advanced"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setStyleSheet("color: #E2E8F0;")
            grid.addWidget(label, 0, col)
            
        # Get exercises for this module
        module_exercises = get_module_exercises(module_num)
        
        for row, exercise in enumerate(module_exercises, 1):
            # Exercise name
            name_label = QLabel(f"{exercise.id}: {exercise.name}")
            name_label.setStyleSheet("color: #E2E8F0;")
            grid.addWidget(name_label, row, 0)
            
            # Tier buttons
            tiers = ['foundation', 'intermediate', 'advanced']
            for col, tier in enumerate(tiers, 1):
                button = QPushButton()
                button.setFixedSize(80, 30)
                
                # Check if accessible
                can_access, reason = self.tier_gating.can_access_exercise(exercise.id, tier)
                
                if can_access:
                    button.setText("Start")
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #2DD4BF;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #26A69A;
                        }
                    """)
                    button.clicked.connect(lambda checked, eid=exercise.id, t=tier: self.start_exercise.emit(eid, t))
                else:
                    button.setText("🔒")
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #374151;
                            color: #9CA3AF;
                            border: 1px solid #4B5563;
                            border-radius: 4px;
                        }
                    """)
                    button.setToolTip(reason)
                    
                grid.addWidget(button, row, col)
                
        return grid
        
    def refresh(self):
        """Refresh the module view to update tier status."""
        # Clear and recreate all module sections
        # This is a simple approach - could be optimized to only update changed sections
        for i in reversed(range(self.layout().count())):
            child = self.layout().itemAt(i).widget()
            if child:
                child.deleteLater()
                
        # Recreate UI
        self.init_ui()
