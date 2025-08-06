"""
Standalone Framework - Replaces LiveKit dependencies
No external service dependencies required
"""
import functools
import asyncio
import logging
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class StandaloneContext:
    """Standalone context to replace LiveKit's RunContext."""
    session_id: str = "standalone_session"
    user_id: str = "local_user"
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# Global context instance
standalone_context = StandaloneContext()

def function_tool(func: Callable) -> Callable:
    """
    Standalone replacement for LiveKit's @function_tool decorator.
    Makes existing tool functions work without modification.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Inject context if the function expects it
            if 'context' in func.__code__.co_varnames and 'context' not in kwargs:
                kwargs['context'] = standalone_context
            
            # Ensure the function is awaitable
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result
            
        except Exception as e:
            logger.error(f"Tool {func.__name__} error: {e}")
            return f"Error in {func.__name__}: {str(e)}"
    
    # Add metadata for tool discovery
    wrapper.is_tool = True
    wrapper.tool_name = func.__name__
    wrapper.tool_description = func.__doc__ or f"Tool: {func.__name__}"
    wrapper.original_function = func
    
    return wrapper

def gemini_tool(func: Callable) -> Callable:
    """Passthrough decorator for Gemini tools."""
    return func

# Type alias for compatibility
RunContext = StandaloneContext

class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, func):
        """Register a tool function."""
        if hasattr(func, 'is_tool') and func.is_tool:
            self.tools[func.tool_name] = func
            logger.info(f"Registered tool: {func.tool_name}")
    
    def get_tool(self, name: str):
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self):
        """List all available tools."""
        return list(self.tools.keys())
    
    def get_tool_info(self, name: str):
        """Get information about a tool."""
        tool = self.tools.get(name)
        if tool:
            return {
                'name': tool.tool_name,
                'description': tool.tool_description,
                'function': tool.original_function.__name__ if hasattr(tool, 'original_function') else name
            }
        return None

# Global tool registry
tool_registry = ToolRegistry()
