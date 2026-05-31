"""Log entry data model."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class LogEntry:
    """Represents a single log entry."""
    
    raw_line: str
    timestamp: Optional[datetime] = None
    level: str = "INFO"
    message: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    line_number: int = 0
    file_source: str = ""
    
    # Level priorities for sorting/filtering
    LEVEL_PRIORITY = {
        "DEBUG": 0,
        "INFO": 1,
        "NOTICE": 2,
        "WARNING": 3,
        "WARN": 3,
        "ERROR": 4,
        "CRITICAL": 5,
        "FATAL": 6,
        "EMERGENCY": 7,
    }
    
    @property
    def level_priority(self) -> int:
        """Get numeric priority of log level."""
        return self.LEVEL_PRIORITY.get(self.level.upper(), 1)
    
    @property
    def is_error(self) -> bool:
        """Check if entry is an error level."""
        return self.level_priority >= 4
    
    @property
    def is_warning(self) -> bool:
        """Check if entry is a warning level."""
        return self.level_priority == 3
    
    def matches(self, pattern: str, case_sensitive: bool = False) -> bool:
        """Check if entry matches search pattern."""
        if not case_sensitive:
            pattern = pattern.lower()
            text = self.raw_line.lower()
        else:
            text = self.raw_line
        
        return pattern in text
    
    def matches_regex(self, pattern: re.Pattern) -> bool:
        """Check if entry matches regex pattern."""
        return bool(pattern.search(self.raw_line))
    
    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "message": self.message,
            "source": self.source,
            "metadata": self.metadata,
            "line_number": self.line_number,
            "file_source": self.file_source,
            "raw_line": self.raw_line,
        }
    
    def __str__(self) -> str:
        """String representation."""
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "N/A"
        return f"[{ts}] {self.level}: {self.message[:100]}"
