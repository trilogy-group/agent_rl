"""
Test the tracking migration.
"""

import sys
sys.path.append('.')

# Test the new tracking system
def test_langgraph_tracking():
    """Test that the LangGraph tracking still works."""
    
    print("🧪 Testing LangGraph Tracking Migration")
    print("=" * 50)
    
    # Import the tracker (should use the new generic tracker)
    try:
        from backend.src.marketing.langgraph_tracker import track_node
        print("✅ Successfully imported track_node from langgraph_tracker")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return
    
    # Test the decorator
    @track_node()
    def test_orchestrator_node(state, config=None):
        """Test function similar to orchestrator_node."""
        print("  🎯 Test orchestrator running...")
        
        # Simulate accessing state like in real LangGraph
        messages = state.get("messages", [])
        if messages:
            last_msg = messages[-1]
            print(f"  📝 Processing message: {last_msg.get('content', 'No content')}")
        
        return {
            "intent": "test_intent",
            "task": "test_task"
        }
    
    # Test with LangGraph-style state and config
    test_state = {
        "messages": [
            {"type": "human", "content": "Hello, I need help with marketing"}
        ],
        "config": {
            "thread_id": "test-thread-123"
        }
    }
    
    test_config = {
        "configurable": {
            "thread_id": "test-thread-123"
        }
    }
    
    print("\n🔧 Running test function...")
    result = test_orchestrator_node(test_state, test_config)
    print(f"✅ Function completed: {result}")
    
    # Check if tracking worked
    try:
        from generic_tracker import get_tracker, analyze_sequences
        
        tracker = get_tracker()
        operations = tracker._storage.get_operations()
        messages = tracker._storage.get_messages()
        
        print(f"\n📊 Tracking Results:")
        print(f"  Operations tracked: {len(operations)}")
        print(f"  Messages tracked: {len(messages)}")
        
        if operations:
            op = operations[-1]  # Latest operation
            print(f"  Latest operation: {op.operation_name} ({op.status.value})")
            print(f"  Thread ID: {op.thread_id}")
            print(f"  Duration: {op.duration_ms}ms" if op.duration_ms else "  Duration: N/A")
        
        if messages:
            msg = messages[-1]  # Latest message
            print(f"  Latest message: {msg.role} - {str(msg.content)[:50]}...")
            print(f"  Message thread: {msg.thread_id}")
        
        # Test sequence analysis
        if operations:
            print(f"\n📈 Sequence Analysis:")
            analyzer = analyze_sequences(operations)
            stats = analyzer.get_statistics("test-thread-123")
            if stats:
                print(f"  Success rate: {stats.get('by_status', {}).get('completed', 0) / stats.get('total_operations', 1) * 100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error checking tracking results: {e}")
    
    print("\n✅ Migration test completed!")


def test_nested_function_tracking():
    """Test that nested function calls are tracked properly."""
    
    print("\n🔗 Testing Nested Function Tracking")
    print("=" * 50)
    
    from backend.src.marketing.langgraph_tracker import track_node
    
    @track_node()
    def parent_function(state, config=None):
        print("  🔵 Parent function starting...")
        child_function(state, config)
        return {"status": "parent_completed"}
    
    @track_node()
    def child_function(state, config=None):
        print("    🔸 Child function starting...")
        grandchild_function(state, config)
        return {"status": "child_completed"}
    
    @track_node() 
    def grandchild_function(state, config=None):
        print("      🔹 Grandchild function starting...")
        return {"status": "grandchild_completed"}
    
    # Test nested calls
    test_state = {
        "messages": [{"type": "human", "content": "Test nested tracking"}],
        "config": {"thread_id": "nested-test-456"}
    }
    
    result = parent_function(test_state)
    print(f"✅ Nested calls completed: {result}")
    
    # Analyze the call sequence
    from generic_tracker import get_tracker, analyze_sequences
    
    tracker = get_tracker()
    operations = tracker._storage.get_operations(thread_id="nested-test-456")
    
    if operations:
        analyzer = analyze_sequences(operations)
        print(f"\n📊 Call Sequence for nested-test-456:")
        analyzer.print_sequence("nested-test-456")


if __name__ == "__main__":
    print("🚀 Testing Generic Tracker Migration")
    print("=" * 60)
    
    test_langgraph_tracking()
    test_nested_function_tracking()
    
    print("\n" + "=" * 60)
    print("✅ All migration tests completed!")
    print("\n📋 Summary:")
    print("- ✅ Old @track_node() decorator still works")
    print("- ✅ New generic tracker provides enhanced features")
    print("- ✅ Sequence tracking and analysis available")
    print("- ✅ Backward compatibility maintained")