"""Statistics panel widget."""
from __future__ import annotations

from rich.bar import Bar
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from ..core.log_parser import LogParser


class StatsPanel(Static):
    """Widget for displaying log statistics."""
    
    DEFAULT_CSS = """
    StatsPanel {
        width: 100%;
        height: 100%;
        padding: 1;
        border: solid $primary;
        background: $surface-darken-1;
    }
    """
    
    LEVEL_COLORS = {
        "DEBUG": "dim",
        "INFO": "cyan",
        "NOTICE": "blue",
        "WARNING": "yellow",
        "WARN": "yellow",
        "ERROR": "red",
        "CRITICAL": "red bold",
        "FATAL": "red bold reverse",
    }
    
    def __init__(self, parser: LogParser) -> None:
        super().__init__()
        self.parser = parser
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.update_stats()
    
    def update_stats(self) -> None:
        """Update the statistics display."""
        stats = self.parser.get_stats_summary()
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="bold cyan", justify="right")
        table.add_column("Value", style="white")
        
        # Basic stats
        table.add_row("📊 Total Entries", f"{stats['total_entries']:,}")
        table.add_row("❌ Errors", f"[red]{stats['error_count']:,}[/red]")
        table.add_row("⚠️ Warnings", f"[yellow]{stats['warning_count']:,}[/yellow]")
        table.add_row("📁 Unique Sources", f"{stats['unique_sources']}")
        
        # Time range
        time_range = stats.get('time_range', {})
        if time_range.get('start') and time_range.get('end'):
            table.add_row("🕐 Time Range", f"{time_range['start'][:19]} → {time_range['end'][:19]}")
        
        # Level distribution
        level_dist = stats.get('level_distribution', {})
        if level_dist:
            table.add_row("", "")
            table.add_row("📈 Level Distribution", "")
            
            total = sum(level_dist.values())
            for level, count in sorted(level_dist.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total * 100) if total > 0 else 0
                color = self.LEVEL_COLORS.get(level.upper(), "white")
                bar = "█" * int(pct / 5)
                table.add_row(
                    f"  [{color}]{level}[/{color}]",
                    f"{count:,} ({pct:.1f}%) {bar}"
                )
        
        # Top sources
        top_sources = stats.get('top_sources', [])
        if top_sources:
            table.add_row("", "")
            table.add_row("📌 Top Sources", "")
            for source, count in top_sources[:5]:
                table.add_row(f"  {source}", f"{count:,} entries")
        
        self.update(table)
