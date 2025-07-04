# src/services/audio/processor.py
from pydub import AudioSegment
import subprocess
import librosa
import soundfile as sf

class AudioProcessor:
    def __init__(self):
        self.target_sample_rate = 16000  # Whisper-optimiert
        
    def normalize_audio(self, input_path: str, output_path: str) -> str:
        """Audio-Normalisierung mit FFmpeg (Whitepaper-konform)"""
        cmd = [
            'ffmpeg', '-i', input_path,
            '-af', 'loudnorm=I=-23:TP=-2:LRA=7',
            '-ar', str(self.target_sample_rate),
            '-y', output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path
        
    def reduce_noise(self, input_path: str, output_path: str) -> str:
        """Rauschreduzierung für bessere Transkription"""
        # Librosa für Rauschfilterung
        y, sr = librosa.load(input_path, sr=self.target_sample_rate)
        # Noise reduction algorithm
        y_denoised = librosa.effects.preemphasis(y)
        sf.write(output_path, y_denoised, sr)
        return output_path