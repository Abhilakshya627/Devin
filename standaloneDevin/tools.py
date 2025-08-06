"""
Core tools for Standalone Devin AI Assistant
Simplified version without LiveKit dependencies
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import asyncio
from standalone_framework import function_tool, RunContext, gemini_tool, tool_registry
from gemini_client import get_gemini_client

# Import system modules
from devin_system import (
    grant_permission, revoke_permission, system_status_report,
    control_applications, file_operations, system_control,
    intelligent_automation, network_diagnostics, voice_response_mode
)
from screen_interaction import (
    take_screenshot, analyze_screen, mouse_control, keyboard_control,
    find_on_screen, window_management, clipboard_operations,
    smart_automation_task
)
from voice_interaction import (
    speak_text, listen_for_command, configure_voice,
    voice_conversation_mode, audio_system_control, devin_wake_word_detection
)

# Enhanced logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@function_tool
async def initialize_devin(context: RunContext) -> str:
    """
    Initialize Standalone DEVIN capabilities and perform system checks.
    """
    try:
        # System initialization
        init_report = []
        init_report.append("🤖 STANDALONE DEVIN INITIALIZATION")
        init_report.append("=" * 50)
        
        # Check system capabilities
        init_report.append("System Capabilities Check:")
        
        # Voice system
        try:
            from voice_interaction import voice_manager
            voice_available = voice_manager.tts_engine is not None
            init_report.append(f"  Voice Synthesis: {'✅' if voice_available else '❌'}")
            
            mic_available = voice_manager.microphone is not None
            init_report.append(f"  Voice Recognition: {'✅' if mic_available else '❌'}")
        except:
            init_report.append("  Voice Systems: ❌ (Install pyttsx3, speechrecognition)")
        
        # Screen interaction
        try:
            import pyautogui
            init_report.append("  Screen Control: ✅")
        except ImportError:
            init_report.append("  Screen Control: ❌ (Install pyautogui)")
        
        # Computer vision
        try:
            import cv2
            init_report.append("  Computer Vision: ✅")
        except ImportError:
            init_report.append("  Computer Vision: ❌ (Install opencv-python)")
        
        # Window management
        try:
            import pygetwindow
            init_report.append("  Window Management: ✅")
        except ImportError:
            init_report.append("  Window Management: ❌ (Install pygetwindow)")
        
        # Clipboard operations
        try:
            import pyperclip
            init_report.append("  Clipboard Control: ✅")
        except ImportError:
            init_report.append("  Clipboard Control: ❌ (Install pyperclip)")
        
        # Check permissions
        init_report.append("")
        init_report.append("Permission Status:")
        from devin_system import permission_manager
        for perm, status in permission_manager.permissions.items():
            init_report.append(f"  {perm.replace('_', ' ').title()}: {'✅' if status else '❌'}")
        
        init_report.append("")
        init_report.append("🎯 STANDALONE DEVIN Status: ONLINE")
        init_report.append("Ready to assist! All core systems initialized.")
        init_report.append("")
        init_report.append("Available Commands:")
        init_report.append("• initialize_devin - Initialize all systems")
        init_report.append("• grant_permission - Enable system permissions")
        init_report.append("• system_status_report - Detailed system analysis")
        init_report.append("• speak_text - Voice synthesis")
        init_report.append("• take_screenshot - Screen capture")
        init_report.append("• analyze_screen - AI screen analysis")
        init_report.append("• control_applications - App management")
        init_report.append("• search_web - Web search")
        init_report.append("• get_current_time - Current date/time")
        
        # Try to speak the initialization if voice is available
        try:
            from voice_interaction import voice_manager
            voice_manager.speak("Standalone Devin systems online. All core functions initialized and ready.")
        except:
            pass
        
        return "\n".join(init_report)
        
    except Exception as e:
        logger.error(f"Devin initialization error: {e}")
        return f"Devin initialization error: {str(e)}"

@function_tool
@gemini_tool
async def devin_command_center(command: str, context: RunContext) -> str:
    """
    Central command processor for Standalone DEVIN operations.
    
    Args:
        command: Natural language command for DEVIN to execute
    """
    try:
        client = get_gemini_client()
        
        # Analyze the command and determine appropriate actions
        analysis_prompt = f"""As Devin, analyze this command and determine the best approach:

Command: {command}

Available capabilities:
- System control (files, applications, processes)
- Screen interaction (screenshots, mouse, keyboard)
- Voice interaction (speech synthesis, recognition)
- Web search and information lookup
- Basic automation tasks
- Window management
- Audio control
- Clipboard operations
- Time/date functions
- Mathematical calculations

Provide:
1. Command interpretation
2. Which functions to call
3. Step-by-step execution plan
4. Any permissions needed
5. Safety considerations

Respond as Devin would - intelligent, helpful, and efficient."""
        
        response = await client.generate_content(analysis_prompt)
        
        return f"🤖 DEVIN Command Analysis\n\n{response}\n\nReady to execute when you give the command!"
        
    except Exception as e:
        logger.error(f"Devin command center error: {e}")
        return f"Command analysis error: {str(e)}"

@function_tool
async def search_web(query: str, context: RunContext, max_results: int = 3) -> str:
    """
    Search the web and return results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return "No results found for your search query."
        
        formatted_results = f"🔍 Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. **{result['title']}**\n"
            formatted_results += f"   {result['body'][:200]}...\n"
            formatted_results += f"   🔗 {result['href']}\n\n"
        
        return formatted_results[:2000]  # Limit response length
        
    except Exception as e:
        logger.error("Error during web search: %s", e)
        return f"Sorry, I encountered an error while searching: {str(e)}"

@function_tool
async def get_current_time(context: RunContext) -> str:
    """
    Get the current date and time.
    """
    current_time = datetime.now()
    return f"📅 Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"

@function_tool
async def calculate_math(expression: str, context: RunContext) -> str:
    """
    Safely calculate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate
    """
    try:
        # Basic safety: only allow certain characters
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression.replace(' ', '')):
            return "Error: Only basic mathematical operations are allowed."
        
        # Use eval safely with limited scope
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "pow": pow,
            "sqrt": lambda x: x ** 0.5,
            "sin": lambda x: __import__('math').sin(x),
            "cos": lambda x: __import__('math').cos(x),
            "tan": lambda x: __import__('math').tan(x),
            "pi": 3.14159265359,
            "e": 2.71828182846
        }
        
        result = eval(expression, safe_dict, {})
        return f"🧮 Result: {result}"
        
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

@function_tool
async def get_system_info(context: RunContext) -> str:
    """
    Get basic system information.
    """
    try:
        import platform
        import psutil
        
        info = {
            "OS": platform.system(),
            "OS Version": platform.release(),
            "Python Version": platform.python_version(),
            "CPU Usage": f"{psutil.cpu_percent(interval=1):.1f}%",
            "Memory Usage": f"{psutil.virtual_memory().percent:.1f}%",
            "Disk Usage": f"{psutil.disk_usage('/').percent:.1f}%" if platform.system() != "Windows" else f"{psutil.disk_usage('C:').percent:.1f}%"
        }
        
        formatted_info = "💻 System Information:\n" + "\n".join([f"• {k}: {v}" for k, v in info.items()])
        return formatted_info
        
    except Exception as e:
        return f"Could not retrieve system information: {str(e)}"

@function_tool
@gemini_tool
async def translate_text(text: str, target_language: str, context: RunContext) -> str:
    """
    Translate text using Google Gemini AI.
    
    Args:
        text: Text to translate
        target_language: Target language
    """
    if not text.strip():
        return "Error: No text provided for translation."
    
    if len(text) > 2000:
        return "Error: Text too long. Please limit to 2000 characters."
    
    client = get_gemini_client()
    
    prompt = f"""Translate the following text to {target_language}:

{text}

Provide only the translation, no explanations."""
    
    try:
        response = await client.generate_content(prompt)
        return f"🌐 Translation to {target_language}:\n{response}"
    except Exception as e:
        return f"Translation error: {str(e)}"

@function_tool
@gemini_tool
async def ai_assistant(query: str, context: RunContext) -> str:
    """
    Advanced AI assistance using Google Gemini.
    
    Args:
        query: Question or task for the AI assistant
    """
    if not query.strip():
        return "Error: No query provided."
    
    if len(query) > 4000:
        return "Error: Query too long. Please break it into smaller parts."
    
    client = get_gemini_client()
    
    enhanced_prompt = f"""As Devin, a helpful AI assistant, provide a comprehensive response to this query:

{query}

Be accurate, practical, and helpful. Structure your response clearly."""
    
    try:
        response = await client.generate_content(enhanced_prompt)
        return f"🤖 Devin's Response:\n{response}"
    except Exception as e:
        return f"AI assistant error: {str(e)}"

@function_tool
async def create_reminder(reminder_text: str, context: RunContext, minutes_from_now: int = 5) -> str:
    """
    Create a simple reminder.
    
    Args:
        reminder_text: What to remind about
        minutes_from_now: When to remind (minutes from now)
    """
    try:
        reminder_time = datetime.now() + timedelta(minutes=minutes_from_now)
        
        # Create reminders directory if it doesn't exist
        reminders_dir = "reminders"
        os.makedirs(reminders_dir, exist_ok=True)
        
        reminder_data = {
            "text": reminder_text,
            "created_at": datetime.now().isoformat(),
            "remind_at": reminder_time.isoformat()
        }
        
        # Save reminder to file
        filename = f"reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(reminders_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(reminder_data, f, indent=2)
        
        return f"⏰ Reminder created: '{reminder_text}' scheduled for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
    except Exception as e:
        logger.error("Error creating reminder: %s", e)
        return f"Sorry, I couldn't create the reminder: {str(e)}"

@function_tool
async def generate_password(context: RunContext, length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Length of the password
        include_symbols: Whether to include special symbols
    """
    try:
        import string
        import secrets
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return f"🔐 Generated secure password: {password}"
        
    except Exception as e:
        return f"Error generating password: {str(e)}"

# Register all tools
def register_all_tools():
    """Register all available tools in the tool registry."""
    tools = [
        # Core tools
        initialize_devin,
        devin_command_center,
        search_web,
        get_current_time,
        calculate_math,
        get_system_info,
        translate_text,
        ai_assistant,
        create_reminder,
        generate_password,
        
        # System tools
        grant_permission,
        revoke_permission,
        system_status_report,
        control_applications,
        file_operations,
        system_control,
        intelligent_automation,
        network_diagnostics,
        voice_response_mode,
        
        # Screen tools
        take_screenshot,
        analyze_screen,
        mouse_control,
        keyboard_control,
        find_on_screen,
        window_management,
        clipboard_operations,
        smart_automation_task,
        
        # Voice tools
        speak_text,
        listen_for_command,
        configure_voice,
        voice_conversation_mode,
        audio_system_control,
        devin_wake_word_detection
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    logger.info(f"Registered {len(tools)} tools")

# Auto-register tools when module is imported
register_all_tools()
