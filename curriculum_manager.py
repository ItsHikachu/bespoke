from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database import Database
from ollama_coach import OllamaCoach


class CurriculumManager:
    """Manages weekly curriculum generation, storage, and retrieval."""
    
    DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    def __init__(self):
        self.db = Database()
        self.coach = OllamaCoach()
        self._cache = None  # In-memory curriculum cache
        
    def get_or_generate_curriculum(self) -> Dict[str, Any]:
        """Get current curriculum from cache, DB, or generate a new one if stale/missing."""
        if self._cache is not None:
            return self._cache
            
        existing = self.db.get_current_curriculum()
        
        if existing and not self._is_stale(existing):
            self._cache = existing
            return existing
            
        # Generate new curriculum
        return self.generate_curriculum()
        
    def generate_curriculum(self) -> Dict[str, Any]:
        """Generate a new weekly curriculum via Ollama (or fallback)."""
        # Gather progress data for Ollama prompt
        progress = self._gather_progress()
        
        # Generate via OllamaCoach (handles its own fallback)
        curriculum_raw = self.coach.weekly_curriculum(progress)
        
        # Normalize and store
        curriculum_data = {
            'week_of': datetime.now().strftime('%Y-%m-%d'),
            'focus_module': curriculum_raw.get('focusModule', 1),
            'daily_plan': curriculum_raw.get('dailyPlan', []),
            'tier_adjustments': curriculum_raw.get('tierAdjustments', {}),
            'rationale': curriculum_raw.get('rationale', '')
        }
        
        self.db.save_curriculum(curriculum_data)
        self._cache = curriculum_data
        return curriculum_data
        
    def get_today_exercises(self) -> List[str]:
        """Get today's recommended exercises from the active curriculum."""
        curriculum = self.get_or_generate_curriculum()
        daily_plan = curriculum.get('daily_plan', [])
        
        if not daily_plan:
            return ["1a", "2a", "3a"]  # Safe default
            
        # Get today's day index (0=Mon, 6=Sun)
        today_index = datetime.now().weekday()
        
        # Find matching day in plan
        if today_index < len(daily_plan):
            day_entry = daily_plan[today_index]
            exercises = day_entry.get('exercises', [])
            if exercises:
                return exercises
                
        # If no match, return first non-empty day's exercises
        for day_entry in daily_plan:
            exercises = day_entry.get('exercises', [])
            if exercises:
                return exercises
                
        return ["1a", "2a", "3a"]  # Safe default
        
    def get_focus_module(self) -> int:
        """Get the current focus module from the curriculum."""
        curriculum = self.get_or_generate_curriculum()
        return curriculum.get('focus_module', 1)
        
    def get_rationale(self) -> str:
        """Get the curriculum rationale text."""
        curriculum = self.get_or_generate_curriculum()
        return curriculum.get('rationale', 'Default balanced plan.')
        
    def get_full_weekly_plan(self) -> List[Dict[str, Any]]:
        """Get the full 7-day plan for display."""
        curriculum = self.get_or_generate_curriculum()
        daily_plan = curriculum.get('daily_plan', [])
        
        if not daily_plan:
            # Return default structure
            return self.coach._default_curriculum()['dailyPlan']
            
        return daily_plan
        
    def _is_stale(self, curriculum: Dict[str, Any]) -> bool:
        """Check if a curriculum is older than 7 days."""
        week_of = curriculum.get('week_of', '')
        if not week_of:
            return True
        try:
            curriculum_date = datetime.fromisoformat(week_of)
            return (datetime.now() - curriculum_date) > timedelta(days=7)
        except (ValueError, TypeError):
            return True
            
    def _gather_progress(self) -> Dict[str, Any]:
        """Gather user progress data for curriculum generation."""
        stats = self.db.get_session_stats(days=30)
        baselines = self.db.get_latest_baselines()
        
        progress = {
            'total_sessions': stats.get('total_sessions', 0),
            'total_duration': stats.get('total_duration', 0),
            'module_counts': stats.get('module_counts', {}),
            'practice_days': len(stats.get('practice_days', [])),
        }
        
        if baselines:
            progress['baselines'] = baselines
            
        return progress

    def invalidate_cache(self):
        """Clear the in-memory cache to force a fresh DB read."""
        self._cache = None
