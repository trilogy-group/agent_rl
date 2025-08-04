"""
In-Memory Storage Implementation

Simple storage that keeps everything in memory.
Useful for testing and lightweight usage.
"""

from typing import List, Optional, Dict
from collections import defaultdict
import asyncio
from ..core.models import TrackedMessage, TrackedOperation
from .base import StorageInterface, SyncStorageInterface


class MemoryStorage(StorageInterface):
    """Async in-memory storage implementation."""
    
    def __init__(self):
        self.messages: List[TrackedMessage] = []
        self.operations: List[TrackedOperation] = []
        self.messages_by_thread: Dict[str, List[TrackedMessage]] = defaultdict(list)
        self.operations_by_thread: Dict[str, List[TrackedOperation]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """No initialization needed for memory storage."""
        pass
    
    async def close(self) -> None:
        """No cleanup needed for memory storage."""
        pass
    
    async def store_message(self, message: TrackedMessage) -> None:
        """Store a message in memory."""
        async with self._lock:
            self.messages.append(message)
            self.messages_by_thread[message.thread_id].append(message)
    
    async def store_operation(self, operation: TrackedOperation) -> None:
        """Store an operation in memory."""
        async with self._lock:
            self.operations.append(operation)
            self.operations_by_thread[operation.thread_id].append(operation)
    
    async def get_messages(self, 
                          thread_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          limit: int = 100) -> List[TrackedMessage]:
        """Retrieve messages with filters."""
        async with self._lock:
            if thread_id:
                messages = self.messages_by_thread.get(thread_id, [])
            else:
                messages = self.messages
            
            if user_id:
                messages = [m for m in messages if m.user_id == user_id]
            
            return messages[-limit:]
    
    async def get_operations(self,
                            thread_id: Optional[str] = None,
                            operation_name: Optional[str] = None,
                            limit: int = 100) -> List[TrackedOperation]:
        """Retrieve operations with filters."""
        async with self._lock:
            if thread_id:
                operations = self.operations_by_thread.get(thread_id, [])
            else:
                operations = self.operations
            
            if operation_name:
                operations = [o for o in operations if o.operation_name == operation_name]
            
            return operations[-limit:]
    
    async def batch_store_messages(self, messages: List[TrackedMessage]) -> None:
        """Store multiple messages."""
        async with self._lock:
            for message in messages:
                self.messages.append(message)
                self.messages_by_thread[message.thread_id].append(message)
    
    async def batch_store_operations(self, operations: List[TrackedOperation]) -> None:
        """Store multiple operations."""
        async with self._lock:
            for operation in operations:
                self.operations.append(operation)
                self.operations_by_thread[operation.thread_id].append(operation)


class SyncMemoryStorage(SyncStorageInterface):
    """Synchronous in-memory storage implementation."""
    
    def __init__(self):
        self.messages: List[TrackedMessage] = []
        self.operations: List[TrackedOperation] = []
        self.messages_by_thread: Dict[str, List[TrackedMessage]] = defaultdict(list)
        self.operations_by_thread: Dict[str, List[TrackedOperation]] = defaultdict(list)
    
    def initialize(self) -> None:
        """No initialization needed for memory storage."""
        pass
    
    def close(self) -> None:
        """No cleanup needed for memory storage."""
        pass
    
    def store_message(self, message: TrackedMessage) -> None:
        """Store a message in memory."""
        self.messages.append(message)
        self.messages_by_thread[message.thread_id].append(message)
    
    def store_operation(self, operation: TrackedOperation) -> None:
        """Store an operation in memory."""
        self.operations.append(operation)
        self.operations_by_thread[operation.thread_id].append(operation)
    
    def get_messages(self, 
                    thread_id: Optional[str] = None,
                    user_id: Optional[str] = None,
                    limit: int = 100) -> List[TrackedMessage]:
        """Retrieve messages with filters."""
        if thread_id:
            messages = self.messages_by_thread.get(thread_id, [])
        else:
            messages = self.messages
        
        if user_id:
            messages = [m for m in messages if m.user_id == user_id]
        
        return messages[-limit:]
    
    def get_operations(self,
                      thread_id: Optional[str] = None,
                      operation_name: Optional[str] = None,
                      limit: int = 100) -> List[TrackedOperation]:
        """Retrieve operations with filters."""
        if thread_id:
            operations = self.operations_by_thread.get(thread_id, [])
        else:
            operations = self.operations
        
        if operation_name:
            operations = [o for o in operations if o.operation_name == operation_name]
        
        return operations[-limit:]