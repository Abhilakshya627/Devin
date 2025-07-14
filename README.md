# Devin - Advanced AI Assistant

An intelligent, feature-rich AI assistant built with LiveKit and OpenAI's Realtime API, inspired by J.A.R.V.I.S. from Iron Man.

## 🚀 Features

### Core Capabilities
- **Web Search**: Search the internet using DuckDuckGo for real-time information
- **Mathematical Calculations**: Perform complex mathematical operations safely
- **Weather Information**: Get current weather data for any location
- **Reminder Management**: Create and manage time-based reminders
- **Text Translation**: Translate text between different languages
- **Password Generation**: Create secure, customizable passwords
- **Memory Management**: Personal memory system for preferences and context
- **Text Analysis**: Analyze text for various metrics and insights
- **System Information**: Get real-time system performance data
- **URL Tools**: Shorten URLs and generate QR codes

### Technical Features
- Real-time voice interaction with LiveKit
- Advanced noise cancellation
- Configurable voice models and parameters
- Persistent memory system
- Enhanced error handling and logging
- Modular architecture for easy extension

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abhilakshya627/Devin.git
   cd Devin
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your API keys:
   - `LIVEKIT_URL`: Your LiveKit server URL
   - `LIVEKIT_API_KEY`: Your LiveKit API key
   - `LIVEKIT_API_SECRET`: Your LiveKit API secret
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENWEATHER_API_KEY`: (Optional) For weather features
   - `GOOGLE_TRANSLATE_API_KEY`: (Optional) For translation features

## 🎮 Usage

### Starting the Agent
```bash
python agent.py
```

### Available Tools

#### Web Search
- Search for current information on any topic
- Returns formatted results with source information

#### Mathematical Calculations
- Safe evaluation of mathematical expressions
- Supports basic operations, trigonometry, and constants
- Example: "Calculate sqrt(144) + 2^3"

#### Weather Information
- Get current weather for any location
- Includes temperature, conditions, humidity, and wind
- Example: "What's the weather in Tokyo?"

#### Reminder System
- Create time-based reminders
- Stores reminders locally with timestamps
- Example: "Remind me to call mom in 30 minutes"

#### Memory Management
- Store and retrieve personal preferences
- Search through conversation history
- Maintain context across sessions
- Actions: add, search, summary, preferences

#### Text Analysis
- Analyze text for character count, word count, reading time
- Calculate readability metrics
- Provide detailed text statistics

#### System Information
- Monitor CPU, memory, and disk usage
- Get OS and Python version information
- Real-time system performance data

#### Security Tools
- Generate secure passwords with customizable parameters
- Support for various character sets and lengths

### Configuration Options

You can customize the agent's behavior through environment variables:

- `AGENT_TEMPERATURE`: Controls response creativity (0.0-1.0)
- `MAX_SEARCH_RESULTS`: Number of search results to return
- `AUDIO_ENABLED`: Enable/disable audio features
- `VIDEO_ENABLED`: Enable/disable video features
- `NOISE_CANCELLATION`: Enable/disable noise cancellation
- `LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)

## 🏗 Architecture

### Core Components

1. **Agent (`agent.py`)**: Main agent class with LiveKit integration
2. **Tools (`tools.py`)**: Collection of available tools and functions
3. **Memory Manager (`memory_manager.py`)**: Persistent memory system
4. **Configuration (`config.py`)**: Centralized configuration management
5. **Prompts (`prompts.py`)**: Agent personality and instructions

### Adding New Tools

To add a new tool:

1. Create a function in `tools.py` with the `@function_tool` decorator
2. Add the tool to the imports in `agent.py`
3. Include the tool in the agent's tools list
4. Update documentation

Example:
```python
@function_tool
async def new_tool(parameter: str, context: RunContext) -> str:
    \"\"\"
    Description of what the tool does.
    
    Args:
        parameter: Description of the parameter
    \"\"\"
    try:
        # Tool implementation
        result = do_something(parameter)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

## 🎯 Personality

Devin is designed to be:
- **Professional yet witty**: Maintains professionalism with subtle humor
- **Proactive**: Anticipates user needs and offers relevant suggestions
- **Efficient**: Minimizes unnecessary tool calls while being thorough
- **Memory-aware**: Remembers user preferences and past interactions
- **Adaptive**: Learns from interactions to provide better assistance

## 🔧 Troubleshooting

### Common Issues

1. **Connection Issues**
   - Verify LiveKit credentials in `.env`
   - Check network connectivity
   - Ensure LiveKit server is accessible

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+)

3. **Tool Errors**
   - Verify API keys for external services
   - Check internet connectivity for web-based tools
   - Review logs for specific error messages

### Logging

Enable debug logging for troubleshooting:
```bash
LOG_LEVEL=DEBUG python agent.py
```

## 🚀 Advanced Features

### Memory System
The memory system allows Devin to:
- Remember user preferences across sessions
- Store important conversation context
- Search through historical interactions
- Maintain personalized assistance

### Error Handling
- Comprehensive error handling for all tools
- Graceful degradation when services are unavailable
- Detailed logging for debugging

### Security
- Safe mathematical expression evaluation
- Secure password generation
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Creator

Created by Abhilakshya Bhatt - An advanced AI assistant inspired by the vision of intelligent, helpful AI from science fiction.

## 🙏 Acknowledgments

- LiveKit for real-time communication infrastructure
- OpenAI for the powerful language models
- The open-source community for various tools and libraries
