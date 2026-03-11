from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

# Matplotlib with Qt backend
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RadarCanvas(FigureCanvas):
    """Matplotlib radar chart embedded in Qt for 4-module overview."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 4), facecolor='#0F1419')
        super().__init__(self.fig)
        self.setParent(parent)
        self.scores = [0, 0, 0, 0]
        self.draw_radar()

    def set_scores(self, scores: list):
        """Set module scores (list of 4 floats 0-100)."""
        self.scores = scores[:4] if len(scores) >= 4 else scores + [0] * (4 - len(scores))
        self.draw_radar()

    def draw_radar(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111, polar=True)
        ax.set_facecolor('#0F1419')

        labels = ['Pitch\nControl', 'Breath &\nSustain', 'Pace &\nRhythm', 'Dynamics &\nProjection']
        num_vars = 4
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        values = self.scores + self.scores[:1]

        # Grid styling
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9, color='#94A3B8')

        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25', '50', '75', '100'], fontsize=7, color='#4B5563')
        ax.tick_params(colors='#4B5563')
        ax.spines['polar'].set_color('#2A3444')
        for spine in ax.spines.values():
            spine.set_color('#2A3444')
        ax.grid(color='#2A3444', linewidth=0.5)

        # Plot data
        ax.fill(angles, values, color='#2DD4BF', alpha=0.15)
        ax.plot(angles, values, color='#2DD4BF', linewidth=2, marker='o', markersize=5)

        self.fig.tight_layout(pad=1.0)
        self.draw()


class LineChartCanvas(FigureCanvas):
    """Matplotlib line chart for per-module score history."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 2.5), facecolor='#0F1419')
        super().__init__(self.fig)
        self.setParent(parent)
        self.draw_empty()

    def draw_empty(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        self._style_ax(ax)
        ax.text(0.5, 0.5, 'No session data yet', transform=ax.transAxes,
                ha='center', va='center', color='#4B5563', fontsize=11)
        self.fig.tight_layout(pad=1.5)
        self.draw()

    def set_data(self, module_data: dict):
        """Plot score history for up to 4 modules.

        Args:
            module_data: {module_num: [(session_index, score), ...]}
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        self._style_ax(ax)

        colors = {1: '#2DD4BF', 2: '#F59E0B', 3: '#8B5CF6', 4: '#EF4444'}
        names = {1: 'Pitch', 2: 'Breath', 3: 'Pace', 4: 'Dynamics'}
        has_data = False

        for module_num, points in module_data.items():
            if not points:
                continue
            has_data = True
            indices = [p[0] for p in points]
            scores = [p[1] for p in points]
            ax.plot(indices, scores, color=colors.get(module_num, '#94A3B8'),
                    linewidth=1.5, label=names.get(module_num, f'M{module_num}'),
                    marker='o', markersize=3)

        if has_data:
            ax.legend(fontsize=8, facecolor='#1A2332', edgecolor='#2A3444',
                      labelcolor='#94A3B8', loc='upper left')
            ax.set_xlabel('Session', fontsize=9, color='#94A3B8')
            ax.set_ylabel('Score %', fontsize=9, color='#94A3B8')
        else:
            ax.text(0.5, 0.5, 'No session data yet', transform=ax.transAxes,
                    ha='center', va='center', color='#4B5563', fontsize=11)

        self.fig.tight_layout(pad=1.5)
        self.draw()

    def _style_ax(self, ax):
        ax.set_facecolor('#0F1419')
        ax.tick_params(colors='#4B5563', labelsize=8)
        ax.spines['bottom'].set_color('#2A3444')
        ax.spines['left'].set_color('#2A3444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, 105)


class ProgressView(QWidget):
    """Full progress view with radar chart, line charts, and stats cards."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Your Progress")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2DD4BF;")
        layout.addWidget(title)

        # Stats cards row
        stats_row = self._create_stats_row()
        layout.addLayout(stats_row)

        # Charts row: radar + line chart
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Radar chart in frame
        radar_frame = self._make_frame("Module Overview")
        self.radar = RadarCanvas()
        radar_frame_layout = radar_frame.layout()
        radar_frame_layout.addWidget(self.radar)
        charts_layout.addWidget(radar_frame, stretch=2)

        # Line chart in frame
        line_frame = self._make_frame("Score History (Last 30 Sessions)")
        self.line_chart = LineChartCanvas()
        line_frame_layout = line_frame.layout()
        line_frame_layout.addWidget(self.line_chart)
        charts_layout.addWidget(line_frame, stretch=3)

        layout.addLayout(charts_layout)

        # Per-module detail cards
        detail_title = QLabel("Module Breakdown")
        detail_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        detail_title.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(detail_title)

        self.module_grid = QGridLayout()
        self.module_grid.setSpacing(15)
        layout.addLayout(self.module_grid)

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Stats cards ──────────────────────────────────────────────

    def _create_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(15)

        self.total_sessions_label = QLabel("0")
        self.total_minutes_label = QLabel("0")
        self.current_streak_label = QLabel("0")
        self.best_module_label = QLabel("—")

        cards = [
            ("Total Sessions", self.total_sessions_label, "#2DD4BF"),
            ("Total Minutes", self.total_minutes_label, "#F59E0B"),
            ("Current Streak", self.current_streak_label, "#8B5CF6"),
            ("Best Module", self.best_module_label, "#EF4444"),
        ]

        for card_title, value_label, accent in cards:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #1A2332;
                    border: 1px solid #2A3444;
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setSpacing(4)

            t = QLabel(card_title)
            t.setFont(QFont("Arial", 10))
            t.setStyleSheet("color: #94A3B8;")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)

            value_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
            value_label.setStyleSheet(f"color: {accent};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cl.addWidget(t)
            cl.addWidget(value_label)
            row.addWidget(card)

        return row

    # ── Module detail cards ──────────────────────────────────────

    def _create_module_cards(self, module_averages: dict):
        # Clear existing
        while self.module_grid.count():
            child = self.module_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        module_names = {
            1: ("Pitch Control", "#2DD4BF"),
            2: ("Breath & Sustain", "#F59E0B"),
            3: ("Pace & Rhythm", "#8B5CF6"),
            4: ("Dynamics & Projection", "#EF4444"),
        }

        for i, (module_num, (name, color)) in enumerate(module_names.items()):
            avg = module_averages.get(module_num, 0)
            sessions_count = module_averages.get(f'{module_num}_count', 0)

            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1A2332;
                    border: 1px solid #2A3444;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            cl = QVBoxLayout(card)

            header = QLabel(f"Module {module_num}: {name}")
            header.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            header.setStyleSheet(f"color: {color};")

            score_label = QLabel(f"{avg:.0f}%")
            score_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
            score_label.setStyleSheet(f"color: {color};")
            score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            detail = QLabel(f"{sessions_count} sessions completed")
            detail.setStyleSheet("color: #94A3B8; font-size: 11px;")
            detail.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cl.addWidget(header)
            cl.addWidget(score_label)
            cl.addWidget(detail)

            self.module_grid.addWidget(card, i // 2, i % 2)

    # ── Helpers ──────────────────────────────────────────────────

    def _make_frame(self, title_text: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1A2332;
                border: 1px solid #2A3444;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(frame)
        t = QLabel(title_text)
        t.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        t.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(t)
        return frame

    # ── Data loading ─────────────────────────────────────────────

    def load_data(self):
        """Load all progress data from the database."""
        stats = self.db.get_session_stats(days=30)
        sessions = self.db.get_sessions(limit=100)

        # Stats cards
        total_sessions = stats.get('total_sessions', 0)
        total_duration = stats.get('total_duration', 0) or 0
        total_minutes = total_duration / 60.0 if total_duration else 0
        practice_days = stats.get('practice_days', [])

        self.total_sessions_label.setText(str(total_sessions))
        self.total_minutes_label.setText(f"{total_minutes:.0f}")

        # Calculate streak
        streak = self._calc_streak(practice_days)
        self.current_streak_label.setText(str(streak))

        # Module scores
        module_scores = {1: [], 2: [], 3: [], 4: []}
        for session in sessions:
            module = session.get('module')
            score_data = session.get('scores', {})
            score = score_data.get('score', score_data.get('overall', 0))
            if module in module_scores:
                module_scores[module].append(score)

        # Module averages
        module_averages = {}
        best_module = 0
        best_avg = -1
        for m in range(1, 5):
            if module_scores[m]:
                avg = sum(module_scores[m]) / len(module_scores[m])
                module_averages[m] = avg
                module_averages[f'{m}_count'] = len(module_scores[m])
                if avg > best_avg:
                    best_avg = avg
                    best_module = m
            else:
                module_averages[m] = 0
                module_averages[f'{m}_count'] = 0

        module_short = {1: 'Pitch', 2: 'Breath', 3: 'Pace', 4: 'Dynamics'}
        if best_module and best_avg > 0:
            self.best_module_label.setText(module_short.get(best_module, '—'))
        else:
            self.best_module_label.setText('—')

        # Radar chart
        self.radar.set_scores([module_averages.get(m, 0) for m in range(1, 5)])

        # Line chart data: convert to indexed points
        line_data = {}
        for m in range(1, 5):
            line_data[m] = [(i, s) for i, s in enumerate(module_scores[m])]
        self.line_chart.set_data(line_data)

        # Module detail cards
        self._create_module_cards(module_averages)

    def _calc_streak(self, practice_days: list) -> int:
        """Calculate current consecutive-day streak."""
        if not practice_days:
            return 0
        from datetime import datetime, timedelta
        today = datetime.now().date()
        sorted_days = sorted(set(practice_days), reverse=True)

        def _count_from(start_date):
            streak = 0
            expected = start_date
            for day_str in sorted_days:
                try:
                    day = datetime.fromisoformat(day_str).date()
                except (ValueError, TypeError):
                    continue
                if day == expected:
                    streak += 1
                    expected -= timedelta(days=1)
                elif day < expected:
                    break
            return streak

        # Try starting from today, then from yesterday (if user hasn't practiced today yet)
        return max(_count_from(today), _count_from(today - timedelta(days=1)))

    def refresh(self):
        """Refresh progress data."""
        self.load_data()
