"""
🧙 LogSage-CLI - Lightweight Terminal Log Intelligence Analysis Engine

A powerful TUI-based log analyzer with AI-powered anomaly detection,
real-time filtering, and intelligent log clustering.
"""

__version__ = "1.0.0"
__author__ = "LogSage Team"
__license__ = "MIT"

from .core.log_parser import LogParser, LogEntry
from .core.format_detector import FormatDetector
from .app import LogSageApp

__all__ = ["LogParser", "LogEntry", "FormatDetector", "LogSageApp"]
