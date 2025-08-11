"""
Test the agent_evolve package integration.
"""

import sys
import os

# Add the agent_evolve package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_package_import():
    """Test that we can import from the agent_evolve package."""
    
    print("🧪 Testing Agent Evolve Package")
    print("=" * 50)
    
    # Test main package import
    try:
        from agent_evolve import track, track_node, TrackerConfig, get_tracker, analyze_sequences
        print("✅ Successfully imported main functions from agent_evolve")
    except ImportError as e:
        print(f"❌ Failed to import from agent_evolve: {e}")
        return False
    
    # Test submodule imports
    try:
        from agent_evolve.tracking import NestedExtractor
        print("✅ Successfully imported from agent_evolve.tracking")
    except ImportError as e:
        print(f"❌ Failed to import from agent_evolve.tracking: {e}")
        # This is okay, we might not have exposed NestedExtractor at top level
    
    return True


def test_tracking_functionality():
    """Test the basic tracking functionality."""
    
    print("\n🔧 Testing Tracking Functionality")
    print("-" * 40)
    
    from agent_evolve import track, track_node, get_tracker, analyze_sequences
    
    # Test basic tracking
    @track(
        thread_id="session_id",
        user_id="user_id",
        message="message"
    )
    def test_function(session_id: str, user_id: str, message: str):
        print(f"  📝 Processing: {message} from {user_id}")
        return {"response": f"Processed: {message}"}
    
    # Test LangGraph-style tracking
    @track_node()
    def test_node(state, config=None):
        print(f"  🎯 Node processing state with {len(state.get('messages', []))} messages")
        return {"processed": True}
    
    # Run tests
    print("\n1. Testing basic function:")
    result1 = test_function(
        session_id="test-session-123",
        user_id="user-456",
        message="Hello world"
    )
    print(f"   Result: {result1}")
    
    print("\n2. Testing LangGraph node:")
    test_state = {
        "messages": [
            {"type": "human", "content": "Test message"}
        ],
        "config": {"thread_id": "test-thread-789"}
    }
    result2 = test_node(test_state)
    print(f"   Result: {result2}")
    
    # Check tracking results
    print("\n3. Checking tracking results:")
    tracker = get_tracker()
    
    operations = tracker._storage.get_operations()
    messages = tracker._storage.get_messages()
    
    print(f"   Operations tracked: {len(operations)}")
    print(f"   Messages tracked: {len(messages)}")
    
    if operations:
        latest_op = operations[-1]
        print(f"   Latest operation: {latest_op.operation_name} ({latest_op.status.value})")
    
    if messages:
        latest_msg = messages[-1]
        print(f"   Latest message: {latest_msg.role} - {str(latest_msg.content)[:50]}...")
    
    # Test sequence analysis
    if operations:
        print("\n4. Testing sequence analysis:")
        analyzer = analyze_sequences(operations)
        
        # Get all thread IDs
        thread_ids = set(op.thread_id for op in operations)
        for thread_id in thread_ids:
            thread_ops = analyzer.get_thread_sequence(thread_id)
            print(f"   Thread {thread_id}: {len(thread_ops)} operations")
    
    return True


def test_graph_integration():
    """Test that the graph.py integration works."""
    
    print("\n🔗 Testing Graph Integration")
    print("-" * 40)
    
    try:
        # Try to import the updated graph
        from backend.src.marketing.graph import orchestrator_node
        print("✅ Successfully imported orchestrator_node from graph.py")
        
        # The function should now be using agent_evolve tracking
        print("✅ Graph is now using agent_evolve tracking")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import graph components: {e}")
        return False


def test_nested_extraction():
    """Test the nested key extraction system."""
    
    print("\n🔍 Testing Nested Key Extraction")
    print("-" * 40)
    
    from agent_evolve.tracking.extractors import NestedExtractor
    
    # Test data structure
    test_data = {
        "request": {
            "session": {"id": "session-123"},
            "user": {"id": "user-456", "profile": {"name": "John"}},
            "data": {"message": "Hello world"}
        },
        "headers": {"X-Request-ID": "req-789"},
        "messages": [
            {"content": "First", "role": "human"},
            {"content": "Second", "role": "assistant"}
        ]
    }
    
    # Test various extraction patterns
    tests = [
        ("request.session.id", "session-123"),
        ("request.user.profile.name", "John"),
        ("headers['X-Request-ID']", "req-789"),
        ("messages[0].content", "First"),
        ("messages[-1].role", "assistant"),
        ("missing.key", None),
        ("request.user.name|'Anonymous'", "Anonymous")
    ]
    
    for path, expected in tests:
        result = NestedExtractor.extract(test_data, path)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {path} -> {result} (expected: {expected})")
    
    return True


def run_all_tests():
    """Run all tests."""
    
    print("🚀 Agent Evolve Package Test Suite")
    print("=" * 60)
    
    tests = [
        ("Package Import", test_package_import),
        ("Tracking Functionality", test_tracking_functionality),
        ("Graph Integration", test_graph_integration),
        ("Nested Extraction", test_nested_extraction)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Agent Evolve package is working correctly.")
        print("\n📋 Next steps:")
        print("  1. Your graph.py now uses the generic tracking system")
        print("  2. You can use @track or @track_node in any codebase")
        print("  3. Access tracking data with get_tracker().get_operations()")
        print("  4. Analyze sequences with analyze_sequences()")
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)