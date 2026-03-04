"""
Live terminal dashboard for VeloSim-MTL simulations.

Uses the `rich` library to render a real-time updating display showing
progress, modal split charts, weather conditions, and agent statistics.
"""

from collections import Counter
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from .models import WeatherState, PolicyState

# ── Colour palette for transport modes ──────────────────────────────────────
MODE_STYLES = {
    "bike":  ("green",  "🚲"),
    "metro": ("blue",   "🚇"),
    "bus":   ("cyan",   "🚌"),
    "car":   ("red",    "🚗"),
    "walk":  ("yellow", "🚶"),
}

BAR_CHAR = "█"
BAR_WIDTH = 40


# ── Helpers ─────────────────────────────────────────────────────────────────

def _weather_text(weather: WeatherState) -> Text:
    """Build a coloured Text representation of the current weather."""
    txt = Text()
    # Temperature
    temp_colour = "cyan" if weather.temperature < -5 else (
        "blue" if weather.temperature < 0 else "green"
    )
    txt.append(f"🌡  {weather.temperature:+.1f}°C", style=temp_colour)
    txt.append("  ")
    # Snow
    if weather.snow_depth_cm > 0:
        txt.append(f"❄  {weather.snow_depth_cm:.0f} cm snow", style="bold white")
        txt.append("  ")
    # Precipitation
    if weather.is_snowing:
        txt.append("🌨  Snowing", style="bold white")
    elif weather.is_raining:
        txt.append("🌧  Raining", style="bold blue")
    else:
        txt.append("☁  Dry", style="dim")
    txt.append("  ")
    # Wind
    wind_style = "red" if weather.wind_speed_kmh > 25 else "yellow"
    txt.append(f"💨 {weather.wind_speed_kmh:.0f} km/h", style=wind_style)
    return txt


def _policy_text(policy: PolicyState) -> Text:
    txt = Text()
    if policy.snow_clearing_priority:
        txt.append("✅ Priority Snow Clearing ACTIVE", style="bold green")
    else:
        txt.append("⛔ Standard Snow Clearing", style="bold red")
    return txt


def _modal_split_panel(mode_counts: Counter, total: int) -> Panel:
    """Render a horizontal bar chart of the current modal split."""
    lines = Text()
    if total == 0:
        lines.append("  Waiting for first decision…", style="dim italic")
        return Panel(lines, title="📊 Modal Split", border_style="magenta")

    for mode in ("bike", "metro", "bus", "car", "walk"):
        count = mode_counts.get(mode, 0)
        pct = (count / total) * 100 if total else 0
        filled = int(round(pct / 100 * BAR_WIDTH))

        colour, icon = MODE_STYLES.get(mode, ("white", "?"))
        label = f"  {icon} {mode:<6}"
        bar = BAR_CHAR * filled + "░" * (BAR_WIDTH - filled)
        stat = f" {pct:5.1f}%  ({count})"

        lines.append(label, style=f"bold {colour}")
        lines.append(bar, style=colour)
        lines.append(stat + "\n", style="dim")

    return Panel(lines, title="📊 Modal Split", border_style="magenta")


def _stats_panel(
    mode_counts: Counter,
    total: int,
    avg_frustration: Optional[float] = None,
) -> Panel:
    """Key summary statistics."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", justify="right")
    table.add_column()

    bike_count = mode_counts.get("bike", 0)
    bike_pct = (bike_count / total * 100) if total else 0
    table.add_row("Bike adoption", f"{bike_pct:.1f}%")
    table.add_row("Decisions made", f"{total}")
    table.add_row("Unique modes", f"{len(mode_counts)}")

    if avg_frustration is not None:
        frust_bar_len = int(round(avg_frustration * 10))
        frust_bar = "■" * frust_bar_len + "□" * (10 - frust_bar_len)
        frust_style = (
            "green" if avg_frustration < 0.3
            else "yellow" if avg_frustration < 0.6
            else "red"
        )
        table.add_row("Avg frustration", Text(f"{frust_bar} {avg_frustration:.2f}", style=frust_style))

    return Panel(table, title="📈 Stats", border_style="cyan")


# ── Dashboard classes ───────────────────────────────────────────────────────

class PopulationDashboard:
    """Live dashboard for the population (single-weather) simulation."""

    def __init__(self, pop_size: int, weather: WeatherState):
        self.pop_size = pop_size
        self.weather = weather
        self.console = Console()

        # State
        self._current_policy: Optional[PolicyState] = None
        self._mode_counts: Counter = Counter()
        self._decisions_made = 0
        self._scenario_label = ""

        # Progress bars
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        self._route_task: Optional[int] = None
        self._decide_task: Optional[int] = None

        self._live = Live(
            self._build_layout(),
            console=self.console,
            refresh_per_second=8,
            transient=False,
        )

    # ── Layout builder ───────────────────────────────────────────────────

    def _build_layout(self) -> Layout:
        layout = Layout()

        header = Panel(
            Align.center(
                Text("🚴  VeloSim-MTL  –  Population Simulation", style="bold white")
            ),
            style="on blue",
        )

        weather_panel = Panel(
            _weather_text(self.weather),
            title="🌦  Weather",
            border_style="blue",
        )

        policy_panel = Panel(
            _policy_text(self._current_policy) if self._current_policy else Text("—", style="dim"),
            title="📋 Policy",
            border_style="yellow",
        )

        top_info = Layout()
        top_info.split_row(
            Layout(weather_panel, name="weather", ratio=2),
            Layout(policy_panel, name="policy", ratio=1),
        )

        progress_panel = Panel(self._progress, title="⏳ Progress", border_style="green")

        modal_panel = _modal_split_panel(self._mode_counts, self._decisions_made)
        stats_panel = _stats_panel(self._mode_counts, self._decisions_made)

        bottom = Layout()
        bottom.split_row(
            Layout(modal_panel, name="chart", ratio=3),
            Layout(stats_panel, name="stats", ratio=1),
        )

        layout.split_column(
            Layout(header, name="header", size=3),
            Layout(top_info, name="info", size=5),
            Layout(progress_panel, name="progress", size=5),
            Layout(bottom, name="bottom"),
        )

        return layout

    # ── Public API ───────────────────────────────────────────────────────

    def start(self) -> None:
        self._live.start()

    def stop(self) -> None:
        self._live.stop()

    def begin_route_analysis(self) -> None:
        self._route_task = self._progress.add_task(
            "Analyzing routes…", total=self.pop_size
        )
        self._refresh()

    def advance_route(self) -> None:
        if self._route_task is not None:
            self._progress.advance(self._route_task)
            self._refresh()

    def begin_scenario(self, policy: PolicyState, label: str) -> None:
        self._current_policy = policy
        self._scenario_label = label
        self._mode_counts = Counter()
        self._decisions_made = 0
        self._decide_task = self._progress.add_task(
            f"Scenario: {label}", total=self.pop_size
        )
        self._refresh()

    def record_decision(self, mode: str) -> None:
        self._mode_counts[mode] += 1
        self._decisions_made += 1
        if self._decide_task is not None:
            self._progress.advance(self._decide_task)
        self._refresh()

    # ── Internal ─────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        self._live.update(self._build_layout())


class TemporalDashboard:
    """Live dashboard for the temporal (multi-day) simulation."""

    def __init__(self, pop_size: int, num_days: int):
        self.pop_size = pop_size
        self.num_days = num_days
        self.console = Console()

        # State
        self._current_policy: Optional[PolicyState] = None
        self._current_day: str = ""
        self._current_weather: Optional[WeatherState] = None
        self._mode_counts: Counter = Counter()
        self._decisions_made = 0
        self._avg_frustration: float = 0.0
        # Track daily bike adoption across days for the sparkline
        self._daily_bike_pcts: list[tuple[str, float]] = []

        # Progress
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        self._day_task: Optional[int] = None

        self._live = Live(
            self._build_layout(),
            console=self.console,
            refresh_per_second=8,
            transient=False,
        )

    # ── Layout ───────────────────────────────────────────────────────────

    def _build_layout(self) -> Layout:
        layout = Layout()

        header = Panel(
            Align.center(
                Text("🚴  VeloSim-MTL  –  Temporal Simulation", style="bold white")
            ),
            style="on blue",
        )

        # Weather + Policy + Day
        weather_content = (
            _weather_text(self._current_weather) if self._current_weather
            else Text("—", style="dim")
        )
        weather_panel = Panel(weather_content, title="🌦  Weather", border_style="blue")

        policy_content = (
            _policy_text(self._current_policy) if self._current_policy
            else Text("—", style="dim")
        )
        day_label = self._current_day or "—"
        info_text = Group(
            policy_content,
            Text(f"\n📅 Day: {day_label}", style="bold white"),
        )
        info_panel = Panel(info_text, title="📋 Scenario", border_style="yellow")

        top_info = Layout()
        top_info.split_row(
            Layout(weather_panel, name="weather", ratio=2),
            Layout(info_panel, name="policy", ratio=1),
        )

        progress_panel = Panel(self._progress, title="⏳ Progress", border_style="green")

        modal_panel = _modal_split_panel(self._mode_counts, self._decisions_made)
        stats_panel = _stats_panel(
            self._mode_counts, self._decisions_made,
            avg_frustration=self._avg_frustration,
        )

        # Bike adoption timeline
        timeline = self._build_timeline()

        bottom = Layout()
        bottom.split_row(
            Layout(modal_panel, name="chart", ratio=2),
            Layout(name="right", ratio=2),
        )
        bottom["right"].split_column(
            Layout(stats_panel, name="stats", ratio=1),
            Layout(timeline, name="timeline", ratio=1),
        )

        layout.split_column(
            Layout(header, name="header", size=3),
            Layout(top_info, name="info", size=5),
            Layout(progress_panel, name="progress", size=5),
            Layout(bottom, name="bottom"),
        )
        return layout

    def _build_timeline(self) -> Panel:
        """Render a simple text-based timeline of bike adoption per day."""
        txt = Text()
        if not self._daily_bike_pcts:
            txt.append("  Waiting for data…", style="dim italic")
            return Panel(txt, title="🚲 Bike Adoption Timeline", border_style="green")

        max_bar = 20
        for day_label, pct in self._daily_bike_pcts:
            filled = int(round(pct / 100 * max_bar))
            bar = BAR_CHAR * filled + "░" * (max_bar - filled)
            colour = "green" if pct > 30 else ("yellow" if pct > 15 else "red")
            txt.append(f"  {day_label:<5} ", style="bold")
            txt.append(bar, style=colour)
            txt.append(f" {pct:5.1f}%\n")

        return Panel(txt, title="🚲 Bike Adoption Timeline", border_style="green")

    # ── Public API ───────────────────────────────────────────────────────

    def start(self) -> None:
        self._live.start()

    def stop(self) -> None:
        self._live.stop()

    def begin_scenario(self, policy: PolicyState, label: str) -> None:
        self._current_policy = policy
        self._daily_bike_pcts = []
        self._refresh()

    def begin_day(self, day_name: str, weather: WeatherState) -> None:
        self._current_day = day_name
        self._current_weather = weather
        self._mode_counts = Counter()
        self._decisions_made = 0
        self._day_task = self._progress.add_task(
            f"Day: {day_name}", total=self.pop_size
        )
        self._refresh()

    def record_decision(self, mode: str, avg_frustration: float = 0.0) -> None:
        self._mode_counts[mode] += 1
        self._decisions_made += 1
        self._avg_frustration = avg_frustration
        if self._day_task is not None:
            self._progress.advance(self._day_task)
        self._refresh()

    def end_day(self) -> None:
        """Snapshot the bike adoption for the timeline."""
        total = self._decisions_made
        bike = self._mode_counts.get("bike", 0)
        pct = (bike / total * 100) if total else 0
        self._daily_bike_pcts.append((self._current_day, pct))
        self._refresh()

    # ── Internal ─────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        self._live.update(self._build_layout())
