from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QSlider, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sounddevice as sd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from audio_engine import AudioEngine


class SettingsView(QWidget):
    """Settings view with mic selection and voice threshold calibration."""
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.audio_engine = None
        self.calibrating = False
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2DD4BF;")
        
        # Audio Settings Group
        audio_group = QGroupBox("Audio Settings")
        audio_group.setStyleSheet("""
            QGroupBox {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 20px;
                margin-top: 10px;
                font-size: 16px;
                font-weight: bold;
                color: #2DD4BF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        audio_layout = QVBoxLayout()
        
        # Microphone selection
        mic_layout = QHBoxLayout()
        mic_label = QLabel("Microphone:")
        mic_label.setFont(QFont("Arial", 12))
        mic_label.setStyleSheet("color: #E2E8F0;")
        
        self.mic_combo = QComboBox()
        self.mic_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F1419;
                color: #E2E8F0;
                border: 1px solid #2A3444;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 300px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # Populate microphones
        self.populate_microphones()
        
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo)
        mic_layout.addStretch()
        
        # Voice threshold calibration
        threshold_layout = QVBoxLayout()
        threshold_label = QLabel("Voice Activation Threshold:")
        threshold_label.setFont(QFont("Arial", 12))
        threshold_label.setStyleSheet("color: #E2E8F0;")
        
        threshold_help = QLabel("Adjust the sensitivity for detecting voice. Lower = more sensitive.")
        threshold_help.setStyleSheet("color: #94A3B8; font-size: 10px;")
        threshold_help.setWordWrap(True)
        
        # Threshold slider
        slider_layout = QHBoxLayout()
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setMinimum(-60)
        self.threshold_slider.setMaximum(-20)
        self.threshold_slider.setValue(-40)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #2A3444;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #2DD4BF;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background-color: #26B5A3;
            }
        """)
        
        self.threshold_value_label = QLabel("-40 dB")
        self.threshold_value_label.setFont(QFont("Monospace", 12))
        self.threshold_value_label.setStyleSheet("color: #2DD4BF;")
        self.threshold_value_label.setMinimumWidth(80)
        
        slider_layout.addWidget(self.threshold_slider)
        slider_layout.addWidget(self.threshold_value_label)
        
        # Calibration controls
        calibrate_layout = QHBoxLayout()
        
        self.calibrate_btn = QPushButton("Auto-Calibrate")
        self.calibrate_btn.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        self.calibrate_btn.clicked.connect(self.start_calibration)
        
        self.calibrate_status = QLabel("Speak normally for 5 seconds to auto-calibrate")
        self.calibrate_status.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.calibrate_status.setWordWrap(True)
        
        # Live level indicator
        self.level_label = QLabel("Current Level: -- dB")
        self.level_label.setFont(QFont("Monospace", 11))
        self.level_label.setStyleSheet("color: #94A3B8;")
        
        calibrate_layout.addWidget(self.calibrate_btn)
        calibrate_layout.addWidget(self.calibrate_status)
        calibrate_layout.addStretch()
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(threshold_help)
        threshold_layout.addLayout(slider_layout)
        threshold_layout.addLayout(calibrate_layout)
        threshold_layout.addWidget(self.level_label)
        
        audio_layout.addLayout(mic_layout)
        audio_layout.addSpacing(20)
        audio_layout.addLayout(threshold_layout)
        
        audio_group.setLayout(audio_layout)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2DD4BF;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #26B5A3;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        # Assemble layout
        main_layout.addWidget(title)
        main_layout.addWidget(audio_group)
        main_layout.addWidget(save_btn)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Timer for live level monitoring
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.update_level)
        
    def populate_microphones(self):
        """Populate microphone dropdown with available devices."""
        try:
            devices = sd.query_devices()
            self.mic_combo.clear()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:  # Input device
                    self.mic_combo.addItem(device['name'], i)
                    
            # Set default device
            default_device = sd.query_devices(kind='input')
            if default_device:
                default_name = default_device['name']
                index = self.mic_combo.findText(default_name)
                if index >= 0:
                    self.mic_combo.setCurrentIndex(index)
        except Exception as e:
            self.mic_combo.addItem("No microphones found", None)
            
    def on_threshold_changed(self, value):
        """Update threshold value label."""
        self.threshold_value_label.setText(f"{value} dB")
        
    def start_calibration(self):
        """Start auto-calibration process."""
        if self.calibrating:
            return
            
        self.calibrating = True
        self.calibrate_btn.setEnabled(False)
        self.calibrate_status.setText("Calibrating... Speak normally now!")
        self.calibrate_status.setStyleSheet("color: #F59E0B; font-size: 10px;")
        
        # Start audio engine for calibration
        device_id = self.mic_combo.currentData()
        self.audio_engine = AudioEngine(device=device_id)
        self.audio_engine.start()
        
        # Start level monitoring
        self.level_timer.start(100)  # Update every 100ms
        
        # Stop after 5 seconds
        QTimer.singleShot(5000, self.finish_calibration)
        
    def finish_calibration(self):
        """Finish calibration and set threshold."""
        if not self.calibrating:
            return
            
        self.calibrating = False
        self.level_timer.stop()
        
        # Calculate average amplitude from history
        if self.audio_engine and len(self.audio_engine.amplitude_history) > 0:
            avg_amplitude = sum(self.audio_engine.amplitude_history) / len(self.audio_engine.amplitude_history)
            # Set threshold 10 dB below average speaking level
            suggested_threshold = int(avg_amplitude - 10)
            suggested_threshold = max(-60, min(-20, suggested_threshold))
            
            self.threshold_slider.setValue(suggested_threshold)
            self.calibrate_status.setText(f"Calibration complete! Threshold set to {suggested_threshold} dB")
            self.calibrate_status.setStyleSheet("color: #2DD4BF; font-size: 10px;")
        else:
            self.calibrate_status.setText("Calibration failed. Please try again.")
            self.calibrate_status.setStyleSheet("color: #EF4444; font-size: 10px;")
        
        # Stop audio engine
        if self.audio_engine:
            self.audio_engine.stop()
            self.audio_engine = None
            
        self.calibrate_btn.setEnabled(True)
        
    def update_level(self):
        """Update live level indicator during calibration."""
        if self.audio_engine:
            current_level = self.audio_engine.amplitude_db
            self.level_label.setText(f"Current Level: {current_level:.1f} dB")
            
            # Color code based on level
            if current_level > -30:
                color = "#2DD4BF"  # Good level
            elif current_level > -50:
                color = "#F59E0B"  # Moderate
            else:
                color = "#EF4444"  # Too quiet
                
            self.level_label.setStyleSheet(f"color: {color}; font-family: monospace; font-size: 11px;")
            
    def load_settings(self):
        """Load settings from database."""
        # Load microphone
        saved_mic = self.database.get_setting('microphone_device')
        if saved_mic:
            index = self.mic_combo.findText(saved_mic)
            if index >= 0:
                self.mic_combo.setCurrentIndex(index)
                
        # Load threshold
        saved_threshold = self.database.get_setting('voice_threshold')
        if saved_threshold:
            try:
                threshold_value = int(saved_threshold)
                self.threshold_slider.setValue(threshold_value)
            except ValueError:
                pass
                
    def save_settings(self):
        """Save settings to database."""
        # Save microphone
        mic_name = self.mic_combo.currentText()
        self.database.set_setting('microphone_device', mic_name)
        
        # Save device ID
        device_id = self.mic_combo.currentData()
        if device_id is not None:
            self.database.set_setting('microphone_device_id', str(device_id))
        
        # Save threshold
        threshold = self.threshold_slider.value()
        self.database.set_setting('voice_threshold', str(threshold))
        
        # Show confirmation
        self.calibrate_status.setText("Settings saved successfully!")
        self.calibrate_status.setStyleSheet("color: #2DD4BF; font-size: 10px;")
        
        # Reset message after 3 seconds
        QTimer.singleShot(3000, lambda: self.calibrate_status.setText("Speak normally for 5 seconds to auto-calibrate"))
        
    def closeEvent(self, event):
        """Clean up when closing."""
        if self.audio_engine:
            self.audio_engine.stop()
        event.accept()
