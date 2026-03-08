import json

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaCoach:
    """Local LLM coaching via Ollama. Gracefully degrades if unavailable."""

    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.available = self._check_availability()

    def _check_availability(self):
        if not OLLAMA_AVAILABLE:
            return False
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def post_session_feedback(self, exercise_name, module, tier, scores: dict) -> str:
        if not self.available:
            return self._fallback_feedback(scores)
        prompt = f"""Exercise completed: {exercise_name} (Module {module}, Tier: {tier})
Scores: {json.dumps(scores, indent=2)}

Provide exactly 2-3 sentences of specific coaching feedback:
1. What was strongest in this attempt
2. One specific adjustment for the next attempt
Be direct and precise. No filler phrases. No pleasantries."""
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "system", "content": "You are a concise voice coach. Respond in 2-3 sentences only. Be specific and actionable."},
                {"role": "user", "content": prompt}
            ])
            return response['message']['content']
        except Exception:
            return self._fallback_feedback(scores)

    def weekly_curriculum(self, progress: dict) -> dict:
        if not self.available:
            return self._default_curriculum()
        prompt = f"""Weekly progress data:
{json.dumps(progress, indent=2)}

Output ONLY a JSON object with these exact keys:
- focusModule: number 1-4 (weakest module)
- tierAdjustments: object mapping module number to "up", "stay", or "down"
- dailyPlan: array of 7 objects, each with "day" and "exercises" (array of exercise IDs like "1a", "2c")
- rationale: one sentence explaining the focus choice

Prioritize the weakest module. Maintain all modules at least twice per week. 3-4 exercises per day."""
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "system", "content": "You are a training program designer. Output valid JSON only. No markdown. No preamble."},
                {"role": "user", "content": prompt}
            ], format='json')
            return json.loads(response['message']['content'])
        except Exception:
            return self._default_curriculum()

    def _fallback_feedback(self, scores: dict) -> str:
        parts = []
        for key, value in scores.items():
            if isinstance(value, (int, float)):
                if value > 80:
                    parts.append(f"Strong {key} score at {value:.0f}%.")
                elif value < 50:
                    parts.append(f"Focus on improving {key} (currently {value:.0f}%).")
        if not parts:
            return "Session completed. Keep practicing for consistent improvement."
        return " ".join(parts[:2])

    def _default_curriculum(self) -> dict:
        return {
            "focusModule": 1,
            "tierAdjustments": {"1": "stay", "2": "stay", "3": "stay", "4": "stay"},
            "dailyPlan": [
                {"day": "Mon", "exercises": ["1a", "2a", "3a"]},
                {"day": "Tue", "exercises": ["1b", "2b", "4a"]},
                {"day": "Wed", "exercises": ["1c", "2c", "3b"]},
                {"day": "Thu", "exercises": ["1d", "2d", "4b"]},
                {"day": "Fri", "exercises": ["1e", "2e", "3c"]},
                {"day": "Sat", "exercises": ["1a", "3d", "4c"]},
                {"day": "Sun", "exercises": []}
            ],
            "rationale": "Default balanced plan. Install Ollama for personalized curriculum."
        }
