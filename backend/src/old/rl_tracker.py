import asyncio
import asyncpg
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from queue import Queue
import threading
from contextlib import asynccontextmanager
from functools import wraps
from langgraph.graph import get_config
from langgraph.errors import GraphInterrupt
import hashlib

logger = logging.getLogger(__name__)

def make_serializable(obj):
    """Convert objects to JSON-serializable format"""
    if obj is None:
        return None
    
    # Handle LangChain message objects
    if hasattr(obj, 'type') and hasattr(obj, 'content'):
        return {
            'type': obj.type,
            'content': obj.content,
            'class_name': obj.__class__.__name__
        }
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    
    # Handle lists
    if isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    
    # Handle primitive types
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # Handle datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # For everything else, convert to string
    return str(obj)

@dataclass
class MessageLog:
    """Data structure for tracking individual messages"""
    thread_id: str
    message_type: str  # 'human', 'ai', 'system'
    message_content: str
    sequence_id: Optional[int] = None  # Auto-incremented per thread
    in_reply_to_id: Optional[int] = None  # References sequence_id of message being replied to
    node_name: Optional[str] = None
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class OperationLog:
    """Data structure for tracking operations/nodes executed"""
    thread_id: str
    operation_name: str  # node name or operation identifier
    operation_type: str  # 'node', 'tool', 'function'
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    status: str = 'completed'  # 'started', 'completed', 'failed'
    error_message: Optional[str] = None
    sequence_order: Optional[int] = None  # Order within the thread processing
    triggered_by_message_id: Optional[int] = None  # Which message triggered this operation
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class RLTracker:
    """
    Reinforcement Learning Tracker for monitoring agent exchanges.
    Handles asynchronous queuing, database storage, and exchange evaluation.
    """
    
    def __init__(self, postgres_url: str = None):
        self.postgres_url = postgres_url or os.getenv('POSTGRES_URL')
        if not self.postgres_url:
            raise ValueError("POSTGRES_URL environment variable is required")
            
        self.message_queue = Queue()
        self.operation_queue = Queue()
        self.processing_thread = None
        self.running = False
        self.pool = None
        
        # Start the async processor
        self._start_processor()
        
    async def _init_db_pool(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            await self._create_tables()
            logger.info("Database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def _create_tables(self):
        """Create necessary database tables"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS message_log (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) NOT NULL,
            message_type VARCHAR(50) NOT NULL, -- 'human', 'ai', 'system'
            message_content TEXT NOT NULL,
            sequence_id INTEGER, -- Auto-incremented per thread
            in_reply_to_id INTEGER, -- References sequence_id of message being replied to
            node_name VARCHAR(100),
            intent VARCHAR(100),
            metadata JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS operation_log (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) NOT NULL,
            operation_name VARCHAR(255) NOT NULL,
            operation_type VARCHAR(50) NOT NULL, -- 'node', 'tool', 'function'
            input_data JSONB DEFAULT '{}',
            output_data JSONB DEFAULT '{}',
            duration_ms FLOAT,
            status VARCHAR(50) DEFAULT 'completed', -- 'started', 'completed', 'failed'
            error_message TEXT,
            sequence_order INTEGER, -- Order within thread processing
            triggered_by_message_id INTEGER, -- Which message triggered this operation
            metadata JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON message_log(thread_id);
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON message_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_messages_type ON message_log(message_type);
        CREATE INDEX IF NOT EXISTS idx_messages_sequence ON message_log(thread_id, sequence_id);
        CREATE INDEX IF NOT EXISTS idx_messages_reply ON message_log(in_reply_to_id);
        
        CREATE INDEX IF NOT EXISTS idx_operations_thread_id ON operation_log(thread_id);
        CREATE INDEX IF NOT EXISTS idx_operations_timestamp ON operation_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_operations_sequence ON operation_log(thread_id, sequence_order);
        CREATE INDEX IF NOT EXISTS idx_operations_triggered_by ON operation_log(triggered_by_message_id);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table_sql)
            logger.info("Database tables created/verified")
    
    def _start_processor(self):
        """Start the background processing thread"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        logger.info("Exchange processor thread started")
    
    def _process_queue(self):
        """Background thread that processes queued exchanges"""
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._async_processor())
        except Exception as e:
            logger.error(f"Error in queue processor: {e}")
        finally:
            loop.close()
    
    async def _async_processor(self):
        """Async processor that handles database operations"""
        await self._init_db_pool()
        
        while self.running:
            try:
                # Process messages
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    await self._store_message(message)
                # Process operations
                elif not self.operation_queue.empty():
                    operation = self.operation_queue.get_nowait()
                    await self._store_operation(operation)
                else:
                    await asyncio.sleep(0.1)  # Small delay when queues are empty
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _store_message(self, message: MessageLog):
        """Store message in database with auto-incremented sequence_id"""
        try:
            # Get next sequence_id for this thread
            if message.sequence_id is None:
                sequence_sql = """
                SELECT COALESCE(MAX(sequence_id), 0) + 1 as next_seq 
                FROM message_log WHERE thread_id = $1
                """
                async with self.pool.acquire() as conn:
                    result = await conn.fetchrow(sequence_sql, message.thread_id)
                    message.sequence_id = result['next_seq']
            
            insert_sql = """
            INSERT INTO message_log (
                thread_id, message_type, message_content, sequence_id, in_reply_to_id,
                node_name, intent, metadata, timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, sequence_id
            """
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    insert_sql,
                    message.thread_id,
                    message.message_type,
                    message.message_content,
                    message.sequence_id,
                    message.in_reply_to_id,
                    message.node_name,
                    message.intent,
                    json.dumps(make_serializable(message.metadata)),
                    message.timestamp
                )
                
            logger.debug(f"Stored message {result['id']} (seq:{result['sequence_id']}) for thread {message.thread_id}")
            return result['id'], result['sequence_id']
            
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            return None, None

    async def _store_operation(self, operation: OperationLog):
        """Store operation in database"""
        try:
            # Get next sequence_order for this thread if not set
            if operation.sequence_order is None:
                sequence_sql = """
                SELECT COALESCE(MAX(sequence_order), 0) + 1 as next_seq 
                FROM operation_log WHERE thread_id = $1
                """
                async with self.pool.acquire() as conn:
                    result = await conn.fetchrow(sequence_sql, operation.thread_id)
                    operation.sequence_order = result['next_seq']
            
            insert_sql = """
            INSERT INTO operation_log (
                thread_id, operation_name, operation_type, input_data, output_data,
                duration_ms, status, error_message, sequence_order, triggered_by_message_id,
                metadata, timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    insert_sql,
                    operation.thread_id,
                    operation.operation_name,
                    operation.operation_type,
                    json.dumps(make_serializable(operation.input_data or {})),
                    json.dumps(make_serializable(operation.output_data or {})),
                    operation.duration_ms,
                    operation.status,
                    operation.error_message,
                    operation.sequence_order,
                    operation.triggered_by_message_id,
                    json.dumps(make_serializable(operation.metadata)),
                    operation.timestamp
                )
                
            logger.debug(f"Stored operation {result['id']} ({operation.operation_name}) for thread {operation.thread_id}")
            return result['id']
            
        except Exception as e:
            logger.error(f"Failed to store operation: {e}")
            return None

    # Public interface methods
    
    def track_message(self, thread_id: str, message_type: str, message_content: str,
                     sequence_id: int = None, in_reply_to_id: int = None,
                     node_name: str = None, intent: str = None, metadata: Dict[str, Any] = None):
        """Track a message (human, ai, system) in sequential order"""
        message = MessageLog(
            thread_id=thread_id,
            message_type=message_type,
            message_content=message_content,
            sequence_id=sequence_id,
            in_reply_to_id=in_reply_to_id,
            node_name=node_name,
            intent=intent,
            metadata=metadata or {}
        )
        
        self.message_queue.put(message)
        logger.debug(f"Queued message for thread {thread_id}")

    def track_operation(self, thread_id: str, operation_name: str, operation_type: str = 'node',
                       input_data: Dict[str, Any] = None, output_data: Dict[str, Any] = None,
                       duration_ms: float = None, status: str = 'completed',
                       error_message: str = None, triggered_by_message_id: int = None,
                       metadata: Dict[str, Any] = None):
        """Track an operation/node execution"""
        operation = OperationLog(
            thread_id=thread_id,
            operation_name=operation_name,
            operation_type=operation_type,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message,
            triggered_by_message_id=triggered_by_message_id,
            metadata=metadata or {}
        )
        
        logger.info(f"Queued operation {operation_name} for thread {thread_id}")
        self.operation_queue.put(operation)
        logger.info(f"Queued operation done {operation_name} for thread {thread_id}")
        logger.debug(f"Queued operation {operation_name} for thread {thread_id}")
    
    def shutdown(self):
        """Clean shutdown of the tracker"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        if self.pool:
            asyncio.create_task(self.pool.close())
        logger.info("RL Tracker shutdown complete")


# Global tracker instance (singleton pattern)
_tracker_instance = None

def get_rl_tracker() -> RLTracker:
    """Get the global RL tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = RLTracker()
    return _tracker_instance

def track_message(thread_id: str, message_type: str, message_content: str,
                 sequence_id: int = None, in_reply_to_id: int = None,
                 node_name: str = None, intent: str = None, metadata: Dict[str, Any] = None):
    """Convenience function for tracking messages in sequence"""
    tracker = get_rl_tracker()
    tracker.track_message(thread_id, message_type, message_content, sequence_id, in_reply_to_id, node_name, intent, metadata)

def track_operation(thread_id: str, operation_name: str, operation_type: str = 'node',
                   input_data: Dict[str, Any] = None, output_data: Dict[str, Any] = None,
                   duration_ms: float = None, status: str = 'completed',
                   error_message: str = None, triggered_by_message_id: int = None,
                   metadata: Dict[str, Any] = None):
    """Convenience function for tracking operations"""
    tracker = get_rl_tracker()
    tracker.track_operation(thread_id, operation_name, operation_type, input_data, output_data,
                           duration_ms, status, error_message, triggered_by_message_id, metadata)

# Decorator for automatic node tracking
def track_node(node_name: str = None):
    """Decorator to automatically track node execution and messages"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state, *args, **kwargs):
            # Try to get thread_id from various sources
            thread_id = 'default'
            
            # Method 1: Check if thread_id is in state
            if isinstance(state, dict) and 'thread_id' in state:
                thread_id = str(state['thread_id'])
            # Method 2: Check kwargs for config
            elif 'config' in kwargs:
                config = kwargs['config']
                if hasattr(config, 'configurable'):
                    thread_id = str(config.configurable.get('thread_id', 'default'))
                elif isinstance(config, dict):
                    thread_id = str(config.get('configurable', {}).get('thread_id', 'default'))
            # Method 3: Try to import and get from LangGraph context
            else:
                try:

                    config = get_config()
                    if config and hasattr(config, 'configurable'):
                        thread_id = str(config.configurable.get('thread_id', 'default'))
                except:
                    # Fallback: generate consistent ID from message content
                    if isinstance(state, dict) and 'messages' in state and state['messages']:
                        last_message = state['messages'][-1]
                        content = getattr(last_message, 'content', str(last_message))
                        thread_id = hashlib.md5(content.encode()).hexdigest()[:8]
            
            actual_node_name = node_name or func.__name__
            
            # Track incoming human message only at orchestrator (entry point)
            if actual_node_name == 'orchestrator_node' and 'messages' in state and state['messages']:
                last_message = state['messages'][-1]
                if hasattr(last_message, 'type') and last_message.type == 'human':
                    track_message(
                        thread_id=thread_id,
                        message_type='human', 
                        message_content=last_message.content,
                        node_name=actual_node_name
                    )
            
            # Track operation start
            start_time = time.time()
            
            try:
                # Execute the original function
                result = func(state, *args, **kwargs)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Track successful operation
                track_operation(
                    thread_id=thread_id,
                    operation_name=actual_node_name,
                    operation_type='node',
                    input_data=state if isinstance(state, dict) else {'state': str(state)},
                    output_data=result if isinstance(result, dict) else {'result': str(result)},
                    duration_ms=duration_ms,
                    status='completed'
                )
                
                # Track outgoing AI message if the result contains messages
                if isinstance(result, dict) and 'messages' in result and result['messages']:
                    ai_message = result['messages'][-1]
                    if hasattr(ai_message, 'content'):
                        # Find the last human message sequence to reply to
                        human_seq_id = None
                        if 'messages' in state and state['messages']:
                            for msg in reversed(state['messages']):
                                if hasattr(msg, 'type') and msg.type == 'human':
                                    # This is a simplified approach - in reality you'd need to get the actual sequence_id
                                    human_seq_id = 1  # placeholder
                                    break
                        
                        track_message(
                            thread_id=thread_id,
                            message_type='ai',
                            message_content=ai_message.content,
                            in_reply_to_id=human_seq_id,
                            node_name=actual_node_name
                        )
                
                return result
                
            except Exception as e:
                # Calculate duration even for failed operations
                duration_ms = (time.time() - start_time) * 1000
                
                # Check if this is an interrupt (not a failure)
                is_interrupt = False
                try:
                    is_interrupt = isinstance(e, GraphInterrupt)
                except ImportError:
                    # Fallback: check if exception message contains interrupt indicators
                    error_str = str(e).lower()
                    is_interrupt = 'interrupt' in error_str or 'human' in error_str
                
                # Track operation with appropriate status
                if is_interrupt:
                    track_operation(
                        thread_id=thread_id,
                        operation_name=actual_node_name,
                        operation_type='node',
                        input_data=state if isinstance(state, dict) else {'state': str(state)},
                        duration_ms=duration_ms,
                        status='interrupted',
                        error_message=f"Human input required: {str(e)}"
                    )
                else:
                    track_operation(
                        thread_id=thread_id,
                        operation_name=actual_node_name,
                        operation_type='node',
                        input_data=state if isinstance(state, dict) else {'state': str(state)},
                        duration_ms=duration_ms,
                        status='failed',
                        error_message=str(e)
                    )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator