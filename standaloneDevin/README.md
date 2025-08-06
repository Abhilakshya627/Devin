# 🤖 Standalone Devin AI Assistant

A complete AI assistant that runs locally without external service dependencies. Features voice interaction, screen automation, system control, and intelligent task execution.

## ✨ Features

- **🎯 No External Services Required** - Runs completely standalone
- **🗣️ Voice Interaction** - Text-to-speech and speech recognition
- **📺 Screen Control** - Screenshots, mouse/keyboard automation
- **💻 System Management** - File operations, application control
- **🧠 AI-Powered** - Google Gemini integration for intelligent responses
- **🔒 Permission-Based Security** - Granular control over system access
- **🌐 Web Search** - Built-in web search capabilities
- **📋 Memory System** - Conversation history and user preferences

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
Edit `.env` and add your Google Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run Devin
```bash
python standalone_devin.py
```

## 🎮 Usage

### Text Mode
```
You: take a screenshot
Devin: Taking screenshot...

You: what time is it?  
Devin: Current date and time: 2025-01-21 15:30:45

You: search web for python tutorials
Devin: Searching the web...
```

### Voice Mode
```
🎧 Listening for wake word 'devin'...
🎤 Heard: devin take a screenshot
🤖 Devin: Taking screenshot of the current screen...
```

### Direct Commands
```
/help      - Show help text
/tools     - List all available tools  
/status    - System status report
/history   - Conversation history
/voice on  - Enable voice output
/quit      - Exit application
```

## 🛠️ Available Tools

### System Control
- `grant_permission` - Enable system permissions
- `system_status_report` - Detailed system analysis  
- `control_applications` - Start/stop applications
- `file_operations` - File management
- `network_diagnostics` - Network connectivity tests

### Screen Interaction  
- `take_screenshot` - Screen capture
- `analyze_screen` - AI screen analysis
- `mouse_control` - Mouse automation
- `keyboard_control` - Keyboard input
- `window_management` - Window control
- `clipboard_operations` - Clipboard management

### Voice & Audio
- `speak_text` - Text-to-speech synthesis
- `listen_for_command` - Speech recognition
- `configure_voice` - Voice settings
- `audio_system_control` - Audio management

### Utilities
- `search_web` - Web search
- `get_current_time` - Date/time
- `calculate_math` - Mathematical calculations
- `translate_text` - Language translation
- `ai_assistant` - General AI assistance
- `create_reminder` - Simple reminders

## 🔐 Security & Permissions

Devin uses a permission-based security system:

```bash
# Enable all permissions for full functionality
You: grant permission all

# Enable specific permissions
You: grant permission screen_interaction
You: grant permission file_operations
```

## 📁 File Structure

```
standaloneDevin/
├── standalone_devin.py      # Main application
├── standalone_framework.py  # Core framework
├── tools.py                # Tool collection
├── devin_system.py         # System interaction
├── screen_interaction.py   # Screen automation
├── voice_interaction.py    # Voice capabilities
├── gemini_client.py        # AI client
├── memory_manager.py       # Memory system
├── requirements.txt        # Dependencies
├── .env                    # Configuration
└── README.md              # This file
```

## 🤝 Getting Started Tips

1. **First Time Setup**:
   ```
   You: grant permission all
   You: initialize devin
   ```

2. **Test Voice**:
   ```
   You: configure voice test hello world
   ```

3. **Take a Screenshot**:
   ```
   You: take a screenshot
   ```

4. **Get Help**:
   ```
   You: /help
   ```

## 🔧 Configuration

Edit `devin_config.json` to customize:
- Wake word ("devin" by default)
- Response personality
- Voice settings
- Auto-initialization

## 🐛 Troubleshooting

**Voice not working?**
```bash
pip install pyaudio pyttsx3 speechrecognition
```

**Screen automation not working?**
```bash
pip install pyautogui opencv-python
```

**Permission errors?**
```
You: grant permission all
```

## 📋 Requirements

- Python 3.8+
- Google Gemini API key (free tier available)
- Windows/Linux/macOS
- Microphone (for voice input)
- Speakers (for voice output)

## 🎯 No LiveKit, No Cloud!

This standalone version eliminates all external service dependencies:
- ✅ No LiveKit server required
- ✅ No cloud infrastructure needed  
- ✅ Runs completely local
- ✅ Your data stays private
- ✅ Works offline (except AI and web search)

---

**Ready to experience the power of a truly standalone AI assistant? Let's get started! 🚀**
