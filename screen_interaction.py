"""
Advanced screen interaction and computer vision capabilities for DEVIN-like functionality.
"""
import cv2
import numpy as np
import pyautogui
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
import base64
import io
from livekit.agents import function_tool, RunContext
from gemini_client import get_gemini_client, gemini_tool

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

@function_tool
async def take_screenshot(context: RunContext, save_path: str = "") -> str:
    """
    Take a screenshot of the current screen.
    
    Args:
        save_path: Optional path to save the screenshot
    """
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        if save_path:
            screenshot.save(save_path)
            return f"📸 Screenshot saved to: {save_path}"
        else:
            # Save to default location with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_path = f"screenshot_{timestamp}.png"
            screenshot.save(default_path)
            return f"📸 Screenshot captured and saved as: {default_path}"
            
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return f"Error taking screenshot: {str(e)}"

@function_tool
@gemini_tool
async def analyze_screen(context: RunContext, task_description: str = "Analyze what's on screen") -> str:
    """
    Analyze the current screen content using AI vision.
    
    Args:
        task_description: What to look for or analyze on screen
    """
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to base64 for AI analysis
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        client = get_gemini_client()
        
        # Create prompt for screen analysis
        prompt = f"""As Devin, analyze this screenshot and provide insights about what's currently displayed on the screen.

Task: {task_description}

Please describe:
1. Main elements visible on screen
2. Applications or windows open
3. Any text or important content
4. UI elements that could be interacted with
5. Suggestions for actions based on what you see

Be specific and actionable in your analysis, Sir."""
        
        # Note: This would need the vision-capable Gemini model
        response = await client.generate_content(prompt)
        
        return f"👁️ DEVIN Screen Analysis:\n{response}"
        
    except Exception as e:
        logger.error(f"Screen analysis error: {e}")
        return f"Error analyzing screen: {str(e)}"

@function_tool
async def mouse_control(action: str, x: int = 0, y: int = 0, context: RunContext = None) -> str:
    """
    Control mouse movements and clicks.
    
    Args:
        action: Mouse action ('move', 'click', 'right_click', 'double_click', 'scroll_up', 'scroll_down', 'position')
        x: X coordinate (for move and click actions)
        y: Y coordinate (for move and click actions)
    """
    from devin_system import permission_manager
    
    permission_check = permission_manager.request_permission(
        "system_control", 
        f"Mouse control: {action}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        if action == "position":
            current_pos = pyautogui.position()
            return f"🖱️ Current mouse position: ({current_pos.x}, {current_pos.y})"
        
        elif action == "move":
            pyautogui.moveTo(x, y, duration=0.5)
            return f"🖱️ Mouse moved to ({x}, {y})"
        
        elif action == "click":
            if x != 0 or y != 0:
                pyautogui.click(x, y)
                return f"🖱️ Clicked at ({x}, {y})"
            else:
                pyautogui.click()
                return "🖱️ Clicked at current position"
        
        elif action == "right_click":
            if x != 0 or y != 0:
                pyautogui.rightClick(x, y)
                return f"🖱️ Right-clicked at ({x}, {y})"
            else:
                pyautogui.rightClick()
                return "🖱️ Right-clicked at current position"
        
        elif action == "double_click":
            if x != 0 or y != 0:
                pyautogui.doubleClick(x, y)
                return f"🖱️ Double-clicked at ({x}, {y})"
            else:
                pyautogui.doubleClick()
                return "🖱️ Double-clicked at current position"
        
        elif action == "scroll_up":
            pyautogui.scroll(3)
            return "🖱️ Scrolled up"
        
        elif action == "scroll_down":
            pyautogui.scroll(-3)
            return "🖱️ Scrolled down"
        
        else:
            return "❌ Invalid action. Available: move, click, right_click, double_click, scroll_up, scroll_down, position"
            
    except Exception as e:
        logger.error(f"Mouse control error: {e}")
        return f"Error controlling mouse: {str(e)}"

@function_tool
async def keyboard_control(action: str, text: str = "", context: RunContext = None) -> str:
    """
    Control keyboard input and hotkeys.
    
    Args:
        action: Keyboard action ('type', 'hotkey', 'press', 'key_combination')
        text: Text to type or key combination
    """
    from devin_system import permission_manager
    
    permission_check = permission_manager.request_permission(
        "system_control", 
        f"Keyboard control: {action} - {text}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        if action == "type":
            pyautogui.typewrite(text, interval=0.05)
            return f"⌨️ Typed: {text}"
        
        elif action == "press":
            pyautogui.press(text)
            return f"⌨️ Pressed key: {text}"
        
        elif action == "hotkey" or action == "key_combination":
            keys = text.split('+')
            pyautogui.hotkey(*keys)
            return f"⌨️ Executed hotkey: {text}"
        
        else:
            return "❌ Invalid action. Available: type, press, hotkey, key_combination"
            
    except Exception as e:
        logger.error(f"Keyboard control error: {e}")
        return f"Error controlling keyboard: {str(e)}"

@function_tool
async def find_on_screen(image_description: str, context: RunContext, confidence: float = 0.8) -> str:
    """
    Find specific elements on screen using image recognition.
    
    Args:
        image_description: Description of what to find on screen
        confidence: Confidence level for image matching (0.0 to 1.0)
    """
    try:
        # Take screenshot for analysis
        screenshot = pyautogui.screenshot()
        
        # For now, we'll use a simpler approach - analyzing the screenshot with AI
        # In a full implementation, you'd use template matching or object detection
        
        # Convert screenshot to text analysis
        screen_size = pyautogui.size()
        
        return f"""🔍 Screen Search Results:
Searching for: {image_description}
Screen Resolution: {screen_size.width}x{screen_size.height}

Note: This feature requires advanced computer vision models for precise element detection.
Consider using 'analyze_screen' for general screen analysis or 'mouse_control' with specific coordinates."""
        
    except Exception as e:
        logger.error(f"Screen search error: {e}")
        return f"Error finding element on screen: {str(e)}"

@function_tool
async def window_management(action: str, window_title: str = "", context: RunContext = None) -> str:
    """
    Manage application windows (minimize, maximize, close, focus).
    
    Args:
        action: Window action ('list', 'focus', 'minimize', 'maximize', 'close', 'resize', 'move')
        window_title: Title or partial title of the window
    """
    from devin_system import permission_manager
    
    permission_check = permission_manager.request_permission(
        "app_control", 
        f"Window management: {action} - {window_title}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        import pygetwindow as gw
        
        if action == "list":
            windows = gw.getAllWindows()
            window_list = []
            for window in windows:
                if window.title.strip():  # Only show windows with titles
                    window_list.append(f"- {window.title} ({window.width}x{window.height})")
            
            return f"🪟 Open Windows:\n" + "\n".join(window_list[:15])  # Limit to 15 windows
        
        elif action in ["focus", "minimize", "maximize", "close"]:
            # Find window by title
            windows = gw.getWindowsWithTitle(window_title)
            
            if not windows:
                # Try partial match
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if window_title.lower() in w.title.lower()]
            
            if not windows:
                return f"❌ Window not found: {window_title}"
            
            window = windows[0]  # Use first match
            
            if action == "focus":
                window.activate()
                return f"🪟 Focused window: {window.title}"
            elif action == "minimize":
                window.minimize()
                return f"🪟 Minimized window: {window.title}"
            elif action == "maximize":
                window.maximize()
                return f"🪟 Maximized window: {window.title}"
            elif action == "close":
                window.close()
                return f"🪟 Closed window: {window.title}"
        
        else:
            return "❌ Invalid action. Available: list, focus, minimize, maximize, close"
            
    except ImportError:
        return "❌ Window management requires 'pygetwindow' package. Install with: pip install pygetwindow"
    except Exception as e:
        logger.error(f"Window management error: {e}")
        return f"Error managing windows: {str(e)}"

@function_tool
async def clipboard_operations(action: str, content: str = "", context: RunContext = None) -> str:
    """
    Manage clipboard operations (copy, paste, get content).
    
    Args:
        action: Clipboard action ('copy', 'paste', 'get', 'clear')
        content: Content to copy to clipboard
    """
    try:
        import pyperclip
        
        if action == "copy":
            pyperclip.copy(content)
            return f"📋 Copied to clipboard: {content[:100]}{'...' if len(content) > 100 else ''}"
        
        elif action == "paste":
            pyautogui.hotkey('ctrl', 'v')
            return "📋 Pasted clipboard content"
        
        elif action == "get":
            clipboard_content = pyperclip.paste()
            return f"📋 Clipboard content: {clipboard_content[:500]}{'...' if len(clipboard_content) > 500 else ''}"
        
        elif action == "clear":
            pyperclip.copy("")
            return "📋 Clipboard cleared"
        
        else:
            return "❌ Invalid action. Available: copy, paste, get, clear"
            
    except ImportError:
        return "❌ Clipboard operations require 'pyperclip' package. Install with: pip install pyperclip"
    except Exception as e:
        logger.error(f"Clipboard error: {e}")
        return f"Error with clipboard operation: {str(e)}"

@function_tool
@gemini_tool
async def smart_automation_task(task: str, context: RunContext) -> str:
    """
    Execute complex automation tasks using AI-guided actions.
    
    Args:
        task: Description of the automation task to perform
    """
    from devin_system import permission_manager
    
    permission_check = permission_manager.request_permission(
        "automation", 
        f"Smart automation: {task}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    client = get_gemini_client()
    
    # Analyze the task and create step-by-step automation
    prompt = f"""As Devin, analyze this automation task and provide specific steps to execute it:

Task: {task}

Break this down into specific actions using available tools:
1. Screen analysis (if needed)
2. Mouse movements and clicks
3. Keyboard inputs
4. Window management
5. Application control

Provide a detailed execution plan with specific coordinates, keys, and commands.
Consider the user's safety and system security."""
    
    response = await client.generate_content(prompt)
    
    return f"""🤖 DEVIN Automation Analysis:

{response}

Sir, I've analyzed the task and prepared an execution strategy. 
Would you like me to proceed with the automation, or would you prefer to review the steps first?

Note: Complex automations are safest when executed step-by-step with your approval."""
