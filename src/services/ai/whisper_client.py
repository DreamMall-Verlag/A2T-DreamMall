# src/services/ai/whisper_client.py
import whisper
import librosa
import numpy as np
from typing import Dict, List
import os

class WhisperClient:
    # Available Whisper models with descriptions
    AVAILABLE_MODELS = {
        "tiny": {"size": "39 MB", "relative_speed": "~32x", "description": "Schnellstes Modell, geringste Qualität"},
        "base": {"size": "74 MB", "relative_speed": "~16x", "description": "Ausgewogen zwischen Geschwindigkeit und Qualität"},
        "small": {"size": "244 MB", "relative_speed": "~6x", "description": "Gute Qualität, moderate Geschwindigkeit"},
        "medium": {"size": "769 MB", "relative_speed": "~2x", "description": "Hohe Qualität, langsamer"},
        "large": {"size": "1550 MB", "relative_speed": "1x", "description": "Beste Qualität, langsamste Verarbeitung"},
        "large-v2": {"size": "1550 MB", "relative_speed": "1x", "description": "Verbesserte Version von Large"},
        "large-v3": {"size": "1550 MB", "relative_speed": "1x", "description": "Neueste Version mit bester Qualität"}
    }
    
    def __init__(self, model_size: str = "base"):
        self.current_model_size = model_size
        self.model = None
        self.load_model(model_size)
        
    def load_model(self, model_size: str):
        """Load or reload Whisper model"""
        try:
            print(f"🔄 Loading Whisper model: {model_size}")
            if model_size not in self.AVAILABLE_MODELS:
                print(f"⚠️ Unknown model {model_size}, falling back to 'base'")
                model_size = "base"
            
            self.model = whisper.load_model(model_size)
            self.current_model_size = model_size
            model_info = self.AVAILABLE_MODELS[model_size]
            print(f"✅ Whisper model '{model_size}' loaded successfully")
            print(f"📊 Model size: {model_info['size']}, Speed: {model_info['relative_speed']}")
            return True
        except Exception as e:
            print(f"❌ Failed to load Whisper model '{model_size}': {e}")
            if model_size != "base":
                print("🔄 Falling back to 'base' model...")
                return self.load_model("base")
            return False
    
    def get_model_info(self) -> Dict:
        """Get current model information"""
        model_info = self.AVAILABLE_MODELS.get(self.current_model_size, {})
        return {
            "current_model": self.current_model_size,
            "model_info": model_info,
            "available_models": self.AVAILABLE_MODELS
        }
        
    def transcribe_with_timestamps(self, audio_path: str, language: str = "de", model_override: str = None) -> Dict:
        """Whisper Transkription mit Zeitstempeln"""
        
        # Check if model change is requested
        if model_override and model_override != self.current_model_size:
            print(f"🔄 Model change requested: {self.current_model_size} -> {model_override}")
            if not self.load_model(model_override):
                print(f"⚠️ Failed to load {model_override}, using current model: {self.current_model_size}")
        
        try:
            print(f"🎤 Starting Whisper transcription with model '{self.current_model_size}' for: {audio_path}")
            
            # First try direct Whisper transcription
            result = self.model.transcribe(
                audio_path, 
                language=language,
                word_timestamps=True,
                verbose=True
            )
            
            # Always calculate duration from segments first (most reliable)
            duration = 0
            if result.get('segments') and len(result['segments']) > 0:
                last_segment = result['segments'][-1]
                duration = last_segment.get('end', 0)
                print(f"⏱️ Duration from segments: {duration:.2f} seconds")
            
            # If duration is still 0 or not available, try librosa
            if duration == 0:
                print("⏱️ No duration from segments, calculating from audio file...")
                try:
                    # Use a timeout approach for librosa loading
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Audio loading timeout")
                    
                    # Set timeout for audio loading (5 seconds)
                    if os.name != 'nt':  # Unix systems
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(5)
                    
                    try:
                        audio, sr = librosa.load(audio_path, sr=None)
                        duration = len(audio) / sr
                        print(f"⏱️ Calculated duration from librosa: {duration:.2f} seconds")
                    finally:
                        if os.name != 'nt':  # Unix systems
                            signal.alarm(0)  # Cancel alarm
                            
                except (TimeoutError, Exception) as e:
                    print(f"⚠️ Could not calculate duration with librosa: {e}")
                    # Final fallback: estimate from file size (very rough)
                    try:
                        file_size = os.path.getsize(audio_path)
                        # Rough estimate: ~1MB per minute for MP3
                        duration = (file_size / 1024 / 1024) * 60
                        print(f"⏱️ Estimated duration from file size: {duration:.2f} seconds")
                    except Exception as e2:
                        print(f"⚠️ File size estimation failed: {e2}")
                        duration = 0
            
            # Update result with calculated duration and model info
            result['duration'] = duration
            result['model_used'] = self.current_model_size
            
            print(f"✅ Transcription completed with model '{self.current_model_size}'. Duration: {duration:.2f}s")
            
        except Exception as e:
            print(f"⚠️ Whisper transcription failed: {e}")
            # Create minimal fallback result
            result = {
                "text": "Transcription failed",
                "segments": [],
                "language": "de",
                "duration": 0,
                "model_used": self.current_model_size
            }
        
        return {
            "text": result.get("text", ""),
            "segments": result.get("segments", []),
            "language": result.get("language", "de"),
            "duration": result.get("duration", 0),
            "model_used": result.get("model_used", self.current_model_size)
        }