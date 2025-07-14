#!/usr/bin/env python3
"""
Utility script for managing the Devin AI Assistant.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    try:
        import livekit
        import openai
        import requests
        import psutil
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are properly configured."""
    print("Checking environment configuration...")
    
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these environment variables.")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def setup_environment():
    """Setup the environment for first-time use."""
    print("Setting up environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("📝 Created .env file from template")
            print("Please edit .env file with your API keys")
        else:
            print("❌ .env.example file not found")
            return False
    
    # Create necessary directories
    directories = ['reminders', 'memory', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    print("✅ Environment setup complete!")
    return True

def run_agent():
    """Run the Devin agent."""
    print("Starting Devin AI Assistant...")
    
    if not check_dependencies():
        return False
    
    if not check_environment():
        return False
    
    try:
        subprocess.run([sys.executable, 'agent.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running agent: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def clean_data():
    """Clean temporary data and logs."""
    print("Cleaning temporary data...")
    
    # Clean directories
    clean_dirs = ['logs', '__pycache__']
    for directory in clean_dirs:
        if os.path.exists(directory):
            import shutil
            shutil.rmtree(directory)
            print(f"🗑️ Cleaned directory: {directory}")
    
    print("✅ Cleanup complete!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Devin AI Assistant Management Tool')
    parser.add_argument('command', choices=['setup', 'run', 'install', 'check', 'clean'], 
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_environment()
    elif args.command == 'run':
        run_agent()
    elif args.command == 'install':
        install_dependencies()
    elif args.command == 'check':
        check_dependencies() and check_environment()
    elif args.command == 'clean':
        clean_data()

if __name__ == '__main__':
    main()
