from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont
import numpy as np


class AmplitudeBar(QWidget):
    """Vertical amplitude meter showing current voice level."""
    
    def __init__(self):
        super().__init__()
        self.amplitude_db = -60.0  # Current amplitude in dB
        self.peak_db = -60.0  # Peak hold
        self.voice_threshold = -40.0  # Voice activation threshold
        self.setFixedWidth(80)
        self.setMinimumHeight(300)
        
    def set_amplitude(self, amplitude_db: float):
        """Update current amplitude value."""
        self.amplitude_db = amplitude_db
        # Update peak hold
        if amplitude_db > self.peak_db:
            self.peak_db = amplitude_db
        self.update()
        
    def set_threshold(self, threshold_db: float):
        """Set voice activation threshold line."""
        self.voice_threshold = threshold_db
        self.update()
        
    def reset_peak(self):
        """Reset peak hold."""
        self.peak_db = -60.0
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for amplitude bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        bar_width = 40
        bar_x = (self.width() - bar_width) // 2
        bar_y = 40
        bar_height = self.height() - 80
        
        # Background
        bg_color = QColor("#1A2332")
        painter.fillRect(self.rect(), bg_color)
        
        # Bar background (empty portion)
        bar_bg = QColor("#2A3444")
        painter.fillRect(bar_x, bar_y, bar_width, bar_height, bar_bg)
        
        # Calculate fill height based on amplitude (-60 to 0 dB range)
        db_range = 60.0
        normalized = (self.amplitude_db + 60.0) / db_range
        normalized = max(0, min(1, normalized))
        fill_height = int(bar_height * normalized)
        
        # Gradient fill (green -> yellow -> red)
        if fill_height > 0:
            gradient = QLinearGradient(0, bar_y + bar_height, 0, bar_y)
            
            # Color stops based on dB levels
            if normalized < 0.5:  # -60 to -30 dB (green)
                gradient.setColorAt(0, QColor("#2DD4BF"))
                gradient.setColorAt(1, QColor("#2DD4BF"))
            elif normalized < 0.75:  # -30 to -15 dB (yellow)
                gradient.setColorAt(0, QColor("#2DD4BF"))
                gradient.setColorAt(0.5, QColor("#F59E0B"))
                gradient.setColorAt(1, QColor("#F59E0B"))
            else:  # -15 to 0 dB (red)
                gradient.setColorAt(0, QColor("#F59E0B"))
                gradient.setColorAt(0.5, QColor("#EF4444"))
                gradient.setColorAt(1, QColor("#EF4444"))
            
            painter.fillRect(
                bar_x,
                bar_y + bar_height - fill_height,
                bar_width,
                fill_height,
                gradient
            )
        
        # Peak hold indicator
        if self.peak_db > -60:
            peak_normalized = (self.peak_db + 60.0) / db_range
            peak_normalized = max(0, min(1, peak_normalized))
            peak_y = bar_y + bar_height - int(bar_height * peak_normalized)
            
            painter.setPen(QColor("#F59E0B"))
            painter.drawLine(bar_x, peak_y, bar_x + bar_width, peak_y)
        
        # Threshold line
        threshold_normalized = (self.voice_threshold + 60.0) / db_range
        threshold_normalized = max(0, min(1, threshold_normalized))
        threshold_y = bar_y + bar_height - int(bar_height * threshold_normalized)
        
        painter.setPen(QColor("#8B5CF6"))
        painter.drawLine(bar_x - 5, threshold_y, bar_x + bar_width + 5, threshold_y)
        
        # Scale markers
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 8))
        
        db_markers = [0, -10, -20, -30, -40, -50, -60]
        for db in db_markers:
            marker_normalized = (db + 60.0) / db_range
            marker_y = bar_y + bar_height - int(bar_height * marker_normalized)
            
            # Tick mark
            painter.drawLine(bar_x - 3, marker_y, bar_x, marker_y)
            
            # Label
            painter.drawText(5, marker_y + 4, f"{db}")
        
        # Current value display at top
        painter.setPen(QColor("#E2E8F0"))
        painter.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
        value_text = f"{self.amplitude_db:.1f} dB"
        painter.drawText(0, 25, self.width(), 20, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Label at bottom
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(0, self.height() - 15, self.width(), 15, 
                        Qt.AlignmentFlag.AlignCenter, "Amplitude")
