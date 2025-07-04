#!/usr/bin/env python3
"""
Test script for new UI and API functionality
"""
import requests
import time
import json

def test_api():
    # Use existing audio file
    audio_file = r"d:\Entwicklung\Projekte\DREAMMALL\luna-1\A2T-Service\temp\uploads\1c85fba0-88c2-4aee-a635-883235e33c33_Business German Besprechung by LinguaTV.mp3"
    
    print("🧪 Testing new A2T API with Web-UI data structure...")
    
    # Test upload
    with open(audio_file, 'rb') as f:
        files = {'audio': f}
        response = requests.post('http://localhost:5000/api/v1/transcribe', files=files)
        
    if response.status_code == 200:
        result = response.json()
        job_id = result['job_id']
        print(f"✅ Upload successful! Job ID: {job_id}")
        
        # Poll status
        while True:
            status_response = requests.get(f'http://localhost:5000/api/v1/status/{job_id}')
            status = status_response.json()
            
            print(f"📊 Status: {status['status']} ({status['progress']}%)")
            
            if status['status'] == 'completed':
                result_data = status['result']
                
                print("\n🎯 Results:")
                print(f"📝 Transcript length: {len(result_data['transcript'])} chars")
                print(f"🎤 Segments: {len(result_data.get('segments', []))}")
                print(f"👥 Speakers: {len(result_data.get('speakers', []))}")
                print(f"📊 Metadata: {result_data.get('metadata', {})}")
                
                # Test new data structure
                if 'segments' in result_data:
                    print(f"\n🔍 First few segments:")
                    for i, segment in enumerate(result_data['segments'][:3]):
                        print(f"  Segment {i+1}: {segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s")
                        print(f"    Text: {segment.get('text', '')[:100]}...")
                
                if result_data.get('speakers'):
                    print(f"\n👥 Speaker info:")
                    for speaker in result_data['speakers'][:3]:
                        print(f"  {speaker.get('speaker', 'Unknown')}: {speaker.get('start', 0):.1f}s - {speaker.get('end', 0):.1f}s")
                
                print(f"\n🤖 Protocol preview:")
                print(result_data.get('protocol', 'No protocol')[:200] + "...")
                
                break
                
            elif status['status'] == 'failed':
                print(f"❌ Failed: {status.get('error', 'Unknown error')}")
                break
                
            time.sleep(2)
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
