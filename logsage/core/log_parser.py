"""Log file parsing and indexing."""
from __future__ import annotations

import gzip
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Callable, Iterator, Optional

from .format_detector import FormatDetector
from .log_entry import LogEntry


class LogParser:
    """Parses and indexes log files."""
    
    def __init__(self):
        self.entries: list[LogEntry] = []
        self.format_detector = FormatDetector()
        self.files: list[str] = []
        self.error_count = 0
        self.warning_count = 0
        self.level_counts: Counter = Counter()
        self.source_counts: Counter = Counter()
        self.hourly_distribution: dict[int, int] = {}
        self._filtered_entries: Optional[list[LogEntry]] = None
        self._filter_pattern: Optional[str] = None
        self._filter_regex: Optional[re.Pattern] = None
        self._level_filter: Optional[str] = None
    
    def load_file(self, filepath: str, progress_callback: Optional[Callable[[int], None]] = None) -> int:
        """Load a log file and parse entries."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self.files.append(filepath)
        
        # Detect format from sample
        sample_lines = self._read_sample(filepath, 50)
        self.format_detector.detect_format(sample_lines)
        
        # Parse all lines
        count = 0
        for line_number, line in enumerate(self._read_lines(filepath), 1):
            entry = self.format_detector.parse_line(line, line_number, filepath)
            self.entries.append(entry)
            self._update_stats(entry)
            count += 1
            
            if progress_callback and count % 1000 == 0:
                progress_callback(count)
        
        # Sort by timestamp if available
        self._sort_entries()
        
        return count
    
    def load_files(self, filepaths: list[str], progress_callback: Optional[Callable[[int, int], None]] = None) -> int:
        """Load multiple log files."""
        total = 0
        for i, filepath in enumerate(filepaths):
            count = self.load_file(filepath)
            total += count
            if progress_callback:
                progress_callback(i + 1, len(filepaths))
        return total
    
    def _read_sample(self, filepath: str, n: int) -> list[str]:
        """Read sample lines from file."""
        lines = []
        for i, line in enumerate(self._read_lines(filepath)):
            if i >= n:
                break
            lines.append(line)
        return lines
    
    def _read_lines(self, filepath: str) -> Iterator[str]:
        """Read lines from file (handles compression)."""
        opener = open
        
        if filepath.endswith('.gz'):
            opener = gzip.open
            mode = 'rt'
        elif filepath.endswith(('.bz2', '.xz')):
            # Would need additional imports for these
            mode = 'r'
        else:
            mode = 'r'
        
        try:
            with opener(filepath, mode, encoding='utf-8', errors='replace') as f:
                for line in f:
                    yield line
        except UnicodeDecodeError:
            # Try with different encoding
            with opener(filepath, mode, encoding='latin-1', errors='replace') as f:
                for line in f:
                    yield line
    
    def _update_stats(self, entry: LogEntry) -> None:
        """Update statistics from entry."""
        self.level_counts[entry.level] += 1
        
        if entry.is_error:
            self.error_count += 1
        elif entry.is_warning:
            self.warning_count += 1
        
        if entry.source:
            self.source_counts[entry.source] += 1
        
        if entry.timestamp:
            hour = entry.timestamp.hour
            self.hourly_distribution[hour] = self.hourly_distribution.get(hour, 0) + 1
    
    def _sort_entries(self) -> None:
        """Sort entries by timestamp."""
        # Separate entries with and without timestamps
        with_ts = [e for e in self.entries if e.timestamp]
        without_ts = [e for e in self.entries if not e.timestamp]
        
        # Sort by timestamp
        with_ts.sort(key=lambda e: e.timestamp)
        
        # Merge back (entries without timestamps keep original order)
        self.entries = with_ts + without_ts
        
        # Update line numbers
        for i, entry in enumerate(self.entries, 1):
            entry.line_number = i
    
    def filter_entries(
        self,
        pattern: Optional[str] = None,
        regex: Optional[str] = None,
        level: Optional[str] = None,
        time_range: Optional[tuple[datetime, datetime]] = None,
        sources: Optional[list[str]] = None,
    ) -> list[LogEntry]:
        """Filter entries based on criteria."""
        filtered = self.entries.copy()
        
        if pattern:
            filtered = [e for e in filtered if e.matches(pattern)]
        
        if regex:
            compiled = re.compile(regex, re.IGNORECASE)
            filtered = [e for e in filtered if e.matches_regex(compiled)]
        
        if level:
            level = level.upper()
            filtered = [e for e in filtered if e.level.upper() == level]
        
        if time_range:
            start, end = time_range
            filtered = [
                e for e in filtered 
                if e.timestamp and start <= e.timestamp <= end
            ]
        
        if sources:
            filtered = [e for e in filtered if e.source in sources]
        
        self._filtered_entries = filtered
        return filtered
    
    def clear_filter(self) -> None:
        """Clear active filters."""
        self._filtered_entries = None
        self._filter_pattern = None
        self._filter_regex = None
        self._level_filter = None
    
    def get_entries(self, filtered: bool = True) -> list[LogEntry]:
        """Get entries (optionally filtered)."""
        if filtered and self._filtered_entries is not None:
            return self._filtered_entries
        return self.entries
    
    def get_errors(self) -> list[LogEntry]:
        """Get all error entries."""
        return [e for e in self.entries if e.is_error]
    
    def get_warnings(self) -> list[LogEntry]:
        """Get all warning entries."""
        return [e for e in self.entries if e.is_warning]
    
    def get_time_range(self) -> Optional[tuple[datetime, datetime]]:
        """Get time range of loaded logs."""
        timestamps = [e.timestamp for e in self.entries if e.timestamp]
        if not timestamps:
            return None
        return min(timestamps), max(timestamps)
    
    def search(self, query: str, case_sensitive: bool = False) -> list[LogEntry]:
        """Search entries for query string."""
        return [e for e in self.entries if e.matches(query, case_sensitive)]
    
    def get_unique_sources(self) -> list[str]:
        """Get list of unique log sources."""
        return sorted(self.source_counts.keys())
    
    def get_level_distribution(self) -> dict[str, int]:
        """Get distribution of log levels."""
        return dict(self.level_counts)
    
    def get_error_clusters(self, similarity_threshold: float = 0.8) -> list[list[LogEntry]]:
        """Cluster similar error messages."""
        errors = self.get_errors()
        if not errors:
            return []
        
        clusters: list[list[LogEntry]] = []
        
        for error in errors:
            # Normalize message for comparison
            normalized = self._normalize_message(error.message)
            
            # Find matching cluster
            found_cluster = False
            for cluster in clusters:
                cluster_normalized = self._normalize_message(cluster[0].message)
                if self._similarity(normalized, cluster_normalized) >= similarity_threshold:
                    cluster.append(error)
                    found_cluster = True
                    break
            
            if not found_cluster:
                clusters.append([error])
        
        # Sort clusters by size (largest first)
        clusters.sort(key=len, reverse=True)
        return clusters
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message for similarity comparison."""
        # Remove numbers and special characters
        normalized = re.sub(r'\d+', '#', message)
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = ' '.join(normalized.lower().split())
        return normalized
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate simple similarity between two strings."""
        if not a or not b:
            return 0.0
        
        # Simple word overlap similarity
        words_a = set(a.split())
        words_b = set(b.split())
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a & words_b
        union = words_a | words_b
        
        return len(intersection) / len(union)
    
    def export_to_json(self, filepath: str, entries: Optional[list[LogEntry]] = None) -> None:
        """Export entries to JSON file."""
        import json
        
        entries = entries or self.entries
        data = [e.to_dict() for e in entries]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def export_to_markdown(self, filepath: str, entries: Optional[list[LogEntry]] = None) -> None:
        """Export entries to Markdown file."""
        entries = entries or self.entries
        
        lines = [
            "# Log Analysis Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Total Entries: {len(entries)}",
            f"Error Count: {sum(1 for e in entries if e.is_error)}",
            f"Warning Count: {sum(1 for e in entries if e.is_warning)}",
            "",
            "## Entries",
            "",
        ]
        
        for entry in entries[:1000]:  # Limit to first 1000
            ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "N/A"
            lines.append(f"### [{entry.level}] {ts}")
            lines.append("")
            lines.append(f"```")
            lines.append(entry.message)
            lines.append(f"```")
            lines.append("")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def get_stats_summary(self) -> dict:
        """Get summary statistics."""
        time_range = self.get_time_range()
        
        return {
            "total_entries": len(self.entries),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "unique_sources": len(self.source_counts),
            "time_range": {
                "start": time_range[0].isoformat() if time_range else None,
                "end": time_range[1].isoformat() if time_range else None,
            },
            "level_distribution": dict(self.level_counts),
            "top_sources": self.source_counts.most_common(10),
            "hourly_distribution": self.hourly_distribution,
        }
