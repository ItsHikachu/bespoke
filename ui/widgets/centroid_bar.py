from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen


class CentroidBar(QWidget):
    """Horizontal bar showing spectral centroid (vocal brightness)."""
    
    def __init__(self):
        super().__init__()
        self.centroid_hz = 0.0
        self.baseline_centroid = 0.0  # User's baseline
        self.centroid_range = (500, 4000)  # Typical range for voice
        self.setMinimumHeight(100)
        self.setMinimumWidth(300)
        
    def set_centroid(self, centroid_hz: float):
        """Update current spectral centroid value."""
        self.centroid_hz = centroid_hz
        self.update()
        
    def set_baseline(self, baseline_hz: float):
        """Set baseline centroid for comparison."""
        self.baseline_centroid = baseline_hz
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for centroid bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#1A2332")
        painter.fillRect(self.rect(), bg_color)
        
        # Bar dimensions
        bar_height = 30
        bar_x = 60
        bar_y = (self.height() - bar_height) // 2
        bar_width = self.width() - 120
        
        # Bar background
        bar_bg = QColor("#2A3444")
        painter.fillRect(bar_x, bar_y, bar_width, bar_height, bar_bg)
        
        # Calculate position based on centroid
        min_hz, max_hz = self.centroid_range
        normalized = (self.centroid_hz - min_hz) / (max_hz - min_hz)
        normalized = max(0, min(1, normalized))
        
        # Gradient fill showing brightness
        if self.centroid_hz > 0:
            fill_width = int(bar_width * normalized)
            
            # Gradient from dark to bright
            gradient = QLinearGradient(bar_x, 0, bar_x + bar_width, 0)
            gradient.setColorAt(0, QColor("#8B5CF6"))  # Purple (darker/warmer)
            gradient.setColorAt(0.5, QColor("#2DD4BF"))  # Teal (balanced)
            gradient.setColorAt(1, QColor("#F59E0B"))  # Amber (brighter)
            
            painter.fillRect(bar_x, bar_y, fill_width, bar_height, gradient)
        
        # Baseline marker (if set)
        if self.baseline_centroid > 0:
            baseline_normalized = (self.baseline_centroid - min_hz) / (max_hz - min_hz)
            baseline_normalized = max(0, min(1, baseline_normalized))
            baseline_x = bar_x + int(bar_width * baseline_normalized)
            
            # Draw baseline line
            painter.setPen(QPen(QColor("#F59E0B"), 3))
            painter.drawLine(baseline_x, bar_y - 5, baseline_x, bar_y + bar_height + 5)
            
            # Baseline label
            painter.setFont(QFont("Arial", 8))
            painter.drawText(baseline_x - 20, bar_y - 10, 40, 10,
                           Qt.AlignmentFlag.AlignCenter, "Baseline")
        
        # Current value indicator (vertical line)
        if self.centroid_hz > 0:
            current_x = bar_x + int(bar_width * normalized)
            painter.setPen(QPen(QColor("#E2E8F0"), 2))
            painter.drawLine(current_x, bar_y, current_x, bar_y + bar_height)
        
        # Scale labels
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 9))
        
        # Min label (left)
        painter.drawText(bar_x - 55, bar_y, 50, bar_height,
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                        f"{min_hz} Hz")
        
        # Max label (right)
        painter.drawText(bar_x + bar_width + 5, bar_y, 50, bar_height,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        f"{max_hz} Hz")
        
        # Current value display at top
        painter.setPen(QColor("#E2E8F0"))
        painter.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
        value_text = f"{self.centroid_hz:.0f} Hz"
        painter.drawText(0, 10, self.width(), 20, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Brightness indicator
        if self.centroid_hz > 0:
            if normalized < 0.33:
                brightness_label = "Warm/Dark"
                brightness_color = "#8B5CF6"
            elif normalized < 0.67:
                brightness_label = "Balanced"
                brightness_color = "#2DD4BF"
            else:
                brightness_label = "Bright"
                brightness_color = "#F59E0B"
            
            painter.setPen(QColor(brightness_color))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(0, 35, self.width(), 15,
                           Qt.AlignmentFlag.AlignCenter, brightness_label)
        
        # Title at bottom
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(0, self.height() - 20, self.width(), 15,
                        Qt.AlignmentFlag.AlignCenter, "Spectral Centroid (Brightness)")
        
        # Comparison to baseline (if set)
        if self.baseline_centroid > 0 and self.centroid_hz > 0:
            diff_hz = self.centroid_hz - self.baseline_centroid
            diff_percent = (diff_hz / self.baseline_centroid) * 100
            
            if abs(diff_percent) > 1:  # Only show if meaningful difference
                if diff_percent > 0:
                    comp_text = f"+{diff_percent:.1f}% vs baseline"
                    comp_color = "#2DD4BF" if diff_percent > 5 else "#94A3B8"
                else:
                    comp_text = f"{diff_percent:.1f}% vs baseline"
                    comp_color = "#EF4444" if diff_percent < -5 else "#94A3B8"
                
                painter.setPen(QColor(comp_color))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(0, bar_y + bar_height + 15, self.width(), 15,
                               Qt.AlignmentFlag.AlignCenter, comp_text)
