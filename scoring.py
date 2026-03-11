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
        
    def _score_sz_ratio(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score S/Z ratio exercise - ratio of sustained /s/ to /z/ duration."""
        tier_params = exercise.get_tier(tier).params
        target_range = tier_params.get("target_ratio_range", [0.8, 1.2])
        
        amplitude_history = data.get("amplitude_history", [])
        pitch_history = data.get("pitch_history", [])
        
        if len(amplitude_history) < 20:
            return {"score": 0.0, "ratio": 0.0}
        
        # Detect voiced (z) vs unvoiced (s) segments using pitch
        # Voiced segments have detectable pitch, unvoiced don't
        voiced_count = sum(1 for p in pitch_history if p > 0)
        unvoiced_count = len(pitch_history) - voiced_count
        
        if voiced_count == 0:
            return {"score": 0.0, "ratio": 0.0}
        
        ratio = unvoiced_count / voiced_count if voiced_count > 0 else 0
        
        # Score based on how close ratio is to target range
        low, high = target_range
        if low <= ratio <= high:
            score = 100.0
        else:
            distance = min(abs(ratio - low), abs(ratio - high))
            score = max(0, 100 - distance * 100)
        
        return {
            "score": min(100, score),
            "ratio": round(ratio, 2),
            "target_range": target_range
        }
    
    def _score_breath_ladder(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score breath ladder exercise - count distinct vocal bursts and consistency."""
        tier_params = exercise.get_tier(tier).params
        target_count = tier_params.get("target_count", 15)
        consistency_threshold = tier_params.get("volume_consistency", 0.4)
        
        amplitude_history = data.get("amplitude_history", [])
        
        if len(amplitude_history) < 20:
            return {"score": 0.0, "burst_count": 0, "consistency": 0.0}
        
        # Detect bursts: amplitude above threshold after being below
        amps = np.array(amplitude_history)
        threshold = np.mean(amps) * 0.6
        above = amps > threshold
        
        # Count transitions from below to above threshold (rising edges)
        burst_count = 0
        burst_peaks = []
        in_burst = False
        current_peak = 0
        for i, a in enumerate(above):
            if a and not in_burst:
                burst_count += 1
                in_burst = True
                current_peak = amps[i]
            elif a and in_burst:
                current_peak = max(current_peak, amps[i])
            elif not a and in_burst:
                burst_peaks.append(current_peak)
                in_burst = False
                current_peak = 0
        if in_burst:
            burst_peaks.append(current_peak)
        
        # Count score
        count_score = min(100, (burst_count / target_count) * 100)
        
        # Consistency score (low CV of burst peaks = consistent)
        if len(burst_peaks) >= 2:
            cv = np.std(burst_peaks) / max(np.mean(burst_peaks), 1e-10)
            consistency = max(0, 1.0 - cv)
            consistency_score = min(100, (consistency / consistency_threshold) * 100)
        else:
            consistency = 0.0
            consistency_score = 0.0
        
        score = (count_score + consistency_score) / 2
        
        return {
            "score": min(100, score),
            "burst_count": burst_count,
            "target_count": target_count,
            "consistency": round(consistency, 2)
        }
    
    def _score_amplitude_correlation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score crescendo/decrescendo - correlation of amplitude to target ramp."""
        tier_params = exercise.get_tier(tier).params
        shape = tier_params.get("shape", "linear_ramp")
        corr_threshold = tier_params.get("correlation_threshold", 0.7)
        
        amplitude_history = data.get("amplitude_history", [])
        
        if len(amplitude_history) < 10:
            return {"score": 0.0, "correlation": 0.0}
        
        amps = np.array(amplitude_history, dtype=float)
        n = len(amps)
        
        # Generate target shape
        if shape == "linear_ramp":
            target = np.linspace(0, 1, n)
        elif shape == "v_shape":
            half = n // 2
            target = np.concatenate([np.linspace(1, 0, half), np.linspace(0, 1, n - half)])
        elif shape == "inverted_v":
            half = n // 2
            target = np.concatenate([np.linspace(0, 1, half), np.linspace(1, 0, n - half)])
        else:
            target = np.linspace(0, 1, n)
        
        # Normalize amplitude to 0-1 range
        amp_min, amp_max = amps.min(), amps.max()
        if amp_max - amp_min > 1e-10:
            amps_norm = (amps - amp_min) / (amp_max - amp_min)
        else:
            return {"score": 0.0, "correlation": 0.0}
        
        correlation = float(np.corrcoef(amps_norm, target)[0, 1])
        if np.isnan(correlation):
            correlation = 0.0
        
        score = max(0, (correlation / corr_threshold) * 100)
        
        return {
            "score": min(100, score),
            "correlation": round(correlation, 3),
            "threshold": corr_threshold
        }
    
    def _score_wpm_deviation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score metronome pace exercise - WPM deviation from target."""
        tier_params = exercise.get_tier(tier).params
        target_wpm = tier_params["target_wpm"]
        deviation_threshold = tier_params["deviation_threshold"]
        
        # Use whisper transcription WPM if available, else fallback
        transcription = data.get("transcription", {})
        actual_wpm = transcription.get("wpm", 0.0) if transcription else data.get("wpm", 0.0)
        
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
    
    def _score_pause_accuracy(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score pause training - accuracy of intentional pauses."""
        tier_params = exercise.get_tier(tier).params
        target_pause_points = tier_params.get("pause_points", 3)
        unplanned_penalty = tier_params.get("unplanned_penalty", 5)
        
        transcription = data.get("transcription", {})
        pauses = transcription.get("pauses", []) if transcription else []
        
        if not transcription or transcription.get("error"):
            # Fallback: estimate pauses from amplitude
            return self._estimate_pause_score(data, target_pause_points)
        
        actual_pauses = len(pauses)
        
        # Score based on having approximately the right number of pauses
        if actual_pauses == 0:
            return {"score": 0.0, "pause_count": 0, "target": target_pause_points}
        
        # Closer to target count = better score
        count_diff = abs(actual_pauses - target_pause_points)
        count_score = max(0, 100 - count_diff * unplanned_penalty)
        
        # Bonus for consistent pause durations
        if len(pauses) >= 2:
            durations = [p["duration"] for p in pauses]
            cv = np.std(durations) / max(np.mean(durations), 1e-10)
            consistency_bonus = max(0, 20 * (1 - cv))
        else:
            consistency_bonus = 0
        
        score = min(100, count_score + consistency_bonus)
        avg_duration = transcription.get("avg_pause_duration", 0)
        
        return {
            "score": score,
            "pause_count": actual_pauses,
            "target": target_pause_points,
            "avg_pause_duration": avg_duration
        }
    
    def _score_tempo_accuracy(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score rate shifting - ability to match different speaking tempos."""
        tier_params = exercise.get_tier(tier).params
        target_tempos = tier_params.get("tempos", [120, 150])
        accuracy_threshold = tier_params.get("accuracy_threshold", 0.7)
        
        transcription = data.get("transcription", {})
        
        if not transcription or transcription.get("error"):
            return {"score": 0.0, "measured_wpm": 0.0}
        
        words = transcription.get("words", [])
        if len(words) < 5:
            return {"score": 0.0, "measured_wpm": 0.0}
        
        # Split recording into segments and measure WPM per segment
        total_duration = transcription.get("duration", 1)
        segment_count = len(target_tempos)
        segment_duration = total_duration / segment_count
        
        segment_wpms = []
        for i in range(segment_count):
            seg_start = i * segment_duration
            seg_end = (i + 1) * segment_duration
            seg_words = [w for w in words if seg_start <= w.get("start", 0) < seg_end]
            seg_wpm = (len(seg_words) / segment_duration * 60) if segment_duration > 0 else 0
            segment_wpms.append(seg_wpm)
        
        # Score each segment's deviation from target tempo
        segment_scores = []
        for measured, target in zip(segment_wpms, target_tempos):
            if target > 0:
                accuracy = 1.0 - abs(measured - target) / target
                segment_scores.append(max(0, accuracy))
        
        if not segment_scores:
            return {"score": 0.0, "measured_wpm": 0.0}
        
        avg_accuracy = np.mean(segment_scores)
        score = min(100, (avg_accuracy / accuracy_threshold) * 100)
        
        return {
            "score": score,
            "segment_wpms": [round(w, 1) for w in segment_wpms],
            "target_tempos": target_tempos,
            "accuracy": round(avg_accuracy, 2)
        }
    
    def _score_silence_composite(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score silence ratio - balance of speech vs silence in delivery."""
        tier_params = exercise.get_tier(tier).params
        talk_ratio_range = tier_params.get("talk_ratio_range", [0.7, 0.8])
        pause_count_range = tier_params.get("pause_count_range", [3, 8])
        
        transcription = data.get("transcription", {})
        
        if not transcription or transcription.get("error"):
            # Fallback: use amplitude to estimate talk ratio
            return self._estimate_silence_score(data, talk_ratio_range, pause_count_range)
        
        total_duration = transcription.get("duration", 0)
        pauses = transcription.get("pauses", [])
        
        if total_duration == 0:
            return {"score": 0.0, "talk_ratio": 0.0, "pause_count": 0}
        
        silence_duration = sum(p["duration"] for p in pauses)
        talk_duration = total_duration - silence_duration
        talk_ratio = talk_duration / total_duration
        pause_count = len(pauses)
        
        # Score talk ratio
        low, high = talk_ratio_range
        if low <= talk_ratio <= high:
            ratio_score = 100
        else:
            distance = min(abs(talk_ratio - low), abs(talk_ratio - high))
            ratio_score = max(0, 100 - distance * 200)
        
        # Score pause count
        plow, phigh = pause_count_range
        if plow <= pause_count <= phigh:
            count_score = 100
        else:
            distance = min(abs(pause_count - plow), abs(pause_count - phigh))
            count_score = max(0, 100 - distance * 15)
        
        score = (ratio_score + count_score) / 2
        
        return {
            "score": min(100, score),
            "talk_ratio": round(talk_ratio, 2),
            "target_talk_ratio": talk_ratio_range,
            "pause_count": pause_count,
            "target_pause_count": pause_count_range
        }
    
    def _score_rhythm_correlation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score cadence lock - consistency of word-to-word timing."""
        tier_params = exercise.get_tier(tier).params
        corr_threshold = tier_params.get("correlation_threshold", 0.6)
        
        transcription = data.get("transcription", {})
        
        if not transcription or transcription.get("error"):
            return {"score": 0.0, "rhythm_score": 0.0}
        
        words = transcription.get("words", [])
        if len(words) < 5:
            return {"score": 0.0, "rhythm_score": 0.0}
        
        # Calculate inter-word intervals
        intervals = []
        for i in range(1, len(words)):
            gap = words[i].get("start", 0) - words[i-1].get("end", 0)
            intervals.append(max(0, gap))
        
        if len(intervals) < 3:
            return {"score": 0.0, "rhythm_score": 0.0}
        
        intervals = np.array(intervals)
        
        # Rhythm = low coefficient of variation of intervals (steady = rhythmic)
        mean_interval = np.mean(intervals)
        if mean_interval < 1e-10:
            return {"score": 0.0, "rhythm_score": 0.0}
        
        cv = float(np.std(intervals) / mean_interval)
        rhythm_score = max(0, 1.0 - cv)
        
        score = min(100, (rhythm_score / corr_threshold) * 100)
        
        return {
            "score": score,
            "rhythm_score": round(rhythm_score, 3),
            "interval_cv": round(cv, 3),
            "threshold": corr_threshold
        }
    
    def _score_emphasis_accuracy(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score emphasis drill - amplitude peaks at emphasis points."""
        tier_params = exercise.get_tier(tier).params
        accuracy_threshold = tier_params.get("accuracy_threshold", 0.7)
        
        amplitude_history = data.get("amplitude_history", [])
        
        if len(amplitude_history) < 20:
            return {"score": 0.0, "emphasis_ratio": 0.0}
        
        amps = np.array(amplitude_history, dtype=float)
        
        # Detect emphasis: peaks significantly above local average
        window = max(5, len(amps) // 10)
        local_means = np.convolve(amps, np.ones(window)/window, mode='same')
        
        # Count significant peaks (above 1.3x local average)
        peaks = amps > (local_means * 1.3)
        peak_count = 0
        in_peak = False
        for p in peaks:
            if p and not in_peak:
                peak_count += 1
                in_peak = True
            elif not p:
                in_peak = False
        
        # Amplitude dynamic range during exercise
        amp_range = float(np.max(amps) - np.min(amps))
        
        # Score: having clear emphasis points (peaks) with good dynamic separation
        emphasis_ratio = amp_range / max(float(np.mean(amps)), 1e-10)
        score = min(100, (emphasis_ratio / (1.0 / accuracy_threshold)) * 100)
        
        return {
            "score": score,
            "peak_count": peak_count,
            "emphasis_ratio": round(emphasis_ratio, 2),
            "dynamic_range": round(amp_range, 2)
        }
    
    def _score_projection_scaling(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score projection scaling - ability to increase volume in steps."""
        tier_params = exercise.get_tier(tier).params
        db_separation = tier_params.get("db_separation", 10)
        
        amplitude_history = data.get("amplitude_history", [])
        
        if len(amplitude_history) < 20:
            return {"score": 0.0, "measured_separation": 0.0}
        
        amps = np.array(amplitude_history, dtype=float)
        
        # Split into two halves (near vs far projection)
        half = len(amps) // 2
        first_half = amps[:half]
        second_half = amps[half:]
        
        mean_first = float(np.mean(first_half))
        mean_second = float(np.mean(second_half))
        
        measured_separation = abs(mean_second - mean_first)
        
        # Score based on achieving target dB separation
        score = min(100, (measured_separation / db_separation) * 100)
        
        return {
            "score": score,
            "measured_separation": round(measured_separation, 1),
            "target_separation": db_separation,
            "quiet_level": round(mean_first, 1),
            "loud_level": round(mean_second, 1)
        }
    
    def _score_volume_correlation(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score volume contouring - correlation of amplitude to target contour."""
        tier_params = exercise.get_tier(tier).params
        contour_type = tier_params.get("contour_type", "simple_ramp")
        corr_threshold = tier_params.get("correlation_threshold", 0.7)
        
        amplitude_history = data.get("amplitude_history", [])
        
        if len(amplitude_history) < 10:
            return {"score": 0.0, "correlation": 0.0}
        
        amps = np.array(amplitude_history, dtype=float)
        n = len(amps)
        
        # Generate target contour
        if contour_type == "simple_ramp":
            target = np.linspace(0, 1, n)
        elif contour_type == "wave":
            target = (np.sin(np.linspace(0, 2 * np.pi, n)) + 1) / 2
        elif contour_type == "staircase":
            steps = 4
            target = np.repeat(np.linspace(0.2, 1.0, steps), n // steps + 1)[:n]
        else:
            target = np.linspace(0, 1, n)
        
        # Normalize amplitude
        amp_min, amp_max = amps.min(), amps.max()
        if amp_max - amp_min > 1e-10:
            amps_norm = (amps - amp_min) / (amp_max - amp_min)
        else:
            return {"score": 0.0, "correlation": 0.0}
        
        correlation = float(np.corrcoef(amps_norm, target)[0, 1])
        if np.isnan(correlation):
            correlation = 0.0
        
        score = max(0, min(100, (correlation / corr_threshold) * 100))
        
        return {
            "score": score,
            "correlation": round(correlation, 3),
            "contour_type": contour_type,
            "threshold": corr_threshold
        }
    
    def _score_centroid_tracking(self, exercise: Exercise, data: Dict[str, Any], tier: str) -> Dict[str, float]:
        """Score brightness tracker - spectral centroid stability and range."""
        tier_params = exercise.get_tier(tier).params
        
        centroid_history = data.get("centroid_history", [])
        
        if len(centroid_history) < 10:
            # Fallback to amplitude-based approximation
            amplitude_history = data.get("amplitude_history", [])
            if len(amplitude_history) < 10:
                return {"score": 0.0, "centroid_mean": 0.0, "centroid_range": 0.0}
            # Approximate brightness from amplitude variation
            amps = np.array(amplitude_history, dtype=float)
            score = min(100, float(np.std(amps)) * 10)
            return {"score": score, "centroid_mean": 0.0, "centroid_range": 0.0, "note": "estimated from amplitude"}
        
        centroids = np.array(centroid_history, dtype=float)
        valid = centroids[centroids > 0]
        
        if len(valid) < 5:
            return {"score": 0.0, "centroid_mean": 0.0, "centroid_range": 0.0}
        
        centroid_mean = float(np.mean(valid))
        centroid_range = float(np.max(valid) - np.min(valid))
        centroid_std = float(np.std(valid))
        
        # Score: ability to produce a range of brightness (higher range = more control)
        # Typical centroid range for voice: 500-4000 Hz
        range_score = min(100, (centroid_range / 1000) * 100)
        
        # Bonus for stability when sustaining (low std relative to mean)
        stability = max(0, 1.0 - centroid_std / max(centroid_mean, 1))
        stability_score = stability * 50
        
        score = min(100, (range_score + stability_score) / 1.5)
        
        return {
            "score": score,
            "centroid_mean": round(centroid_mean, 1),
            "centroid_range": round(centroid_range, 1),
            "centroid_std": round(centroid_std, 1)
        }
    
    def _estimate_pause_score(self, data: Dict[str, Any], target_pauses: int) -> Dict[str, float]:
        """Fallback pause scoring from amplitude data when whisper unavailable."""
        amplitude_history = data.get("amplitude_history", [])
        if len(amplitude_history) < 20:
            return {"score": 0.0, "pause_count": 0, "target": target_pauses, "note": "estimated"}
        
        amps = np.array(amplitude_history, dtype=float)
        threshold = np.mean(amps) * 0.3
        silent = amps < threshold
        
        # Count silence segments
        pause_count = 0
        in_silence = False
        for s in silent:
            if s and not in_silence:
                pause_count += 1
                in_silence = True
            elif not s:
                in_silence = False
        
        diff = abs(pause_count - target_pauses)
        score = max(0, 100 - diff * 15)
        return {"score": score, "pause_count": pause_count, "target": target_pauses, "note": "estimated from amplitude"}
    
    def _estimate_silence_score(self, data: Dict[str, Any], talk_ratio_range: list, pause_count_range: list) -> Dict[str, float]:
        """Fallback silence ratio scoring from amplitude data."""
        amplitude_history = data.get("amplitude_history", [])
        if len(amplitude_history) < 20:
            return {"score": 0.0, "talk_ratio": 0.0, "pause_count": 0, "note": "estimated"}
        
        amps = np.array(amplitude_history, dtype=float)
        threshold = np.mean(amps) * 0.3
        voiced = amps > threshold
        talk_ratio = float(np.sum(voiced)) / len(voiced)
        
        low, high = talk_ratio_range
        if low <= talk_ratio <= high:
            score = 80.0  # Good but capped since estimated
        else:
            distance = min(abs(talk_ratio - low), abs(talk_ratio - high))
            score = max(0, 80 - distance * 200)
        
        return {"score": score, "talk_ratio": round(talk_ratio, 2), "pause_count": 0, "note": "estimated from amplitude"}
    
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
