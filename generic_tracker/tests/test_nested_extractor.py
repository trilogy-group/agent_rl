"""
Tests for Nested Extractor

Verify that nested key extraction works correctly.
"""

import pytest
from generic_tracker.extractors.nested_extractor import NestedExtractor, PathExtractor


def test_simple_dot_notation():
    """Test simple dot notation extraction."""
    obj = {"user": {"name": "John", "id": 123}}
    
    assert NestedExtractor.extract(obj, "user.name") == "John"
    assert NestedExtractor.extract(obj, "user.id") == 123
    assert NestedExtractor.extract(obj, "user.missing", "default") == "default"


def test_bracket_notation():
    """Test bracket notation extraction."""
    obj = {"headers": {"X-Request-ID": "req-123", "Content-Type": "json"}}
    
    assert NestedExtractor.extract(obj, "headers['X-Request-ID']") == "req-123"
    assert NestedExtractor.extract(obj, 'headers["Content-Type"]') == "json"


def test_array_indexing():
    """Test array index extraction."""
    obj = {"messages": [
        {"content": "first", "role": "user"},
        {"content": "second", "role": "assistant"},
        {"content": "third", "role": "user"}
    ]}
    
    assert NestedExtractor.extract(obj, "messages[0].content") == "first"
    assert NestedExtractor.extract(obj, "messages[-1].content") == "third"
    assert NestedExtractor.extract(obj, "messages[1].role") == "assistant"


def test_mixed_notation():
    """Test mixed notation extraction."""
    obj = {
        "state": {
            "messages": [
                {"id": 1, "data": {"content": "Hello"}},
                {"id": 2, "data": {"content": "World"}}
            ]
        }
    }
    
    assert NestedExtractor.extract(obj, "state.messages[0].data.content") == "Hello"
    assert NestedExtractor.extract(obj, "state.messages[-1]['data']['content']") == "World"


def test_default_values():
    """Test default value handling."""
    obj = {"name": "test"}
    
    assert NestedExtractor.extract(obj, "missing|'default'") == "default"
    assert NestedExtractor.extract(obj, "name|'default'") == "test"
    assert NestedExtractor.extract(obj, "missing", "fallback") == "fallback"


def test_path_extractor():
    """Test PathExtractor with multiple paths."""
    extractor = PathExtractor([
        "config.thread_id",
        "state.thread_id",
        "thread_id",
        "generate_from:message"
    ])
    
    # Test with different argument structures
    result = extractor.extract(
        {"state": {"thread_id": "found-in-state"}},
        config={"thread_id": "found-in-config"}
    )
    assert result == "found-in-config"  # First path wins
    
    # Test fallback
    result = extractor.extract(
        {"message": "Hello world"},
        other="data"
    )
    assert result is not None  # Should generate from message
    assert len(result) == 16  # Generated ID length


def test_attribute_access():
    """Test attribute access on objects."""
    class TestObj:
        def __init__(self):
            self.name = "test"
            self.nested = type('obj', (object,), {'value': 42})()
    
    obj = TestObj()
    assert NestedExtractor.extract(obj, "name") == "test"
    assert NestedExtractor.extract(obj, "nested.value") == 42


def test_complex_real_world_example():
    """Test with a complex real-world data structure."""
    langchain_state = {
        "messages": [
            {
                "type": "human",
                "content": "What's the weather?",
                "id": "msg-123",
                "metadata": {"user_id": "user-456"}
            }
        ],
        "config": {
            "configurable": {
                "thread_id": "thread-789",
                "session_id": "session-abc"
            }
        },
        "user": {
            "id": "user-456",
            "profile": {"name": "John Doe"}
        }
    }
    
    # Various extraction tests
    assert NestedExtractor.extract(langchain_state, "config.configurable.thread_id") == "thread-789"
    assert NestedExtractor.extract(langchain_state, "messages[-1].content") == "What's the weather?"
    assert NestedExtractor.extract(langchain_state, "messages[0].metadata.user_id") == "user-456"
    assert NestedExtractor.extract(langchain_state, "user.profile.name") == "John Doe"


if __name__ == "__main__":
    # Run basic tests
    test_simple_dot_notation()
    test_bracket_notation()
    test_array_indexing()
    test_mixed_notation()
    test_default_values()
    test_path_extractor()
    test_attribute_access()
    test_complex_real_world_example()
    print("✅ All tests passed!")