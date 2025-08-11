# Generic Tracker

A flexible Python decorator system for tracking function executions, messages, and custom data with support for nested key extraction from complex data structures.

## Features

- **Flexible Configuration**: Extract data from nested structures using dot notation, bracket notation, and array indexing
- **Multiple Storage Backends**: In-memory, SQLite, PostgreSQL (extensible)
- **Async Support**: Both synchronous and asynchronous function tracking
- **Message Tracking**: Automatically track messages with role detection
- **Operation Tracking**: Track function executions with timing and status
- **LangGraph Compatible**: Special support for LangGraph state tracking
- **Minimal Overhead**: Async queue-based processing for performance

## Installation

```python
# Add to your Python path
import sys
sys.path.append('/path/to/generic_tracker')
```

## Quick Start

### Basic Usage

```python
from generic_tracker import track

@track()
def my_function(message: str):
    print(f"Processing: {message}")
    return {"response": "Done"}

# Call the function normally
my_function("Hello world")
```

### Nested Data Extraction

```python
@track(
    thread_id="request.session.id",
    user_id="request.user.id",
    message="request.data.message"
)
def api_endpoint(request):
    # Automatically extracts:
    # - thread_id from request['session']['id']
    # - user_id from request['user']['id']
    # - message from request['data']['message']
    return {"status": "success"}
```

### LangGraph Integration

```python
from generic_tracker import track_node

@track_node()
def orchestrator_node(state, config=None):
    """Compatible with LangGraph nodes."""
    # Automatically extracts from common LangGraph paths:
    # - thread_id from state.config.thread_id or config.configurable.thread_id
    # - messages from state.messages
    return state
```

## Configuration

### Path Notation

The tracker supports various path notations for extracting data:

- **Dot notation**: `"user.profile.name"`
- **Bracket notation**: `"headers['X-Request-ID']"`
- **Array indexing**: `"messages[0]"` or `"messages[-1]"`
- **Mixed notation**: `"state.messages[0]['content']"`
- **Default values**: `"user.name|'Anonymous'"`

### Multiple Extraction Paths

Configure fallback paths that are tried in order:

```python
from generic_tracker import TrackerConfig

config = TrackerConfig(
    extractors={
        "thread_id": [
            "config.thread_id",          # Try first
            "state.thread_id",           # Try second
            "headers['X-Thread-ID']",    # Try third
            "generate_from:messages[0]"  # Generate if not found
        ]
    }
)

@track(config=config)
def my_function(state, config=None):
    pass
```

### Role Detection

Configure how to detect message roles:

```python
config = TrackerConfig(
    role_config={
        "field": "message.role",  # Where to look for role
        "mapping": {
            "human": ["user", "human", "customer"],
            "assistant": ["ai", "assistant", "bot", "agent"]
        },
        "default": "unknown"
    }
)
```

### Storage Configuration

```python
# In-memory storage (default)
config = TrackerConfig(storage="memory")

# SQLite (coming soon)
config = TrackerConfig(storage="sqlite:///tracking.db")

# PostgreSQL (coming soon)
config = TrackerConfig(storage="postgresql://user:pass@host/db")
```

## Advanced Usage

### Custom Configuration

```python
config = TrackerConfig(
    # Storage settings
    storage="memory",
    
    # Extraction paths
    extractors={
        "thread_id": "session.id",
        "user_id": "auth.user.id",
        "message": "body.text",
        "role": "body.sender_type"
    },
    
    # What to track
    track_operations=True,
    track_messages=True,
    track_custom_fields=["request.ip", "request.user_agent"],
    
    # Performance settings
    async_mode=True,
    batch_size=100
)

@track(config=config)
def process_request(session, auth, body):
    pass
```

### Class Method Tracking

```python
class ChatBot:
    @track(
        thread_id="conversation_id",
        user_id="user.id",
        message="message.text"
    )
    def process_message(self, message, user, conversation_id):
        return {"response": "Processed"}
```

### Accessing Tracked Data

```python
from generic_tracker import get_tracker

# Get the global tracker instance
tracker = get_tracker()

# Retrieve messages
messages = tracker._storage.get_messages(
    thread_id="specific-thread",
    limit=50
)

# Retrieve operations
operations = tracker._storage.get_operations(
    operation_name="process_message",
    limit=20
)
```

## API Reference

### Decorators

- `@track()` - Main tracking decorator
- `@track_node()` - LangGraph-compatible decorator

### Configuration

- `TrackerConfig` - Main configuration class
- `RoleConfig` - Role detection configuration

### Models

- `TrackedMessage` - Message data model
- `TrackedOperation` - Operation data model
- `OperationStatus` - Operation status enum
- `MessageRole` - Message role enum

### Core Classes

- `Tracker` - Main tracker class
- `NestedExtractor` - Nested key extraction utility
- `PathExtractor` - Path extraction with fallbacks

## Examples

See the `examples/` directory for more detailed examples:
- `basic_usage.py` - Various usage patterns
- More examples coming soon...

## Extension Points

The system is designed to be extensible:

1. **Storage Backends**: Implement `StorageInterface` for new backends
2. **Extraction Strategies**: Add new strategies like `generate_from:`
3. **Role Detection**: Customize role detection logic
4. **Message Formats**: Handle different message structures

## Performance Considerations

- Uses async queue processing to minimize impact on function execution
- Batches storage operations for efficiency
- Configurable batch size and processing intervals
- In-memory storage for testing/development
- Production-ready storage backends coming soon

## Roadmap

- [ ] SQLite storage implementation
- [ ] PostgreSQL storage implementation  
- [ ] Redis storage implementation
- [ ] Elasticsearch storage implementation
- [ ] Additional extraction strategies (JSONPath, XPath)
- [ ] Metrics and monitoring integration
- [ ] REST API for querying tracked data
- [ ] Web UI for visualization

## Contributing

This is an internal tool, but suggestions and improvements are welcome!

## License

Internal use only.