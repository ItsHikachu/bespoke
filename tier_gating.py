from database import Database
from typing import Dict, List, Tuple
import exercises


class TierGating:
    """Manages tier unlocking based on exercise performance."""
    
    def __init__(self):
        self.db = Database()
        
    def get_exercise_scores(self, exercise_ids: List[str], tier: str) -> Dict[str, float]:
        """Get latest scores for specified exercises and tier."""
        scores = {}
        for exercise_id in exercise_ids:
            try:
                # Get latest session score for this exercise and tier
                session_data = self.db.get_latest_session(exercise_id, tier)
                if session_data and 'scores' in session_data:
                    # Extract overall score from session data
                    score_data = session_data['scores']
                    overall_score = score_data.get('score', score_data.get('overall', 0))
                    scores[exercise_id] = overall_score
                else:
                    scores[exercise_id] = 0.0
            except Exception as e:
                # If there's any error getting scores, default to 0
                scores[exercise_id] = 0.0
        return scores
        
    def count_qualifying_scores(self, scores: Dict[str, float], threshold: float) -> int:
        """Count how many scores meet or exceed the threshold."""
        return sum(1 for score in scores.values() if score >= threshold)
        
    def is_intermediate_unlocked(self, module: int) -> Tuple[bool, Dict[str, float]]:
        """Check if intermediate tier is unlocked for a module."""
        # Get foundation exercise IDs for this module
        foundation_exercises = [f"{module}{chr(97+i)}" for i in range(5)]  # 1a, 1b, 1c, 1d, 1e
        
        # Get latest foundation scores
        foundation_scores = self.get_exercise_scores(foundation_exercises, 'foundation')
        
        # Count qualifying scores (need 3/5 with >70%)
        qualifying_count = self.count_qualifying_scores(foundation_scores, 70.0)
        
        is_unlocked = qualifying_count >= 3
        return is_unlocked, foundation_scores
        
    def is_advanced_unlocked(self, module: int) -> Tuple[bool, Dict[str, float]]:
        """Check if advanced tier is unlocked for a module."""
        # Get intermediate exercise IDs for this module
        intermediate_exercises = [f"{module}{chr(97+i)}" for i in range(5)]  # 2a, 2b, 2c, 2d, 2e
        
        # Get latest intermediate scores
        intermediate_scores = self.get_exercise_scores(intermediate_exercises, 'intermediate')
        
        # Count qualifying scores (need 3/5 with >70%)
        qualifying_count = self.count_qualifying_scores(intermediate_scores, 70.0)
        
        is_unlocked = qualifying_count >= 3
        return is_unlocked, intermediate_scores
        
    def get_module_tier_status(self, module: int) -> Dict[str, any]:
        """Get complete tier status for a module."""
        # Check intermediate unlock
        intermediate_unlocked, foundation_scores = self.is_intermediate_unlocked(module)
        
        # Check advanced unlock (only if intermediate is unlocked)
        advanced_unlocked = False
        intermediate_scores = {}
        if intermediate_unlocked:
            advanced_unlocked, intermediate_scores = self.is_advanced_unlocked(module)
            
        return {
            'module': module,
            'foundation_unlocked': True,  # Always available
            'intermediate_unlocked': intermediate_unlocked,
            'advanced_unlocked': advanced_unlocked,
            'foundation_scores': foundation_scores,
            'intermediate_scores': intermediate_scores,
            'foundation_qualifying': self.count_qualifying_scores(foundation_scores, 70.0),
            'intermediate_qualifying': self.count_qualifying_scores(intermediate_scores, 70.0) if intermediate_scores else 0
        }
        
    def get_all_module_status(self) -> List[Dict[str, any]]:
        """Get tier status for all modules."""
        all_status = []
        for module in range(1, 5):  # Modules 1-4
            status = self.get_module_tier_status(module)
            all_status.append(status)
        return all_status
        
    def can_access_exercise(self, exercise_id: str, tier: str) -> Tuple[bool, str]:
        """Check if user can access a specific exercise tier."""
        exercise = getattr(exercises, f'EXERCISE_{exercise_id.upper()}')
        module = exercise.module
        
        if tier == 'foundation':
            return True, "Foundation tier always available"
            
        elif tier == 'intermediate':
            unlocked, scores = self.is_intermediate_unlocked(module)
            if unlocked:
                return True, "Intermediate tier unlocked"
            else:
                qualifying = self.count_qualifying_scores(scores, 70.0)
                return False, f"Complete 3/5 foundation exercises with 70%+ score (currently {qualifying}/5)"
                
        elif tier == 'advanced':
            # First check if intermediate is unlocked
            intermediate_unlocked, _ = self.is_intermediate_unlocked(module)
            if not intermediate_unlocked:
                return False, "Must unlock intermediate tier first"
                
            # Then check advanced unlock
            advanced_unlocked, scores = self.is_advanced_unlocked(module)
            if advanced_unlocked:
                return True, "Advanced tier unlocked"
            else:
                qualifying = self.count_qualifying_scores(scores, 70.0)
                return False, f"Complete 3/5 intermediate exercises with 70%+ score (currently {qualifying}/5)"
                
        else:
            return False, f"Unknown tier: {tier}"
