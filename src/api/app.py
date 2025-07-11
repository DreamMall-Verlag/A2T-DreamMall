# src/api/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import os
import sys
from threading import Thread
from datetime import datetime
import librosa
import soundfile as sf
import tempfile
import numpy as np
import requests

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import A2TSettings
from services.ai.whisper_client import WhisperClient
from services.ai.diarization import SpeakerDiarization
from services.ai.ollama_client import OllamaClient
from services.protocol.generator import ProtocolGenerator

def create_app():
    """Application factory function"""
    return app

app = Flask(__name__)
CORS(app)

# Job-Management für Async Processing
active_jobs = {}

class A2TJob:
    def __init__(self, job_id: str, audio_file: str, model: str = None):
        self.job_id = job_id
        self.audio_file = audio_file
        self.model = model or A2TSettings.WHISPER_MODEL  # Use setting default
        self.status = "queued"
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.now()

# Initialize AI Services for local operation
print(f"🔧 Initializing A2T Services for local operation")

# Print startup configuration info
A2TSettings.print_startup_info()

# Use "small" as default Whisper model for best balance of quality and speed
whisper_client = WhisperClient(model_size=A2TSettings.WHISPER_MODEL)
diarization_client = SpeakerDiarization()
ollama_client = OllamaClient(base_url=A2TSettings.OLLAMA_BASE_URL)
protocol_generator = ProtocolGenerator(ollama_client, whisper_client, diarization_client)

def process_audio_async(job: A2TJob):
    """Background processing function with enhanced debugging"""
    try:
        print(f"🚀 [DEBUG] Starting async processing for job {job.job_id}")
        job.status = "processing"
        job.progress = 10
        
        print(f"🎵 Processing audio file: {job.audio_file}")
        print(f"🎯 Using Whisper model: {job.model}")
        
        # File path should already be absolute
        audio_path = job.audio_file
        print(f"📍 Using path: {audio_path}")
        print(f"📂 File exists: {os.path.exists(audio_path)}")
        
        if not os.path.exists(audio_path):
            # Try different path variations
            base_name = os.path.basename(audio_path)
            alt_path = os.path.join("temp", "uploads", base_name)
            abs_alt_path = os.path.abspath(alt_path)
            
            print(f"🔍 Trying alternative path: {abs_alt_path}")
            if os.path.exists(abs_alt_path):
                audio_path = abs_alt_path
                print(f"✅ Found file at: {audio_path}")
            else:
                raise FileNotFoundError(f"Audio file not found at: {audio_path} or {abs_alt_path}")
        
        print(f"✅ File confirmed: {audio_path}")
        print(f"📏 File size: {os.path.getsize(audio_path)} bytes")
        
        # Convert audio to WAV for better Whisper compatibility
        print(f"🔄 [DEBUG] Converting audio to optimal WAV format...")
        converted_audio_path = convert_audio_to_wav(audio_path)
        print(f"✅ [DEBUG] Audio conversion completed: {converted_audio_path}")
        
        # Process audio through pipeline with selected model
        job.progress = 20
        print(f"🔄 [DEBUG] Starting protocol generation with model: {job.model}")
        
        # Add more specific error handling
        try:
            # Pass converted audio and model to protocol generator
            print(f"🎤 [DEBUG] Calling protocol_generator.process_audio_to_protocol")
            result = protocol_generator.process_audio_to_protocol(converted_audio_path, whisper_model=job.model)
            print(f"✅ [DEBUG] Protocol generation completed successfully")
            
        except Exception as processing_error:
            print(f"❌ [DEBUG] Protocol generation failed: {processing_error}")
            print(f"🔧 [DEBUG] Creating fallback result due to error: {type(processing_error).__name__}")
            
            # Create fallback result
            from services.protocol.generator import ProtocolData
            result = ProtocolData(
                audio_file=converted_audio_path,
                transcript=f"Processing failed: {str(processing_error)}",
                segments=[],
                speakers=[],
                protocol_text=f"# Processing Error\n\nAudio processing failed with error:\n{str(processing_error)}\n\nThis may be due to audio format compatibility issues.",
                metadata={
                    "language": "de",
                    "duration": 0,
                    "speaker_count": 0,
                    "segments_count": 0,
                    "diarization_available": False,
                    "error": str(processing_error),
                    "error_type": type(processing_error).__name__
                }
            )
        
        job.progress = 100
        job.status = "completed"
        job.result = result
        
        # Cleanup converted audio file if different from original
        if converted_audio_path != audio_path:
            try:
                os.remove(converted_audio_path)
                print(f"🧹 [DEBUG] Cleaned up converted audio file: {converted_audio_path}")
            except Exception as cleanup_error:
                print(f"⚠️ [DEBUG] Failed to cleanup converted file: {cleanup_error}")
        
        print(f"✅ [DEBUG] Audio processing completed for job {job.job_id}")
        print(f"📊 [DEBUG] Result metadata: {result.metadata}")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        print(f"❌ [DEBUG] Audio processing failed for job {job.job_id}: {e}")
        print(f"🔍 [DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"📋 [DEBUG] Full traceback:")
        traceback.print_exc()

def convert_audio_to_wav(audio_path: str) -> str:
    """
    Convert any audio file to WAV format for better Whisper compatibility
    Returns path to converted WAV file (or original if already optimal)
    """
    try:
        print(f"🔄 [AUDIO] Checking audio format: {audio_path}")
        
        # Check if file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path)
        print(f"📏 [AUDIO] Original file size: {file_size} bytes")
        
        # Get file extension
        _, ext = os.path.splitext(audio_path.lower())
        print(f"📁 [AUDIO] File extension: {ext}")
        
        # If already WAV and reasonable size, check if it needs processing
        if ext == '.wav':
            try:
                # Quick check if WAV is already optimal
                audio, sr = librosa.load(audio_path, sr=None, duration=1.0)  # Load just 1 second to test
                if sr == 16000 and len(audio.shape) == 1:  # Mono, 16kHz
                    print(f"✅ [AUDIO] WAV file already optimal: {sr}Hz, mono")
                    return audio_path
                else:
                    print(f"🔄 [AUDIO] WAV needs reprocessing: {sr}Hz, shape: {audio.shape}")
            except Exception as e:
                print(f"⚠️ [AUDIO] WAV check failed, will reprocess: {e}")
        
        # Load full audio with librosa (handles most formats)
        print(f"🔄 [AUDIO] Loading audio with librosa...")
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        print(f"✅ [AUDIO] Audio loaded: {len(audio)} samples at {sr}Hz")
        
        # Handle edge cases
        if len(audio) == 0:
            print("⚠️ [AUDIO] Empty audio detected, creating silence")
            audio = np.zeros(16000)  # 1 second silence
        elif len(audio) < 1600:  # Less than 0.1 seconds
            print(f"⚠️ [AUDIO] Very short audio ({len(audio)} samples), padding")
            audio = np.pad(audio, (0, 16000 - len(audio)), mode='constant')
        
        # Normalize audio to prevent clipping
        if np.max(np.abs(audio)) > 0:
            max_val = np.max(np.abs(audio))
            if max_val > 1.0:
                audio = audio / max_val * 0.95
                print(f"✅ [AUDIO] Normalized audio (max was: {max_val:.3f})")
        else:
            print("⚠️ [AUDIO] Audio appears to be silent")
        
        # Create output path for converted WAV
        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        wav_filename = f"{base_name}_converted.wav"
        wav_path = os.path.join(temp_dir, wav_filename)
        
        print(f"💾 [AUDIO] Saving converted WAV to: {wav_path}")
        
        # Save as WAV with consistent format (16-bit PCM, 16kHz, mono)
        sf.write(wav_path, audio, 16000, format='WAV', subtype='PCM_16')
        
        # Verify converted file
        if os.path.exists(wav_path):
            converted_size = os.path.getsize(wav_path)
            print(f"✅ [AUDIO] Conversion successful: {converted_size} bytes")
            print(f"📊 [AUDIO] Duration: {len(audio) / 16000:.2f} seconds")
            return wav_path
        else:
            raise Exception("Failed to save converted WAV file")
        
    except Exception as e:
        print(f"❌ [AUDIO] Conversion failed: {e}")
        print(f"🔄 [AUDIO] Using original file: {audio_path}")
        import traceback
        traceback.print_exc()
        return audio_path

@app.route('/')
def home():
    """Health check endpoint with configuration info"""
    return jsonify({
        "service": "A2T-DreamMall",
        "status": "running",
        "version": "1.0.0",
        "configuration": {
            "whisper_model": A2TSettings.WHISPER_MODEL,
            "language": A2TSettings.WHISPER_LANGUAGE,
            "huggingface_available": bool(A2TSettings.HUGGINGFACE_TOKEN),
            "ollama_url": A2TSettings.OLLAMA_BASE_URL
        },
        "endpoints": {
            "transcribe": "/api/v1/transcribe",
            "status": "/api/v1/status/<job_id>",
            "config": "/api/v1/config",
            "models": "/api/v1/models",
            "web": "/web"
        }
    })

@app.route('/health')
def health():
    """Service health check"""
    return jsonify({
        "status": "healthy",
        "components": {
            "whisper": whisper_client is not None,
            "diarization": diarization_client.available,
            "ollama": True
        },
        "active_jobs": len(active_jobs),
        "service": "A2T-DreamMall"
    })

@app.route('/api/v1/config', methods=['GET'])
def get_configuration():
    """Get current system configuration and requirements"""
    try:
        return jsonify({
            "status": A2TSettings.get_status(),
            "requirements": A2TSettings.get_requirements(),
            "service_status": {
                "whisper": whisper_client is not None,
                "diarization": diarization_client.available,
                "ollama": ollama_client.available,
                "protocol_generator": protocol_generator is not None
            }
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to get configuration: {str(e)}"
        }), 500

@app.route('/api/v1/models', methods=['GET'])
def get_available_models():
    """Get available Whisper models"""
    return jsonify({
        "current_model": whisper_client.current_model_size,
        "available_models": whisper_client.AVAILABLE_MODELS,
        "model_info": whisper_client.get_model_info()
    })

@app.route('/api/v1/ollama/models', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models for protocol generation"""
    try:
        if not ollama_client.available:
            return jsonify({
                "available": False,
                "error": "Ollama not available",
                "models": []
            })
        
        # Get models from Ollama
        response = requests.get(f"{A2TSettings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models_data = response.json()
            
            # Format models for frontend
            formatted_models = []
            for model in models_data.get('models', []):
                formatted_models.append({
                    "name": model.get('name', 'Unknown'),
                    "size": model.get('size', 0),
                    "size_formatted": f"{model.get('size', 0) / 1024 / 1024 / 1024:.1f} GB",
                    "parameter_size": model.get('details', {}).get('parameter_size', 'Unknown'),
                    "quantization": model.get('details', {}).get('quantization_level', 'Unknown'),
                    "family": model.get('details', {}).get('family', 'Unknown'),
                    "modified": model.get('modified_at', ''),
                    "recommended": model.get('name', '').startswith('llama3')  # Recommend llama3 models
                })
            
            return jsonify({
                "available": True,
                "models": formatted_models,
                "current_default": A2TSettings.OLLAMA_MODEL,
                "base_url": A2TSettings.OLLAMA_BASE_URL
            })
        else:
            return jsonify({
                "available": False,
                "error": f"Ollama API returned status {response.status_code}",
                "models": []
            })
            
    except Exception as e:
        return jsonify({
            "available": False,
            "error": f"Failed to fetch Ollama models: {str(e)}",
            "models": []
        })

@app.route('/api/v1/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio-Upload und Transkription"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get model selection from form data (default from settings)
    selected_model = request.form.get('model', A2TSettings.WHISPER_MODEL)
    
    job_id = str(uuid.uuid4())
    
    # Ensure upload directory exists with absolute path
    upload_dir = os.path.abspath("temp/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded file with absolute path
    upload_filename = f"{job_id}_{audio_file.filename}"
    upload_path = os.path.join(upload_dir, upload_filename)
    audio_file.save(upload_path)
    
    print(f"📁 File saved to: {upload_path}")
    print(f"📂 File exists: {os.path.exists(upload_path)}")
    print(f"🎯 Selected model: {selected_model}")
    
    # Ensure absolute path for job
    absolute_upload_path = os.path.abspath(upload_path)
    print(f"📍 Absolute path: {absolute_upload_path}")
    
    # Create job with absolute path and model selection
    job = A2TJob(job_id, absolute_upload_path, selected_model)
    active_jobs[job_id] = job
    
    # Start background processing
    Thread(target=process_audio_async, args=(job,)).start()
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "message": "Audio processing started",
        "selected_model": selected_model
    })

@app.route('/api/v1/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """Job-Status prüfen"""
    if job_id not in active_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = active_jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job.status,
        "progress": job.progress
    }
    
    if job.status == "completed" and job.result:
        response["result"] = {
            "transcript": job.result.transcript,
            "segments": job.result.segments,
            "speakers": job.result.speakers,
            "protocol": job.result.protocol_text,  # Changed from protocol_text to protocol
            "metadata": job.result.metadata
        }
    elif job.status == "failed" and job.error:
        response["error"] = str(job.error)
    
    return jsonify(response)

@app.route('/api/v1/generate-protocol', methods=['POST'])
def generate_protocol_endpoint():
    """Generate meeting protocol with custom speaker names and model selection"""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({"error": "Missing transcript data"}), 400
        
        transcript = data.get('transcript', '')
        speakers = data.get('speakers', [])
        metadata = data.get('metadata', {})
        selected_model = data.get('model', A2TSettings.OLLAMA_MODEL)  # Allow model selection
        
        print(f"🤖 [PROTOCOL] Generating protocol with model: {selected_model}")
        print(f"📝 [PROTOCOL] Speakers: {[s.get('name', 'Unknown') for s in speakers]}")
        print(f"📊 [PROTOCOL] Transcript length: {len(transcript)} characters")
        
        # Try to generate protocol with Ollama if available
        if ollama_client.available:
            try:
                protocol_text = ollama_client.generate_protocol(
                    transcript=transcript,
                    speakers=speakers,
                    model=selected_model  # Use selected model
                )
                print(f"✅ [PROTOCOL] Ollama protocol generated successfully with {selected_model}")
                
                return jsonify({
                    "success": True,
                    "protocol": protocol_text,
                    "method": "ollama",
                    "model_used": selected_model,
                    "speakers": speakers,
                    "metadata": metadata,
                    "generation_time": datetime.now().isoformat()
                })
                
            except Exception as ollama_error:
                print(f"⚠️ [PROTOCOL] Ollama failed: {ollama_error}")
                # Fall through to fallback
        
        # Fallback protocol generation
        print(f"🔄 [PROTOCOL] Using fallback protocol generation")
        
        from datetime import datetime
        now = datetime.now()
        speaker_names = [s.get('name', f"Sprecher {i+1}") for i, s in enumerate(speakers)]
        
        fallback_protocol = f"""# Meeting-Protokoll

## Allgemeine Informationen
- **Datum:** {now.strftime('%d.%m.%Y')}
- **Uhrzeit:** {now.strftime('%H:%M')}
- **Dauer:** {metadata.get('duration_formatted', 'Unbekannt')}
- **Teilnehmer:** {', '.join(speaker_names)}
- **Sprache:** {metadata.get('language', 'de').upper()}

## Transkription
{transcript}

## Hinweise
- Automatisch generiert aus Audio-Transkription
- Ollama-LLM nicht verfügbar - Fallback-Protokoll verwendet
- Für erweiterte Protokolle: Ollama-Server starten und Modelle laden
"""
        
        return jsonify({
            "success": True,
            "protocol": fallback_protocol,
            "method": "fallback",
            "model_used": "none",
            "speakers": speakers,
            "metadata": metadata,
            "generation_time": now.isoformat()
        })
        
    except Exception as e:
        print(f"❌ [PROTOCOL] Protocol generation failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Protocol generation failed: {str(e)}"
        }), 500

@app.route('/api/v1/protocol/prompt', methods=['POST'])
def get_protocol_prompt():
    """Gibt einen strukturierten JSON-Prompt für das 9-Punkte-Protokoll zurück"""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({"error": "Missing transcript data"}), 400
        
        transcript = data.get('transcript', '')
        speakers = data.get('speakers', [])
        
        # Strukturierten Prompt generieren
        structured_prompt = ollama_client.get_structured_protocol_prompt(transcript, speakers)
        
        return jsonify({
            "success": True,
            "prompt": structured_prompt,
            "usage_example": {
                "description": "Verwende diesen Prompt mit deinem bevorzugten LLM",
                "api_call_example": {
                    "model": "llama3:latest",
                    "messages": [structured_prompt],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            }
        })
        
    except Exception as e:
        print(f"❌ [PROMPT] Prompt generation failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Prompt generation failed: {str(e)}"
        }), 500

@app.route('/web')
@app.route('/web/')
def web_interface():
    """Serve the web interface"""
    try:
        # Running in local development mode
        web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'web')
        web_dir = os.path.abspath(web_dir)
        
        index_path = os.path.join(web_dir, 'index.html')
        
        if os.path.exists(index_path):
            return send_from_directory(web_dir, 'index.html')
        else:
            return jsonify({
                "error": "Web interface not found",
                "web_dir": web_dir,
                "index_path": index_path
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": f"Failed to serve web interface: {str(e)}"
        }), 500

@app.route('/web/<path:filename>')
def web_static(filename):
    """Serve static web assets"""
    try:
        # Running in local development mode
        web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'web')
        web_dir = os.path.abspath(web_dir)
        
        return send_from_directory(web_dir, filename)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to serve static file: {str(e)}",
            "filename": filename
        }), 404

if __name__ == '__main__':
    # Ensure temp directories exist
    os.makedirs("temp/uploads", exist_ok=True)
    os.makedirs("temp/processed", exist_ok=True)
    
    print("🚀 Starting A2T-DreamMall Service...")
    print("📝 Web Interface: http://localhost:5000/web")
    print("🔌 API Endpoint: http://localhost:5000/api/v1/transcribe")
    
    app.run(host='0.0.0.0', port=5000, debug=True)