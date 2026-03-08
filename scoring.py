import numpy as np
from typing import Dict, Any, List
from exercises import Exercise


class ScoringEngine:
    """Computes scores for different exercise types."""
    
    def __init__(self):
        pass
        
    def score_exercise(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score an exercise based on collected data."""
        scoring_method = f"_score_{exercise.scoring_type}"
        if hasattr(self, scoring_method):
            return getattr(self, scoring_method)(exercise, data, tier)
        else:
            return {"score": 0.0, "error": f"Unknown scoring type: {exercise.scoring_type}"}
            
    def _score_pitch_tolerance(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score pitch hold exercise - % time within tolerance band."""
        tier_params = exercise.get_tier(tier).params
        target_pitch = tier_params["target_pitch"]
        tolerance = tier_params["tolerance"]
        
        pitch_history = data.get("pitch_history", [])
        if not pitch_history:
            return {"score": 0.0, "time_in_tolerance": 0.0}
            
        # Count time within tolerance
        in_tolerance = 0
        for pitch in pitch_history:
            if pitch > 0 and abs(pitch - target_pitch) <= tolerance:
                in_tolerance += 1
                
        time_in_tolerance = (in_tolerance / len(pitch_history)) * 100
        score = min(100, time_in_tolerance)  # Cap at 100%
        
        return {
            "score": score,
            "time_in_tolerance": time_in_tolerance,
            "target_pitch": target_pitch,
            "tolerance": tolerance
        }
        
    def _score_pitch_deviation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score pitch glide exercise - mean deviation from target line."""
        tier_params = exercise.get_tier(tier).params
        
        pitch_history = data.get("pitch_history", [])
        time_stamps = data.get("time_stamps", [])
        
        if not pitch_history or len(pitch_history) < 2:
            return {"score": 0.0, "mean_deviation": float('inf')}
            
        # Generate target pitch line based on exercise parameters
        target_pitches = self._generate_target_line(exercise, tier_params, time_stamps)
        
        # Calculate mean deviation
        deviations = []
        for i, pitch in enumerate(pitch_history):
            if pitch > 0 and i < len(target_pitches):
                deviations.append(abs(pitch - target_pitches[i]))
                
        if not deviations:
            return {"score": 0.0, "mean_deviation": float('inf')}
            
        mean_deviation = np.mean(deviations)
        
        # Score based on how close to target (lower deviation = higher score)
        # Target deviation depends on tier
        target_deviation = tier_params.get("target_deviation", 15)
        score = max(0, 100 - (mean_deviation / target_deviation) * 100)
        
        return {
            "score": min(100, score),
            "mean_deviation": mean_deviation,
            "target_deviation": target_deviation
        }
        
    def _score_pitch_variance(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score variation reading exercise - pitch standard deviation."""
        tier_params = exercise.get_tier(tier).params
        target_variance = tier_params["target_variance"]
        
        pitch_history = data.get("pitch_history", [])
        voiced_pitches = [p for p in pitch_history if p > 0]
        
        if len(voiced_pitches) < 10:
            return {"score": 0.0, "pitch_variance": 0.0}
            
        pitch_variance = np.std(voiced_pitches)
        
        # Score based on how close to target variance
        variance_diff = abs(pitch_variance - target_variance)
        score = max(0, 100 - (variance_diff / target_variance) * 50)  # 50% penalty per target variance
        
        return {
            "score": min(100, score),
            "pitch_variance": pitch_variance,
            "target_variance": target_variance
        }
        
    def _score_pitch_correlation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score emotional contrast exercise - correlation to target envelope."""
        tier_params = exercise.get_tier(tier).params
        correlation_threshold = tier_params["correlation_threshold"]
        
        pitch_history = data.get("pitch_history", [])
        time_stamps = data.get("time_stamps", [])
        
        if not pitch_history or len(pitch_history) < 10:
            return {"score": 0.0, "correlation": 0.0}
            
        # Generate target envelope (would be based on emotion cues in real implementation)
        target_envelope = self._generate_emotional_envelope(exercise, tier_params, time_stamps)
        
        # Calculate correlation
        correlation = np.corrcoef(pitch_history, target_envelope)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
            
        # Score based on correlation
        score = max(0, correlation * 100)
        
        return {
            "score": min(100, score),
            "correlation": correlation,
            "threshold": correlation_threshold
        }
        
    def _score_pitch_range(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score range expansion exercise - range in Hz and semitones."""
        tier_params = exercise.get_tier(tier).params
        
        pitch_history = data.get("pitch_history", [])
        voiced_pitches = [p for p in pitch_history if p > 0]
        
        if len(voiced_pitches) < 10:
            return {"score": 0.0, "range_hz": 0.0, "range_semitones": 0.0}
            
        min_pitch = min(voiced_pitches)
        max_pitch = max(voiced_pitches)
        range_hz = max_pitch - min_pitch
        
        # Convert to semitones (logarithmic scale)
        range_semitones = 12 * np.log2(max_pitch / min_pitch) if min_pitch > 0 else 0
        
        # Score based on meeting expansion targets
        if "target_expansion_semitones" in tier_params:
            target_semitones = tier_params["target_expansion_semitones"]
            score = min(100, (range_semitones / target_semitones) * 100)
        else:
            # Measurement tier - score based on having reasonable range
            score = min(100, range_semitones * 2)  # 50 semitones = 100%
            
        return {
            "score": score,
            "range_hz": range_hz,
            "range_semitones": range_semitones,
            "min_pitch": min_pitch,
            "max_pitch": max_pitch
        }
        
    def _score_duration_stability(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score sustained tone exercise - duration + amplitude stability."""
        tier_params = exercise.get_tier(tier).params
        target_duration = tier_params["target_duration"]
        stability_threshold = tier_params["stability_threshold"]
        
        amplitude_history = data.get("amplitude_history", [])
        actual_duration = data.get("duration", 0.0)
        
        if not amplitude_history:
            return {"score": 0.0, "duration": 0.0, "stability": 0.0}
            
        # Calculate amplitude stability (coefficient of variation)
        voiced_amplitudes = [a for a in amplitude_history if a > -60]  # Above threshold
        if len(voiced_amplitudes) < 10:
            stability = 0.0
        else:
            stability = 1.0 - (np.std(voiced_amplitudes) / max(np.mean(voiced_amplitudes), 1e-10))
            stability = max(0, stability)
            
        # Duration score
        duration_score = min(100, (actual_duration / target_duration) * 100)
        
        # Stability score
        stability_score = min(100, (stability / stability_threshold) * 100)
        
        # Combined score (50% each)
        score = (duration_score + stability_score) / 2
        
        return {
            "score": score,
            "duration": actual_duration,
            "target_duration": target_duration,
            "stability": stability,
            "stability_threshold": stability_threshold
        }
        
    def _score_amplitude_cv(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score volume sustain exercise - amplitude coefficient of variation."""
        tier_params = exercise.get_tier(tier).params
        target_cv = tier_params["target_cv"]
        
        amplitude_history = data.get("amplitude_history", [])
        voiced_amplitudes = [a for a in amplitude_history if a > -60]
        
        if len(voiced_amplitudes) < 10:
            return {"score": 0.0, "cv": 1.0}
            
        # Calculate coefficient of variation
        mean_amp = np.mean(voiced_amplitudes)
        std_amp = np.std(voiced_amplitudes)
        cv = std_amp / max(mean_amp, 1e-10)
        
        # Lower CV is better
        score = max(0, 100 - (cv / target_cv) * 100)
        
        return {
            "score": min(100, score),
            "cv": cv,
            "target_cv": target_cv
        }
        
    def _score_wpm_deviation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score metronome pace exercise - WPM deviation from target."""
        tier_params = exercise.get_tier(tier).params
        target_wpm = tier_params["target_wpm"]
        deviation_threshold = tier_params["deviation_threshold"]
        
        actual_wpm = data.get("wpm", 0.0)
        
        if actual_wpm == 0.0:
            return {"score": 0.0, "wpm": 0.0, "deviation": target_wpm}
            
        deviation = abs(actual_wpm - target_wpm)
        score = max(0, 100 - (deviation / deviation_threshold) * 100)
        
        return {
            "score": min(100, score),
            "wpm": actual_wpm,
            "target_wpm": target_wpm,
            "deviation": deviation
        }
        
    def _score_dynamic_range(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score dynamic range finder exercise - range in dB."""
        tier_params = exercise.get_tier(tier).params
        target_range = tier_params["target_range_db"]
        
        amplitude_history = data.get("amplitude_history", [])
        if len(amplitude_history) < 10:
            return {"score": 0.0, "range_db": 0.0}
            
        min_db = min(amplitude_history)
        max_db = max(amplitude_history)
        range_db = max_db - min_db
        
        score = min(100, (range_db / target_range) * 100)
        
        return {
            "score": score,
            "range_db": range_db,
            "target_range": target_range,
            "min_db": min_db,
            "max_db": max_db
        }
        
    # Helper methods
    def _generate_target_line(self, exercise: Exercise, params: Dict[str, Any], time_stamps: List[float]) -> List[float]:
        """Generate target pitch line for glide exercises."""
        start_pitch = params.get("start_pitch", 150)
        end_pitch = params.get("end_pitch", 250)
        glide_duration = params.get("glide_duration", 5.0)
        
        if not time_stamps:
            return []
            
        target_pitches = []
        for t in time_stamps:
            if t < glide_duration:
                # Linear interpolation
                progress = t / glide_duration
                pitch = start_pitch + (end_pitch - start_pitch) * progress
            else:
                pitch = end_pitch
            target_pitches.append(pitch)
            
        return target_pitches
        
    def _generate_emotional_envelope(self, exercise: Exercise, params: Dict[str, Any], time_stamps: List[float]) -> List[float]:
        """Generate emotional pitch envelope for contrast exercises."""
        # Simplified implementation - would be more sophisticated in real app
        emotions = params.get("emotions", ["happy", "sad"])
        base_pitch = 200.0
        
        if not time_stamps:
            return []
            
        envelope = []
        emotion_duration = len(time_stamps) // len(emotions)
        
        for i, t in enumerate(time_stamps):
            emotion_idx = min(i // emotion_duration, len(emotions) - 1)
            emotion = emotions[emotion_idx]
            
            # Different pitch ranges for different emotions
            if emotion in ["happy", "excited"]:
                pitch = base_pitch + 50
            elif emotion in ["sad", "calm"]:
                pitch = base_pitch - 30
            elif emotion in ["angry", "fearful"]:
                pitch = base_pitch + 80
            else:
                pitch = base_pitch
                
            envelope.append(pitch)
            
        return envelope
