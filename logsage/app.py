"""Main TUI application."""
from __future__ import annotations

import os
import sys
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from .core.log_parser import LogParser
from .ui.detail_view import DetailView
from .ui.log_view import LogView
from .ui.stats_panel import StatsPanel


class LogSageApp(App):
    """LogSage TUI Application."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
    }
    
    #top-section {
        height: 70%;
        border-bottom: solid $primary;
    }
    
    #bottom-section {
        height: 30%;
    }
    
    #left-panel {
        width: 70%;
        border-right: solid $primary;
    }
    
    #right-panel {
        width: 30%;
    }
    
    #search-bar {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
    }
    
    #search-input {
        width: 100%;
    }
    
    #status-bar {
        height: 1;
        background: $surface-darken-1;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }
    
    LogView {
        height: 100%;
    }
    
    StatsPanel {
        height: 100%;
    }
    
    DetailView {
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("f", "search", "Find", show=True),
        Binding("e", "next_error", "Next Error", show=True),
        Binding("E", "prev_error", "Prev Error", show=True),
        Binding("s", "stats", "Stats", show=True),
        Binding("d", "details", "Details", show=True),
        Binding("c", "clear_filter", "Clear Filter", show=True),
        Binding("o", "open_file", "Open File", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self, filepaths: Optional[list[str]] = None) -> None:
        super().__init__()
        self.parser = LogParser()
        self.filepaths = filepaths or []
        self.log_view: Optional[LogView] = None
        self.detail_view: Optional[DetailView] = None
        self.stats_panel: Optional[StatsPanel] = None
        self.search_input: Optional[Input] = None
        self.status_label: Optional[Label] = None
        self.showing_stats = False
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(show_clock=True)
        
        with Vertical(id="main-container"):
            # Search bar
            with Horizontal(id="search-bar"):
                self.search_input = Input(
                    placeholder="🔍 Search logs... (press Enter to filter)",
                    id="search-input",
                )
                yield self.search_input
            
            # Main content
            with Horizontal(id="top-section"):
                with Vertical(id="left-panel"):
                    self.log_view = LogView(self.parser)
                    yield self.log_view
                
                with Vertical(id="right-panel"):
                    with TabbedContent():
                        with TabPane("📊 Stats", id="stats-tab"):
                            self.stats_panel = StatsPanel(self.parser)
                            yield self.stats_panel
                        with TabPane("ℹ️ Help", id="help-tab"):
                            yield Static(self._get_help_text())
            
            # Bottom detail panel
            with Horizontal(id="bottom-section"):
                self.detail_view = DetailView()
                yield self.detail_view
            
            # Status bar
            self.status_label = Label("Ready", id="status-bar")
            yield self.status_label
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = "🧙 LogSage - Log Intelligence Engine"
        
        # Load files if provided
        if self.filepaths:
            self.load_files(self.filepaths)
        
        # Focus log view
        if self.log_view:
            self.log_view.focus()
    
    def load_files(self, filepaths: list[str]) -> None:
        """Load log files."""
        self.notify(f"Loading {len(filepaths)} file(s)...", severity="information")
        
        try:
            total = self.parser.load_files(filepaths)
            self._update_status(f"Loaded {total:,} entries from {len(filepaths)} file(s)")
            
            if self.log_view:
                self.log_view.refresh_data()
            if self.stats_panel:
                self.stats_panel.update_stats()
            
            self.notify(f"✅ Loaded {total:,} entries", severity="information")
        except Exception as e:
            self.notify(f"❌ Error loading files: {e}", severity="error")
    
    def on_data_table_cursor_changed(self, event: LogView.CursorChanged) -> None:
        """Handle log view cursor change."""
        if self.log_view and self.detail_view:
            entry = self.log_view.get_selected_entry()
            self.detail_view.set_entry(entry)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input":
            self._apply_filter(event.value)
    
    def _apply_filter(self, pattern: str) -> None:
        """Apply filter to log entries."""
        if not pattern.strip():
            self.parser.clear_filter()
            if self.log_view:
                self.log_view.refresh_data()
            self._update_status("Filter cleared")
            return
        
        try:
            filtered = self.parser.filter_entries(pattern=pattern)
            if self.log_view:
                self.log_view.refresh_data(filtered)
            self._update_status(f"Filter: '{pattern}' ({len(filtered)} matches)")
        except Exception as e:
            self.notify(f"Filter error: {e}", severity="error")
    
    def action_refresh(self) -> None:
        """Refresh the view."""
        if self.log_view:
            self.log_view.refresh_data()
        if self.stats_panel:
            self.stats_panel.update_stats()
        self.notify("🔄 Refreshed", severity="information")
    
    def action_search(self) -> None:
        """Focus search input."""
        if self.search_input:
            self.search_input.focus()
    
    def action_next_error(self) -> None:
        """Jump to next error."""
        if self.log_view:
            entry = self.log_view.scroll_to_next_error()
            if entry:
                self._update_status(f"Error at line {entry.line_number}")
            else:
                self.notify("No more errors found", severity="warning")
    
    def action_prev_error(self) -> None:
        """Jump to previous error."""
        if self.log_view:
            entry = self.log_view.scroll_to_prev_error()
            if entry:
                self._update_status(f"Error at line {entry.line_number}")
            else:
                self.notify("No previous errors found", severity="warning")
    
    def action_stats(self) -> None:
        """Toggle stats panel."""
        if self.stats_panel:
            self.stats_panel.update_stats()
    
    def action_details(self) -> None:
        """Focus detail view."""
        if self.detail_view:
            self.detail_view.focus()
    
    def action_clear_filter(self) -> None:
        """Clear active filter."""
        self.parser.clear_filter()
        if self.search_input:
            self.search_input.value = ""
        if self.log_view:
            self.log_view.refresh_data()
        self._update_status("Filter cleared")
    
    def action_open_file(self) -> None:
        """Open file dialog (placeholder)."""
        self.notify("Use: logsage <file1> [file2] ...", severity="information")
    
    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Shortcuts: q=quit, r=refresh, f=search, e=next error, E=prev error, c=clear filter",
            severity="information",
            timeout=5,
        )
    
    def _update_status(self, message: str) -> None:
        """Update status bar."""
        if self.status_label:
            self.status_label.update(message)
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
🧙 LogSage - Log Intelligence Engine

📖 NAVIGATION
  ↑/↓ or j/k    Move cursor up/down
  PageUp/PageDn  Scroll page
  Home/End       Jump to start/end
  g/G            Jump to first/last entry

🔍 SEARCH & FILTER
  f              Focus search box
  Enter          Apply filter
  c              Clear filter
  /pattern       Regex search

⚠️ ERRORS
  e              Jump to next error
  E              Jump to previous error

📊 VIEWS
  r              Refresh data
  s              Update stats
  d              Focus detail view

⚡ OTHER
  o              Open file (use CLI)
  ?              Show this help
  q              Quit

💡 TIPS
  • Multiple files are merged by timestamp
  • Supports gzip (.gz) files
  • Auto-detects 15+ log formats
  • Export with: logsage export <format>
"""


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧙 LogSage - Lightweight Terminal Log Intelligence Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  logsage /var/log/syslog
  logsage app.log error.log
  logsage *.log
  logsage /var/log/nginx/access.log.gz
        """
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Log files to analyze"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s 1.0.0"
    )
    parser.add_argument(
        "--export",
        choices=["json", "markdown"],
        help="Export mode (requires files)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Export output file"
    )
    
    args = parser.parse_args()
    
    # Handle export mode
    if args.export and args.files:
        from .core.log_parser import LogParser
        
        lp = LogParser()
        lp.load_files(args.files)
        
        output = args.output or f"logsage_export.{args.export}"
        
        if args.export == "json":
            lp.export_to_json(output)
        elif args.export == "markdown":
            lp.export_to_markdown(output)
        
        print(f"✅ Exported to {output}")
        return
    
    # Run TUI app
    app = LogSageApp(filepaths=args.files)
    app.run()


if __name__ == "__main__":
    main()
