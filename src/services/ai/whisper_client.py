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
            print(f"🎤 Starting Whisper transcription for: {audio_path}")
            
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
            
            # Update result with calculated duration
            result['duration'] = duration
            
            print(f"✅ Transcription completed. Final duration: {duration:.2f}s")
            
        except Exception as e:
            print(f"⚠️ Whisper transcription failed: {e}")
            # Create minimal fallback result
            result = {
                "text": "Transcription failed",
                "segments": [],
                "language": "de",
                "duration": 0
            }
        
        return {
            "text": result.get("text", ""),
            "segments": result.get("segments", []),
            "language": result.get("language", "de"),
            "duration": result.get("duration", 0)
        }