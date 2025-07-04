# src/services/ai/whisper_client.py
import whisper
import librosa
import numpy as np
from typing import Dict, List
import os

class WhisperClient:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)
        
    def transcribe_with_timestamps(self, audio_path: str, language: str = "de") -> Dict:
        """Whisper Transkription mit Zeitstempeln"""
        try:
            # First try direct Whisper transcription
            result = self.model.transcribe(
                audio_path, 
                language=language,
                word_timestamps=True,
                verbose=True
            )
        except Exception as e:
            print(f"⚠️ Direct Whisper transcription failed: {e}")
            print("🔄 Trying with librosa audio loading...")
            
            # Fallback: Load audio with librosa and convert
            try:
                audio, sr = librosa.load(audio_path, sr=16000)
                result = self.model.transcribe(
                    audio,
                    language=language,
                    word_timestamps=True,
                    verbose=True
                )
            except Exception as e2:
                print(f"❌ Librosa fallback also failed: {e2}")
                raise e
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"],
            "duration": result.get("duration", 0)
        }