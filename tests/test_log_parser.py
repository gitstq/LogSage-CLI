"""Tests for log parser."""
import os
import tempfile
import pytest
from datetime import datetime

from logsage.core.log_parser import LogParser
from logsage.core.log_entry import LogEntry


class TestLogParser:
    """Test cases for LogParser."""
    
    def test_load_file(self):
        """Test loading a log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2025-01-15 08:30:45 INFO Test message 1\n")
            f.write("2025-01-15 08:31:12 ERROR Test message 2\n")
            f.write("2025-01-15 08:32:00 DEBUG Test message 3\n")
            temp_path = f.name
        
        try:
            parser = LogParser()
            count = parser.load_file(temp_path)
            
            assert count == 3
            assert len(parser.entries) == 3
            assert parser.error_count == 1
            assert parser.level_counts["ERROR"] == 1
            assert parser.level_counts["INFO"] == 1
        finally:
            os.unlink(temp_path)
    
    def test_filter_entries(self):
        """Test filtering entries."""
        parser = LogParser()
        
        # Add entries manually
        parser.entries = [
            LogEntry(raw_line="ERROR message", level="ERROR", message="error msg"),
            LogEntry(raw_line="INFO message", level="INFO", message="info msg"),
            LogEntry(raw_line="ERROR another", level="ERROR", message="another error"),
        ]
        
        filtered = parser.filter_entries(level="ERROR")
        assert len(filtered) == 2
        
        filtered = parser.filter_entries(pattern="another")
        assert len(filtered) == 1
    
    def test_search(self):
        """Test searching entries."""
        parser = LogParser()
        
        parser.entries = [
            LogEntry(raw_line="Database connection failed"),
            LogEntry(raw_line="User login successful"),
            LogEntry(raw_line="Database query executed"),
        ]
        
        results = parser.search("Database")
        assert len(results) == 2
        
        results = parser.search("login")
        assert len(results) == 1
    
    def test_get_errors(self):
        """Test getting error entries."""
        parser = LogParser()
        
        parser.entries = [
            LogEntry(raw_line="ERROR message", level="ERROR"),
            LogEntry(raw_line="INFO message", level="INFO"),
            LogEntry(raw_line="CRITICAL message", level="CRITICAL"),
        ]
        
        errors = parser.get_errors()
        assert len(errors) == 2
    
    def test_get_stats_summary(self):
        """Test statistics summary."""
        parser = LogParser()
        
        parser.entries = [
            LogEntry(raw_line="ERROR", level="ERROR", timestamp=datetime(2025, 1, 15, 8, 30, 0)),
            LogEntry(raw_line="INFO", level="INFO", timestamp=datetime(2025, 1, 15, 8, 31, 0)),
        ]
        parser.error_count = 1
        parser.level_counts["ERROR"] = 1
        parser.level_counts["INFO"] = 1
        
        stats = parser.get_stats_summary()
        
        assert stats["total_entries"] == 2
        assert stats["error_count"] == 1
        assert stats["level_distribution"]["ERROR"] == 1
        assert stats["level_distribution"]["INFO"] == 1
    
    def test_error_clustering(self):
        """Test error clustering."""
        parser = LogParser()
        
        parser.entries = [
            LogEntry(raw_line="", level="ERROR", message="Connection timeout to host 192.168.1.1"),
            LogEntry(raw_line="", level="ERROR", message="Connection timeout to host 192.168.1.2"),
            LogEntry(raw_line="", level="ERROR", message="Database query failed"),
            LogEntry(raw_line="", level="INFO", message="Normal operation"),
        ]
        
        clusters = parser.get_error_clusters()
        
        # Should have at least 2 clusters (connection timeouts and database error)
        assert len(clusters) >= 2
        # First cluster should have the most similar errors
        assert len(clusters[0]) >= 1
