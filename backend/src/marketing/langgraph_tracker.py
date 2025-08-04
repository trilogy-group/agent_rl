"""
LangGraph Adapter for Generic Tracker

Provides backward compatibility with the old rl_tracker.py
"""

import sys
import os

# Import from the installed agent-evolve package
from agent_evolve.tracking.decorator import track_node as generic_track_node
from agent_evolve.tracking.config import TrackerConfig
from agent_evolve.config import DEFAULT_DB_PATH

# Create LangGraph-specific configuration
langgraph_config = TrackerConfig(
    storage=f"sqlite://{DEFAULT_DB_PATH}",  # SQLite storage using configured path
    extractors={
        "thread_id": [
            "state.config.thread_id",
            "config.configurable.thread_id", 
            "config.thread_id",
            "generate_from:state.messages[0].content"
        ],
        "user_id": "state.user_id",
        "message": "state.messages[-1]",
        "role": "state.messages[-1].type"
    },
    track_operations=True,
    track_messages=True,
    async_mode=True,
    batch_size=50
)

def track_node(**kwargs):
    """
    Backward-compatible track_node decorator for LangGraph.
    
    This provides the same interface as the old tracker but uses
    the new generic tracker underneath with enhanced capabilities:
    
    - Nested key extraction from state/config
    - Operation sequencing with parent-child relationships
    - Message tracking with role detection
    - Flexible storage backends
    - Performance optimizations
    
    Usage (unchanged from old tracker):
        @track_node()
        def my_node(state: AgentState):
            return state
    """
    # Use the configured LangGraph settings
    config = langgraph_config
    
    # Allow customization if needed
    if kwargs:
        custom_extractors = {}
        for key, value in kwargs.items():
            if key in ['thread_id', 'user_id', 'message', 'role']:
                custom_extractors[key] = value
        
        if custom_extractors:
            # Create a new config with custom extractors
            new_extractors = config.extractors.copy()
            new_extractors.update(custom_extractors)
            config = TrackerConfig(
                storage=config.storage,
                extractors=new_extractors,
                track_operations=config.track_operations,
                track_messages=config.track_messages,
                async_mode=config.async_mode,
                batch_size=config.batch_size
            )
    
    return generic_track_node(config=config)