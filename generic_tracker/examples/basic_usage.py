"""
Basic Usage Examples for Generic Tracker

Demonstrates various ways to use the tracking decorator.
"""

from generic_tracker import track, TrackerConfig, get_tracker


# Example 1: Simple tracking with default configuration
@track()
def simple_function(message: str, user_id: str = "anonymous"):
    """Simple function with basic tracking."""
    print(f"Processing message from {user_id}: {message}")
    return {"response": f"Processed: {message}"}


# Example 2: Tracking with nested data extraction
@track(
    thread_id="request.session.id",
    user_id="request.user.id",
    message="request.data.message"
)
def api_endpoint(request):
    """API endpoint with request object."""
    print(f"Handling request from user {request['user']['id']}")
    return {"status": "success", "message": "Request processed"}


# Example 3: LangGraph-style state tracking
@track(
    thread_id="state.config.thread_id",
    user_id="state.user_id",
    message="state.messages[-1].content",
    role="state.messages[-1].type"
)
def agent_node(state: dict, config: dict = None):
    """LangGraph-compatible node."""
    last_message = state["messages"][-1]
    print(f"Processing message: {last_message['content']}")
    
    # Add response
    state["messages"].append({
        "type": "assistant",
        "content": "I've processed your request"
    })
    return state


# Example 4: Using full configuration
config = TrackerConfig(
    storage="memory",  # Use in-memory storage
    extractors={
        "thread_id": [
            "config.thread_id",
            "state.thread_id", 
            "generate_from:message"  # Generate from message if not found
        ],
        "user_id": "kwargs.user_id",
        "message": "0",  # First positional argument
        "role": "kwargs.role"
    },
    role_config={
        "field": "role",
        "mapping": {
            "human": ["user", "human", "customer"],
            "assistant": ["ai", "bot", "agent"]
        }
    }
)

@track(config=config)
def custom_function(message: str, user_id: str = None, role: str = "user"):
    """Function with custom configuration."""
    print(f"[{role}] {user_id}: {message}")
    return "Message received"


# Example 5: Class method tracking
class ChatBot:
    @track(
        thread_id="conversation_id",
        user_id="user.id",
        message="message.text"
    )
    def process_message(self, message: dict, user: dict, conversation_id: str):
        """Process a chat message."""
        print(f"Bot processing: {message['text']}")
        return {
            "response": f"You said: {message['text']}",
            "conversation_id": conversation_id
        }


def run_examples():
    """Run all examples."""
    print("=== Example 1: Simple tracking ===")
    simple_function("Hello world", user_id="user123")
    
    print("\n=== Example 2: API endpoint ===")
    request = {
        "session": {"id": "session-123"},
        "user": {"id": "user-456"},
        "data": {"message": "Process this request"}
    }
    api_endpoint(request)
    
    print("\n=== Example 3: LangGraph node ===")
    state = {
        "messages": [
            {"type": "human", "content": "What's the weather?"}
        ],
        "user_id": "user-789",
        "config": {"thread_id": "thread-abc"}
    }
    agent_node(state)
    
    print("\n=== Example 4: Custom config ===")
    custom_function("Custom tracked message", user_id="custom-user", role="human")
    
    print("\n=== Example 5: Class method ===")
    bot = ChatBot()
    bot.process_message(
        message={"text": "Hello bot!"},
        user={"id": "user-999"},
        conversation_id="conv-123"
    )
    
    # Show tracked data
    print("\n=== Tracked Messages ===")
    tracker = get_tracker()
    messages = tracker._storage.get_messages(limit=10)
    for msg in messages:
        print(f"[{msg.role}] Thread {msg.thread_id}: {msg.content}")
    
    print("\n=== Tracked Operations ===")
    operations = tracker._storage.get_operations(limit=10)
    for op in operations:
        print(f"{op.operation_name} ({op.status.value}) - Thread: {op.thread_id}")


if __name__ == "__main__":
    run_examples()