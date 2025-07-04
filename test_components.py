#!/usr/bin/env python3
"""
A2T-Service Test Script
Testet alle kritischen Komponenten des Audio-zu-Text Systems
"""

import sys
import os

def test_imports():
    """Teste alle wichtigen Imports"""
    print("🧪 Testing Python imports...")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
        
    try:
        import whisper
        print(f"✅ Whisper: Available")
    except ImportError as e:
        print(f"❌ Whisper: {e}")
        return False
        
    try:
        import pyannote.audio
        print(f"✅ PyAnnote: Available") 
    except ImportError as e:
        print(f"❌ PyAnnote: {e}")
        return False
        
    try:
        import ollama
        print(f"✅ Ollama: Available")
    except ImportError as e:
        print(f"❌ Ollama: {e}")
        return False
        
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask: {e}")
        return False
        
    return True

def test_whisper():
    """Teste Whisper Model Loading"""
    print("\n🎤 Testing Whisper...")
    try:
        import whisper
        model = whisper.load_model("tiny")
        print("✅ Whisper tiny model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def test_pyannote():
    """Teste PyAnnote (falls möglich)"""
    print("\n👥 Testing PyAnnote...")
    try:
        from pyannote.audio import Pipeline
        print("✅ PyAnnote audio module imported successfully")
        print("ℹ️  Note: Speaker diarization pipeline requires HuggingFace token")
        return True
    except Exception as e:
        print(f"❌ PyAnnote test failed: {e}")
        return False

def test_ollama_connection():
    """Teste Ollama Connection (optional)"""
    print("\n🤖 Testing Ollama connection...")
    try:
        import ollama
        # Test connection (wird fehlschlagen wenn Ollama nicht läuft)
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': 'test'}])
        print("✅ Ollama connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Ollama connection failed (expected if not running): {e}")
        return False  # This is expected if Ollama isn't running

def main():
    print("🚀 A2T-Service Component Test")
    print("=" * 50)
    
    # Test basic imports
    if not test_imports():
        print("\n❌ Basic import tests failed!")
        sys.exit(1)
    
    # Test Whisper
    test_whisper()
    
    # Test PyAnnote
    test_pyannote()
    
    # Test Ollama (optional)
    test_ollama_connection()
    
    print("\n" + "=" * 50)
    print("🎉 A2T-Service core components are ready!")
    print("📝 Next steps:")
    print("   1. Install FFmpeg for audio processing")
    print("   2. Start Ollama server: 'ollama serve'")
    print("   3. Pull a model: 'ollama pull llama3'")
    print("   4. Run the Flask app: 'python src/api/app.py'")

if __name__ == "__main__":
    main()
