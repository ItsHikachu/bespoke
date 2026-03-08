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
