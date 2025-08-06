#!/usr/bin/env python3
"""
Setup script for Standalone Devin AI Assistant
Automatically installs dependencies and configures the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing dependencies")

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔧 Creating .env file...")
    env_content = """# Standalone Devin Configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Voice Settings
VOICE_ENABLED=true
WAKE_WORD=devin

# System Settings  
AUTO_PERMISSIONS=false
DEBUG_MODE=false
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env and add your Google Gemini API key")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        "google.generativeai",
        "pyautogui", 
        "pyttsx3",
        "speech_recognition",
        "cv2",
        "PIL",
        "pyperclip"
    ]
    
    print("🔧 Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules imported successfully")
    return True

def main():
    """Main setup function"""
    print("🤖 Standalone Devin AI Assistant Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("💡 Try manually running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit .env and add your Google Gemini API key")
    print("2. Run: python standalone_devin.py")
    print("3. Grant permissions: 'grant permission all'")
    print("4. Start chatting with Devin!")
    
    print("\n🚀 Ready to launch your standalone AI assistant!")

if __name__ == "__main__":
    main()
