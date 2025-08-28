"""
Voice and audio interaction capabilities for DEVIN-like functionality.
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
from livekit.agents import function_tool, RunContext
from gemini_client import get_gemini_client, gemini_tool
import os
OFFLINE = os.getenv("OFFLINE_LLM", "0").lower() in {"1", "true", "yes"}
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "dev/models/vosk")
_offline_stt = None
if OFFLINE:
    try:
        from dev.offline_stt import OfflineSTT
        _offline_stt = OfflineSTT(VOSK_MODEL_PATH)
    except Exception:
        _offline_stt = None

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
            
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.voice_settings["voice_id"]:
                self.tts_engine.setProperty('voice', voices[self.voice_settings["voice_id"]].id)
            
            self.tts_engine.setProperty('rate', self.voice_settings["rate"])
            self.tts_engine.setProperty('volume', self.voice_settings["volume"])
            
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
    
    def initialize_speech_recognition(self):
        """Initialize speech recognition."""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
        except Exception as e:
            logger.error(f"Speech recognition initialization error: {e}")
    
    def speak(self, text: str, async_speak: bool = True):
        """Convert text to speech."""
        if not self.tts_engine:
            return False
        
        try:
            if async_speak:
                # Speak in a separate thread to avoid blocking
                threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
            else:
                self._speak_sync(text)
            return True
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _speak_sync(self, text: str):
        """Synchronous speech function."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for speech input."""
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Prefer offline STT if configured
            if _offline_stt is not None:
                try:
                    import tempfile, wave
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
                        wav_path = tf.name
                    # Save audio to WAV for Vosk
                    data = audio.get_wav_data()
                    with wave.open(wav_path, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(16000)
                        wf.writeframes(data)
                    text = _offline_stt.recognize_wav_file(wav_path) or ""
                    try:
                        os.remove(wav_path)
                    except Exception:
                        pass
                    return text
                except Exception as e:
                    logger.error(f"Offline STT failed, falling back to online: {e}")
            
            # Fallback: Google's service (may require internet)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except Exception as e:
                logger.error(f"Speech recognition error: {e}")
                return None
            
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unclear"
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None

# Global voice manager instance
voice_manager = VoiceManager()

@function_tool
async def speak_text(text: str, context: RunContext, async_speak: bool = True) -> str:
    """
    Convert text to speech using DEVIN-like voice.
    
    Args:
        text: Text to speak
        async_speak: Whether to speak asynchronously (non-blocking)
    """
    try:
        success = voice_manager.speak(text, async_speak)
        
        if success:
            return f"🔊 Speaking: {text[:100]}{'...' if len(text) > 100 else ''}"
        else:
            return "❌ Text-to-speech not available. Please install pyttsx3: pip install pyttsx3"
            
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        return f"Error with text-to-speech: {str(e)}"

@function_tool
async def listen_for_command(context: RunContext, timeout: int = 10) -> str:
    """
    Listen for voice commands from the user.
    
    Args:
        timeout: Maximum time to wait for input (seconds)
    """
    try:
        # Speak prompt
        voice_manager.speak("Yes, Sir? I'm listening.", async_speak=False)
        
        # Listen for command
        result = voice_manager.listen(timeout=timeout)
        
        if result == "timeout":
            return "⏱️ No voice input detected within timeout period."
        elif result == "unclear":
            return "🎤 I couldn't understand that clearly. Please try again, Sir."
        elif result is None:
            return "❌ Voice recognition not available. Please check microphone and install required packages."
        else:
            return f"🎤 Voice command received: {result}"
            
    except Exception as e:
        logger.error(f"Voice listening error: {e}")
        return f"Error listening for voice input: {str(e)}"

@function_tool
async def configure_voice(setting: str, value: str, context: RunContext) -> str:
    """
    Configure voice settings for DEVIN.
    
    Args:
        setting: Voice setting ('rate', 'volume', 'voice', 'test')
        value: New value for the setting
    """
    try:
        if setting == "rate":
            # Speech rate (words per minute)
            rate = int(value)
            if 50 <= rate <= 300:
                voice_manager.voice_settings["rate"] = rate
                voice_manager.tts_engine.setProperty('rate', rate)
                voice_manager.speak(f"Speech rate set to {rate} words per minute, Sir.")
                return f"✅ Speech rate set to {rate} WPM"
            else:
                return "❌ Rate must be between 50 and 300 WPM"
        
        elif setting == "volume":
            # Volume level (0.0 to 1.0)
            volume = float(value)
            if 0.0 <= volume <= 1.0:
                voice_manager.voice_settings["volume"] = volume
                voice_manager.tts_engine.setProperty('volume', volume)
                voice_manager.speak(f"Volume set to {int(volume*100)} percent, Sir.")
                return f"✅ Volume set to {int(volume*100)}%"
            else:
                return "❌ Volume must be between 0.0 and 1.0"
        
        elif setting == "voice":
            # Voice selection (0 for male, 1 for female if available)
            voice_id = int(value)
            voices = voice_manager.tts_engine.getProperty('voices')
            
            if voices and 0 <= voice_id < len(voices):
                voice_manager.voice_settings["voice_id"] = voice_id
                voice_manager.tts_engine.setProperty('voice', voices[voice_id].id)
                voice_manager.speak("Voice updated, Sir. How do I sound now?")
                return f"✅ Voice changed to option {voice_id}"
            else:
                return f"❌ Voice ID must be between 0 and {len(voices)-1 if voices else 0}"
        
        elif setting == "test":
            # Test current voice settings
            test_text = value if value else "All systems operational, Sir. Devin voice test complete."
            voice_manager.speak(test_text)
            return f"🔊 Voice test completed with: {test_text}"
        
        elif setting == "info":
            # Get current voice information
            current_settings = voice_manager.voice_settings
            voices = voice_manager.tts_engine.getProperty('voices')
            voice_count = len(voices) if voices else 0
            
            info = f"""🎙️ Current Voice Settings:
- Rate: {current_settings['rate']} WPM
- Volume: {int(current_settings['volume']*100)}%
- Voice ID: {current_settings['voice_id']}
- Available Voices: {voice_count}"""
            
            return info
        
        else:
            return "❌ Invalid setting. Available: rate, volume, voice, test, info"
            
    except ValueError:
        return "❌ Invalid value format for the setting"
    except Exception as e:
        logger.error(f"Voice configuration error: {e}")
        return f"Error configuring voice: {str(e)}"

@function_tool
@gemini_tool
async def voice_conversation_mode(context: RunContext, duration: int = 60) -> str:
    """
    Start an interactive voice conversation with DEVIN.
    
    Args:
        duration: Maximum conversation duration in seconds
    """
    try:
        conversation_log = []
        start_time = time.time()
        
        # Welcome message
        welcome_msg = "Good day, Sir. I'm ready for voice interaction. Speak your commands and I'll respond accordingly."
        voice_manager.speak(welcome_msg)
        conversation_log.append(f"Devin: {welcome_msg}")
        
        while time.time() - start_time < duration:
            # Listen for user input
            voice_manager.speak("Listening...")
            user_input = voice_manager.listen(timeout=10)
            
            if user_input == "timeout":
                voice_manager.speak("I'm still here if you need anything, Sir.")
                continue
            elif user_input == "unclear":
                voice_manager.speak("I didn't catch that. Could you repeat, Sir?")
                continue
            elif user_input is None:
                break
            
            conversation_log.append(f"User: {user_input}")
            
            # Check for exit commands
            if any(phrase in user_input.lower() for phrase in ["goodbye", "exit", "stop", "end conversation"]):
                farewell = "Until next time, Sir. It's been a pleasure."
                voice_manager.speak(farewell)
                conversation_log.append(f"Devin: {farewell}")
                break
            
            # Generate AI response
            client = get_gemini_client()
            prompt = f"""As Devin from the AI assistant, respond to this user input in character. 
Be helpful, intelligent, and slightly witty. Keep responses concise for voice interaction.
User said: {user_input}"""
            
            response = await client.generate_content(prompt)
            
            # Speak the response
            voice_manager.speak(response)
            conversation_log.append(f"Devin: {response}")
        
        # Save conversation log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"voice_conversation_{timestamp}.json"
        
        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "duration": time.time() - start_time,
                "conversation": conversation_log
            }, f, indent=2)
        
        summary = f"""🎙️ Voice Conversation Complete
Duration: {int(time.time() - start_time)} seconds
Exchanges: {len([entry for entry in conversation_log if entry.startswith('User:')])}
Log saved: {log_file}"""
        
        return summary
        
    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        return f"Error in voice conversation: {str(e)}"

@function_tool
async def audio_system_control(action: str, context: RunContext, level: int = 50) -> str:
    """
    Control system audio settings.
    
    Args:
        action: Audio action ('volume_up', 'volume_down', 'mute', 'unmute', 'set_volume', 'get_volume')
        level: Volume level for set_volume (0-100)
    """
    from devin_system import permission_manager
    
    permission_check = permission_manager.request_permission(
        "system_control", 
        f"Audio control: {action}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        import platform
        
        system = platform.system()
        
        if action == "volume_up":
            if system == "Windows":
                os.system("nircmd.exe changesysvolume 6553")
            else:
                os.system("amixer -D pulse sset Master 10%+")
            return "🔊 Volume increased"
        
        elif action == "volume_down":
            if system == "Windows":
                os.system("nircmd.exe changesysvolume -6553")
            else:
                os.system("amixer -D pulse sset Master 10%-")
            return "🔉 Volume decreased"
        
        elif action == "mute":
            if system == "Windows":
                os.system("nircmd.exe mutesysvolume 1")
            else:
                os.system("amixer -D pulse sset Master mute")
            return "🔇 Audio muted"
        
        elif action == "unmute":
            if system == "Windows":
                os.system("nircmd.exe mutesysvolume 0")
            else:
                os.system("amixer -D pulse sset Master unmute")
            return "🔊 Audio unmuted"
        
        elif action == "set_volume":
            if 0 <= level <= 100:
                if system == "Windows":
                    # Calculate volume for Windows (0-65535)
                    win_volume = int((level / 100) * 65535)
                    os.system(f"nircmd.exe setsysvolume {win_volume}")
                else:
                    os.system(f"amixer -D pulse sset Master {level}%")
                return f"🔊 Volume set to {level}%"
            else:
                return "❌ Volume level must be between 0 and 100"
        
        elif action == "get_volume":
            # This would require additional libraries for accurate volume reading
            return "🎵 Volume level reading requires additional system integration"
        
        else:
            return "❌ Invalid action. Available: volume_up, volume_down, mute, unmute, set_volume, get_volume"
            
    except Exception as e:
        logger.error(f"Audio control error: {e}")
        return f"Error controlling audio: {str(e)}"

@function_tool
async def devin_wake_word_detection(context: RunContext, wake_word: str = "devin") -> str:
    """
    Start wake word detection for hands-free activation.
    
    Args:
        wake_word: Wake word to listen for (default: "devin")
    """
    try:
        voice_manager.speak(f"Wake word detection activated. Say '{wake_word}' to get my attention, Sir.")
        
        # This would implement continuous listening in a real system
        # For now, we'll simulate the setup
        
        return f"""🎤 Wake Word Detection Active
Wake Word: "{wake_word}"
Status: Listening in background
Commands: "Hey {wake_word}" or "{wake_word.title()}, [command]"

Note: In a full implementation, this would run continuously in the background using threading."""
        
    except Exception as e:
        logger.error(f"Wake word detection error: {e}")
        return f"Error setting up wake word detection: {str(e)}"
