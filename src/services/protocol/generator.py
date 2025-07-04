# src/services/protocol/generator.py
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class ProtocolData:
    audio_file: str
    transcript: str
    segments: List[Dict]  # Whisper segments with timestamps
    speakers: List[Dict]
    protocol_text: str
    metadata: Dict

class ProtocolGenerator:
    def __init__(self, ollama_client, whisper_client, diarization_client):
        self.ollama = ollama_client
        self.whisper = whisper_client
        self.diarization = diarization_client
        
    def process_audio_to_protocol(self, audio_path: str) -> ProtocolData:
        """Komplette Pipeline: Audio → Protokoll"""
        
        # 1. Transkription
        transcript_result = self.whisper.transcribe_with_timestamps(audio_path)
        
        # 2. Speaker Diarization
        speakers = self.diarization.identify_speakers(audio_path)
        
        # 3. Protokoll-Generierung
        protocol_text = self.ollama.generate_protocol(
            transcript_result["text"], 
            speakers
        )
        
        return ProtocolData(
            audio_file=audio_path,
            transcript=transcript_result["text"],
            segments=transcript_result["segments"],
            speakers=speakers,
            protocol_text=protocol_text,
            metadata={
                "language": transcript_result["language"],
                "duration": transcript_result["duration"],
                "speaker_count": len(set(s["speaker"] for s in speakers)),
                "segments_count": len(transcript_result["segments"])
            }
        )