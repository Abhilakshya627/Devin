"""
Standalone Devin AI Assistant - Main Application
No external service dependencies - runs completely local
"""
import asyncio
import logging
import sys
import os
from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from standalone_framework import tool_registry, standalone_context
from gemini_client import get_gemini_client
from tools import initialize_devin, devin_command_center
from voice_interaction import voice_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('devin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StandaloneDevin:
    """Main Standalone Devin AI Assistant application."""
    
    def __init__(self):
        self.running = False
        self.voice_enabled = True
        self.conversation_history = []
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from file."""
        config_file = Path("devin_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "devin_settings": {
                "personality": "helpful_assistant",
                "wake_word": "devin",
                "response_mode": "friendly",
                "voice_enabled": True,
                "auto_initialize": True
            }
        }
    
    async def initialize_systems(self) -> bool:
        """Initialize all Devin systems."""
        try:
            print("🤖 STANDALONE DEVIN AI ASSISTANT")
            print("=" * 60)
            print("Initializing systems...")
            
            # Check API key
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print("❌ Error: GOOGLE_API_KEY not found in .env file")
                return False
            
            # Initialize Devin
            result = await initialize_devin(standalone_context)
            print(result)
            
            # Test voice system
            if self.config["devin_settings"]["voice_enabled"]:
                try:
                    voice_manager.speak("Standalone Devin systems online and ready.")
                    self.voice_enabled = True
                    print("✅ Voice system initialized")
                except Exception as e:
                    print(f"⚠️  Voice system unavailable: {e}")
                    self.voice_enabled = False
            
            print("\n🎯 Devin is ready to assist!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def process_command(self, command: str) -> str:
        """Process user command and return response."""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": command,
                "type": "user_input"
            })
            
            # Check for direct tool commands
            if command.lower().startswith('/'):
                return await self.handle_direct_command(command[1:])
            
            # Use Devin's command center for AI-powered command processing
            response = await devin_command_center(command, standalone_context)
            
            # Add response to history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "devin": response,
                "type": "devin_response"
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return f"I encountered an error processing that command: {str(e)}"
    
    async def handle_direct_command(self, command: str) -> str:
        """Handle direct tool commands (e.g., /help, /tools, /status)."""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "help":
                return self.get_help_text()
            
            elif cmd == "tools":
                tools = tool_registry.list_tools()
                return f"📋 Available tools ({len(tools)}):\n" + "\n".join([f"• {tool}" for tool in tools[:20]])
            
            elif cmd == "status":
                from devin_system import system_status_report
                return await system_status_report(standalone_context)
            
            elif cmd == "history":
                return self.get_conversation_history()
            
            elif cmd == "clear":
                self.conversation_history.clear()
                return "🗑️ Conversation history cleared"
            
            elif cmd == "voice":
                if len(parts) > 1:
                    if parts[1].lower() == "on":
                        self.voice_enabled = True
                        return "🔊 Voice output enabled"
                    elif parts[1].lower() == "off":
                        self.voice_enabled = False
                        return "🔇 Voice output disabled"
                
                return f"🔊 Voice status: {'Enabled' if self.voice_enabled else 'Disabled'}"
            
            else:
                return f"❌ Unknown command: /{cmd}. Type '/help' for available commands."
                
        except Exception as e:
            return f"Error handling command: {str(e)}"
    
    def get_help_text(self) -> str:
        """Get help text for the user."""
        help_text = """
🤖 STANDALONE DEVIN AI ASSISTANT - HELP

💬 BASIC USAGE:
• Type any question or command naturally
• Example: "take a screenshot"
• Example: "what time is it?"
• Example: "search the web for python tutorials"

🛠️ DIRECT COMMANDS:
• /help - Show this help text
• /tools - List all available tools
• /status - System status report
• /history - Show conversation history
• /clear - Clear conversation history
• /voice on/off - Enable/disable voice output
• /quit or /exit - Exit the application

🎯 CAPABILITIES:
• System control and file operations
• Screen capture and automation
• Voice synthesis and recognition
• Web search and information lookup
• Mathematical calculations
• Text translation
• Window management
• Clipboard operations
• And much more!

🔐 PERMISSIONS:
• Use "grant permission all" to enable all features
• Use "grant permission [specific]" for individual permissions

💡 TIP: Start with "grant permission all" for full functionality!
        """
        return help_text.strip()
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history."""
        if not self.conversation_history:
            return "📝 No conversation history yet"
        
        history = ["📝 CONVERSATION HISTORY", "=" * 30]
        
        for entry in self.conversation_history[-10:]:  # Last 10 entries
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
            
            if entry["type"] == "user_input":
                history.append(f"[{timestamp}] You: {entry['user']}")
            elif entry["type"] == "devin_response":
                history.append(f"[{timestamp}] Devin: {entry['devin'][:100]}...")
        
        return "\n".join(history)
    
    async def text_mode(self):
        """Run in text-only mode."""
        print("\n💬 TEXT MODE - Type '/quit' to exit, '/help' for commands")
        print("=" * 60)
        
        while self.running:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                    break
                
                if not user_input:
                    continue
                
                # Process the command
                print("\n🤖 Devin: Thinking...")
                response = await self.process_command(user_input)
                print(f"\n🤖 Devin: {response}")
                
                # Optionally speak the response
                if self.voice_enabled and voice_manager.tts_engine:
                    try:
                        # Speak a shortened version for better experience
                        speak_text = response[:200] + "..." if len(response) > 200 else response
                        # Remove emojis and formatting for cleaner speech
                        speak_text = ''.join(char for char in speak_text if char.isalnum() or char.isspace() or char in '.,!?')
                        voice_manager.speak(speak_text)
                    except Exception as e:
                        logger.debug(f"Voice output error: {e}")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Goodbye! Devin systems shutting down.")
    
    async def voice_mode(self):
        """Run in voice interaction mode."""
        print("\n🎤 VOICE MODE - Say 'devin quit' to exit")
        print("=" * 60)
        
        # Check if voice input is available
        if not voice_manager.recognizer or not voice_manager.microphone:
            print("❌ Voice input not available. Switching to text mode...")
            await self.text_mode()
            return
        
        while self.running:
            try:
                print("\n🎧 Listening for wake word 'devin'...")
                
                # Listen for wake word or command
                recognized_text = voice_manager.listen(timeout=30)
                
                if not recognized_text:
                    continue
                
                print(f"🎤 Heard: {recognized_text}")
                
                # Check for wake word
                wake_word = self.config["devin_settings"]["wake_word"].lower()
                if wake_word not in recognized_text.lower():
                    print("💭 (Wake word not detected)")
                    continue
                
                # Remove wake word from command
                command = recognized_text.lower().replace(wake_word, "").strip()
                
                if not command or command in ["quit", "exit", "goodbye"]:
                    break
                
                print(f"🤖 Devin: Processing '{command}'...")
                
                # Process the command
                response = await self.process_command(command)
                print(f"🤖 Devin: {response}")
                
                # Speak the response
                if voice_manager.tts_engine:
                    speak_text = response[:200] + "..." if len(response) > 200 else response
                    speak_text = ''.join(char for char in speak_text if char.isalnum() or char.isspace() or char in '.,!?')
                    voice_manager.speak(speak_text)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Voice mode error: {e}")
                print("Switching to text mode...")
                await self.text_mode()
                break
    
    async def run(self, mode: str = "auto"):
        """Run the Devin assistant."""
        self.running = True
        
        # Initialize systems
        if not await self.initialize_systems():
            return
        
        try:
            # Choose interaction mode
            if mode == "text":
                await self.text_mode()
            elif mode == "voice":
                await self.voice_mode()
            else:
                # Auto mode - show menu
                print("\n🔄 Choose interaction mode:")
                print("1. Text mode (keyboard input)")
                print("2. Voice mode (speech input)")
                print("3. Auto (voice with text fallback)")
                
                try:
                    choice = input("\nEnter choice (1-3, default=1): ").strip()
                    
                    if choice == "2":
                        await self.voice_mode()
                    elif choice == "3":
                        if self.voice_enabled and voice_manager.recognizer:
                            print("\n🔄 Starting voice mode (Ctrl+C for text mode)")
                            try:
                                await self.voice_mode()
                            except KeyboardInterrupt:
                                print("\n🔄 Switching to text mode...")
                                await self.text_mode()
                        else:
                            print("Voice input not available, using text mode...")
                            await self.text_mode()
                    else:
                        await self.text_mode()
                        
                except (KeyboardInterrupt, EOFError):
                    print("\n👋 Goodbye!")
        
        finally:
            self.running = False

async def main():
    """Main entry point for Standalone Devin."""
    try:
        devin = StandaloneDevin()
        await devin.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Application error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
