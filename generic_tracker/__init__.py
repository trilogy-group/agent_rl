"""
Generic Tracker Library

A flexible tracking decorator system that can extract data from nested structures
and track function executions, messages, and custom data.
"""

from .core.decorator import track, track_node
from .core.config import TrackerConfig
from .core.tracker import Tracker, get_tracker
from .analysis.sequence import analyze_sequences

__version__ = "0.1.0"
__all__ = ["track", "track_node", "TrackerConfig", "Tracker", "get_tracker", "analyze_sequences"]