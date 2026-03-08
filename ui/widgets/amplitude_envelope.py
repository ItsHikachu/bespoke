import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import numpy as np
from collections import deque


class AmplitudeEnvelope(QWidget):
    """Scrolling amplitude envelope trace showing volume over time."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Data storage
        self.time_window = 10.0  # seconds
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.fps = 60
        
        # Amplitude data (time, amplitude_db) pairs
        self.amplitude_data = []
        self.target_amplitude = None  # Optional target line
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / self.fps))
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Volume Envelope")
        title.setFont(QFont("Arial", 10))
        title.setStyleSheet("color: #94A3B8;")
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Amplitude', units='dB')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setYRange(-60, 0)
        self.plot_widget.setXRange(0, self.time_window)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Create plot curve
        self.amplitude_curve = self.plot_widget.plot(pen=pg.mkPen('#2DD4BF', width=2))
        
        # Target line (optional)
        self.target_line = None
        
        layout.addWidget(title)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
    def set_target(self, target_db: float):
        """Set target amplitude line."""
        self.target_amplitude = target_db
        
        if self.target_line is None:
            self.target_line = self.plot_widget.plot(
                [0, self.time_window],
                [target_db, target_db],
                pen=pg.mkPen('#F59E0B', width=1.5, dash=[5, 5])
            )
        else:
            self.target_line.setData([0, self.time_window], [target_db, target_db])
        
    def add_data_point(self, amplitude_db: float, timestamp=None):
        """Add a new amplitude data point."""
        if timestamp is None:
            timestamp = len(self.amplitude_data) * self.buffer_size / self.sample_rate
            
        self.amplitude_data.append((timestamp, amplitude_db))
        
        # Keep only data within time window
        cutoff_time = timestamp - self.time_window
        self.amplitude_data = [(t, a) for t, a in self.amplitude_data if t >= cutoff_time]
        
    def update_plot(self):
        """Update the plot with current data."""
        if not self.amplitude_data:
            return
            
        # Extract time and amplitude arrays
        times, amplitudes = zip(*self.amplitude_data)
        
        # Adjust times to be relative to current time window
        if times:
            current_time = times[-1]
            relative_times = [t - (current_time - self.time_window) for t in times]
            
            # Update plot data
            self.amplitude_curve.setData(relative_times, amplitudes)
            
            # Update x-axis range
            self.plot_widget.setXRange(0, self.time_window)
            
    def clear(self):
        """Clear all amplitude data."""
        self.amplitude_data = []
        self.amplitude_curve.clear()
        
    def get_statistics(self):
        """Get statistics from current data."""
        if not self.amplitude_data:
            return {"mean": 0, "std": 0, "min": -60, "max": -60}
            
        amplitudes = [a for _, a in self.amplitude_data]
        return {
            "mean": np.mean(amplitudes),
            "std": np.std(amplitudes),
            "min": np.min(amplitudes),
            "max": np.max(amplitudes),
            "cv": np.std(amplitudes) / max(abs(np.mean(amplitudes)), 1e-10)  # Coefficient of variation
        }
