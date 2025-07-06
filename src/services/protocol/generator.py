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
        
        print("🎵 Starting audio processing pipeline...")
        
        # 1. Transkription
        print("📝 Starting transcription...")
        transcript_result = self.whisper.transcribe_with_timestamps(audio_path)
        print(f"📝 Transcription completed. Length: {len(transcript_result['text'])} chars")
        print(f"📝 Duration: {transcript_result.get('duration', 'unknown')} seconds")
        print(f"📝 Segments: {len(transcript_result.get('segments', []))}")
        
        # 2. Speaker Diarization
        print("🎭 Starting speaker diarization...")
        speakers = self.diarization.identify_speakers(audio_path)
        print(f"🎭 Speaker diarization completed. Found {len(speakers)} segments")
        
        # 3. Merge transcription with speaker information
        enhanced_segments = self._merge_transcription_with_speakers(
            transcript_result["segments"], speakers
        )
        
        # 4. Calculate metadata with proper values
        unique_speakers = list(set(s["speaker"] for s in speakers)) if speakers else []
        duration = transcript_result.get("duration", 0)
        
        # Calculate actual speaker count
        speaker_count = len(unique_speakers) if unique_speakers else 1
        
        metadata = {
            "language": transcript_result.get("language", "de"),
            "duration": duration,
            "duration_formatted": self._format_duration(duration),
            "speaker_count": speaker_count,
            "unique_speakers": unique_speakers,
            "segments_count": len(transcript_result.get("segments", [])),
            "diarization_available": len(speakers) > 0,
            "transcript_length": len(transcript_result["text"]),
            "average_segment_duration": duration / len(transcript_result.get("segments", [1])) if duration > 0 else 0
        }
        
        print(f"📊 Enhanced Metadata: {metadata}")
        
        # 5. Protokoll-Generierung
        print("🤖 Starting protocol generation...")
        protocol_text = self.ollama.generate_protocol(
            transcript_result["text"], 
            speakers
        )
        print("🤖 Protocol generation completed")
        
        return ProtocolData(
            audio_file=audio_path,
            transcript=transcript_result["text"],
            segments=enhanced_segments if enhanced_segments else transcript_result.get("segments", []),
            speakers=speakers,
            protocol_text=protocol_text,
            metadata=metadata
        )
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds <= 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes >= 60:
            hours = int(minutes // 60)
            minutes = int(minutes % 60)
            return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
        else:
            return f"{minutes}:{remaining_seconds:02d}"
    
    def _merge_transcription_with_speakers(self, whisper_segments: List[Dict], speaker_segments: List[Dict]) -> List[Dict]:
        """Merge Whisper transcription segments with speaker diarization"""
        if not speaker_segments:
            # No speaker diarization available, add default speaker to Whisper segments
            return [
                {
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0),
                    'text': seg.get('text', ''),
                    'speaker': 'Speaker_1'
                }
                for seg in whisper_segments
            ]
        
        enhanced_segments = []
        
        for whisper_seg in whisper_segments:
            whisper_start = whisper_seg.get('start', 0)
            whisper_end = whisper_seg.get('end', 0)
            whisper_text = whisper_seg.get('text', '')
            
            # Find overlapping speaker segment
            speaker = "Speaker_Unknown"
            best_overlap = 0
            
            for speaker_seg in speaker_segments:
                speaker_start = speaker_seg.get('start', 0)
                speaker_end = speaker_seg.get('end', 0)
                
                # Calculate overlap
                overlap_start = max(whisper_start, speaker_start)
                overlap_end = min(whisper_end, speaker_end)
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    speaker = speaker_seg.get('speaker', 'Speaker_Unknown')
            
            enhanced_segments.append({
                'start': whisper_start,
                'end': whisper_end,
                'text': whisper_text,
                'speaker': speaker
            })
        
        return enhanced_segments