import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import lru_cache
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import asyncio
from gemini_client import get_gemini_client, gemini_tool

# Import DEVIN-like capabilities
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
    Initialize DEVIN-like capabilities and perform system checks.
    """
    try:
        from devin_system import permission_manager
        from voice_interaction import voice_manager
        
        # System initialization
        init_report = []
        init_report.append("🤖 DEVIN INITIALIZATION SEQUENCE")
        init_report.append("=" * 40)
        
        # Check system capabilities
        init_report.append("System Capabilities Check:")
        
        # Voice system
        try:
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
        
        init_report.append("")
        init_report.append("Permission Status:")
        for perm, status in permission_manager.permissions.items():
            init_report.append(f"  {perm.replace('_', ' ').title()}: {'✅' if status else '❌'}")
        
        init_report.append("")
        init_report.append("🎯 DEVIN Systems Status: ONLINE")
        init_report.append("Ready to assist, Sir. All core systems initialized.")
        init_report.append("")
        init_report.append("Available Commands:")
        init_report.append("• grant_permission - Enable system permissions")
        init_report.append("• system_status_report - Detailed system analysis")
        init_report.append("• speak_text - Voice synthesis")
        init_report.append("• voice_conversation_mode - Interactive voice chat")
        init_report.append("• take_screenshot - Screen capture")
        init_report.append("• analyze_screen - AI screen analysis")
        init_report.append("• control_applications - App management")
        init_report.append("• intelligent_automation - AI-guided automation")
        
        # Try to speak the initialization if voice is available
        try:
            voice_manager.speak("Devin systems online. All core functions initialized and ready, Sir.")
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
    Central command processor for complex DEVIN-like operations.
    
    Args:
        command: Natural language command for DEVIN to execute
    """
    try:
        client = get_gemini_client()
        
        # Analyze the command and determine appropriate actions
        analysis_prompt = f"""As Devin, analyze this command and determine the best approach to execute it:

Command: {command}

Available capabilities:
- System control (files, applications, processes)
- Screen interaction (screenshots, mouse, keyboard)
- Voice interaction (speech synthesis, recognition)
- Network operations (diagnostics, connectivity)
- Automation (intelligent task execution)
- Window management
- Audio control
- Clipboard operations

Provide:
1. Command interpretation
2. Required tools/functions to execute
3. Step-by-step execution plan
4. Any permissions needed
5. Safety considerations

Respond as Devin would - intelligent, helpful, and slightly witty."""
        
        response = await client.generate_content(analysis_prompt)
        
        return f"""🤖 DEVIN Command Analysis

{response}

Sir, I've analyzed your request and prepared an execution strategy. 
Would you like me to proceed with the recommended approach, or shall I wait for your approval on specific steps?"""
        
    except Exception as e:
        logger.error(f"Devin command center error: {e}")
        return f"Command analysis error: {str(e)}"

# Cache for frequently accessed data
@lru_cache(maxsize=100)
def _cached_search(query: str) -> str:
    """Cache search results to avoid repeated API calls."""
    pass

@function_tool
async def search_web(query: str, context: RunContext, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo and return multiple results with better formatting.
    
    Args:
        query: The search query
        context: The run context
        max_results: Maximum number of results to return (default: 3)
    """
    try:
        search_tool = DuckDuckGoSearchRun()
        results = await search_tool.arun(tool_input=query)
        
        if not results:
            logger.warning("No results found for query: %s", query)
            return "No results found for your search query."
        
        # Format results better
        formatted_results = f"Search results for '{query}':\n\n{results}"
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
    return f"Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"

@function_tool
async def calculate_math(expression: str, context: RunContext) -> str:
    """
    Safely calculate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")
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
        return f"Result: {result}"
        
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

@function_tool
async def get_weather_info(location: str, context: RunContext) -> str:
    """
    Get weather information for a specific location using a free weather API.
    
    Args:
        location: City name or location
    """
    try:
        # Using OpenWeatherMap free tier (you'll need to get an API key)
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return "Weather service not configured. Please set OPENWEATHER_API_KEY environment variable."
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_info = (
            f"Weather in {data['name']}, {data['sys']['country']}:\n"
            f"Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)\n"
            f"Condition: {data['weather'][0]['description'].title()}\n"
            f"Humidity: {data['main']['humidity']}%\n"
            f"Wind: {data['wind']['speed']} m/s"
        )
        
        return weather_info
        
    except requests.RequestException as e:
        logger.error("Failed to fetch weather data: %s", e)
        return f"Sorry, I couldn't fetch weather data for {location}. Please try again later."
    except Exception as e:
        logger.error("Error processing weather request: %s", e)
        return f"Error getting weather information: {str(e)}"

@function_tool
async def create_reminder(reminder_text: str, context: RunContext, minutes_from_now: int = 5) -> str:
    """
    Create a simple reminder (stores locally).
    
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
        
        return f"Reminder created: '{reminder_text}' scheduled for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
    except Exception as e:
        logger.error("Error creating reminder: %s", e)
        return f"Sorry, I couldn't create the reminder: {str(e)}"

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
        
        formatted_info = "System Information:\n" + "\n".join([f"{k}: {v}" for k, v in info.items()])
        return formatted_info
        
    except Exception as e:
        return f"Could not retrieve system information: {str(e)}"

async def fetch_upi_apps() -> str:
    """
    Fetch a list of UPI apps from the provided URL with better error handling.
    """
    url = "https://raw.githubusercontent.com/LiveKit/livekit-agents/main/agents/upi_apps.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse and format the JSON response
        data = response.json()
        if isinstance(data, list):
            apps_list = "\n".join([f"- {app}" for app in data[:10]])  # Limit to first 10
            return f"Popular UPI Apps:\n{apps_list}"
        else:
            return response.text
            
    except requests.RequestException as e:
        logger.error("Failed to fetch UPI apps: %s", e)
        return "Error fetching UPI apps. Please try again later."
    except json.JSONDecodeError as e:
        logger.error("Failed to parse UPI apps JSON: %s", e)
        return "Error parsing UPI apps data."

@function_tool
@gemini_tool
async def translate_text(text: str, target_language: str, context: RunContext) -> str:
    """
    Translate text using Google Gemini AI with enhanced accuracy.
    
    Args:
        text: Text to translate
        target_language: Target language (e.g., 'Spanish', 'French', 'German', 'Hindi')
    """
    if not text.strip():
        return "Error: No text provided for translation."
    
    if len(text) > 5000:
        return "Error: Text too long. Please limit to 5000 characters."
    
    client = get_gemini_client()
    
    prompt = f"""Translate the following text to {target_language}. 
Rules:
- Maintain the original tone and style
- Preserve formatting (line breaks, punctuation)
- Keep proper nouns and technical terms appropriate
- Only return the translation, no explanations

Text to translate:
{text}"""
    
    response = await client.generate_content(prompt)
    return f"Translation to {target_language}:\n{response}"

@function_tool
async def generate_password(context: RunContext, length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Length of the password (default: 12)
        include_symbols: Whether to include special symbols (default: True)
    """
    try:
        import string
        import secrets
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return f"Generated secure password: {password}"
        
    except Exception as e:
        return f"Error generating password: {str(e)}"

@function_tool
async def manage_memory(action: str, content: str = "", context: RunContext = None) -> str:
    """
    Manage personal memories and preferences.
    
    Args:
        action: Action to perform ('add', 'search', 'summary', 'preferences')
        content: Content for add/search actions
    """
    try:
        from memory_manager import memory_manager
        
        if action == "add":
            memory_manager.add_memory(content, memory_type="user_preference")
            return f"Added to memory: {content}"
        
        elif action == "search":
            memories = memory_manager.search_memories(content)
            if memories:
                results = "\n".join([f"- {m.content}" for m in memories[:5]])
                return f"Found memories:\n{results}"
            else:
                return "No matching memories found."
        
        elif action == "summary":
            return memory_manager.get_memory_summary()
        
        elif action == "preferences":
            prefs = memory_manager.get_user_preferences()
            if prefs:
                results = "\n".join([f"- {p.content}" for p in prefs[:10]])
                return f"Your preferences:\n{results}"
            else:
                return "No preferences stored yet."
        
        else:
            return "Available actions: add, search, summary, preferences"
            
    except Exception as e:
        return f"Memory management error: {str(e)}"

@function_tool
async def url_shortener(long_url: str, context: RunContext) -> str:
    """
    Shorten a long URL using a free service.
    
    Args:
        long_url: The URL to shorten
    """
    try:
        # Using a simple URL shortener service
        # This is a placeholder - you'd want to use a proper service like bit.ly
        import hashlib
        import base64
        
        # Create a simple hash-based short URL
        hash_object = hashlib.md5(long_url.encode())
        short_hash = base64.urlsafe_b64encode(hash_object.digest())[:8].decode()
        
        return f"Shortened URL: https://short.ly/{short_hash} (Original: {long_url})"
        
    except Exception as e:
        return f"Error shortening URL: {str(e)}"

@function_tool
async def qr_code_generator(text: str, context: RunContext) -> str:
    """
    Generate a QR code description for text or URL.
    
    Args:
        text: Text or URL to encode in QR code
    """
    try:
        # This would generate a QR code in a real implementation
        # For now, we'll just provide instructions
        return f"QR Code for '{text}' can be generated. Use a QR code library like 'qrcode' to create the actual image."
        
    except Exception as e:
        return f"Error generating QR code: {str(e)}"

@function_tool
async def text_analyzer(text: str, context: RunContext) -> str:
    """
    Analyze text for various metrics.
    
    Args:
        text: Text to analyze
    """
    try:
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        analysis = {
            "Characters": len(text),
            "Characters (no spaces)": len(text.replace(' ', '')),
            "Words": len(words),
            "Sentences": len([s for s in sentences if s.strip()]),
            "Paragraphs": len([p for p in paragraphs if p.strip()]),
            "Average words per sentence": round(len(words) / max(len(sentences), 1), 2),
            "Reading time (approx)": f"{len(words) // 200 + 1} minutes"
        }
        
        result = "Text Analysis:\n"
        for key, value in analysis.items():
            result += f"{key}: {value}\n"
        
        return result
        
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

@function_tool
@gemini_tool
async def ai_assistant(query: str, context: RunContext) -> str:
    """
    Advanced AI assistance using Google Gemini for complex queries and analysis.
    
    Args:
        query: Complex question or task that requires advanced AI reasoning
    """
    if not query.strip():
        return "Error: No query provided."
    
    if len(query) > 8000:
        return "Error: Query too long. Please break it into smaller parts."
    
    client = get_gemini_client()
    
    # Enhanced prompt for better responses
    enhanced_prompt = f"""As Devin, an advanced AI assistant, provide a comprehensive and helpful response to this query. 

Guidelines:
- Be accurate, informative, and practical
- Structure your response clearly with headings if needed
- Provide actionable insights where applicable
- Include examples or step-by-step instructions when helpful
- If the query is complex, break down your answer into logical sections

Query: {query}"""
    
    response = await client.generate_content(enhanced_prompt)
    return f"AI Analysis:\n{response}"

@function_tool
async def code_analyzer(code: str, language: str, context: RunContext) -> str:
    """
    Analyze code for bugs, improvements, and best practices using Gemini.
    
    Args:
        code: The code to analyze
        language: Programming language (e.g., 'python', 'javascript', 'java')
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "Code analysis service not configured. Please set GOOGLE_API_KEY environment variable."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze this {language} code for:
1. Potential bugs or errors
2. Performance improvements
3. Best practices and code quality
4. Security considerations
5. Suggestions for optimization

Code:
```{language}
{code}
```

Provide a structured analysis with specific recommendations."""
        
        response = model.generate_content(prompt)
        return f"Code Analysis Results:\n{response.text}"
        
    except Exception as e:
        logger.error("Code analysis error: %s", e)
        return f"Code analysis error: {str(e)}"

@function_tool
async def explain_concept(concept: str, context: RunContext, complexity: str = "intermediate") -> str:
    """
    Explain complex concepts using Gemini AI with adjustable complexity.
    
    Args:
        concept: The concept to explain
        complexity: Explanation level ('beginner', 'intermediate', 'advanced')
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "Concept explanation service not configured. Please set GOOGLE_API_KEY environment variable."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Explain the concept of "{concept}" at a {complexity} level.

Guidelines:
- If beginner: Use simple language, analogies, and avoid jargon
- If intermediate: Include technical details but keep it accessible
- If advanced: Provide comprehensive technical depth and nuances

Structure the explanation with:
1. Simple definition
2. Key components or principles
3. Real-world applications or examples
4. Common misconceptions (if any)
5. Further learning suggestions

Concept: {concept}"""
        
        response = model.generate_content(prompt)
        return f"Concept Explanation ({complexity} level):\n{response.text}"
        
    except Exception as e:
        logger.error("Concept explanation error: %s", e)
        return f"Concept explanation error: {str(e)}"

@function_tool
async def creative_writing(prompt_text: str, writing_type: str, context: RunContext) -> str:
    """
    Generate creative content using Gemini AI.
    
    Args:
        prompt_text: The creative prompt or topic
        writing_type: Type of content ('story', 'poem', 'article', 'email', 'summary')
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "Creative writing service not configured. Please set GOOGLE_API_KEY environment variable."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if writing_type.lower() == 'story':
            system_prompt = "Write an engaging short story with a clear beginning, middle, and end. Include vivid descriptions and character development."
        elif writing_type.lower() == 'poem':
            system_prompt = "Write a creative poem with meaningful imagery and rhythm. Consider different poetic forms and styles."
        elif writing_type.lower() == 'article':
            system_prompt = "Write an informative article with a clear structure, engaging introduction, and valuable insights."
        elif writing_type.lower() == 'email':
            system_prompt = "Write a professional and clear email that effectively communicates the intended message."
        elif writing_type.lower() == 'summary':
            system_prompt = "Create a concise and comprehensive summary that captures the key points and main ideas."
        else:
            system_prompt = f"Create high-quality {writing_type} content that is engaging and well-structured."
        
        full_prompt = f"{system_prompt}\n\nTopic/Prompt: {prompt_text}"
        
        response = model.generate_content(full_prompt)
        return f"Generated {writing_type.title()}:\n\n{response.text}"
        
    except Exception as e:
        logger.error("Creative writing error: %s", e)
        return f"Creative writing error: {str(e)}"

@function_tool
async def data_insights(data_description: str, context: RunContext) -> str:
    """
    Analyze data patterns and provide insights using Gemini AI.
    
    Args:
        data_description: Description of the data or actual data to analyze
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "Data insights service not configured. Please set GOOGLE_API_KEY environment variable."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze the following data and provide insights:

Data: {data_description}

Please provide:
1. Key patterns and trends
2. Notable observations
3. Potential correlations
4. Actionable insights
5. Recommendations for further analysis
6. Visualization suggestions

Be specific and practical in your analysis."""
        
        response = model.generate_content(prompt)
        return f"Data Insights:\n{response.text}"
        
    except Exception as e:
        logger.error("Data insights error: %s", e)
        return f"Data insights error: {str(e)}"
    