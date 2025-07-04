# src/api/routes/transcription.py
from flask import Blueprint, request, jsonify
import uuid
import os

transcription_bp = Blueprint('transcription', __name__)

@transcription_bp.route('/api/v1/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio-Upload und Transkription"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_path = f"temp/{job_id}_{audio_file.filename}"
    os.makedirs("temp", exist_ok=True)
    audio_file.save(upload_path)
    
    # Start async processing
    job = A2TJob(job_id, upload_path)
    active_jobs[job_id] = job
    
    # Process in background thread
    Thread(target=process_audio_async, args=(job,)).start()
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "message": "Audio processing started"
    })

@transcription_bp.route('/api/v1/status/<job_id>', methods=['GET'])
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
            "speakers": job.result.speakers,
            "protocol": job.result.protocol_text,
            "metadata": job.result.metadata
        }
    elif job.status == "failed" and job.error:
        response["error"] = str(job.error)
    
    return jsonify(response)