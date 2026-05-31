"""Detail view for log entry inspection."""
from __future__ import annotations

from rich.syntax import Syntax
from rich.text import Text
from textual.widgets import Static

from ..core.log_entry import LogEntry


class DetailView(Static):
    """Widget for displaying detailed log entry information."""
    
    DEFAULT_CSS = """
    DetailView {
        width: 100%;
        height: 100%;
        padding: 1;
        border: solid $primary;
        background: $surface-darken-1;
    }
    DetailView > .title {
        text-style: bold;
        color: $primary;
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
    
    def __init__(self) -> None:
        super().__init__()
        self.entry: LogEntry | None = None
    
    def set_entry(self, entry: LogEntry | None) -> None:
        """Set the entry to display."""
        self.entry = entry
        self.update_content()
    
    def update_content(self) -> None:
        """Update the displayed content."""
        if self.entry is None:
            self.update("Select a log entry to view details")
            return
        
        lines = []
        
        # Header
        lines.append(Text("═" * 60, style="primary"))
        lines.append(Text("📋 Log Entry Details", style="bold primary"))
        lines.append(Text("═" * 60, style="primary"))
        lines.append("")
        
        # Basic info
        if self.entry.timestamp:
            ts_str = self.entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            lines.append(Text(f"📅 Timestamp: {ts_str}", style="cyan"))
        
        level_style = self.LEVEL_COLORS.get(self.entry.level.upper(), "white")
        lines.append(Text(f"📊 Level: ", style="") + Text(self.entry.level, style=level_style))
        
        if self.entry.source:
            lines.append(Text(f"📁 Source: {self.entry.source}", style="magenta"))
        
        lines.append(Text(f"🔢 Line: {self.entry.line_number}", style="dim"))
        
        if self.entry.file_source:
            lines.append(Text(f"📄 File: {self.entry.file_source}", style="dim"))
        
        lines.append("")
        lines.append(Text("─" * 60, style="dim"))
        lines.append("")
        
        # Message
        lines.append(Text("📝 Message:", style="bold"))
        lines.append("")
        
        # Try to format as JSON if it looks like JSON
        message = self.entry.message
        if message.strip().startswith(("{", "[")):
            try:
                import json
                parsed = json.loads(message)
                formatted = json.dumps(parsed, indent=2)
                syntax = Syntax(formatted, "json", theme="monokai", word_wrap=True)
                lines.append(syntax)
            except json.JSONDecodeError:
                lines.append(Text(message))
        else:
            lines.append(Text(message))
        
        lines.append("")
        
        # Metadata
        if self.entry.metadata:
            lines.append(Text("─" * 60, style="dim"))
            lines.append("")
            lines.append(Text("🔧 Metadata:", style="bold"))
            lines.append("")
            for key, value in self.entry.metadata.items():
                lines.append(Text(f"  {key}: {value}", style="dim"))
        
        lines.append("")
        lines.append(Text("═" * 60, style="primary"))
        
        # Raw line
        lines.append("")
        lines.append(Text("📜 Raw Line:", style="bold dim"))
        lines.append(Text(self.entry.raw_line[:500], style="dim"))
        
        self.update("\n".join(str(line) for line in lines))
    
    def clear(self) -> None:
        """Clear the view."""
        self.entry = None
        self.update("Select a log entry to view details")
