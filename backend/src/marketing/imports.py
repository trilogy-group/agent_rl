"""
Import helper for agent_evolve package.

This module handles the import of agent_evolve components with proper path resolution.
"""

import sys
import os
from pathlib import Path

def setup_agent_evolve_path():
    """Add agent_evolve package to Python path if not already present."""
    
    # Get the directory where this file is located
    current_file = Path(__file__).resolve()
    
    # Navigate to the agent_evolve directory (should be ../../../agent_evolve from here)
    agent_evolve_parent = current_file.parent.parent.parent.parent
    agent_evolve_path = str(agent_evolve_parent)
    
    # Add to path if not already there
    if agent_evolve_path not in sys.path:
        sys.path.insert(0, agent_evolve_path)

# Set up the path when this module is imported
setup_agent_evolve_path()

# Now import the components we need
try:
    from agent_evolve import track_node, evolve
    print(f"✅ Successfully imported real decorators from agent_evolve")
    __all__ = ['track_node', 'evolve']
except ImportError as e:
    # Fallback - create dummy decorators that do nothing
    print(f"⚠️  Warning: Could not import agent_evolve components: {e}")
    print("🔄 Using dummy decorators...")
    
    def track_node(**kwargs):
        """Dummy track_node decorator that does nothing."""
        print(f"🟡 Dummy track_node decorator called with {kwargs}")
        def decorator(func):
            print(f"🟡 Dummy track_node decorating function: {func.__name__}")
            return func
        return decorator
    
    def evolve(**kwargs):
        """Dummy evolve decorator that does nothing."""
        print(f"🟡 Dummy evolve decorator called with {kwargs}")
        def decorator(func):
            print(f"🟡 Dummy evolve decorating function: {func.__name__}")
            return func
        return decorator
    
    __all__ = ['track_node', 'evolve']