#!/usr/bin/env python3
"""
Bespoke - Local Voice Practice Gym
A desktop application for voice practice with real-time audio biofeedback.
"""

import sys
import os
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QIcon

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def setup_pyqtgraph():
    """Configure pyqtgraph for dark theme."""
    pg.setConfigOptions(
        background='#0F1419',
        foreground='#94A3B8',
        antialias=True
    )
    
    # Set default plot styles
    pg.setConfigOption('useOpenGL', False)  # More compatible
    

def setup_application():
    """Set up the QApplication."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Bespoke")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Bespoke Voice Practice")
    
    return app


def main():
    """Main entry point."""
    # Configure pyqtgraph first
    setup_pyqtgraph()
    
    # Create QApplication
    app = setup_application()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
