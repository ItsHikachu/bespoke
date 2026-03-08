from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ExerciseTier:
    """Parameters for an exercise tier."""
    name: str
    params: Dict[str, Any]


@dataclass
class Exercise:
    """Exercise definition with all tiers."""
    id: str
    name: str
    module: int
    duration: int  # seconds
    description: str
    scoring_type: str
    visualizer: str
    uses_whisper: bool = False
    foundation: ExerciseTier = None
    intermediate: ExerciseTier = None
    advanced: ExerciseTier = None
    
    def get_tier(self, tier: str) -> ExerciseTier:
        """Get tier parameters."""
        tier_map = {
            'foundation': self.foundation,
            'intermediate': self.intermediate,
            'advanced': self.advanced
        }
        return tier_map.get(tier, self.foundation)


# Module 1: Pitch Control (visualizer: pitch_graph)
EXERCISE_1A = Exercise(
    id="1a",
    name="Pitch Hold",
    module=1,
    duration=60,
    description="Hold a steady pitch within a tolerance band",
    scoring_type="pitch_tolerance",
    visualizer="pitch_graph",
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_pitch": 200, "tolerance": 30}
    ),
    intermediate=ExerciseTier(
        name="Intermediate", 
        params={"target_pitch": 200, "tolerance": 15}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"target_pitch": 200, "tolerance": 8}
    )
)

EXERCISE_1B = Exercise(
    id="1b",
    name="Pitch Glide",
    module=1,
    duration=45,
    description="Glide pitch smoothly between targets",
    scoring_type="pitch_deviation",
    visualizer="pitch_graph",
    foundation=ExerciseTier(
        name="Foundation",
        params={"start_pitch": 150, "end_pitch": 250, "glide_duration": 5}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"start_pitch": 150, "end_pitch": 250, "glide_duration": 3, "include_descend": True}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"zigzag_pattern": True, "target_deviation": 10}
    )
)

EXERCISE_1C = Exercise(
    id="1c",
    name="Variation Reading",
    module=1,
    duration=60,
    description="Read with natural pitch variation",
    scoring_type="pitch_variance",
    visualizer="pitch_graph",
    foundation=ExerciseTier(
        name="Foundation",
        params={"text_type": "short_sentences", "target_variance": 40}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"text_type": "paragraphs", "target_variance": 50}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"text_type": "emotional_passages", "target_variance": 60}
    )
)

EXERCISE_1D = Exercise(
    id="1d",
    name="Emotional Contrast",
    module=1,
    duration=60,
    description="Express different emotions through pitch",
    scoring_type="pitch_correlation",
    visualizer="pitch_graph",
    foundation=ExerciseTier(
        name="Foundation",
        params={"emotions": ["happy", "sad"], "correlation_threshold": 0.6}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"emotions": ["happy", "sad", "angry", "calm"], "correlation_threshold": 0.7}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"emotions": ["happy", "sad", "angry", "calm", "excited", "fearful"], "correlation_threshold": 0.8}
    )
)

EXERCISE_1E = Exercise(
    id="1e",
    name="Range Expansion",
    module=1,
    duration=45,
    description="Expand your vocal range",
    scoring_type="pitch_range",
    visualizer="pitch_graph",
    foundation=ExerciseTier(
        name="Foundation",
        params={"measure_current": True, "target_expansion": 0}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"target_expansion_semitones": 2}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"target_expansion_semitones": 4}
    )
)

# Module 2: Breath & Sustain (visualizer: amplitude_bar + amplitude_envelope)
EXERCISE_2A = Exercise(
    id="2a",
    name="Sustained Tone",
    module=2,
    duration=45,
    description="Maintain a steady tone",
    scoring_type="duration_stability",
    visualizer="amplitude_bar",
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_duration": 10, "stability_threshold": 0.3}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"target_duration": 20, "stability_threshold": 0.2}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"target_duration": 30, "stability_threshold": 0.15}
    )
)

EXERCISE_2B = Exercise(
    id="2b",
    name="S/Z Ratio",
    module=2,
    duration=30,
    description="Measure breath control through s/z sounds",
    scoring_type="sz_ratio",
    visualizer="amplitude_bar",
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_ratio_range": [0.8, 1.2]}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"consistency_trials": 3, "target_ratio_range": [0.8, 1.2]}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"consistency_trials": 5, "target_ratio_range": [0.9, 1.1]}
    )
)

EXERCISE_2C = Exercise(
    id="2c",
    name="Breath Ladder",
    module=2,
    duration=60,
    description="Count with increasing breath control",
    scoring_type="breath_ladder",
    visualizer="amplitude_bar",
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_count": 15, "volume_consistency": 0.4}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"target_count": 25, "volume_consistency": 0.3}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"target_count": 35, "volume_consistency": 0.2}
    )
)

EXERCISE_2D = Exercise(
    id="2d",
    name="Volume Sustain",
    module=2,
    duration=60,
    description="Maintain consistent volume while speaking",
    scoring_type="amplitude_cv",
    visualizer="amplitude_envelope",
    foundation=ExerciseTier(
        name="Foundation",
        params={"text_type": "short_sentence", "target_cv": 0.3}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"text_type": "paragraph", "target_cv": 0.25}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"text_type": "passage", "target_cv": 0.2}
    )
)

EXERCISE_2E = Exercise(
    id="2e",
    name="Crescendo/Decrescendo",
    module=2,
    duration=45,
    description="Control volume changes smoothly",
    scoring_type="amplitude_correlation",
    visualizer="amplitude_envelope",
    foundation=ExerciseTier(
        name="Foundation",
        params={"shape": "linear_ramp", "correlation_threshold": 0.7}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"shape": "steep_ramp", "correlation_threshold": 0.8}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"shape": "complex_curves", "correlation_threshold": 0.85}
    )
)

# Module 3: Pace & Rhythm (visualizer: wpm_gauge, post-exercise: uses_whisper: true)
EXERCISE_3A = Exercise(
    id="3a",
    name="Metronome Pace",
    module=3,
    duration=60,
    description="Speak at a steady target pace",
    scoring_type="wpm_deviation",
    visualizer="wpm_gauge",
    uses_whisper=True,
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_wpm": 130, "deviation_threshold": 15}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"target_wpm": 150, "deviation_threshold": 10}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"alternating_wpm": [120, 160], "deviation_threshold": 8}
    )
)

EXERCISE_3B = Exercise(
    id="3b",
    name="Pause Training",
    module=3,
    duration=60,
    description="Control pauses in speech",
    scoring_type="pause_accuracy",
    visualizer="wpm_gauge",
    uses_whisper=True,
    foundation=ExerciseTier(
        name="Foundation",
        params={"pause_points": 3, "unplanned_penalty": 5}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"pause_points": 6, "unplanned_penalty": 3}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"pause_points": 10, "unplanned_penalty": 2}
    )
)

EXERCISE_3C = Exercise(
    id="3c",
    name="Rate Shifting",
    module=3,
    duration=60,
    description="Shift between different speaking rates",
    scoring_type="tempo_accuracy",
    visualizer="wpm_gauge",
    uses_whisper=True,
    foundation=ExerciseTier(
        name="Foundation",
        params={"tempos": [120, 150], "accuracy_threshold": 0.7}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"tempos": [120, 150, 180], "accuracy_threshold": 0.8}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"rapid_alternation": True, "accuracy_threshold": 0.85}
    )
)

EXERCISE_3D = Exercise(
    id="3d",
    name="Silence Ratio",
    module=3,
    duration=60,
    description="Balance speech and silence",
    scoring_type="silence_composite",
    visualizer="wpm_gauge",
    uses_whisper=True,
    foundation=ExerciseTier(
        name="Foundation",
        params={"talk_ratio_range": [0.7, 0.8], "pause_count_range": [3, 8]}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"talk_ratio_range": [0.75, 0.85], "pause_count_range": [4, 10]}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"talk_ratio_range": [0.75, 0.85], "pause_count_range": [4, 10], "filler_penalty": True}
    )
)

EXERCISE_3E = Exercise(
    id="3e",
    name="Cadence Lock",
    module=3,
    duration=45,
    description="Maintain rhythmic speech patterns",
    scoring_type="rhythm_correlation",
    visualizer="wpm_gauge",
    uses_whisper=True,
    foundation=ExerciseTier(
        name="Foundation",
        params={"beat_pattern": "steady", "correlation_threshold": 0.6}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"beat_pattern": "two_beat", "correlation_threshold": 0.7}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"beat_pattern": "syncopated", "correlation_threshold": 0.8}
    )
)

# Module 4: Dynamics & Projection (visualizer: db_meter + centroid_bar)
EXERCISE_4A = Exercise(
    id="4a",
    name="Dynamic Range Finder",
    module=4,
    duration=30,
    description="Measure your dynamic range",
    scoring_type="dynamic_range",
    visualizer="db_meter",
    foundation=ExerciseTier(
        name="Foundation",
        params={"target_range_db": 15}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"target_range_db": 20}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"target_range_db": 25}
    )
)

EXERCISE_4B = Exercise(
    id="4b",
    name="Emphasis Drill",
    module=4,
    duration=60,
    description="Place emphasis correctly in sentences",
    scoring_type="emphasis_accuracy",
    visualizer="db_meter",
    foundation=ExerciseTier(
        name="Foundation",
        params={"emphasis_type": "obvious_words", "accuracy_threshold": 0.7}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"emphasis_type": "subtle_words", "accuracy_threshold": 0.8}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"emphasis_type": "multi_word_deemphasis", "accuracy_threshold": 0.85}
    )
)

EXERCISE_4C = Exercise(
    id="4c",
    name="Projection Scaling",
    module=4,
    duration=45,
    description="Adjust volume for different distances",
    scoring_type="projection_scaling",
    visualizer="db_meter",
    foundation=ExerciseTier(
        name="Foundation",
        params={"distances": ["3ft", "15ft"], "db_separation": 10}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"distances": ["3ft", "15ft", "50ft"], "db_separation": 12}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"distances": ["3ft", "15ft", "50ft"], "db_separation": 15, "centroid_check": True}
    )
)

EXERCISE_4D = Exercise(
    id="4d",
    name="Volume Contouring",
    module=4,
    duration=60,
    description="Follow volume patterns dynamically",
    scoring_type="volume_correlation",
    visualizer="db_meter",
    foundation=ExerciseTier(
        name="Foundation",
        params={"contour_type": "simple_ramp", "correlation_threshold": 0.7}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"contour_type": "two_peaks", "correlation_threshold": 0.8}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"contour_type": "emotional_arc", "correlation_threshold": 0.85}
    )
)

EXERCISE_4E = Exercise(
    id="4e",
    name="Brightness Tracker",
    module=4,
    duration=45,
    description="Control vocal brightness through spectral content",
    scoring_type="centroid_tracking",
    visualizer="centroid_bar",
    foundation=ExerciseTier(
        name="Foundation",
        params={"measure_baseline": True}
    ),
    intermediate=ExerciseTier(
        name="Intermediate",
        params={"maintain_above_baseline": True}
    ),
    advanced=ExerciseTier(
        name="Advanced",
        params={"improvement_target": 0.1}  # 10% improvement
    )
)


# Exercise database
ALL_EXERCISES = {
    "1a": EXERCISE_1A,
    "1b": EXERCISE_1B,
    "1c": EXERCISE_1C,
    "1d": EXERCISE_1D,
    "1e": EXERCISE_1E,
    "2a": EXERCISE_2A,
    "2b": EXERCISE_2B,
    "2c": EXERCISE_2C,
    "2d": EXERCISE_2D,
    "2e": EXERCISE_2E,
    "3a": EXERCISE_3A,
    "3b": EXERCISE_3B,
    "3c": EXERCISE_3C,
    "3d": EXERCISE_3D,
    "3e": EXERCISE_3E,
    "4a": EXERCISE_4A,
    "4b": EXERCISE_4B,
    "4c": EXERCISE_4C,
    "4d": EXERCISE_4D,
    "4e": EXERCISE_4E,
}


def get_exercise(exercise_id: str) -> Exercise:
    """Get exercise by ID."""
    return ALL_EXERCISES.get(exercise_id)


def get_module_exercises(module: int) -> List[Exercise]:
    """Get all exercises for a module."""
    return [ex for ex in ALL_EXERCISES.values() if ex.module == module]


def get_all_exercises() -> List[Exercise]:
    """Get all exercises."""
    return list(ALL_EXERCISES.values())
