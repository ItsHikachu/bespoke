from collections import deque
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioEngine:
    """Real-time audio capture and analysis via sounddevice."""

    def __init__(self, sample_rate=44100, buffer_size=1024, device=None):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.device = device
        self.voice_threshold = -40  # dB, adjustable in settings
        self.stream = None
        self.recording_buffer = []
        self.is_recording = False

        # Analysis outputs (updated every buffer callback):
        self.pitch = 0.0             # Hz, 0 if unvoiced
        self.pitch_confidence = 0.0  # 0-1
        self.amplitude_rms = 0.0     # Linear RMS
        self.amplitude_db = -60.0    # dB
        self.spectral_centroid = 0.0 # Hz
        self.is_voice_active = False

        # Histories (ring buffers, last 5 seconds = ~215 frames at 44100/1024):
        self.pitch_history = deque(maxlen=215)
        self.amplitude_history = deque(maxlen=215)
        self.centroid_history = deque(maxlen=215)

        # Callback for UI updates (set by practice_session.py)
        self.on_analysis = None  # callback(pitch, amplitude_db, centroid, is_voice)

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio buffer. Runs in a separate thread."""
        audio = indata[:, 0].copy()  # Mono

        # Accumulate recording if active
        if self.is_recording:
            self.recording_buffer.append(audio.copy())

        # RMS amplitude
        rms = np.sqrt(np.mean(audio ** 2))
        self.amplitude_rms = rms
        self.amplitude_db = 20 * np.log10(max(rms, 1e-10))

        # Voice activity detection
        self.is_voice_active = self.amplitude_db > self.voice_threshold

        # Pitch detection (autocorrelation method for low latency)
        if self.is_voice_active:
            self.pitch, self.pitch_confidence = self._autocorrelation_pitch(audio)
        else:
            self.pitch, self.pitch_confidence = 0.0, 0.0

        # Spectral centroid
        fft = np.abs(np.fft.rfft(audio * np.hanning(len(audio))))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
        self.spectral_centroid = np.sum(freqs * fft) / max(np.sum(fft), 1e-10)

        # Update histories
        self.pitch_history.append(self.pitch)
        self.amplitude_history.append(self.amplitude_db)
        self.centroid_history.append(self.spectral_centroid)

        # Notify UI (must be thread-safe -- use QTimer or signal in practice)
        if self.on_analysis:
            self.on_analysis(self.pitch, self.amplitude_db, self.spectral_centroid, self.is_voice_active)

    def _autocorrelation_pitch(self, audio, fmin=60, fmax=600):
        """Autocorrelation pitch detection. Returns (freq_hz, confidence)."""
        audio = audio - np.mean(audio)
        if np.max(np.abs(audio)) < 1e-6:
            return 0.0, 0.0
        audio = audio / np.max(np.abs(audio))

        n = len(audio)
        fft = np.fft.rfft(audio, n=2*n)
        acf = np.fft.irfft(fft * np.conj(fft))[:n]
        acf = acf / acf[0]

        lag_min = int(self.sample_rate / fmax)
        lag_max = int(self.sample_rate / fmin)
        lag_max = min(lag_max, n - 1)
        if lag_min >= lag_max:
            return 0.0, 0.0

        segment = acf[lag_min:lag_max]
        peak_idx = np.argmax(segment)
        confidence = segment[peak_idx]
        if confidence < 0.8:
            return 0.0, 0.0

        lag = peak_idx + lag_min
        freq = self.sample_rate / lag
        return freq, confidence

    def start(self):
        """Open sounddevice InputStream with callback."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            device=self.device,
            channels=1,
            dtype='float32',
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """Close stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def start_recording(self):
        self.recording_buffer = []
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False
        if self.recording_buffer:
            return np.concatenate(self.recording_buffer)
        return np.array([])

    def save_recording(self, filepath):
        """Save accumulated recording to .wav."""
        audio = self.stop_recording()
        if len(audio) > 0:
            sf.write(filepath, audio, self.sample_rate)
        return filepath
