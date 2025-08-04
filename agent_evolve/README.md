# Agent Evolve

A comprehensive toolkit for evolving and tracking AI agents across any codebase.

## Features

### 🔄 Generic Tracking System
- **Flexible Decorators**: `@track` and `@track_node` for any function
- **Nested Key Extraction**: Extract data from complex nested structures using dot notation, bracket notation, and array indexing
- **Operation Sequencing**: Automatic parent-child relationship tracking for function calls
- **Message Tracking**: Track conversations with role detection
- **Multiple Storage**: Memory, PostgreSQL, SQLite support (extensible)
- **Performance Optimized**: Async queue processing, batching, minimal overhead

### 🧬 Evolution Framework
- OpenEvolve integration for function and prompt optimization
- Automatic tool extraction with decorators
- Training data generation
- Evaluator creation for different function types

## Quick Start

### Installation

```bash
# From source
cd agent_evolve
pip install -e .

# Or direct import (development)
import sys
sys.path.append('/path/to/agent_evolve')
from agent_evolve import track, track_node
```

### Basic Usage

```python
from agent_evolve import track

# Simple tracking
@track()
def my_function(message: str):
    print(f"Processing: {message}")
    return {"response": "Done"}

# Advanced nested extraction
@track(
    thread_id="request.session.id",
    user_id="request.user.id", 
    message="request.data.message"
)
def api_endpoint(request):
    return {"status": "success"}
```

### LangGraph Integration

```python
from agent_evolve import track_node

@track_node()
def orchestrator_node(state, config=None):
    """Automatically extracts from LangGraph state/config"""
    # Your LangGraph node logic here
    return state
```

### Sequence Analysis

```python
from agent_evolve import get_tracker, analyze_sequences

# Get tracked operations
tracker = get_tracker()
operations = tracker._storage.get_operations(thread_id="some-thread")

# Analyze sequences
analyzer = analyze_sequences(operations)
analyzer.print_sequence("some-thread")  # Visual timeline
tree = analyzer.get_call_tree("some-thread")  # Hierarchical view
stats = analyzer.get_statistics("some-thread")  # Performance metrics
```

## Advanced Configuration

### Nested Key Extraction

The tracking system supports powerful path notation:

```python
@track(
    thread_id=[
        "config.thread_id",           # Try first
        "state.config.thread_id",     # Fallback
        "headers['X-Thread-ID']",     # Bracket notation
        "generate_from:messages[0]"   # Generate if not found
    ],
    user_id="state.user.profile.id", # Nested access
    message="state.messages[-1]",    # Array indexing
    role="kwargs.message_type"       # Function arguments
)
def complex_function(state, config, **kwargs):
    pass
```

### Custom Configuration

```python
from agent_evolve import TrackerConfig

config = TrackerConfig(
    storage="memory",  # or "postgresql://..." 
    extractors={
        "thread_id": "session.id",
        "user_id": "auth.user.id",
        "message": "body.text"
    },
    track_operations=True,
    track_messages=True,
    async_mode=True,
    batch_size=100
)

@track(config=config)
def my_function():
    pass
```

## Supported Path Formats

- **Dot notation**: `"user.profile.name"`
- **Bracket notation**: `"headers['Content-Type']"`
- **Array indexing**: `"messages[0]"` or `"messages[-1]"`
- **Mixed notation**: `"state.messages[0]['content']"`
- **Default values**: `"user.name|'Anonymous'"`
- **Generation**: `"generate_from:messages"` (creates hash-based ID)

## Use Cases

### 1. LangGraph Nodes
Track execution flow through your agent graph:

```python
@track_node()
def research_node(state):
    # Automatically tracks thread_id, messages, timing
    return {"research_data": "..."}
```

### 2. API Endpoints
Track user interactions:

```python
@track(
    thread_id="request.session_id",
    user_id="request.user.id"
)
def handle_request(request):
    return process_user_request(request)
```

### 3. Microservices
Track calls across service boundaries:

```python
@track(
    thread_id="headers.X-Trace-ID",
    user_id="jwt_payload.user_id"
)
def service_function(headers, jwt_payload, data):
    return call_downstream_service(data)
```

### 4. Nested Function Calls
Automatic call tree generation:

```python
@track(thread_id="session_id")
def parent_function(session_id):
    return child_function(session_id)  # Automatically linked

@track(thread_id="session_id") 
def child_function(session_id):
    return "result"
```

## Storage Backends

- **Memory**: `storage="memory"` (development/testing)
- **PostgreSQL**: `storage="postgresql://user:pass@host/db"` (production)
- **SQLite**: `storage="sqlite:///path/db.sqlite"` (coming soon)
- **Custom**: Implement storage interface for your needs

## Performance

- **Async Processing**: Non-blocking operation tracking
- **Batching**: Efficient bulk storage operations  
- **Minimal Overhead**: ~1-5ms per tracked function call
- **Queue Management**: Background thread processing
- **Memory Efficient**: Configurable retention policies

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI
from agent_evolve import track

app = FastAPI()

@app.post("/api/chat")
@track(
    thread_id="headers.X-Session-ID",
    user_id="current_user.id",
    message="request.message"
)
async def chat_endpoint(request, current_user):
    return {"response": "Hello!"}
```

### With Flask
```python
from flask import Flask, request
from agent_evolve import track

app = Flask(__name__)

@app.route("/process", methods=["POST"])
@track(
    thread_id="request.headers['X-Request-ID']",
    message="request.json['message']"
)
def process_request():
    return {"status": "processed"}
```

### With Django
```python
from django.http import JsonResponse
from agent_evolve import track

@track(
    thread_id="request.session.session_key",
    user_id="request.user.id"
)
def my_view(request):
    return JsonResponse({"result": "success"})
```

## Contributing

This package is part of the agent evolution toolkit. Contributions welcome!

## License

Internal use - part of the agent evolution framework.