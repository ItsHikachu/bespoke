from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import math


class WPMGauge(QWidget):
    """Large WPM display with circular ring gauge."""
    
    def __init__(self):
        super().__init__()
        self.wpm = 0.0
        self.target_wpm = 130.0
        self.wpm_range = (60, 200)  # Min and max WPM for gauge
        self.is_speaking = False
        self.setMinimumSize(300, 300)
        
    def set_wpm(self, wpm: float):
        """Update current WPM value."""
        self.wpm = wpm
        self.update()
        
    def set_target(self, target_wpm: float):
        """Set target WPM."""
        self.target_wpm = target_wpm
        self.update()
        
    def set_speaking(self, is_speaking: bool):
        """Update speaking status."""
        self.is_speaking = is_speaking
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for WPM gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#0F1419")
        painter.fillRect(self.rect(), bg_color)
        
        # Center point
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Ring dimensions
        ring_radius = min(self.width(), self.height()) // 2 - 40
        ring_thickness = 20
        
        # Background ring
        bg_ring_color = QColor("#2A3444")
        bg_pen = QPen(bg_ring_color, ring_thickness)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        
        rect = QRectF(
            center_x - ring_radius,
            center_y - ring_radius,
            ring_radius * 2,
            ring_radius * 2
        )
        
        # Draw background arc (240 degrees, from -210 to 30)
        start_angle = -210 * 16
        span_angle = 240 * 16
        painter.drawArc(rect, start_angle, span_angle)
        
        # Calculate WPM position on gauge
        wpm_min, wpm_max = self.wpm_range
        normalized_wpm = (self.wpm - wpm_min) / (wpm_max - wpm_min)
        normalized_wpm = max(0, min(1, normalized_wpm))
        
        # WPM arc (color based on proximity to target)
        if self.wpm > 0:
            deviation = abs(self.wpm - self.target_wpm)
            if deviation < 10:
                wpm_color = QColor("#2DD4BF")  # On target
            elif deviation < 20:
                wpm_color = QColor("#F59E0B")  # Close
            else:
                wpm_color = QColor("#EF4444")  # Off target
                
            wpm_pen = QPen(wpm_color, ring_thickness)
            wpm_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(wpm_pen)
            
            wpm_span = int(240 * normalized_wpm * 16)
            painter.drawArc(rect, start_angle, wpm_span)
        
        # Target marker
        if self.target_wpm:
            normalized_target = (self.target_wpm - wpm_min) / (wpm_max - wpm_min)
            normalized_target = max(0, min(1, normalized_target))
            
            target_angle = -210 + (240 * normalized_target)
            target_rad = math.radians(target_angle)
            
            # Draw target line
            marker_inner = ring_radius - ring_thickness // 2 - 10
            marker_outer = ring_radius + ring_thickness // 2 + 10
            
            inner_x = center_x + marker_inner * math.cos(target_rad)
            inner_y = center_y + marker_inner * math.sin(target_rad)
            outer_x = center_x + marker_outer * math.cos(target_rad)
            outer_y = center_y + marker_outer * math.sin(target_rad)
            
            painter.setPen(QPen(QColor("#F59E0B"), 3))
            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))
        
        # Center WPM value
        painter.setPen(QColor("#E2E8F0"))
        painter.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        wpm_text = f"{int(self.wpm)}"
        text_rect = QRectF(center_x - 100, center_y - 40, 200, 60)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, wpm_text)
        
        # WPM label
        painter.setFont(QFont("Arial", 14))
        painter.setPen(QColor("#94A3B8"))
        label_rect = QRectF(center_x - 100, center_y + 20, 200, 30)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "WPM")
        
        # Speaking indicator
        if self.is_speaking:
            indicator_color = QColor("#2DD4BF")
            painter.setBrush(indicator_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - 8, center_y + 60, 16, 16)
            
            painter.setPen(QColor("#2DD4BF"))
            painter.setFont(QFont("Arial", 10))
            status_rect = QRectF(center_x - 50, center_y + 80, 100, 20)
            painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, "Speaking")
        else:
            painter.setPen(QColor("#6B7280"))
            painter.setFont(QFont("Arial", 10))
            status_rect = QRectF(center_x - 50, center_y + 80, 100, 20)
            painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, "Silent")
        
        # Scale labels
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 10))
        
        # Min label (bottom left)
        min_angle = -210
        min_rad = math.radians(min_angle)
        min_label_x = center_x + (ring_radius + 30) * math.cos(min_rad)
        min_label_y = center_y + (ring_radius + 30) * math.sin(min_rad)
        painter.drawText(int(min_label_x - 20), int(min_label_y + 5), f"{wpm_min}")
        
        # Max label (bottom right)
        max_angle = 30
        max_rad = math.radians(max_angle)
        max_label_x = center_x + (ring_radius + 30) * math.cos(max_rad)
        max_label_y = center_y + (ring_radius + 30) * math.sin(max_rad)
        painter.drawText(int(max_label_x - 10), int(max_label_y + 5), f"{wpm_max}")
        
        # Target label (if set)
        if self.target_wpm:
            painter.setPen(QColor("#F59E0B"))
            painter.setFont(QFont("Arial", 9))
            target_label = f"Target: {int(self.target_wpm)}"
            target_rect = QRectF(center_x - 60, 10, 120, 20)
            painter.drawText(target_rect, Qt.AlignmentFlag.AlignCenter, target_label)
