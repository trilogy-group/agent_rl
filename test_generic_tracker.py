"""Test the generic tracker implementation."""

import sys
sys.path.append('.')

from generic_tracker import track, TrackerConfig
from generic_tracker.extractors.nested_extractor import NestedExtractor


def test_nested_extraction():
    """Test nested key extraction."""
    print("Testing Nested Extraction...")
    
    # Test data
    data = {
        "user": {"id": "user-123", "name": "John"},
        "messages": [
            {"content": "Hello", "role": "human"},
            {"content": "Hi there", "role": "assistant"}
        ],
        "config": {"thread_id": "thread-456"}
    }
    
    # Test extractions
    tests = [
        ("user.id", "user-123"),
        ("user.name", "John"),
        ("messages[0].content", "Hello"),
        ("messages[-1].role", "assistant"),
        ("config.thread_id", "thread-456"),
        ("missing.key", None)
    ]
    
    for path, expected in tests:
        result = NestedExtractor.extract(data, path)
        status = "✅" if result == expected else "❌"
        print(f"{status} {path} -> {result} (expected: {expected})")


def test_decorator():
    """Test the track decorator."""
    print("\nTesting Track Decorator...")
    
    # Simple tracking
    @track(
        thread_id="state.thread_id",
        user_id="state.user_id",
        message="state.message"
    )
    def process_state(state):
        print(f"  Processing: {state['message']}")
        return {"response": "Processed"}
    
    # Test it
    test_state = {
        "thread_id": "test-thread",
        "user_id": "test-user",
        "message": "Test message"
    }
    
    result = process_state(test_state)
    print(f"✅ Function executed successfully")
    print(f"  Result: {result}")
    
    # Check tracked data
    from generic_tracker import get_tracker
    tracker = get_tracker()
    messages = tracker._storage.get_messages()
    operations = tracker._storage.get_operations()
    
    print(f"\n📊 Tracking Results:")
    print(f"  Messages tracked: {len(messages)}")
    print(f"  Operations tracked: {len(operations)}")
    
    if messages:
        msg = messages[0]
        print(f"  Last message: {msg.content} (thread: {msg.thread_id})")
    
    if operations:
        op = operations[0]
        print(f"  Last operation: {op.operation_name} ({op.status.value})")


def test_langgraph_style():
    """Test LangGraph-style tracking."""
    print("\nTesting LangGraph-Style Tracking...")
    
    from generic_tracker import track_node
    
    @track_node()
    def orchestrator_node(state, config=None):
        """Simulate a LangGraph node."""
        print(f"  Orchestrator processing...")
        
        # Add a response message
        state["messages"].append({
            "type": "assistant",
            "content": "I'll help you with that."
        })
        
        return state
    
    # Test with LangGraph-style state
    state = {
        "messages": [
            {"type": "human", "content": "Help me plan a trip"}
        ],
        "config": {
            "thread_id": "lg-thread-123"
        }
    }
    
    config = {
        "configurable": {
            "thread_id": "lg-thread-123"
        }
    }
    
    result = orchestrator_node(state, config)
    print(f"✅ LangGraph node executed")
    print(f"  Messages in state: {len(result['messages'])}")


if __name__ == "__main__":
    print("🧪 Testing Generic Tracker System\n")
    
    test_nested_extraction()
    test_decorator()
    test_langgraph_style()
    
    print("\n✅ All tests completed!")