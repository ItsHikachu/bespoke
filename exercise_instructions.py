"""
Exercise-specific instructions and guidance for practice sessions.
"""

from typing import Dict, List


class ExerciseInstructions:
    """Provides phase-aware instructions for each exercise."""
    
    @staticmethod
    def get_instructions(exercise_id: str, tier: str, phase: str = "ready") -> str:
        """
        Get instructions for a specific exercise, tier, and phase.
        
        Args:
            exercise_id: Exercise ID (e.g., "1a", "1b")
            tier: Tier name ("foundation", "intermediate", "advanced")
            phase: Current phase ("ready", "recording", "completed")
        
        Returns:
            Instruction text to display
        """
        instructions_map = {
            "1a": ExerciseInstructions._get_1a_instructions,
            "1b": ExerciseInstructions._get_1b_instructions,
            "1c": ExerciseInstructions._get_1c_instructions,
            "1d": ExerciseInstructions._get_1d_instructions,
            "1e": ExerciseInstructions._get_1e_instructions,
            "2a": ExerciseInstructions._get_2a_instructions,
            "2b": ExerciseInstructions._get_2b_instructions,
            "2c": ExerciseInstructions._get_2c_instructions,
            "2d": ExerciseInstructions._get_2d_instructions,
            "2e": ExerciseInstructions._get_2e_instructions,
            "3a": ExerciseInstructions._get_3a_instructions,
            "3b": ExerciseInstructions._get_3b_instructions,
            "3c": ExerciseInstructions._get_3c_instructions,
            "3d": ExerciseInstructions._get_3d_instructions,
            "3e": ExerciseInstructions._get_3e_instructions,
            "4a": ExerciseInstructions._get_4a_instructions,
            "4b": ExerciseInstructions._get_4b_instructions,
            "4c": ExerciseInstructions._get_4c_instructions,
            "4d": ExerciseInstructions._get_4d_instructions,
            "4e": ExerciseInstructions._get_4e_instructions,
        }
        
        if exercise_id in instructions_map:
            return instructions_map[exercise_id](tier, phase)
        else:
            return f"Exercise {exercise_id} - {phase.title()}"
    
    @staticmethod
    def _get_1a_instructions(tier: str, phase: str) -> str:
        """Pitch Hold instructions."""
        if phase == "ready":
            return "Hold a steady pitch at 200 Hz. Try to stay within the tolerance band shown on the graph."
        elif phase == "recording":
            target_hz = 200
            tolerance_map = {"foundation": 30, "intermediate": 15, "advanced": 8}
            tolerance = tolerance_map.get(tier, 30)
            return f"Hold steady at {target_hz} Hz (±{tolerance} Hz tolerance). Keep your pitch within the highlighted band."
        else:
            return "Exercise complete! Review your score below."
    
    @staticmethod
    def _get_1b_instructions(tier: str, phase: str) -> str:
        """Pitch Glide instructions."""
        if phase == "ready":
            return "Smoothly glide your pitch from low to high following the target line."
        elif phase == "recording":
            if tier == "foundation":
                return "Glide slowly from 150 Hz to 250 Hz over 5 seconds. Follow the orange target line."
            elif tier == "intermediate":
                return "Glide from 150 Hz to 250 Hz in 3 seconds, then back down. Match the target pattern."
            else:
                return "Follow the zigzag pattern. Quick transitions, smooth glides. Stay close to the target."
        else:
            return "Exercise complete! Check your mean deviation from the target line."
    
    @staticmethod
    def _get_1c_instructions(tier: str, phase: str) -> str:
        """Variation Reading instructions."""
        if phase == "ready":
            return "Read the passage with natural pitch variation. Avoid monotone delivery."
        elif phase == "recording":
            if tier == "foundation":
                return "Read these short sentences with expression. Vary your pitch naturally."
            elif tier == "intermediate":
                return "Read this paragraph with natural intonation. Use pitch to convey meaning."
            else:
                return "Read with emotional shifts. Let your pitch reflect the changing mood of the passage."
        else:
            return "Exercise complete! Your pitch variation score is shown below."
    
    @staticmethod
    def _get_1d_instructions(tier: str, phase: str) -> str:
        """Emotional Contrast instructions."""
        if phase == "ready":
            return "Express different emotions through pitch changes. Match the target emotional contours."
        elif phase == "recording":
            if tier == "foundation":
                return "Switch between HAPPY (high pitch) and SAD (low pitch). Make the contrast clear."
            elif tier == "intermediate":
                return "Express 4 emotions: Happy → Sad → Angry → Calm. Use pitch to convey each emotion."
            else:
                return "Cycle through 6 emotions with clear pitch patterns. Match the target envelope closely."
        else:
            return "Exercise complete! Check your emotional pitch correlation score."
    
    @staticmethod
    def _get_1e_instructions(tier: str, phase: str) -> str:
        """Range Expansion instructions."""
        if phase == "ready":
            return "Explore your full vocal range from lowest to highest comfortable pitch."
        elif phase == "recording":
            if tier == "foundation":
                return "Slide from your lowest comfortable pitch to your highest. We'll measure your current range."
            elif tier == "intermediate":
                return "Expand your range by 2 semitones beyond your baseline. Push gently at both ends."
            else:
                return "Target 4+ semitones expansion. Slide smoothly through your full extended range."
        else:
            return "Exercise complete! Your vocal range is displayed below."

    @staticmethod
    def _get_2a_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Sustain a steady tone for as long as possible with consistent volume."
        elif phase == "recording":
            targets = {"foundation": 10, "intermediate": 20, "advanced": 30}
            return f"Hold a steady tone for {targets.get(tier, 10)} seconds. Keep amplitude stable."
        return "Exercise complete! Check your sustain duration and stability score."

    @staticmethod
    def _get_2b_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Measure breath control by comparing 'S' and 'Z' sound durations."
        elif phase == "recording":
            return "Say 'SSSS' for as long as possible, then 'ZZZZ' for as long as possible. Healthy ratio is 0.8-1.2."
        return "Exercise complete! Check your S/Z ratio."

    @staticmethod
    def _get_2c_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Count upward on a single breath, maintaining consistent volume."
        elif phase == "recording":
            targets = {"foundation": 15, "intermediate": 25, "advanced": 35}
            return f"Count: 1, 2, 3... on one breath. Target: {targets.get(tier, 15)} numbers with steady volume."
        return "Exercise complete! Check how far you counted."

    @staticmethod
    def _get_2d_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Read while maintaining consistent volume throughout."
        elif phase == "recording":
            return "Read the passage with steady, consistent volume. Avoid volume drops or spikes."
        return "Exercise complete! Check your volume consistency score."

    @staticmethod
    def _get_2e_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Smoothly increase and decrease volume following the target pattern."
        elif phase == "recording":
            return "Follow the volume contour shown. Crescendo (get louder) and decrescendo (get quieter) smoothly."
        return "Exercise complete! Check how well you matched the target shape."

    @staticmethod
    def _get_3a_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Speak at a consistent target pace measured in words per minute."
        elif phase == "recording":
            targets = {"foundation": 130, "intermediate": 150, "advanced": "alternating"}
            return f"Speak at {targets.get(tier, 130)} WPM. Match the metronome pace shown."
        return "Exercise complete! Check your WPM accuracy."

    @staticmethod
    def _get_3b_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Practice controlled pauses at marked points in the text."
        elif phase == "recording":
            return "Read the passage. Pause at marked points (|). Avoid unplanned pauses."
        return "Exercise complete! Check your pause accuracy."

    @staticmethod
    def _get_3c_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Shift between different speaking rates on cue."
        elif phase == "recording":
            return "Follow the tempo changes. Speed up and slow down as indicated."
        return "Exercise complete! Check your tempo accuracy."

    @staticmethod
    def _get_3d_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Balance speaking time and silence for optimal pacing."
        elif phase == "recording":
            return "Speak naturally with appropriate pauses. Target 70-80% talk time, rest silence."
        return "Exercise complete! Check your talk/silence ratio."

    @staticmethod
    def _get_3e_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Lock into a rhythmic speaking pattern with consistent syllable timing."
        elif phase == "recording":
            return "Speak with rhythmic cadence. Match the beat pattern shown."
        return "Exercise complete! Check your rhythm correlation."

    @staticmethod
    def _get_4a_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Explore your full dynamic range from quietest to loudest comfortable volume."
        elif phase == "recording":
            targets = {"foundation": 15, "intermediate": 20, "advanced": 25}
            return f"Speak from very quiet to very loud. Target range: {targets.get(tier, 15)} dB."
        return "Exercise complete! Check your dynamic range."

    @staticmethod
    def _get_4b_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Place vocal emphasis on specific words for meaning and impact."
        elif phase == "recording":
            return "Read the passage. EMPHASIZE the marked words with increased volume."
        return "Exercise complete! Check your emphasis accuracy."

    @staticmethod
    def _get_4c_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Adjust volume for different projection distances."
        elif phase == "recording":
            return "Speak as if addressing: close (3ft), medium (15ft), far (50ft). Clear volume steps."
        return "Exercise complete! Check your projection scaling."

    @staticmethod
    def _get_4d_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Follow a dynamic volume pattern that creates emotional impact."
        elif phase == "recording":
            return "Match the volume contour shown. Build and release tension through dynamics."
        return "Exercise complete! Check your volume correlation."

    @staticmethod
    def _get_4e_instructions(tier: str, phase: str) -> str:
        if phase == "ready":
            return "Control vocal brightness through resonance and articulation."
        elif phase == "recording":
            if tier == "foundation":
                return "Speak naturally. We'll measure your baseline brightness."
            else:
                return "Speak with brighter tone quality. Increase spectral centroid above baseline."
        return "Exercise complete! Check your brightness tracking."


class ExerciseContent:
    """Provides reading passages and prompts for exercises."""
    
    @staticmethod
    def get_reading_text(exercise_id: str, tier: str) -> str:
        """Get reading passage for variation/contrast exercises."""
        
        if exercise_id == "1c":  # Variation Reading
            if tier == "foundation":
                return """The sun rises in the east.
Birds sing in the morning.
Coffee smells wonderful.
Rain falls gently outside."""
            elif tier == "intermediate":
                return """Voice training requires patience and consistent practice. Each session builds upon previous work, gradually improving control and confidence. The key is regular, focused effort rather than occasional intense practice. Small improvements compound over time into significant gains."""
            else:
                return """Excitement builds as the moment approaches! Hearts race with anticipation, pulses quickening with each passing second. Then suddenly... calm descends like a gentle blanket, soft and reassuring. The contrast between these states creates powerful emotional resonance, a dance between tension and release that captivates and moves us."""
        
        elif exercise_id == "1d":  # Emotional Contrast
            if tier == "foundation":
                return """HAPPY: What a wonderful day this is!
SAD: Everything feels heavy and gray."""
            elif tier == "intermediate":
                return """HAPPY: I can't believe we won! This is amazing!
SAD: Nothing seems to matter anymore.
ANGRY: This is completely unacceptable!
CALM: Let's take a deep breath and think clearly."""
            else:
                return """HAPPY: Pure joy fills every moment!
SAD: Darkness surrounds everything now.
ANGRY: How dare they treat us this way!
CALM: Peace flows through like a gentle stream.
EXCITED: We're about to make history!
FEARFUL: What if everything falls apart?"""
        
        return ""
    
    @staticmethod
    def get_emotional_cues(tier: str) -> List[str]:
        """Get list of emotions for emotional contrast exercise."""
        if tier == "foundation":
            return ["happy", "sad"]
        elif tier == "intermediate":
            return ["happy", "sad", "angry", "calm"]
        else:
            return ["happy", "sad", "angry", "calm", "excited", "fearful"]
