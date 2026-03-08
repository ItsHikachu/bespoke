from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import math


class ProgressRings(QWidget):
    """Circular progress indicators for all 4 modules."""
    
    def __init__(self):
        super().__init__()
        self.module_progress = {1: 0, 2: 0, 3: 0, 4: 0}  # 0-100 for each module
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Module Progress")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Rings container
        rings_layout = QHBoxLayout()
        rings_layout.setSpacing(20)
        
        # Create 4 module rings
        self.rings = []
        module_names = ["Pitch", "Breath", "Pace", "Dynamics"]
        module_colors = ["#2DD4BF", "#F59E0B", "#8B5CF6", "#EC4899"]
        
        for i in range(4):
            ring = ModuleRing(i+1, module_names[i], module_colors[i])
            rings_layout.addWidget(ring)
            self.rings.append(ring)
        
        layout.addWidget(title)
        layout.addLayout(rings_layout)
        self.setLayout(layout)
        
    def set_module_progress(self, module: int, progress: float):
        """Set progress for a specific module (0-100)."""
        if 1 <= module <= 4:
            self.module_progress[module] = progress
            self.rings[module-1].set_progress(progress)


class ModuleRing(QWidget):
    """Individual circular progress ring for a module."""
    
    def __init__(self, module_num: int, module_name: str, color: str):
        super().__init__()
        self.module_num = module_num
        self.module_name = module_name
        self.color = QColor(color)
        self.progress = 0.0  # 0-100
        self.setFixedSize(100, 120)
        
    def set_progress(self, progress: float):
        """Update progress value (0-100)."""
        self.progress = max(0, min(100, progress))
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for the progress ring."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ring dimensions
        ring_size = 80
        ring_x = (self.width() - ring_size) // 2
        ring_y = 5
        ring_thickness = 8
        
        # Background ring (unfilled portion)
        bg_color = QColor("#2A3444")
        bg_pen = QPen(bg_color, ring_thickness)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        
        rect = QRectF(ring_x, ring_y, ring_size, ring_size)
        painter.drawArc(rect, 90 * 16, -360 * 16)  # Full circle
        
        # Progress ring (filled portion)
        if self.progress > 0:
            progress_pen = QPen(self.color, ring_thickness)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(progress_pen)
            
            # Draw arc from top (90 degrees) clockwise
            span_angle = int(-360 * (self.progress / 100) * 16)
            painter.drawArc(rect, 90 * 16, span_angle)
        
        # Center text (percentage)
        painter.setPen(QColor("#E2E8F0"))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        text = f"{int(self.progress)}%"
        text_rect = QRectF(ring_x, ring_y, ring_size, ring_size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        
        # Module name below ring
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 10))
        name_rect = QRectF(0, ring_y + ring_size + 5, self.width(), 20)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, self.module_name)
