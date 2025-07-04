# src/services/ai/diarization.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from pyannote.audio import Pipeline
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
                    "pyannote/speaker-diarization",
                    use_auth_token=hf_token
                )
            else:
                print("🔑 No HuggingFace token found, trying without authentication...")
                self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
            
            self.available = True
            print("✅ PyAnnote Speaker Diarization loaded successfully")
        except Exception as e:
            print(f"⚠️ PyAnnote Pipeline failed to load: {e}")
            print("💡 To enable Speaker Diarization:")
            print("   1. Visit https://hf.co/pyannote/speaker-diarization to accept user conditions")
            print("   2. Create HuggingFace token at https://hf.co/settings/tokens")
            print("   3. Set HUGGINGFACE_TOKEN in .env file")
            self.available = False
            
    def identify_speakers(self, audio_path: str, num_speakers: int = None) -> List[Dict]:
        """Speaker Diarization mit PyAnnote"""
        if not self.available or not self.pipeline:
            print("⚠️ Speaker Diarization not available - returning empty speaker list")
            return []
            
        try:
            diarization = self.pipeline(audio_path, num_speakers=num_speakers)
            
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker,
                    "duration": turn.end - turn.start
                })
            return speakers
        except Exception as e:
            print(f"❌ Speaker Diarization failed: {e}")
            return []