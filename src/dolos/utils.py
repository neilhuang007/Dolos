"""Utility functions for Dolos."""

import random
from datetime import datetime, timedelta
from typing import List, Tuple
from pathlib import Path


def generate_random_intervals(
    count: int,
    min_seconds: int,
    max_seconds: int
) -> List[int]:
    """Generate random time intervals within specified bounds.

    Args:
        count: Number of intervals to generate
        min_seconds: Minimum interval in seconds
        max_seconds: Maximum interval in seconds

    Returns:
        List of random intervals in seconds
    """
    return [random.randint(min_seconds, max_seconds) for _ in range(count)]


def generate_timestamps(
    start_time: datetime,
    count: int,
    min_interval: int = 30,
    max_interval: int = 300
) -> List[datetime]:
    """Generate a list of timestamps with random intervals.

    Args:
        start_time: Starting timestamp
        count: Number of timestamps to generate
        min_interval: Minimum interval between timestamps (seconds)
        max_interval: Maximum interval between timestamps (seconds)

    Returns:
        List of datetime objects
    """
    timestamps = [start_time]
    current_time = start_time

    for _ in range(count - 1):
        interval = random.randint(min_interval, max_interval)
        current_time = current_time + timedelta(seconds=interval)
        timestamps.append(current_time)

    return timestamps


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string in various formats.

    Args:
        timestamp_str: Timestamp string

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If timestamp format is not recognized
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Could not parse timestamp: {timestamp_str}")


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted timestamp string
    """
    return dt.strftime(format_str)
