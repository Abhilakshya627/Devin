"""
Screen interaction and computer vision capabilities for Standalone DEVIN.
"""
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageDraw
import time
import logging
from typing import Tuple, List, Optional, Dict, Any
import pygetwindow as gw
import pyperclip
from pathlib import Path
from standalone_framework import function_tool, RunContext, gemini_tool
from gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class ScreenManager:
    """Manages screen interaction and computer vision operations."""
    
    def __init__(self):
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Take a screenshot and save it."""
        try:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filepath)
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise
    
    def find_image_on_screen(self, template_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find an image on screen using template matching."""
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
            return None
            
        except Exception as e:
            logger.error(f"Image search error: {e}")
            return None
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get the RGB color of a pixel at specified coordinates."""
        try:
            screenshot = pyautogui.screenshot()
            return screenshot.getpixel((x, y))
        except Exception as e:
            logger.error(f"Pixel color error: {e}")
            return (0, 0, 0)

# Global screen manager
screen_manager = ScreenManager()

@function_tool
async def take_screenshot(region: str = "", context: RunContext = None) -> str:
    """
    Take a screenshot of the screen or a specific region.
    
    Args:
        region: Region to capture (format: "x,y,width,height" or empty for full screen)
    """
    try:
        region_tuple = None
        if region:
            coords = [int(x.strip()) for x in region.split(',')]
            if len(coords) == 4:
                region_tuple = tuple(coords)
        
        filepath = screen_manager.take_screenshot(region_tuple)
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        return f"📸 Screenshot saved: {filepath}\nScreen size: {screen_width}x{screen_height}"
        
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return f"Screenshot error: {str(e)}"

@function_tool
@gemini_tool
async def analyze_screen(query: str = "describe what you see", context: RunContext = None) -> str:
    """
    Take a screenshot and analyze it using AI vision.
    
    Args:
        query: What to analyze in the screenshot
    """
    try:
        # Take screenshot
        screenshot_path = screen_manager.take_screenshot()
        
        # For now, return basic info since we don't have vision API integrated
        # In a full implementation, you would send the image to a vision API
        
        screen_width, screen_height = pyautogui.size()
        mouse_x, mouse_y = pyautogui.position()
        
        # Get active window info
        try:
            active_window = gw.getActiveWindow()
            window_info = f"Active window: {active_window.title}" if active_window else "No active window detected"
        except:
            window_info = "Window information unavailable"
        
        analysis = f"""🔍 SCREEN ANALYSIS
Screenshot saved: {screenshot_path}
Screen resolution: {screen_width}x{screen_height}
Mouse position: ({mouse_x}, {mouse_y})
{window_info}

Query: {query}

Note: Advanced AI vision analysis requires integration with vision API.
For full analysis, the screenshot can be manually reviewed or processed with computer vision tools."""
        
        return analysis
        
    except Exception as e:
        logger.error(f"Screen analysis error: {e}")
        return f"Screen analysis error: {str(e)}"

@function_tool
async def mouse_control(action: str, x: int = 0, y: int = 0, button: str = "left", context: RunContext = None) -> str:
    """
    Control mouse movements and clicks.
    
    Args:
        action: Action to perform ('move', 'click', 'drag', 'scroll', 'position')
        x: X coordinate
        y: Y coordinate  
        button: Mouse button ('left', 'right', 'middle')
    """
    try:
        if action == "position":
            mouse_x, mouse_y = pyautogui.position()
            return f"🖱️ Current mouse position: ({mouse_x}, {mouse_y})"
        
        elif action == "move":
            pyautogui.moveTo(x, y, duration=0.5)
            return f"🖱️ Mouse moved to ({x}, {y})"
        
        elif action == "click":
            if button == "left":
                pyautogui.click(x, y)
            elif button == "right":
                pyautogui.rightClick(x, y)
            elif button == "middle":
                pyautogui.middleClick(x, y)
            else:
                return f"❌ Unknown button: {button}"
            
            return f"🖱️ {button.title()} clicked at ({x}, {y})"
        
        elif action == "drag":
            current_x, current_y = pyautogui.position()
            pyautogui.drag(x - current_x, y - current_y, duration=1.0, button=button)
            return f"🖱️ Dragged from ({current_x}, {current_y}) to ({x}, {y})"
        
        elif action == "scroll":
            # x represents scroll amount, y represents scroll direction
            pyautogui.scroll(x)
            return f"🖱️ Scrolled {x} units"
        
        else:
            return f"❌ Unknown action: {action}. Use: move, click, drag, scroll, position"
            
    except Exception as e:
        logger.error(f"Mouse control error: {e}")
        return f"Mouse control error: {str(e)}"

@function_tool
async def keyboard_control(action: str, text: str = "", key: str = "", context: RunContext = None) -> str:
    """
    Control keyboard input and key presses.
    
    Args:
        action: Action to perform ('type', 'press', 'hotkey', 'shortcut')
        text: Text to type (for 'type' action)
        key: Key name or combination (for 'press', 'hotkey' actions)
    """
    try:
        if action == "type":
            if text:
                pyautogui.typewrite(text, interval=0.02)
                return f"⌨️ Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
            else:
                return "❌ No text provided to type"
        
        elif action == "press":
            if key:
                pyautogui.press(key)
                return f"⌨️ Pressed key: {key}"
            else:
                return "❌ No key specified"
        
        elif action == "hotkey":
            if key:
                keys = [k.strip() for k in key.split('+')]
                pyautogui.hotkey(*keys)
                return f"⌨️ Hotkey combination: {key}"
            else:
                return "❌ No hotkey combination specified"
        
        elif action == "shortcut":
            # Common shortcuts
            shortcuts = {
                "copy": ["ctrl", "c"],
                "paste": ["ctrl", "v"],
                "cut": ["ctrl", "x"],
                "undo": ["ctrl", "z"],
                "redo": ["ctrl", "y"],
                "save": ["ctrl", "s"],
                "select_all": ["ctrl", "a"],
                "find": ["ctrl", "f"]
            }
            
            if key.lower() in shortcuts:
                pyautogui.hotkey(*shortcuts[key.lower()])
                return f"⌨️ Shortcut executed: {key}"
            else:
                available = ", ".join(shortcuts.keys())
                return f"❌ Unknown shortcut: {key}. Available: {available}"
        
        else:
            return f"❌ Unknown action: {action}. Use: type, press, hotkey, shortcut"
            
    except Exception as e:
        logger.error(f"Keyboard control error: {e}")
        return f"Keyboard control error: {str(e)}"

@function_tool
async def find_on_screen(target: str, action: str = "locate", context: RunContext = None) -> str:
    """
    Find text or images on the screen.
    
    Args:
        target: Text to find or path to image template
        action: Action to perform ('locate', 'click', 'highlight')
    """
    try:
        # For text finding, we'd need OCR (like pytesseract)
        # For now, implement basic image finding
        
        if target.endswith(('.png', '.jpg', '.jpeg')):
            # Image template matching
            location = screen_manager.find_image_on_screen(target)
            
            if location:
                x, y = location
                
                if action == "locate":
                    return f"🎯 Found image at ({x}, {y})"
                elif action == "click":
                    pyautogui.click(x, y)
                    return f"🎯 Found and clicked image at ({x}, {y})"
                elif action == "highlight":
                    # Move mouse to highlight
                    pyautogui.moveTo(x, y, duration=0.5)
                    return f"🎯 Found and highlighted image at ({x}, {y})"
            else:
                return f"❌ Image not found: {target}"
        
        else:
            # Text finding would require OCR
            return f"🔍 Text search for '{target}' requires OCR implementation. Currently supports image templates only."
            
    except Exception as e:
        logger.error(f"Screen search error: {e}")
        return f"Screen search error: {str(e)}"

@function_tool
async def window_management(action: str, window_title: str = "", context: RunContext = None) -> str:
    """
    Manage windows on the desktop.
    
    Args:
        action: Action to perform ('list', 'activate', 'minimize', 'maximize', 'close')
        window_title: Title of the window (or partial match)
    """
    try:
        if action == "list":
            windows = gw.getAllWindows()
            window_list = []
            for i, window in enumerate(windows[:20]):  # Limit to 20 windows
                if window.title.strip():  # Only show windows with titles
                    window_list.append(f"{i}: {window.title} ({window.width}x{window.height})")
            
            return f"🪟 Open windows:\n" + "\n".join(window_list)
        
        elif action in ["activate", "minimize", "maximize", "close"]:
            if not window_title:
                return "❌ Window title required for this action"
            
            # Find window by title (partial match)
            matching_windows = []
            for window in gw.getAllWindows():
                if window_title.lower() in window.title.lower():
                    matching_windows.append(window)
            
            if not matching_windows:
                return f"❌ No window found with title containing: {window_title}"
            
            window = matching_windows[0]  # Use first match
            
            try:
                if action == "activate":
                    window.activate()
                    return f"🪟 Activated window: {window.title}"
                elif action == "minimize":
                    window.minimize()
                    return f"🪟 Minimized window: {window.title}"
                elif action == "maximize":
                    window.maximize()
                    return f"🪟 Maximized window: {window.title}"
                elif action == "close":
                    window.close()
                    return f"🪟 Closed window: {window.title}"
            except Exception as e:
                return f"❌ Failed to {action} window: {str(e)}"
        
        else:
            return f"❌ Unknown action: {action}. Use: list, activate, minimize, maximize, close"
            
    except Exception as e:
        logger.error(f"Window management error: {e}")
        return f"Window management error: {str(e)}"

@function_tool
async def clipboard_operations(action: str, text: str = "", context: RunContext = None) -> str:
    """
    Perform clipboard operations.
    
    Args:
        action: Action to perform ('copy', 'paste', 'get', 'set', 'clear')
        text: Text to set in clipboard (for 'set' action)
    """
    try:
        if action == "get":
            clipboard_content = pyperclip.paste()
            return f"📋 Clipboard content: {clipboard_content[:200]}{'...' if len(clipboard_content) > 200 else ''}"
        
        elif action == "set":
            if text:
                pyperclip.copy(text)
                return f"📋 Clipboard set to: {text[:100]}{'...' if len(text) > 100 else ''}"
            else:
                return "❌ No text provided to set in clipboard"
        
        elif action == "clear":
            pyperclip.copy("")
            return "📋 Clipboard cleared"
        
        elif action == "copy":
            # Perform Ctrl+C
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)  # Wait for copy to complete
            clipboard_content = pyperclip.paste()
            return f"📋 Copied to clipboard: {clipboard_content[:100]}{'...' if len(clipboard_content) > 100 else ''}"
        
        elif action == "paste":
            # Perform Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            return "📋 Pasted from clipboard"
        
        else:
            return f"❌ Unknown action: {action}. Use: get, set, clear, copy, paste"
            
    except Exception as e:
        logger.error(f"Clipboard operation error: {e}")
        return f"Clipboard operation error: {str(e)}"

@function_tool
@gemini_tool
async def smart_automation_task(task_description: str, context: RunContext) -> str:
    """
    Use AI to analyze and execute screen automation tasks.
    
    Args:
        task_description: Description of the automation task to perform
    """
    try:
        # Take screenshot for context
        screenshot_path = screen_manager.take_screenshot()
        
        client = get_gemini_client()
        
        prompt = f"""As Devin, analyze this screen automation task:

Task: {task_description}

I have access to these screen interaction capabilities:
- Take screenshots and analyze screen content
- Control mouse (move, click, drag, scroll)
- Control keyboard (type, press keys, shortcuts)
- Find images and text on screen
- Manage windows (activate, minimize, maximize, close)
- Clipboard operations (copy, paste, get, set)

Please provide:
1. Step-by-step plan to accomplish this task
2. Specific commands/coordinates if possible
3. Safety considerations
4. Alternative approaches

Current screenshot saved at: {screenshot_path}

Be practical and consider user safety."""
        
        response = await client.generate_content(prompt)
        
        return f"🤖 DEVIN Automation Plan:\n\n{response}\n\n📸 Current screenshot: {screenshot_path}"
        
    except Exception as e:
        logger.error(f"Smart automation error: {e}")
        return f"Smart automation error: {str(e)}"
