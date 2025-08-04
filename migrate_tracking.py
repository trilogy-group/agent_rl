"""
Migration script to replace old tracking with generic tracker.
"""

def migrate_graph_tracking():
    """Replace the old tracking import with the new generic tracker."""
    
    # Path to the graph file
    graph_file = "backend/src/marketing/graph.py"
    
    # Read the current file
    with open(graph_file, 'r') as f:
        content = f.read()
    
    # Replace the import
    old_import = "from src.marketing.rl_tracker import track_node"
    new_import = "from generic_tracker import track_node"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print(f"✅ Replaced import: {old_import}")
    else:
        print(f"❌ Old import not found: {old_import}")
        return
    
    # Write back the updated content
    with open(graph_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {graph_file}")
    print("📝 The existing @track_node() decorators will work unchanged!")


def create_langgraph_adapter():
    """Create a backward-compatible adapter for the old tracker."""
    
    adapter_code = '''"""
LangGraph Adapter for Generic Tracker

Provides backward compatibility with the old rl_tracker.py
"""

from generic_tracker import track_node as generic_track_node, TrackerConfig

# Create LangGraph-specific configuration
langgraph_config = TrackerConfig(
    storage="memory",  # You can change this to postgresql://... for production
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
    track_messages=True
)

def track_node(**kwargs):
    """
    Backward-compatible track_node decorator for LangGraph.
    
    This provides the same interface as the old tracker but uses
    the new generic tracker underneath.
    """
    # Merge any custom config
    config = langgraph_config
    if kwargs:
        # Override defaults with provided kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            elif key in ['thread_id', 'user_id', 'message', 'role']:
                config.extractors[key] = value
    
    return generic_track_node(config=config)
'''
    
    with open("backend/src/marketing/langgraph_tracker.py", 'w') as f:
        f.write(adapter_code)
    
    print("✅ Created langgraph_tracker.py adapter")


if __name__ == "__main__":
    print("🔄 Migrating to Generic Tracker...")
    
    # Option 1: Direct replacement (requires generic_tracker to be in path)
    print("\n1. Creating backward-compatible adapter...")
    create_langgraph_adapter()
    
    print("\n2. Choose migration approach:")
    print("   A) Direct replacement (change import to generic_tracker)")
    print("   B) Use adapter (change import to langgraph_tracker)")
    
    choice = input("\nEnter choice (A/B): ").strip().upper()
    
    if choice == 'A':
        migrate_graph_tracking()
    elif choice == 'B':
        # Update to use the adapter
        with open("backend/src/marketing/graph.py", 'r') as f:
            content = f.read()
        
        old_import = "from src.marketing.rl_tracker import track_node"
        new_import = "from src.marketing.langgraph_tracker import track_node"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            with open("backend/src/marketing/graph.py", 'w') as f:
                f.write(content)
            print("✅ Updated to use langgraph_tracker adapter")
        else:
            print("❌ Old import not found")
    else:
        print("❌ Invalid choice")
        
    print("\n✅ Migration completed!")
    print("\n📋 Next steps:")
    print("1. Test your graph functions to ensure tracking works")
    print("2. Use generic_tracker.get_tracker() to access tracked data")
    print("3. Use generic_tracker.analyze_sequences() for sequence analysis")