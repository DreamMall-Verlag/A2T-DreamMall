# src/services/ai/whisper_client.py
import whisper
from typing import Dict, List

class WhisperClient:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)
        
    def transcribe_with_timestamps(self, audio_path: str, language: str = "de") -> Dict:
        """Whisper Transkription mit Zeitstempeln"""
        result = self.model.transcribe(
            audio_path, 
            language=language,
            word_timestamps=True,
            verbose=True
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"],
            "duration": result.get("duration", 0)
        }