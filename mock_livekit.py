"""
Simple decorator replacement for LiveKit's @function_tool
Allows existing tools to work without LiveKit dependency
"""
import functools
from typing import Any, Callable, Optional

class MockRunContext:
    """Mock RunContext to replace LiveKit's RunContext."""
    
    def __init__(self):
        self.session_id = "standalone_session"
        self.user_id = "local_user"
        self.metadata = {}

# Global mock context for standalone operation
mock_context = MockRunContext()

def function_tool(func: Callable) -> Callable:
    """
    Replacement for LiveKit's @function_tool decorator.
    Allows existing tool functions to work without modification.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Inject mock context if needed
        if 'context' in func.__code__.co_varnames and 'context' not in kwargs:
            kwargs['context'] = mock_context
        
        return await func(*args, **kwargs)
    
    # Add tool metadata
    wrapper.is_tool = True
    wrapper.tool_name = func.__name__
    wrapper.tool_description = func.__doc__ or f"Tool: {func.__name__}"
    
    return wrapper

def gemini_tool(func: Callable) -> Callable:
    """
    Replacement for Gemini tool decorator.
    Simply passes through the function.
    """
    return func

# Mock RunContext class for compatibility
RunContext = MockRunContext
