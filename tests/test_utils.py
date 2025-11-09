"""Tests for utility functions."""

import pytest
from datetime import datetime
from dolos.utils import (
    generate_random_intervals,
    generate_timestamps,
    parse_timestamp,
    format_timestamp
)


class TestUtils:
    """Test utility functions."""

    def test_generate_random_intervals(self):
        """Test generating random intervals."""
        intervals = generate_random_intervals(10, 30, 300)

        assert len(intervals) == 10
        for interval in intervals:
            assert 30 <= interval <= 300

    def test_generate_timestamps(self):
        """Test generating timestamps."""
        start = datetime(2025, 1, 1, 10, 0, 0)
        timestamps = generate_timestamps(start, 5, 30, 120)

        assert len(timestamps) == 5
        assert timestamps[0] == start

        # All timestamps should be in order
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]

    def test_parse_timestamp_various_formats(self):
        """Test parsing timestamps in various formats."""
        formats = [
            "2025-01-15 14:30:00",
            "2025-01-15T14:30:00",
            "2025-01-15 14:30",
            "2025-01-15",
            "2025/01/15 14:30:00",
            "2025/01/15"
        ]

        for fmt_str in formats:
            result = parse_timestamp(fmt_str)
            assert isinstance(result, datetime)

    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        with pytest.raises(ValueError):
            parse_timestamp("invalid-timestamp")

    def test_format_timestamp(self):
        """Test formatting timestamp."""
        dt = datetime(2025, 6, 15, 14, 30, 45)
        result = format_timestamp(dt)

        assert "2025" in result
        assert "06" in result or "6" in result
        assert "15" in result
