"""
Standalone Devin AI Assistant - No LiveKit Required
A complete desktop AI assistant with voice, screen control, and system automation.
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import json

# Import your existing modules (they'll work without LiveKit)
from devin_system import (
    grant_permission, revoke_permission, system_status_report,
    control_applications, file_operations, system_control,
    intelligent_automation, network_diagnostics
)
from screen_interaction import (
    take_screenshot, analyze_screen, mouse_control, keyboard_control,
    find_on_screen, window_management, clipboard_operations
)
from voice_interaction import (
    speak_text, listen_for_command, configure_voice,
    voice_conversation_mode, audio_system_control
)
from gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class StandaloneDevin:
    """Standalone Devin AI Assistant without LiveKit dependency."""
    
    def __init__(self):
        self.running = False
        self.gemini_client = get_gemini_client()
        self.voice_enabled = True
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for the assistant."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def initialize(self):
        """Initialize Devin systems."""
        print("🤖 DEVIN STANDALONE ASSISTANT")
        print("=" * 50)
        
        # Initialize voice system
        try:
            await speak_text("Devin systems initializing...", context=None)
            print("✅ Voice system ready")
        except Exception as e:
            print(f"❌ Voice system error: {e}")
            self.voice_enabled = False
        
        # Check system permissions
        try:
            status = await system_status_report(context=None)
            print("✅ System interface ready")
        except Exception as e:
            print(f"❌ System interface error: {e}")
        
        print("\n🎯 Devin is online and ready to assist!")
        return True
    
    async def process_command(self, command: str) -> str:
        """Process a user command and return response."""
        try:
            # Use Gemini to understand and route the command
            analysis_prompt = f"""
            As Devin, analyze this command and determine the best action:
            
            Command: {command}
            
            Available capabilities:
            - System control (files, applications, processes)
            - Screen interaction (screenshots, mouse, keyboard)
            - Voice interaction (speech synthesis, recognition)
            - Web search and information lookup
            - Automation tasks
            - Window management
            - Audio control
            - Clipboard operations
            
            Respond with:
            1. What action should be taken
            2. Which function to call
            3. Any parameters needed
            
            Be helpful and direct like Devin would be.
            """
            
            response = await self.gemini_client.generate_content(analysis_prompt)
            
            # For now, return the AI analysis
            # In a full implementation, you'd parse this and call appropriate functions
            return f"Devin: {response}"
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def text_mode(self):
        """Run in text-only mode."""
        print("\n💬 TEXT MODE - Type 'quit' to exit")
        print("=" * 40)
        
        while self.running:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                
                if not user_input:
                    continue
                
                # Process the command
                response = await self.process_command(user_input)
                print(f"\n{response}")
                
                # Optionally speak the response
                if self.voice_enabled:
                    try:
                        await speak_text(response, context=None)
                    except:
                        pass  # Continue even if voice fails
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Goodbye! Devin systems shutting down.")
    
    async def voice_mode(self):
        """Run in voice interaction mode."""
        print("\n🎤 VOICE MODE - Say 'devin quit' to exit")
        print("=" * 40)
        
        while self.running:
            try:
                # Listen for voice command
                print("\n🎧 Listening...")
                command = await listen_for_command(context=None)
                
                if not command or "quit" in command.lower():
                    break
                
                print(f"You said: {command}")
                
                # Process the command
                response = await self.process_command(command)
                print(f"Devin: {response}")
                
                # Speak the response
                await speak_text(response, context=None)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Voice error: {e}")
                # Fall back to text mode
                print("Switching to text mode...")
                await self.text_mode()
                break
    
    async def run(self, mode="auto"):
        """Run the Devin assistant."""
        self.running = True
        
        # Initialize systems
        await self.initialize()
        
        # Choose interaction mode
        if mode == "text":
            await self.text_mode()
        elif mode == "voice":
            await self.voice_mode()
        else:
            # Auto mode - try voice, fall back to text
            if self.voice_enabled:
                print("\n🔄 Starting in voice mode (Ctrl+C for text mode)")
                try:
                    await self.voice_mode()
                except KeyboardInterrupt:
                    print("\n🔄 Switching to text mode...")
                    await self.text_mode()
            else:
                await self.text_mode()

async def main():
    """Main entry point for standalone Devin."""
    devin = StandaloneDevin()
    
    print("Choose mode:")
    print("1. Auto (voice with text fallback)")
    print("2. Text only")
    print("3. Voice only")
    
    try:
        choice = input("Enter choice (1-3, default=1): ").strip()
        
        if choice == "2":
            await devin.run("text")
        elif choice == "3":
            await devin.run("voice")
        else:
            await devin.run("auto")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
 