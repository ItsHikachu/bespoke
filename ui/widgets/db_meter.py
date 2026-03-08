from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont
import numpy as np


class DBMeter(QWidget):
    """Peak and RMS dB meter for dynamics exercises."""
    
    def __init__(self):
        super().__init__()
        self.peak_db = -60.0
        self.rms_db = -60.0
        self.peak_hold = -60.0
        self.dynamic_range = 0.0  # Current session range
        self.min_db = 0.0
        self.max_db = -60.0
        self.setFixedWidth(120)
        self.setMinimumHeight(300)
        
    def set_levels(self, peak_db: float, rms_db: float):
        """Update peak and RMS levels."""
        self.peak_db = peak_db
        self.rms_db = rms_db
        
        # Update peak hold
        if peak_db > self.peak_hold:
            self.peak_hold = peak_db
            
        # Update range
        if peak_db > self.max_db:
            self.max_db = peak_db
        if peak_db < self.min_db and peak_db > -60:
            self.min_db = peak_db
            
        self.dynamic_range = self.max_db - self.min_db
        self.update()
        
    def reset_range(self):
        """Reset dynamic range tracking."""
        self.min_db = 0.0
        self.max_db = -60.0
        self.peak_hold = -60.0
        self.dynamic_range = 0.0
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for dB meter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#1A2332")
        painter.fillRect(self.rect(), bg_color)
        
        # Dimensions for two bars (Peak and RMS)
        bar_width = 35
        bar_spacing = 10
        bar_y = 60
        bar_height = self.height() - 120
        
        peak_bar_x = 15
        rms_bar_x = peak_bar_x + bar_width + bar_spacing
        
        # dB range (-60 to 0)
        db_range = 60.0
        
        # Draw Peak bar
        self._draw_bar(painter, peak_bar_x, bar_y, bar_width, bar_height, 
                      self.peak_db, db_range, "Peak")
        
        # Draw RMS bar
        self._draw_bar(painter, rms_bar_x, bar_y, bar_width, bar_height,
                      self.rms_db, db_range, "RMS")
        
        # Peak hold indicator on Peak bar
        if self.peak_hold > -60:
            peak_normalized = (self.peak_hold + 60.0) / db_range
            peak_normalized = max(0, min(1, peak_normalized))
            peak_y = bar_y + bar_height - int(bar_height * peak_normalized)
            
            painter.setPen(QPen(QColor("#F59E0B"), 2))
            painter.drawLine(peak_bar_x, peak_y, peak_bar_x + bar_width, peak_y)
        
        # Scale markers (on the left)
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 8))
        
        db_markers = [0, -10, -20, -30, -40, -50, -60]
        for db in db_markers:
            marker_normalized = (db + 60.0) / db_range
            marker_y = bar_y + bar_height - int(bar_height * marker_normalized)
            
            # Tick mark
            painter.drawLine(5, marker_y, 10, marker_y)
            
            # Label
            painter.drawText(0, marker_y - 10, 5, 20, 
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                           f"{db}")
        
        # Dynamic range display at top
        painter.setPen(QColor("#E2E8F0"))
        painter.setFont(QFont("Monospace", 11, QFont.Weight.Bold))
        range_text = f"Range: {self.dynamic_range:.1f} dB"
        painter.drawText(0, 10, self.width(), 20, Qt.AlignmentFlag.AlignCenter, range_text)
        
        # Current values at bottom
        painter.setFont(QFont("Monospace", 9))
        painter.setPen(QColor("#94A3B8"))
        peak_text = f"P: {self.peak_db:.1f}"
        rms_text = f"R: {self.rms_db:.1f}"
        painter.drawText(0, self.height() - 35, self.width(), 15,
                        Qt.AlignmentFlag.AlignCenter, peak_text)
        painter.drawText(0, self.height() - 20, self.width(), 15,
                        Qt.AlignmentFlag.AlignCenter, rms_text)
        
    def _draw_bar(self, painter, x, y, width, height, db_value, db_range, label):
        """Draw a single meter bar."""
        # Background
        bar_bg = QColor("#2A3444")
        painter.fillRect(x, y, width, height, bar_bg)
        
        # Calculate fill
        normalized = (db_value + 60.0) / db_range
        normalized = max(0, min(1, normalized))
        fill_height = int(height * normalized)
        
        if fill_height > 0:
            # Gradient based on level
            gradient = QLinearGradient(0, y + height, 0, y)
            
            if normalized < 0.5:  # Green zone
                gradient.setColorAt(0, QColor("#2DD4BF"))
                gradient.setColorAt(1, QColor("#2DD4BF"))
            elif normalized < 0.75:  # Yellow zone
                gradient.setColorAt(0, QColor("#2DD4BF"))
                gradient.setColorAt(0.5, QColor("#F59E0B"))
                gradient.setColorAt(1, QColor("#F59E0B"))
            else:  # Red zone
                gradient.setColorAt(0, QColor("#F59E0B"))
                gradient.setColorAt(0.5, QColor("#EF4444"))
                gradient.setColorAt(1, QColor("#EF4444"))
            
            painter.fillRect(x, y + height - fill_height, width, fill_height, gradient)
        
        # Label below bar
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(x, y + height + 5, width, 15,
                        Qt.AlignmentFlag.AlignCenter, label)
