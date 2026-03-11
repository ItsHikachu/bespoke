import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class Database:
    """SQLite wrapper for Bespoke voice practice data."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to ~/.bespoke/bespoke.db
            bespoke_dir = os.path.expanduser("~/.bespoke")
            os.makedirs(bespoke_dir, exist_ok=True)
            db_path = os.path.join(bespoke_dir, "bespoke.db")
            
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Baselines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    pitch_min REAL,
                    pitch_max REAL,
                    sustain_duration REAL,
                    dynamic_range REAL,
                    avg_wpm REAL
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    module INTEGER NOT NULL,
                    exercise TEXT NOT NULL,
                    tier TEXT DEFAULT 'foundation',
                    duration REAL,
                    scores TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Migration: add tier column if missing (existing DBs)
            cursor.execute("PRAGMA table_info(sessions)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'tier' not in columns:
                cursor.execute("ALTER TABLE sessions ADD COLUMN tier TEXT DEFAULT 'foundation'")
            
            # Curriculum table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curriculum (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_of TEXT NOT NULL,
                    focus_module INTEGER,
                    daily_plan TEXT,
                    tier_adjustments TEXT,
                    rationale TEXT DEFAULT ''
                )
            """)
            
            # Migration: add rationale column if missing (existing DBs)
            cursor.execute("PRAGMA table_info(curriculum)")
            curr_columns = [col[1] for col in cursor.fetchall()]
            if 'rationale' not in curr_columns:
                cursor.execute("ALTER TABLE curriculum ADD COLUMN rationale TEXT DEFAULT ''")
            
            # Recordings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER REFERENCES sessions(id),
                    filepath TEXT,
                    transcript TEXT,
                    wpm REAL,
                    filler_count INTEGER
                )
            """)
            
            conn.commit()
            
    # Settings methods
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
            
    def get_setting(self, key: str, default=None):
        """Get a setting value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default
            
    # Baseline methods
    def save_baseline(self, baseline_data: Dict[str, Any]):
        """Save a baseline assessment."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baselines 
                (date, pitch_min, pitch_max, sustain_duration, dynamic_range, avg_wpm)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                baseline_data['date'],
                baseline_data.get('pitch_min'),
                baseline_data.get('pitch_max'),
                baseline_data.get('sustain_duration'),
                baseline_data.get('dynamic_range'),
                baseline_data.get('avg_wpm')
            ))
            conn.commit()
            return cursor.lastrowid
            
    def get_latest_baseline(self) -> Optional[Dict[str, Any]]:
        """Get the most recent baseline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM baselines 
                ORDER BY date DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                columns = ['id', 'date', 'pitch_min', 'pitch_max', 'sustain_duration', 
                          'dynamic_range', 'avg_wpm']
                return dict(zip(columns, row))
            return None
            
    # Session methods
    def save_session(self, session_data: Dict[str, Any]):
        """Save a practice session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions 
                (date, module, exercise, tier, duration, scores, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['date'],
                session_data['module'],
                session_data['exercise'],
                session_data.get('tier', 'foundation'),
                session_data.get('duration'),
                json.dumps(session_data.get('scores', {})),
                session_data['timestamp']
            ))
            conn.commit()
            return cursor.lastrowid
            
    def get_sessions(self, limit: int = 50, module: int = None) -> List[Dict[str, Any]]:
        """Get recent sessions, optionally filtered by module."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, date, module, exercise, tier, duration, scores, timestamp
                FROM sessions 
                WHERE 1=1
            """
            params = []
            
            if module is not None:
                query += " AND module = ?"
                params.append(module)
                
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            sessions = []
            columns = ['id', 'date', 'module', 'exercise', 'tier', 'duration', 'scores', 'timestamp']
            for row in rows:
                session = dict(zip(columns, row))
                # Parse JSON scores
                if session['scores']:
                    session['scores'] = json.loads(session['scores'])
                else:
                    session['scores'] = {}
                sessions.append(session)
                
            return sessions
            
    def get_latest_session(self, exercise_id: str, tier: str) -> Optional[Dict[str, Any]]:
        """Get the latest session for a specific exercise and tier."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, date, module, exercise, tier, duration, scores, timestamp
                    FROM sessions 
                    WHERE exercise = ? 
                    AND tier = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (exercise_id, tier))
                row = cursor.fetchone()
                if row:
                    columns = ['id', 'date', 'module', 'exercise', 'tier', 'duration', 'scores', 'timestamp']
                    session = dict(zip(columns, row))
                    # Parse JSON scores
                    session['scores'] = json.loads(session['scores'] or '{}')
                    return session
                return None
        except Exception as e:
            # If there's any error, return None
            return None
            
    def get_session_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get practice statistics for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total sessions and duration
            cursor.execute("""
                SELECT COUNT(*), SUM(duration) 
                FROM sessions 
                WHERE date >= date('now', '-{} days')
            """.format(days))
            total_sessions, total_duration = cursor.fetchone() or (0, 0)
            
            # Sessions per module
            cursor.execute("""
                SELECT module, COUNT(*) 
                FROM sessions 
                WHERE date >= date('now', '-{} days')
                GROUP BY module
            """.format(days))
            module_counts = dict(cursor.fetchall())
            
            # Recent streak (consecutive days with practice)
            cursor.execute("""
                SELECT DISTINCT date 
                FROM sessions 
                WHERE date >= date('now', '-30 days')
                ORDER BY date DESC
            """)
            practice_days = [row[0] for row in cursor.fetchall()]
            
            return {
                'total_sessions': total_sessions,
                'total_duration': total_duration or 0,
                'module_counts': module_counts,
                'practice_days': practice_days
            }
            
    # Curriculum methods
    def save_curriculum(self, curriculum_data: Dict[str, Any]):
        """Save weekly curriculum."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO curriculum 
                (week_of, focus_module, daily_plan, tier_adjustments, rationale)
                VALUES (?, ?, ?, ?, ?)
            """, (
                curriculum_data['week_of'],
                curriculum_data.get('focus_module'),
                json.dumps(curriculum_data.get('daily_plan', {})),
                json.dumps(curriculum_data.get('tier_adjustments', {})),
                curriculum_data.get('rationale', '')
            ))
            conn.commit()
            
    def get_current_curriculum(self) -> Optional[Dict[str, Any]]:
        """Get the current week's curriculum."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, week_of, focus_module, daily_plan, tier_adjustments, rationale
                FROM curriculum 
                WHERE week_of >= date('now', '-7 days')
                ORDER BY week_of DESC, id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                columns = ['id', 'week_of', 'focus_module', 'daily_plan', 'tier_adjustments', 'rationale']
                curriculum = dict(zip(columns, row))
                # Parse JSON fields
                curriculum['daily_plan'] = json.loads(curriculum['daily_plan'] or '{}')
                curriculum['tier_adjustments'] = json.loads(curriculum['tier_adjustments'] or '{}')
                curriculum['rationale'] = curriculum.get('rationale', '') or ''
                return curriculum
            return None
            
    # Baseline methods
    def save_baselines(self, pitch_min: float, pitch_max: float, 
                      sustain_duration: float, dynamic_range: float, avg_wpm: float):
        """Save baseline measurements."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baselines 
                (date, pitch_min, pitch_max, sustain_duration, dynamic_range, avg_wpm)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                pitch_min,
                pitch_max,
                sustain_duration,
                dynamic_range,
                avg_wpm
            ))
            conn.commit()
            
    def get_latest_baselines(self) -> Optional[Dict[str, float]]:
        """Get the most recent baseline measurements."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pitch_min, pitch_max, sustain_duration, dynamic_range, avg_wpm
                FROM baselines
                ORDER BY date DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return {
                    'pitch_min': row[0] or 0,
                    'pitch_max': row[1] or 0,
                    'sustain_duration': row[2] or 0,
                    'dynamic_range': row[3] or 0,
                    'avg_wpm': row[4] or 0
                }
            return None
            
    def has_baselines(self) -> bool:
        """Check if user has completed baseline assessment."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM baselines")
            count = cursor.fetchone()[0]
            return count > 0
