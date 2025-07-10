# src/services/ai/diarization.py
import os
import sys
import librosa
import soundfile as sf
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Skip PyAnnote imports if not available
try:
    from pyannote.audio import Pipeline
    from pyannote.audio.pipelines import SpeakerDiarization as SpeakerDiarizationPipeline
    PYANNOTE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ PyAnnote not available: {e}")
    PYANNOTE_AVAILABLE = False
    Pipeline = None

from typing import List, Dict

class SpeakerDiarization:
    def __init__(self):
        self.available = False
        self.pipeline = None
        
        if not PYANNOTE_AVAILABLE:
            print("⚠️ PyAnnote Pipeline not available - Speaker Diarization disabled")
            return
            
        try:
            # Load HuggingFace token from environment
            hf_token = os.getenv('HUGGINGFACE_TOKEN')
            
            if hf_token:
                print(f"🔑 Using HuggingFace token: {hf_token[:8]}...")
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                )
            else:
                print("🔑 No HuggingFace token found, trying without authentication...")
                self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
            
            self.available = True
            print("✅ PyAnnote Speaker Diarization loaded successfully")
        except Exception as e:
            print(f"⚠️ PyAnnote Pipeline failed to load: {e}")
            print("💡 To enable Speaker Diarization:")
            print("   1. Visit https://hf.co/pyannote/speaker-diarization to accept user conditions")
            print("   2. Create HuggingFace token at https://hf.co/settings/tokens")
            print("   3. Set HUGGINGFACE_TOKEN in .env file")
            self.available = False
    
    def _preprocess_audio_for_pyannote(self, audio_path: str) -> str:
        """Convert audio to PyAnnote-compatible format"""
        try:
            print(f"🔄 Preprocessing audio for PyAnnote: {audio_path}")
            
            # Load audio with librosa (handles various formats well)
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Create temporary WAV file
            temp_dir = tempfile.gettempdir()
            temp_filename = f"pyannote_temp_{os.path.basename(audio_path)}.wav"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Save as WAV with consistent format
            sf.write(temp_path, audio, 16000, format='WAV', subtype='PCM_16')
            
            print(f"✅ Audio preprocessed and saved to: {temp_path}")
            print(f"📏 Audio shape: {audio.shape}, Sample rate: 16000")
            
            return temp_path
            
        except Exception as e:
            print(f"❌ Audio preprocessing failed: {e}")
            raise e
            
    def identify_speakers(self, audio_path: str, num_speakers: int = None) -> List[Dict]:
        """Speaker Diarization mit PyAnnote oder Fallback"""
        if not self.available or not self.pipeline:
            print("⚠️ Speaker Diarization not available - using single speaker fallback")
            return self._create_single_speaker_fallback(audio_path)
        
        preprocessed_path = None
        try:
            print(f"🎭 Starting speaker diarization for: {audio_path}")
            
            # Preprocess audio to avoid tensor size issues
            preprocessed_path = self._preprocess_audio_for_pyannote(audio_path)
            
            # Apply diarization on preprocessed audio
            if num_speakers:
                print(f"🎭 Running diarization with {num_speakers} speakers")
                diarization = self.pipeline(preprocessed_path, num_speakers=num_speakers)
            else:
                print("🎭 Running diarization with automatic speaker detection")
                diarization = self.pipeline(preprocessed_path)
            
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    "start": float(turn.start),
                    "end": float(turn.end),
                    "speaker": speaker,
                    "duration": float(turn.end - turn.start)
                })
            
            unique_speakers = len(set(s['speaker'] for s in speakers))
            print(f"🎭 Speaker diarization found {unique_speakers} unique speakers")
            print(f"🎭 Total segments: {len(speakers)}")
            
            return speakers
            
        except Exception as e:
            print(f"❌ Speaker Diarization failed: {e}")
            print("🔄 Falling back to single speaker mode")
            return self._create_single_speaker_fallback(audio_path)
        
        finally:
            # Clean up temporary file
            if preprocessed_path and os.path.exists(preprocessed_path):
                try:
                    os.remove(preprocessed_path)
                    print(f"🧹 Cleaned up temporary file: {preprocessed_path}")
                except Exception as e:
                    print(f"⚠️ Failed to clean up temporary file: {e}")
    
    def _create_single_speaker_fallback(self, audio_path: str) -> List[Dict]:
        """Create a single speaker segment for the entire audio duration"""
        try:
            # Try to get audio duration
            duration = 0
            try:
                audio, sr = librosa.load(audio_path, sr=None)
                duration = len(audio) / sr
                print(f"⏱️ Audio duration calculated: {duration:.2f} seconds")
            except Exception as e:
                print(f"⚠️ Could not calculate duration: {e}")
                # Fallback to file size estimation
                try:
                    file_size = os.path.getsize(audio_path)
                    duration = (file_size / 1024 / 1024) * 60  # Rough estimate
                    print(f"⏱️ Estimated duration from file size: {duration:.2f} seconds")
                except:
                    duration = 300  # 5 minutes default
            
            return [{
                "start": 0.0,
                "end": duration,
                "speaker": "SPEAKER_00",
                "duration": duration
            }]
            
        except Exception as e:
            print(f"⚠️ Fallback speaker creation failed: {e}")
            return [{
                "start": 0.0,
                "end": 300.0,  # 5 minutes default
                "speaker": "SPEAKER_00", 
                "duration": 300.0
            }]