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
    
    def __init__(self, model_size: str = "small"):
        self.current_model_size = model_size
        self.model = None
        self.load_model(model_size)
        
    def load_model(self, model_size: str):
        """Load or reload Whisper model"""
        try:
            print(f"🔄 Loading Whisper model: {model_size}")
            if model_size not in self.AVAILABLE_MODELS:
                print(f"⚠️ Unknown model {model_size}, falling back to 'small'")
                model_size = "small"
            
            self.model = whisper.load_model(model_size)
            self.current_model_size = model_size
            model_info = self.AVAILABLE_MODELS[model_size]
            print(f"✅ Whisper model '{model_size}' loaded successfully")
            print(f"📊 Model size: {model_info['size']}, Speed: {model_info['relative_speed']}")
            return True
        except Exception as e:
            print(f"❌ Failed to load Whisper model '{model_size}': {e}")
            if model_size != "small":
                print("🔄 Falling back to 'small' model...")
                return self.load_model("small")
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
        """Whisper Transkription mit Zeitstempeln und robustem Fallback-System"""
        
        # Check if model change is requested
        if model_override and model_override != self.current_model_size:
            print(f"🔄 Model change requested: {self.current_model_size} -> {model_override}")
            if not self.load_model(model_override):
                print(f"⚠️ Failed to load {model_override}, using current model: {self.current_model_size}")
        
        try:
            print(f"🎤 Starting Whisper transcription with model '{self.current_model_size}' for: {audio_path}")
            
            # Verify audio file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            print("🚀 Starting Whisper transcription...")
            
            # Try multiple transcription strategies with increasing simplicity
            result = None
            last_error = None
            
            # Strategy 1: Simple direct transcription (most reliable)
            try:
                print("🔄 Strategy 1: Direct transcription")
                result = self.model.transcribe(
                    audio_path, 
                    language=language,
                    verbose=False,
                    fp16=False  # Ensure no FP16 issues
                )
                print("✅ Direct transcription successful")
                
            except Exception as e1:
                print(f"⚠️ Direct transcription failed: {e1}")
                last_error = e1
                
                # Strategy 2: Try with explicit audio loading
                try:
                    print("🔄 Strategy 2: Manual audio loading")
                    import librosa
                    
                    # Load audio with librosa for better compatibility
                    audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)
                    
                    # Ensure minimum length (avoid empty audio)
                    if len(audio_data) < 1600:  # 0.1 seconds minimum
                        print(f"⚠️ Very short audio ({len(audio_data)} samples), padding")
                        audio_data = np.pad(audio_data, (0, 1600 - len(audio_data)))
                    
                    # Normalize audio to prevent issues
                    if np.max(np.abs(audio_data)) > 0:
                        audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95
                    
                    result = self.model.transcribe(
                        audio_data, 
                        language=language,
                        verbose=False,
                        fp16=False
                    )
                    print("✅ Manual loading transcription successful")
                    
                except Exception as e2:
                    print(f"⚠️ Manual loading failed: {e2}")
                    last_error = e2
                    
                    # Strategy 3: Try with minimal parameters
                    try:
                        print("🔄 Strategy 3: Minimal parameters")
                        result = self.model.transcribe(audio_path)
                        print("✅ Minimal transcription successful")
                        
                    except Exception as e3:
                        print(f"⚠️ Minimal transcription failed: {e3}")
                        last_error = e3
                        
                        # Strategy 4: Try with different model (fallback to tiny)
                        if self.current_model_size != "tiny":
                            try:
                                print("🔄 Strategy 4: Fallback to tiny model")
                                original_model = self.current_model_size
                                if self.load_model("tiny"):
                                    result = self.model.transcribe(
                                        audio_path,
                                        language=language,
                                        verbose=False,
                                        fp16=False
                                    )
                                    print("✅ Tiny model transcription successful")
                                    # Restore original model
                                    self.load_model(original_model)
                                    
                            except Exception as e4:
                                print(f"⚠️ Tiny model fallback failed: {e4}")
                                last_error = e4
                                # Restore original model
                                self.load_model(original_model)
            
            if not result:
                raise Exception(f"All transcription strategies failed. Last error: {last_error}")
                
            print(f"✅ Whisper transcription completed!")
            print(f"📝 Text length: {len(result.get('text', ''))}")
            print(f"📊 Segments found: {len(result.get('segments', []))}")
            
            # Calculate duration from segments or estimate from audio
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
    
    def _preprocess_audio_for_whisper(self, audio_path: str) -> str:
        """Preprocess audio for better Whisper compatibility"""
        try:
            print(f"🔄 Preprocessing audio for Whisper: {audio_path}")
            
            # Check if file exists and is readable
            if not os.path.exists(audio_path):
                print(f"❌ Audio file not found: {audio_path}")
                return audio_path
            
            file_size = os.path.getsize(audio_path)
            print(f"📏 Original file size: {file_size} bytes")
            
            # Try to load audio with librosa
            print("🔄 Loading audio with librosa...")
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            print(f"✅ Audio loaded: {len(audio)} samples at {sr}Hz")
            
            # Handle empty or very short audio
            if len(audio) == 0:
                print("⚠️ Empty audio file detected")
                # Create minimal silence
                audio = np.zeros(16000)  # 1 second of silence
                print("✅ Created 1 second of silence as fallback")
            elif len(audio) < 1600:  # Less than 0.1 seconds
                print(f"⚠️ Very short audio detected: {len(audio)} samples, padding...")
                # Pad to at least 1 second
                audio = np.pad(audio, (0, 16000 - len(audio)), mode='constant')
                print(f"✅ Padded to {len(audio)} samples")
            
            # Normalize audio to prevent overflow
            if np.max(np.abs(audio)) > 0:
                max_val = np.max(np.abs(audio))
                audio = audio / max_val * 0.95
                print(f"✅ Audio normalized (max: {max_val:.3f})")
            else:
                print("⚠️ Audio appears to be silent")
            
            # Create temporary preprocessed file
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_filename = f"whisper_preprocessed_{os.path.basename(audio_path)}.wav"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            print(f"💾 Saving preprocessed audio to: {temp_path}")
            
            # Save as WAV with consistent format
            import soundfile as sf
            sf.write(temp_path, audio, 16000, format='WAV', subtype='PCM_16')
            
            # Verify saved file
            if os.path.exists(temp_path):
                saved_size = os.path.getsize(temp_path)
                print(f"✅ Preprocessed file saved: {saved_size} bytes")
                return temp_path
            else:
                print(f"❌ Failed to save preprocessed file")
                return audio_path
            
        except Exception as e:
            print(f"❌ Audio preprocessing failed: {e}")
            import traceback
            traceback.print_exc()
            print("🔄 Using original file")
            return audio_path