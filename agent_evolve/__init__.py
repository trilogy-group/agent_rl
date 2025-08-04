"""
Agent Evolve Package

A comprehensive toolkit for evolving and tracking AI agents, including:
- Evolution framework with decorators and evaluation
- Generic tracking system for function calls and sequences
- Tool extraction and optimization utilities
"""

# Import tracking functionality at the top level for easy access
from .tracking import track, track_node, TrackerConfig, get_tracker, analyze_sequences

# Import evolution functionality
from .evolve_decorator import evolve

__version__ = "1.0.0"
__all__ = ["track", "track_node", "TrackerConfig", "get_tracker", "analyze_sequences", "evolve"]