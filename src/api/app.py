# src/api/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import os
import sys
from threading import Thread
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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
    def __init__(self, job_id: str, audio_file: str):
        self.job_id = job_id
        self.audio_file = audio_file
        self.status = "queued"
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.now()

# Initialize AI Services
whisper_client = WhisperClient()
diarization_client = SpeakerDiarization()
ollama_client = OllamaClient()
protocol_generator = ProtocolGenerator(ollama_client, whisper_client, diarization_client)

def process_audio_async(job: A2TJob):
    """Background processing function"""
    try:
        job.status = "processing"
        job.progress = 10
        
        print(f"🎵 Processing audio file: {job.audio_file}")
        
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
        
        # Process audio through pipeline with timeout protection
        job.progress = 20
        
        # Add timeout for the entire processing
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Audio processing timeout")
        
        try:
            # Set timeout for processing (10 minutes)
            if os.name != 'nt':  # Unix systems
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(600)  # 10 minutes
            
            result = protocol_generator.process_audio_to_protocol(audio_path)
            
            if os.name != 'nt':  # Unix systems
                signal.alarm(0)  # Cancel alarm
            
        except TimeoutError:
            print("⏰ Processing timeout - creating fallback result")
            # Create fallback result
            from services.protocol.generator import ProtocolData
            result = ProtocolData(
                audio_file=audio_path,
                transcript="Processing timeout - please try with a shorter audio file",
                segments=[],
                speakers=[],
                protocol_text="# Processing Timeout\n\nThe audio file took too long to process. Please try with a shorter file.",
                metadata={
                    "language": "de",
                    "duration": 0,
                    "speaker_count": 0,
                    "segments_count": 0,
                    "diarization_available": False,
                    "error": "timeout"
                }
            )
        
        job.progress = 100
        job.status = "completed"
        job.result = result
        
        print(f"✅ Audio processing completed for job {job.job_id}")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        print(f"❌ Audio processing failed for job {job.job_id}: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "service": "A2T-DreamMall",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "transcribe": "/api/v1/transcribe",
            "status": "/api/v1/status/<job_id>",
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

@app.route('/api/v1/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio-Upload und Transkription"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
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
    
    # Ensure absolute path for job
    absolute_upload_path = os.path.abspath(upload_path)
    print(f"📍 Absolute path: {absolute_upload_path}")
    
    # Create job with absolute path
    job = A2TJob(job_id, absolute_upload_path)
    active_jobs[job_id] = job
    
    # Start background processing
    Thread(target=process_audio_async, args=(job,)).start()
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "message": "Audio processing started"
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

@app.route('/web')
@app.route('/web/')
def web_interface():
    """Serve the web interface"""
    try:
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            web_dir = os.path.join(sys._MEIPASS, 'web')
        else:
            # Running in development
            web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'web')
            web_dir = os.path.abspath(web_dir)
        
        index_path = os.path.join(web_dir, 'index.html')
        
        if os.path.exists(index_path):
            return send_from_directory(web_dir, 'index.html')
        else:
            return jsonify({
                "error": "Web interface not found",
                "web_dir": web_dir,
                "index_path": index_path,
                "frozen": getattr(sys, 'frozen', False)
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": f"Failed to serve web interface: {str(e)}",
            "frozen": getattr(sys, 'frozen', False)
        }), 500

@app.route('/web/<path:filename>')
def web_static(filename):
    """Serve static web assets"""
    try:
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            web_dir = os.path.join(sys._MEIPASS, 'web')
        else:
            # Running in development
            web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'web')
            web_dir = os.path.abspath(web_dir)
        
        return send_from_directory(web_dir, filename)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to serve static file: {str(e)}",
            "filename": filename,
            "frozen": getattr(sys, 'frozen', False)
        }), 404

if __name__ == '__main__':
    # Ensure temp directories exist
    os.makedirs("temp/uploads", exist_ok=True)
    os.makedirs("temp/processed", exist_ok=True)
    
    print("🚀 Starting A2T-DreamMall Service...")
    print("📝 Web Interface: http://localhost:5000/web")
    print("🔌 API Endpoint: http://localhost:5000/api/v1/transcribe")
    
    app.run(host='0.0.0.0', port=5000, debug=True)