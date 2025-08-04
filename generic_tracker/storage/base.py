"""
Storage Interface for Generic Tracker

Defines the abstract base class for all storage implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..core.models import TrackedMessage, TrackedOperation


class StorageInterface(ABC):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage (create tables, connections, etc.)."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close storage connections and cleanup."""
        pass
    
    @abstractmethod
    async def store_message(self, message: TrackedMessage) -> None:
        """Store a tracked message."""
        pass
    
    @abstractmethod
    async def store_operation(self, operation: TrackedOperation) -> None:
        """Store a tracked operation."""
        pass
    
    @abstractmethod
    async def get_messages(self, 
                          thread_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          limit: int = 100) -> List[TrackedMessage]:
        """Retrieve messages with optional filters."""
        pass
    
    @abstractmethod
    async def get_operations(self,
                            thread_id: Optional[str] = None,
                            operation_name: Optional[str] = None,
                            limit: int = 100) -> List[TrackedOperation]:
        """Retrieve operations with optional filters."""
        pass
    
    @abstractmethod
    async def batch_store_messages(self, messages: List[TrackedMessage]) -> None:
        """Store multiple messages efficiently."""
        pass
    
    @abstractmethod
    async def batch_store_operations(self, operations: List[TrackedOperation]) -> None:
        """Store multiple operations efficiently."""
        pass


class SyncStorageInterface(ABC):
    """Synchronous version of the storage interface."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage (create tables, connections, etc.)."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close storage connections and cleanup."""
        pass
    
    @abstractmethod
    def store_message(self, message: TrackedMessage) -> None:
        """Store a tracked message."""
        pass
    
    @abstractmethod
    def store_operation(self, operation: TrackedOperation) -> None:
        """Store a tracked operation."""
        pass
    
    @abstractmethod
    def get_messages(self, 
                    thread_id: Optional[str] = None,
                    user_id: Optional[str] = None,
                    limit: int = 100) -> List[TrackedMessage]:
        """Retrieve messages with optional filters."""
        pass
    
    @abstractmethod
    def get_operations(self,
                      thread_id: Optional[str] = None,
                      operation_name: Optional[str] = None,
                      limit: int = 100) -> List[TrackedOperation]:
        """Retrieve operations with optional filters."""
        pass