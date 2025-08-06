"""
Voice and audio interaction capabilities for Standalone DEVIN.
"""
import speech_recognition as sr
import pyttsx3
import threading
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from standalone_framework import function_tool, RunContext, gemini_tool
from gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class VoiceManager:
    """Manages voice synthesis and recognition."""
    
    def __init__(self):
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.voice_settings = {
            "rate": 180,
            "volume": 0.8,
            "voice_id": 0  # 0 for male, 1 for female (if available)
        }
        self.initialize_tts()
        self.initialize_speech_recognition()
    
    def initialize_tts(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice settings
            self.tts_engine.setProperty('rate', self.voice_settings['rate'])
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])
            
            # Try to set voice
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.voice_settings['voice_id']:
                self.tts_engine.setProperty('voice', voices[self.voice_settings['voice_id']].id)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            self.tts_engine = None
    
    def initialize_speech_recognition(self):
        """Initialize speech recognition."""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("Speech recognition initialized successfully")
            
        except Exception as e:
            logger.error(f"Speech recognition initialization error: {e}")
            self.recognizer = None
            self.microphone = None
    
    def speak(self, text: str):
        """Speak the given text."""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        else:
            logger.warning("TTS engine not available")
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech and return recognized text."""
        if not self.recognizer or not self.microphone:
            logger.warning("Speech recognition not available")
            return None
        
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Recognition service error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None

# Global voice manager instance
voice_manager = VoiceManager()

@function_tool
async def speak_text(text: str, context: RunContext) -> str:
    """
    Convert text to speech using DEVIN's voice system.
    
    Args:
        text: Text to speak
    """
    try:
        if not text.strip():
            return "Error: No text provided to speak"
        
        # Limit text length for safety
        if len(text) > 500:
            text = text[:500] + "... text truncated"
        
        # Speak in a separate thread to avoid blocking
        def speak_async():
            voice_manager.speak(text)
        
        thread = threading.Thread(target=speak_async)
        thread.daemon = True
        thread.start()
        
        return f"🗣️ Speaking: {text[:50]}{'...' if len(text) > 50 else ''}"
        
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        return f"Speech synthesis error: {str(e)}"

@function_tool
async def listen_for_command(context: RunContext, timeout: int = 10) -> str:
    """
    Listen for voice commands using DEVIN's speech recognition.
    
    Args:
        timeout: Maximum time to listen in seconds
    """
    try:
        recognized_text = voice_manager.listen(timeout=timeout)
        
        if recognized_text:
            return f"Voice command received: {recognized_text}"
        else:
            return "No voice command recognized. Please try again."
            
    except Exception as e:
        logger.error(f"Voice recognition error: {e}")
        return f"Voice recognition error: {str(e)}"

@function_tool
async def configure_voice(setting: str, value: str, context: RunContext) -> str:
    """
    Configure voice settings for DEVIN.
    
    Args:
        setting: Setting to change ('rate', 'volume', 'voice', 'test')
        value: New value for the setting
    """
    try:
        if setting == "rate":
            rate = int(value)
            if 50 <= rate <= 300:
                voice_manager.voice_settings['rate'] = rate
                if voice_manager.tts_engine:
                    voice_manager.tts_engine.setProperty('rate', rate)
                return f"✅ Speech rate set to {rate} words per minute"
            else:
                return "❌ Rate must be between 50 and 300"
        
        elif setting == "volume":
            volume = float(value)
            if 0.0 <= volume <= 1.0:
                voice_manager.voice_settings['volume'] = volume
                if voice_manager.tts_engine:
                    voice_manager.tts_engine.setProperty('volume', volume)
                return f"✅ Volume set to {int(volume * 100)}%"
            else:
                return "❌ Volume must be between 0.0 and 1.0"
        
        elif setting == "voice":
            voice_id = int(value)
            if voice_manager.tts_engine:
                voices = voice_manager.tts_engine.getProperty('voices')
                if voices and 0 <= voice_id < len(voices):
                    voice_manager.voice_settings['voice_id'] = voice_id
                    voice_manager.tts_engine.setProperty('voice', voices[voice_id].id)
                    return f"✅ Voice changed to {voices[voice_id].name}"
                else:
                    return f"❌ Voice ID must be between 0 and {len(voices)-1 if voices else 0}"
            else:
                return "❌ TTS engine not available"
        
        elif setting == "test":
            test_text = value if value else "Hello, I am Devin. Voice system test complete."
            voice_manager.speak(test_text)
            return f"🔊 Voice test: {test_text}"
        
        elif setting == "list_voices":
            if voice_manager.tts_engine:
                voices = voice_manager.tts_engine.getProperty('voices')
                if voices:
                    voice_list = []
                    for i, voice in enumerate(voices):
                        voice_list.append(f"{i}: {voice.name}")
                    return "Available voices:\n" + "\n".join(voice_list)
                else:
                    return "No voices available"
            else:
                return "❌ TTS engine not available"
        
        else:
            return "❌ Unknown setting. Use: rate, volume, voice, test, list_voices"
            
    except ValueError:
        return f"❌ Invalid value for {setting}: {value}"
    except Exception as e:
        logger.error(f"Voice configuration error: {e}")
        return f"Error configuring voice: {str(e)}"

@function_tool
async def voice_conversation_mode(context: RunContext) -> str:
    """
    Enter interactive voice conversation mode with DEVIN.
    """
    try:
        conversation_log = []
        conversation_log.append("🎤 DEVIN Voice Conversation Mode Activated")
        conversation_log.append("Say 'exit' or 'quit' to end conversation")
        
        # Initial greeting
        greeting = "Hello! I'm Devin. I'm ready for voice conversation. How can I assist you?"
        voice_manager.speak(greeting)
        conversation_log.append(f"Devin: {greeting}")
        
        # Conversation loop would be handled by the main application
        return "\n".join(conversation_log) + "\n\nNote: Full conversation mode requires integration with main application"
        
    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        return f"Voice conversation error: {str(e)}"

@function_tool
async def audio_system_control(action: str, parameter: str = "", context: RunContext = None) -> str:
    """
    Control audio system settings.
    
    Args:
        action: Action to perform ('mute', 'unmute', 'volume_up', 'volume_down', 'status')
        parameter: Additional parameter (e.g., volume level)
    """
    try:
        if action == "status":
            status = []
            status.append("🔊 AUDIO SYSTEM STATUS")
            status.append(f"TTS Engine: {'✅ Available' if voice_manager.tts_engine else '❌ Not Available'}")
            status.append(f"Speech Recognition: {'✅ Available' if voice_manager.recognizer else '❌ Not Available'}")
            status.append(f"Current Rate: {voice_manager.voice_settings['rate']} WPM")
            status.append(f"Current Volume: {int(voice_manager.voice_settings['volume'] * 100)}%")
            
            return "\n".join(status)
        
        elif action in ["mute", "unmute", "volume_up", "volume_down"]:
            # These would integrate with system audio controls
            return f"🔊 Audio action '{action}' noted. System audio control requires additional permissions."
        
        else:
            return "❌ Unknown action. Use: status, mute, unmute, volume_up, volume_down"
            
    except Exception as e:
        logger.error(f"Audio control error: {e}")
        return f"Audio control error: {str(e)}"

@function_tool
async def devin_wake_word_detection(context: RunContext) -> str:
    """
    Listen for DEVIN wake word activation.
    """
    try:
        wake_words = ["devin", "hey devin", "ok devin"]
        
        # This would implement continuous listening for wake words
        # For now, return status
        return f"🎧 Wake word detection ready. Listening for: {', '.join(wake_words)}\nNote: Continuous detection requires background service"
        
    except Exception as e:
        logger.error(f"Wake word detection error: {e}")
        return f"Wake word detection error: {str(e)}"
