import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPen
import numpy as np


class PitchGraph(QWidget):
    """Real-time scrolling pitch visualization with target overlay."""
    
    def __init__(self):
        super().__init__()
        # Data storage
        self.time_window = 5.0  # seconds
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.fps = 60
        
        # Pitch data (time, pitch) pairs
        self.pitch_data = []
        self.target_pitch = 200.0  # Hz, will be set per exercise
        self.tolerance = 30.0  # Hz, will be set per exercise

        self.init_ui()
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / self.fps))
        
    def init_ui(self):
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Pitch', units='Hz')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setYRange(80, 400)
        self.plot_widget.setXRange(0, self.time_window)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Create plot curve
        self.pitch_curve = self.plot_widget.plot(pen=pg.mkPen('#2DD4BF', width=2))
        
        # Target lines
        self.target_line = self.plot_widget.plot(
            [0, self.time_window], 
            [self.target_pitch, self.target_pitch],
            pen=pg.mkPen('#F59E0B', width=1.5, dash=[5, 5])
        )
        
        self.upper_tolerance_line = self.plot_widget.plot(
            [0, self.time_window],
            [self.target_pitch + self.tolerance, self.target_pitch + self.tolerance],
            pen=pg.mkPen('#F59E0B', width=1, dash=[2, 4])
        )
        
        self.lower_tolerance_line = self.plot_widget.plot(
            [0, self.time_window],
            [self.target_pitch - self.tolerance, self.target_pitch - self.tolerance],
            pen=pg.mkPen('#F59E0B', width=1, dash=[2, 4])
        )
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
    def set_target(self, pitch_hz, tolerance_hz):
        """Update target pitch and tolerance band."""
        self.target_pitch = pitch_hz
        self.tolerance = tolerance_hz
        
        # Update target lines
        self.target_line.setData(
            [0, self.time_window],
            [self.target_pitch, self.target_pitch]
        )
        self.upper_tolerance_line.setData(
            [0, self.time_window],
            [self.target_pitch + self.tolerance, self.target_pitch + self.tolerance]
        )
        self.lower_tolerance_line.setData(
            [0, self.time_window],
            [self.target_pitch - self.tolerance, self.target_pitch - self.tolerance]
        )
        
    def add_data_point(self, pitch_hz, timestamp=None):
        """Add a new pitch data point."""
        if timestamp is None:
            timestamp = len(self.pitch_data) * self.buffer_size / self.sample_rate
            
        self.pitch_data.append((timestamp, pitch_hz))
        
        # Keep only data within time window
        cutoff_time = timestamp - self.time_window
        self.pitch_data = [(t, p) for t, p in self.pitch_data if t >= cutoff_time]
        
    def update_plot(self):
        """Update the plot with current data."""
        if not self.pitch_data:
            return
            
        # Extract time and pitch arrays
        times, pitches = zip(*self.pitch_data)
        
        # Adjust times to be relative to current time window
        if times:
            current_time = times[-1]
            relative_times = [t - (current_time - self.time_window) for t in times]
            
            # Update plot data
            self.pitch_curve.setData(relative_times, pitches)
            
            # Update x-axis range
            self.plot_widget.setXRange(0, self.time_window)
            
    def clear(self):
        """Clear all pitch data."""
        self.pitch_data = []
        self.pitch_curve.clear()
