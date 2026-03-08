import numpy as np
import os

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class WhisperTranscriber:
    """Local speech-to-text via faster-whisper. Used for Module 3 only."""

    def __init__(self, model_size="base.en"):
        self.available = WHISPER_AVAILABLE
        self.model = None
        self.model_size = model_size
        self.filler_words = {
            "um", "uh", "like", "you know", "basically",
            "actually", "so", "right", "kind of", "sort of",
            "i mean", "literally", "honestly"
        }

    def ensure_loaded(self):
        if not self.available:
            return False
        if self.model is None:
            try:
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            except Exception:
                self.available = False
                return False
        return True

    def transcribe(self, audio_path: str) -> dict:
        if not self.ensure_loaded():
            return {"error": "faster-whisper not available", "wpm": 0, "filler_count": 0}

        try:
            segments, info = self.model.transcribe(audio_path, word_timestamps=True)
            words = []
            full_text = []
            for segment in segments:
                if segment.words:
                    for word in segment.words:
                        words.append({"text": word.word.strip(), "start": word.start, "end": word.end})
                        full_text.append(word.word.strip())

            if not words:
                return {"transcript": "", "word_count": 0, "duration": 0, "wpm": 0,
                        "filler_count": 0, "pauses": [], "avg_pause_duration": 0, "words": []}

            duration = words[-1]["end"]
            word_count = len([w for w in words if len(w["text"]) > 0])
            wpm = (word_count / duration * 60) if duration > 0 else 0

            text_lower = " ".join(full_text).lower()
            filler_count = sum(text_lower.count(f) for f in self.filler_words)

            pauses = []
            for i in range(1, len(words)):
                gap = words[i]["start"] - words[i-1]["end"]
                if gap > 0.3:
                    pauses.append({"start": words[i-1]["end"], "duration": round(gap, 2)})

            return {
                "transcript": " ".join(full_text),
                "word_count": word_count,
                "duration": round(duration, 2),
                "wpm": round(wpm, 1),
                "filler_count": filler_count,
                "pauses": pauses,
                "avg_pause_duration": round(np.mean([p["duration"] for p in pauses]), 2) if pauses else 0,
                "words": words
            }
        except Exception as e:
            return {"error": str(e), "wpm": 0, "filler_count": 0}
