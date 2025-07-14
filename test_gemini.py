#!/usr/bin/env python3
"""
Test script to verify Gemini API integration.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_connection():
    """Test if Gemini API is working correctly."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return False
        
        print("✅ GOOGLE_API_KEY found")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different model names to find the correct one
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
            except:
                model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Test simple query
        print("🧪 Testing Gemini API connection...")
        response = model.generate_content("Say 'Hello, Devin AI is working!' in a creative way.")
        
        print("✅ Gemini API test successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Devin AI Assistant - Gemini Integration")
    print("=" * 50)
    
    success = test_gemini_connection()
    
    if success:
        print("\n🎉 All tests passed! Devin is ready to use with Gemini AI.")
    else:
        print("\n⚠️ Some tests failed. Please check your configuration.")
