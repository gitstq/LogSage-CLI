"""Main log viewer widget."""
from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.widgets import DataTable

from ..core.log_entry import LogEntry
from ..core.log_parser import LogParser


class LogView(DataTable):
    """Widget for displaying log entries."""
    
    DEFAULT_CSS = """
    LogView {
        width: 100%;
        height: 100%;
        border: none;
    }
    LogView > .datatable--header {
        background: $surface-darken-1;
        color: $text;
        text-style: bold;
    }
    LogView > .datatable--cursor {
        background: $accent;
    }
    """
    
    # Level colors
    LEVEL_COLORS = {
        "DEBUG": "dim",
        "INFO": "cyan",
        "NOTICE": "blue",
        "WARNING": "yellow",
        "WARN": "yellow",
        "ERROR": "red",
        "CRITICAL": "red bold",
        "FATAL": "red bold reverse",
        "EMERGENCY": "red bold reverse",
    }
    
    def __init__(self, parser: LogParser) -> None:
        super().__init__()
        self.parser = parser
        self.show_columns = ["Time", "Level", "Source", "Message"]
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.header_height = 1
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.add_columns(*self.show_columns)
        self.refresh_data()
    
    def refresh_data(self, entries: Optional[list[LogEntry]] = None) -> None:
        """Refresh the displayed data."""
        self.clear()
        
        entries = entries or self.parser.get_entries()
        
        for entry in entries:
            row = self._format_entry(entry)
            self.add_row(*row, key=str(entry.line_number))
    
    def _format_entry(self, entry: LogEntry) -> tuple:
        """Format a log entry for display."""
        # Timestamp
        if entry.timestamp:
            time_str = entry.timestamp.strftime("%H:%M:%S")
        else:
            time_str = "--:--:--"
        
        # Level with styling
        level = entry.level[:10].upper()
        
        # Source
        source = entry.source[:15] if entry.source else ""
        
        # Message (truncated)
        message = entry.message[:80] + "..." if len(entry.message) > 80 else entry.message
        
        # Create styled text
        time_text = Text(time_str, style="dim")
        level_style = self.LEVEL_COLORS.get(entry.level.upper(), "white")
        level_text = Text(level, style=level_style)
        source_text = Text(source, style="magenta")
        message_text = Text(message)
        
        return (time_text, level_text, source_text, message_text)
    
    def get_selected_entry(self) -> Optional[LogEntry]:
        """Get the currently selected log entry."""
        cursor_row = self.cursor_row
        if cursor_row is None:
            return None
        
        entries = self.parser.get_entries()
        if 0 <= cursor_row < len(entries):
            return entries[cursor_row]
        return None
    
    def scroll_to_entry(self, entry: LogEntry) -> None:
        """Scroll to a specific entry."""
        entries = self.parser.get_entries()
        for i, e in enumerate(entries):
            if e.line_number == entry.line_number:
                self.move_cursor(row=i)
                break
    
    def scroll_to_next_error(self) -> Optional[LogEntry]:
        """Scroll to next error entry."""
        entries = self.parser.get_entries()
        current_row = self.cursor_row or 0
        
        for i in range(current_row + 1, len(entries)):
            if entries[i].is_error:
                self.move_cursor(row=i)
                return entries[i]
        return None
    
    def scroll_to_prev_error(self) -> Optional[LogEntry]:
        """Scroll to previous error entry."""
        entries = self.parser.get_entries()
        current_row = self.cursor_row or len(entries) - 1
        
        for i in range(current_row - 1, -1, -1):
            if entries[i].is_error:
                self.move_cursor(row=i)
                return entries[i]
        return None
