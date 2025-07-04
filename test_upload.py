#!/usr/bin/env python3
"""Test-Skript für Audio-Upload und Verarbeitung"""

import requests
import json
import time
import os

# Test-Audiodatei
audio_file_path = "temp/uploads/1c85fba0-88c2-4aee-a635-883235e33c33_Business German Besprechung by LinguaTV.mp3"

def test_upload_and_process():
    """Teste Audio-Upload und Verarbeitung"""
    
    print("🎵 Testing A2T-DreamMall Audio Processing...")
    
    # 1. Health Check
    print("\n1. Health Check...")
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"✅ Health Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return
    
    # 2. Upload Audio File
    print("\n2. Uploading Audio File...")
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return
        
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'audio': ('test_audio.mp3', f, 'audio/mpeg')}
            response = requests.post('http://localhost:5000/api/v1/transcribe', files=files)
            
        print(f"✅ Upload Status: {response.status_code}")
        upload_result = response.json()
        print(json.dumps(upload_result, indent=2))
        
        if 'job_id' not in upload_result:
            print("❌ No job_id in response")
            return
            
        job_id = upload_result['job_id']
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # 3. Monitor Processing
    print(f"\n3. Monitoring Job {job_id}...")
    
    for i in range(30):  # Max 30 checks (5 minutes)
        try:
            response = requests.get(f'http://localhost:5000/api/v1/status/{job_id}')
            status_result = response.json()
            
            print(f"📊 Status ({i+1}/30): {status_result.get('status', 'unknown')} - Progress: {status_result.get('progress', 0)}%")
            
            if status_result.get('status') == 'completed':
                print("✅ Processing completed!")
                print(json.dumps(status_result, indent=2))
                break
            elif status_result.get('status') == 'failed':
                print("❌ Processing failed!")
                print(f"Error: {status_result.get('error', 'Unknown error')}")
                break
                
            time.sleep(10)  # Wait 10 seconds
            
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            break
    else:
        print("⏰ Timeout - Processing took too long")

if __name__ == "__main__":
    test_upload_and_process()
