from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPainter, QColor
from datetime import datetime, timedelta
from typing import List


class StreakCalendar(QWidget):
    """30-day practice streak calendar with colored dots."""
    
    def __init__(self):
        super().__init__()
        self.practice_days = []  # List of date strings "YYYY-MM-DD"
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title = QLabel("30-Day Practice Streak")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Calendar grid
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(8)
        
        # Create 30 day cells (6 rows x 5 cols)
        self.day_cells = []
        today = datetime.now().date()
        
        for i in range(30):
            day_date = today - timedelta(days=29-i)
            cell = DayCell(day_date)
            row = i // 5
            col = i % 5
            self.calendar_grid.addWidget(cell, row, col)
            self.day_cells.append(cell)
        
        layout.addWidget(title)
        layout.addLayout(self.calendar_grid)
        self.setLayout(layout)
        
    def set_practice_days(self, practice_days: List[str]):
        """Update calendar with practice days."""
        self.practice_days = practice_days
        
        # Update each cell
        for cell in self.day_cells:
            date_str = cell.date.strftime("%Y-%m-%d")
            if date_str in practice_days:
                cell.set_practiced(True)
            else:
                cell.set_practiced(False)
                
    def get_current_streak(self) -> int:
        """Calculate current consecutive practice streak."""
        if not self.practice_days:
            return 0
            
        streak = 0
        today = datetime.now().date()
        
        # Check backwards from today
        for i in range(30):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in self.practice_days:
                streak += 1
            else:
                break
                
        return streak


class DayCell(QWidget):
    """Individual day cell in the streak calendar."""
    
    def __init__(self, date):
        super().__init__()
        self.date = date
        self.practiced = False
        self.is_today = date == datetime.now().date()
        self.setFixedSize(50, 50)
        
    def set_practiced(self, practiced: bool):
        """Mark this day as practiced or not."""
        self.practiced = practiced
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for the day cell."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        if self.is_today:
            bg_color = QColor("#2A3444")
        else:
            bg_color = QColor("#1A2332")
        painter.fillRect(self.rect(), bg_color)
        
        # Border
        border_color = QColor("#2A3444")
        painter.setPen(border_color)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        
        # Day number
        painter.setPen(QColor("#94A3B8"))
        painter.setFont(QFont("Arial", 10))
        day_num = str(self.date.day)
        painter.drawText(5, 15, day_num)
        
        # Practice indicator (dot)
        if self.practiced:
            dot_color = QColor("#2DD4BF")
            painter.setBrush(dot_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(15, 25, 20, 20)
        elif self.is_today:
            # Pulsing outline for today if not practiced
            dot_color = QColor("#F59E0B")
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(dot_color)
            painter.drawEllipse(15, 25, 20, 20)
        else:
            # Empty dot for missed days
            dot_color = QColor("#2A3444")
            painter.setBrush(dot_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(15, 25, 20, 20)
