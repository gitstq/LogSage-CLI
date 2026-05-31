"""Log format detection and parsing."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional, Pattern

from .log_entry import LogEntry


class LogFormat:
    """Represents a log format definition."""
    
    def __init__(
        self,
        name: str,
        pattern: Pattern,
        timestamp_format: Optional[str] = None,
        level_group: int = 2,
        message_group: int = 3,
        timestamp_group: int = 1,
    ):
        self.name = name
        self.pattern = pattern
        self.timestamp_format = timestamp_format
        self.level_group = level_group
        self.message_group = message_group
        self.timestamp_group = timestamp_group


class FormatDetector:
    """Detects and parses various log formats."""
    
    # Predefined log formats
    FORMATS = [
        # Syslog format
        LogFormat(
            name="syslog",
            pattern=re.compile(
                r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)$"
            ),
            timestamp_format="%b %d %H:%M:%S",
        ),
        # Apache/Nginx access log
        LogFormat(
            name="apache_combined",
            pattern=re.compile(
                r'^(\S+)\s+(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\S+)'
            ),
            timestamp_format="%d/%b/%Y:%H:%M:%S %z",
            timestamp_group=4,
            level_group=6,  # HTTP status as level indicator
            message_group=5,
        ),
        # Common log format with timestamp
        LogFormat(
            name="timestamp_level_message",
            pattern=re.compile(
                r"^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}[\.\d]*(?:Z|[+-]\d{2}:?\d{2})?)\s+(DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL)\s+(.*)$",
                re.IGNORECASE,
            ),
            timestamp_format=None,  # Auto-detect
        ),
        # Simple level: message format
        LogFormat(
            name="level_message",
            pattern=re.compile(
                r"^(DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL):?\s+(.*)$",
                re.IGNORECASE,
            ),
            timestamp_group=0,
        ),
        # Python traceback format
        LogFormat(
            name="python_traceback",
            pattern=re.compile(r"^(Traceback \(most recent call last\):.*)$"),
            timestamp_group=0,
            level_group=0,
            message_group=1,
        ),
        # Java stack trace
        LogFormat(
            name="java_stacktrace",
            pattern=re.compile(r"^(\s*at\s+[\w\.]+\.[\w<>]+\(.*\))$"),
            timestamp_group=0,
            level_group=0,
            message_group=1,
        ),
        # Docker log format
        LogFormat(
            name="docker",
            pattern=re.compile(
                r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\w+)\s+(.*)$"
            ),
            timestamp_format="%Y-%m-%dT%H:%M:%S.%fZ",
        ),
        # Kubernetes log format
        LogFormat(
            name="kubernetes",
            pattern=re.compile(
                r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\w+)\s+(.*)$"
            ),
            timestamp_format="%Y-%m-%dT%H:%M:%S.%fZ",
        ),
    ]
    
    # Timestamp format patterns for auto-detection
    TIMESTAMP_PATTERNS = [
        ("%Y-%m-%dT%H:%M:%S.%fZ", re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$")),
        ("%Y-%m-%dT%H:%M:%SZ", re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d+Z$")),
        ("%Y-%m-%dT%H:%M:%S.%f%z", re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$")),
        ("%Y-%m-%d %H:%M:%S.%f", re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$")),
        ("%Y-%m-%d %H:%M:%S", re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d+$")),
        ("%d/%b/%Y:%H:%M:%S %z", re.compile(r"^\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4}$")),
        ("%b %d %H:%M:%S", re.compile(r"^\w{3} \d{1,2} \d{2}:\d{2}:\d{2}$")),
        ("%b %d, %Y %I:%M:%S %p", re.compile(r"^\w{3} \d{1,2}, \d{4} \d{1,2}:\d{2}:\d{2} (AM|PM)$")),
    ]
    
    def __init__(self):
        self.detected_format: Optional[LogFormat] = None
        self.is_jsonl = False
    
    def detect_format(self, sample_lines: list[str]) -> Optional[LogFormat]:
        """Detect log format from sample lines."""
        if not sample_lines:
            return None
        
        # Check for JSON Lines format
        if self._is_jsonl(sample_lines):
            self.is_jsonl = True
            return None
        
        # Try each format
        for fmt in self.FORMATS:
            matches = sum(1 for line in sample_lines if fmt.pattern.match(line.strip()))
            if matches >= len(sample_lines) * 0.5:  # 50% match threshold
                self.detected_format = fmt
                return fmt
        
        return None
    
    def _is_jsonl(self, lines: list[str]) -> bool:
        """Check if lines are JSON Lines format."""
        json_count = 0
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                json_count += 1
            except json.JSONDecodeError:
                pass
        return json_count >= min(3, len([l for l in lines if l.strip()]))
    
    def parse_line(self, line: str, line_number: int = 0, file_source: str = "") -> LogEntry:
        """Parse a single log line into LogEntry."""
        line = line.rstrip('\n\r')
        
        # Try JSON parsing first
        if self.is_jsonl:
            return self._parse_json_line(line, line_number, file_source)
        
        # Try detected format
        if self.detected_format:
            return self._parse_formatted_line(line, line_number, file_source)
        
        # Fallback: plain text
        return LogEntry(
            raw_line=line,
            message=line,
            line_number=line_number,
            file_source=file_source,
        )
    
    def _parse_json_line(self, line: str, line_number: int, file_source: str) -> LogEntry:
        """Parse JSON log line."""
        try:
            data = json.loads(line.strip())
            
            # Extract timestamp
            timestamp = None
            ts_field = data.get("timestamp") or data.get("time") or data.get("ts")
            if ts_field:
                timestamp = self._parse_timestamp(str(ts_field))
            
            # Extract level
            level = data.get("level", "INFO")
            if isinstance(level, str):
                level = level.upper()
            
            # Extract message
            message = data.get("message") or data.get("msg") or data.get("log") or str(data)
            
            # Extract source
            source = data.get("source") or data.get("logger") or data.get("component") or ""
            
            # Remaining fields as metadata
            metadata = {k: v for k, v in data.items() 
                       if k not in ("timestamp", "time", "ts", "level", "message", "msg", "log", "source", "logger")}
            
            return LogEntry(
                raw_line=line,
                timestamp=timestamp,
                level=level,
                message=str(message),
                source=str(source),
                metadata=metadata,
                line_number=line_number,
                file_source=file_source,
            )
        except (json.JSONDecodeError, ValueError):
            return LogEntry(
                raw_line=line,
                message=line,
                line_number=line_number,
                file_source=file_source,
            )
    
    def _parse_formatted_line(self, line: str, line_number: int, file_source: str) -> LogEntry:
        """Parse line using detected format."""
        fmt = self.detected_format
        match = fmt.pattern.match(line.strip())
        
        if not match:
            return LogEntry(
                raw_line=line,
                message=line,
                line_number=line_number,
                file_source=file_source,
            )
        
        # Extract timestamp
        timestamp = None
        if fmt.timestamp_group > 0:
            ts_str = match.group(fmt.timestamp_group)
            timestamp = self._parse_timestamp(ts_str)
        
        # Extract level
        level = "INFO"
        if fmt.level_group > 0 and fmt.level_group <= len(match.groups()):
            level_str = match.group(fmt.level_group)
            # For HTTP status codes
            if level_str.isdigit():
                code = int(level_str)
                if code >= 500:
                    level = "ERROR"
                elif code >= 400:
                    level = "WARNING"
                else:
                    level = "INFO"
            else:
                level = level_str.upper()
        
        # Extract message
        message = match.group(fmt.message_group) if fmt.message_group <= len(match.groups()) else line
        
        return LogEntry(
            raw_line=line,
            timestamp=timestamp,
            level=level,
            message=message,
            line_number=line_number,
            file_source=file_source,
        )
    
    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Parse timestamp string using various formats."""
        ts_str = ts_str.strip()
        
        # Try detected format first
        if self.detected_format and self.detected_format.timestamp_format:
            try:
                return datetime.strptime(ts_str, self.detected_format.timestamp_format)
            except ValueError:
                pass
        
        # Try auto-detection
        for fmt, pattern in self.TIMESTAMP_PATTERNS:
            if pattern.match(ts_str):
                try:
                    return datetime.strptime(ts_str, fmt)
                except ValueError:
                    continue
        
        # Try ISO format with various precisions
        iso_formats = [
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for fmt in iso_formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        
        return None
