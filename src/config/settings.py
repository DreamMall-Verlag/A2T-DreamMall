# src/config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class A2TSettings:
    """Zentrale Konfiguration für A2T-Service"""
    
    # === API KEYS & TOKENS ===
    # HuggingFace Token für PyAnnote Speaker Diarization
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')
    
    # === WHISPER KONFIGURATION ===
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'small')
    WHISPER_LANGUAGE = os.getenv('WHISPER_LANGUAGE', 'de')
    
    # === OLLAMA KONFIGURATION ===
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
    
    # === FLASK KONFIGURATION ===
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # === AUDIO VERARBEITUNG ===
    AUDIO_UPLOAD_FOLDER = os.getenv('AUDIO_UPLOAD_FOLDER', 'temp/uploads')
    AUDIO_OUTPUT_FOLDER = os.getenv('AUDIO_OUTPUT_FOLDER', 'temp/processed')
    MAX_AUDIO_SIZE_MB = int(os.getenv('MAX_AUDIO_SIZE_MB', 100))
    
    @classmethod
    def get_status(cls) -> dict:
        """Gibt den Status aller Konfigurationen zurück"""
        return {
            "huggingface_token_available": bool(cls.HUGGINGFACE_TOKEN),
            "huggingface_token_preview": cls.HUGGINGFACE_TOKEN[:8] + "..." if cls.HUGGINGFACE_TOKEN else "Nicht gesetzt",
            "whisper_model": cls.WHISPER_MODEL,
            "whisper_language": cls.WHISPER_LANGUAGE,
            "ollama_url": cls.OLLAMA_BASE_URL,
            "ollama_model": cls.OLLAMA_MODEL,
            "flask_config": {
                "host": cls.FLASK_HOST,
                "port": cls.FLASK_PORT,
                "debug": cls.FLASK_DEBUG
            },
            "audio_config": {
                "upload_folder": cls.AUDIO_UPLOAD_FOLDER,
                "output_folder": cls.AUDIO_OUTPUT_FOLDER,
                "max_size_mb": cls.MAX_AUDIO_SIZE_MB
            }
        }
    
    @classmethod
    def get_requirements(cls) -> dict:
        """Gibt die Anforderungen für vollständige Funktionalität zurück"""
        return {
            "required_for_speaker_diarization": {
                "description": "HuggingFace Token für automatische Sprecher-Erkennung",
                "current_status": "✅ Vorhanden" if cls.HUGGINGFACE_TOKEN else "❌ Nicht gesetzt",
                "required": False,  # Fallback verfügbar
                "setup_url": "https://hf.co/settings/tokens",
                "env_variable": "HUGGINGFACE_TOKEN"
            },
            "required_for_ai_protocols": {
                "description": "Ollama für KI-basierte Protokoll-Generierung",
                "current_status": "🔍 Wird zur Laufzeit getestet",
                "required": False,  # Fallback verfügbar
                "setup_info": "Ollama lokal installieren und llama3 Modell laden",
                "env_variable": "OLLAMA_BASE_URL"
            },
            "whisper_models": {
                "description": "Whisper Modelle für Spracherkennung",
                "current_model": cls.WHISPER_MODEL,
                "models_info": {
                    "tiny": "39 MB - Schnellstes Modell, geringste Qualität",
                    "base": "74 MB - Ausgewogen",
                    "small": "244 MB - Empfohlen für lokale Nutzung",
                    "medium": "769 MB - Hohe Qualität",
                    "large": "1550 MB - Beste Qualität"
                }
            }
        }
    
    @classmethod
    def print_startup_info(cls):
        """Zeigt Startup-Informationen an"""
        print("\n" + "="*60)
        print("🔧 A2T-DreamMall Konfiguration")
        print("="*60)
        
        print(f"🎯 Whisper Modell: {cls.WHISPER_MODEL}")
        print(f"🌍 Sprache: {cls.WHISPER_LANGUAGE}")
        
        if cls.HUGGINGFACE_TOKEN:
            print(f"🔑 HuggingFace Token: {cls.HUGGINGFACE_TOKEN[:8]}... ✅")
        else:
            print("🔑 HuggingFace Token: ❌ Nicht gesetzt")
            print("   → Speaker Diarization verwendet Fallback (alle Sprecher als 'Sprecher 1')")
        
        print(f"🤖 Ollama URL: {cls.OLLAMA_BASE_URL}")
        print("   → Wird zur Laufzeit getestet")
        
        print(f"🌐 Server: {cls.FLASK_HOST}:{cls.FLASK_PORT}")
        print("="*60 + "\n")
