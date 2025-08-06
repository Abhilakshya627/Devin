"""
Memory management for the Devin AI Assistant using mem0.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Memory:
    """Represents a memory item."""
    content: str
    timestamp: datetime
    type: str  # 'user_preference', 'fact', 'conversation', 'reminder'
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class MemoryManager:
    """Enhanced memory management for the AI agent."""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.memories: List[Memory] = []
        self._ensure_memory_dir()
        self._load_memories()
    
    def _ensure_memory_dir(self):
        """Create memory directory if it doesn't exist."""
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def _load_memories(self):
        """Load existing memories from files."""
        try:
            memory_file = os.path.join(self.memory_dir, "memories.json")
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    self.memories = [Memory.from_dict(mem) for mem in data]
                logger.info(f"Loaded {len(self.memories)} memories")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            self.memories = []
    
    def _save_memories(self):
        """Save memories to file."""
        try:
            memory_file = os.path.join(self.memory_dir, "memories.json")
            with open(memory_file, 'w') as f:
                json.dump([mem.to_dict() for mem in self.memories], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    def add_memory(self, content: str, memory_type: str = "conversation", metadata: Optional[Dict[str, Any]] = None):
        """Add a new memory."""
        memory = Memory(
            content=content,
            timestamp=datetime.now(),
            type=memory_type,
            metadata=metadata or {}
        )
        self.memories.append(memory)
        self._save_memories()
        logger.info(f"Added {memory_type} memory: {content[:50]}...")
    
    def get_memories(self, memory_type: Optional[str] = None, limit: int = 10) -> List[Memory]:
        """Get recent memories, optionally filtered by type."""
        filtered_memories = self.memories
        
        if memory_type:
            filtered_memories = [m for m in self.memories if m.type == memory_type]
        
        # Sort by timestamp (most recent first) and limit
        sorted_memories = sorted(filtered_memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:limit]
    
    def search_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Search memories by content."""
        query_lower = query.lower()
        matching_memories = [
            m for m in self.memories 
            if query_lower in m.content.lower()
        ]
        
        # Sort by timestamp (most recent first) and limit
        sorted_memories = sorted(matching_memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:limit]
    
    def get_user_preferences(self) -> List[Memory]:
        """Get user preferences."""
        return self.get_memories(memory_type="user_preference", limit=20)
    
    def clean_old_memories(self, days_old: int = 30):
        """Remove memories older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        old_count = len(self.memories)
        
        self.memories = [m for m in self.memories if m.timestamp > cutoff_date]
        
        new_count = len(self.memories)
        removed_count = old_count - new_count
        
        if removed_count > 0:
            self._save_memories()
            logger.info(f"Cleaned {removed_count} old memories")
    
    def get_memory_summary(self) -> str:
        """Get a summary of stored memories."""
        if not self.memories:
            return "No memories stored yet."
        
        memory_types = {}
        for memory in self.memories:
            memory_types[memory.type] = memory_types.get(memory.type, 0) + 1
        
        summary = f"Total memories: {len(self.memories)}\n"
        for mem_type, count in memory_types.items():
            summary += f"- {mem_type}: {count}\n"
        
        oldest_memory = min(self.memories, key=lambda m: m.timestamp)
        newest_memory = max(self.memories, key=lambda m: m.timestamp)
        
        summary += f"Oldest memory: {oldest_memory.timestamp.strftime('%Y-%m-%d')}\n"
        summary += f"Newest memory: {newest_memory.timestamp.strftime('%Y-%m-%d')}"
        
        return summary

# Global memory manager instance
memory_manager = MemoryManager()
