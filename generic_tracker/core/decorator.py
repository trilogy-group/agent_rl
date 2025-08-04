"""
Generic Track Decorator

Main decorator for tracking function executions with flexible configuration.
"""

import functools
import inspect
import time
from typing import Callable, Optional, Union, Dict, Any
from datetime import datetime
import logging

from .config import TrackerConfig
from .tracker import get_tracker, Tracker
from .models import OperationStatus, MessageRole
from .context import (
    OperationContext, get_current_operation, push_operation, 
    pop_operation, get_operation_depth, get_operation_chain
)

logger = logging.getLogger(__name__)


def track(
    config: Optional[Union[TrackerConfig, Dict[str, Any]]] = None,
    tracker: Optional[Tracker] = None,
    # Shorthand parameters for simple configuration
    thread_id: Optional[Union[str, list]] = None,
    user_id: Optional[Union[str, list]] = None,
    message: Optional[Union[str, list]] = None,
    role: Optional[Union[str, list]] = None,
    operation_name: Optional[str] = None,
    track_messages: bool = True,
    track_operations: bool = True,
):
    """
    Decorator to track function executions.
    
    Args:
        config: TrackerConfig instance or dict to create one
        tracker: Specific Tracker instance to use (otherwise uses global)
        thread_id: Path(s) to extract thread ID
        user_id: Path(s) to extract user ID
        message: Path(s) to extract message content
        role: Path(s) to extract role
        operation_name: Name for the operation (defaults to function name)
        track_messages: Whether to track messages
        track_operations: Whether to track operations
        
    Examples:
        # Using full configuration
        @track(config=TrackerConfig(
            extractors={
                "thread_id": "state.config.thread_id",
                "user_id": "state.user.id"
            }
        ))
        def process(state):
            pass
            
        # Using shorthand
        @track(
            thread_id="request.session.id",
            user_id="request.user.id",
            message="request.json.message"
        )
        def api_endpoint(request):
            pass
            
        # Using existing tracker
        my_tracker = Tracker(my_config)
        @track(tracker=my_tracker)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Create configuration
        if config is not None:
            if isinstance(config, dict):
                actual_config = TrackerConfig.from_dict(config)
            else:
                actual_config = config
        elif any([thread_id, user_id, message, role]):
            # Create from shorthand parameters
            actual_config = TrackerConfig.from_simple(
                thread_id=thread_id,
                user_id=user_id,
                message=message,
                role=role
            )
        else:
            # Use default configuration
            actual_config = TrackerConfig()
        
        # Override tracking options if specified
        if not track_messages:
            actual_config.track_messages = False
        if not track_operations:
            actual_config.track_operations = False
        
        # Get tracker instance
        actual_tracker = tracker or get_tracker(actual_config)
        
        # Get operation name
        op_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Synchronous wrapper."""
            start_time = time.time()
            operation_id = None
            context = {}
            
            try:
                # Extract tracking context
                context = actual_tracker.extract_and_track(*args, **kwargs)
                thread_id = context.get('thread_id', 'unknown')
                
                # Get parent operation context
                parent_op = get_current_operation()
                parent_id = parent_op.operation_id if parent_op else None
                depth = get_operation_depth()
                
                # Track operation start
                if actual_config.track_operations:
                    operation_id = actual_tracker.track_operation(
                        operation_name=op_name,
                        thread_id=thread_id,
                        status=OperationStatus.STARTED,
                        input_data=_safe_serialize_args(args, kwargs),
                        metadata={
                            "function": func.__name__,
                            "parent_operation_id": parent_id,
                            "depth": depth,
                            "call_chain": get_operation_chain()
                        }
                    )
                    
                    # Push operation context
                    op_context = OperationContext(
                        operation_id=operation_id,
                        operation_name=op_name,
                        thread_id=thread_id,
                        started_at=datetime.utcnow(),
                        parent_id=parent_id,
                        depth=depth
                    )
                    push_operation(op_context)
                
                # Track incoming message if configured
                if actual_config.track_messages and 'message' in context:
                    message_content = context['message']
                    role = context.get('role') or actual_tracker.detect_role(
                        message_content, context
                    )
                    
                    # Special handling for entry points (like orchestrator)
                    if op_name in ['orchestrator', 'orchestrator_node', 'entry']:
                        role = 'human'  # Assume human input at entry
                    
                    actual_tracker.track_message(
                        content=message_content,
                        role=role,
                        thread_id=thread_id,
                        user_id=context.get('user_id'),
                        metadata={"source": op_name}
                    )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Track output message if present
                if actual_config.track_messages and result:
                    output_message = None
                    output_role = 'assistant'
                    
                    # Try to extract message from result
                    if isinstance(result, dict):
                        # Look for common message fields
                        for field in ['message', 'response', 'output', 'content']:
                            if field in result:
                                output_message = result[field]
                                break
                    elif isinstance(result, str):
                        output_message = result
                    
                    if output_message:
                        actual_tracker.track_message(
                            content=output_message,
                            role=output_role,
                            thread_id=thread_id,
                            user_id=context.get('user_id'),
                            metadata={"source": op_name}
                        )
                
                # Track operation completion
                if actual_config.track_operations and operation_id:
                    duration_ms = (time.time() - start_time) * 1000
                    actual_tracker.track_operation(
                        operation_name=op_name,
                        thread_id=thread_id,
                        status=OperationStatus.COMPLETED,
                        output_data=_safe_serialize_result(result),
                        metadata={
                            "function": func.__name__,
                            "duration_ms": duration_ms,
                            "parent_operation_id": parent_id,
                            "depth": depth
                        }
                    )
                    
                    # Pop operation context
                    pop_operation()
                
                return result
                
            except Exception as e:
                # Check if it's an interruption (for LangGraph compatibility)
                if "NodeInterrupt" in str(type(e).__name__):
                    status = OperationStatus.INTERRUPTED
                else:
                    status = OperationStatus.FAILED
                
                # Track operation failure
                if actual_config.track_operations:
                    duration_ms = (time.time() - start_time) * 1000
                    actual_tracker.track_operation(
                        operation_name=op_name,
                        thread_id=context.get('thread_id', 'unknown'),
                        status=status,
                        error=str(e),
                        metadata={
                            "function": func.__name__,
                            "duration_ms": duration_ms,
                            "error_type": type(e).__name__,
                            "parent_operation_id": parent_id if 'parent_id' in locals() else None,
                            "depth": depth if 'depth' in locals() else 0
                        }
                    )
                    
                    # Pop operation context on error
                    if 'operation_id' in locals() and operation_id:
                        pop_operation()
                        
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Asynchronous wrapper."""
            # Similar to sync_wrapper but with async/await
            # TODO: Implement async version
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _safe_serialize_args(args, kwargs, max_length=1000):
    """Safely serialize function arguments for storage."""
    try:
        # Simple serialization - can be enhanced
        serialized = {
            "args": str(args)[:max_length] if args else None,
            "kwargs": str(kwargs)[:max_length] if kwargs else None
        }
        return serialized
    except:
        return {"error": "Could not serialize arguments"}


def _safe_serialize_result(result, max_length=1000):
    """Safely serialize function result for storage."""
    try:
        if result is None:
            return None
        elif isinstance(result, (str, int, float, bool)):
            return {"value": result}
        elif isinstance(result, dict):
            # Truncate large dicts
            return {k: str(v)[:100] for k, v in list(result.items())[:10]}
        else:
            return {"type": type(result).__name__, "str": str(result)[:max_length]}
    except:
        return {"error": "Could not serialize result"}


# Convenience function for LangGraph compatibility
def track_node(**kwargs):
    """
    Convenience decorator for LangGraph nodes.
    
    Automatically configures common LangGraph extraction paths.
    """
    default_config = {
        "thread_id": [
            "state.config.thread_id",
            "config.configurable.thread_id",
            "config.thread_id",
            "generate_from:state.messages[0].content"
        ],
        "user_id": "state.user_id",
        "message": "state.messages[-1]",
        "role": "state.messages[-1].type"
    }
    
    # Merge with provided kwargs
    for key, value in kwargs.items():
        if key in default_config:
            default_config[key] = value
    
    return track(**default_config)