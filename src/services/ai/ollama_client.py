# src/services/ai/ollama_client.py
import requests
import json
import sys
from typing import Dict, List

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available = False
        
        # Test Ollama connection
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.available = True
                print("✅ Ollama server available")
            else:
                print("⚠️ Ollama server not responding")
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
            print("💡 Meeting protocols will use fallback generation")
        
    def generate_protocol(self, transcript: str, speakers: List[Dict], 
                         model: str = "llama3") -> str:
        """Protokoll-Generierung via Ollama"""
        
        if not self.available:
            print("⚠️ Ollama not available - using fallback protocol generation")
            return self._generate_fallback_protocol(transcript, speakers)
        
        # Speaker-Timeline erstellen
        speaker_timeline = "\n".join([
            f"{s['speaker']} ({s['start']:.1f}s - {s['end']:.1f}s)"
            for s in speakers
        ])
        
        prompt = f"""
        Erstelle ein strukturiertes Meeting-Protokoll aus folgender Transkription:
        
        SPRECHER-TIMELINE:
        {speaker_timeline}
        
        TRANSKRIPTION:
        {transcript}
        
        GEWÜNSCHTES FORMAT:
        # Meeting-Protokoll
        
        ## Teilnehmer
        - [Automatisch erkannte Sprecher]
        
        ## Agenda-Punkte
        - [Hauptthemen aus der Diskussion]
        
        ## Wichtige Entscheidungen
        - [Getroffene Beschlüsse]
        
        ## Action Items
        - [ ] [Aufgabe] - [Verantwortlicher] - [Deadline]
        
        ## Zusammenfassung
        [Kurze Zusammenfassung der wichtigsten Punkte]
        """
        
        try:
            response = requests.post(f'{self.base_url}/api/generate', 
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }, timeout=30)
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"⚠️ Ollama API error: {response.text}")
                return self._generate_fallback_protocol(transcript, speakers)
        except Exception as e:
            print(f"⚠️ Ollama request failed: {e}")
            return self._generate_fallback_protocol(transcript, speakers)
    
    def _generate_fallback_protocol(self, transcript: str, speakers: List[Dict]) -> str:
        """Fallback-Protokoll ohne LLM"""
        
        # Einfache Textanalyse für Fallback
        words = transcript.lower().split()
        
        # Keywords für verschiedene Kategorien
        decision_keywords = ["entscheidung", "beschluss", "beschließen", "entscheiden", "beschlossen"]
        action_keywords = ["aufgabe", "todo", "erledigen", "zuständig", "verantwortlich", "bis", "deadline"]
        
        # Speaker-Liste erstellen
        unique_speakers = list(set([s['speaker'] for s in speakers])) if speakers else ["Sprecher 1"]
        speaker_list = "\n".join([f"- {speaker}" for speaker in unique_speakers])
        
        # Einfache Struktur generieren
        protocol = f"""# Meeting-Protokoll
*Automatisch generiert aus Audio-Transkription*

## Teilnehmer
{speaker_list}

## Transkription
{transcript[:1000]}{"..." if len(transcript) > 1000 else ""}

## Speaker-Timeline"""
        
        if speakers:
            protocol += "\n"
            for speaker in speakers[:10]:  # Erste 10 Speaker-Segmente
                protocol += f"- {speaker['speaker']}: {speaker['start']:.1f}s - {speaker['end']:.1f}s\n"
        else:
            protocol += "\n- Keine Speaker-Diarization verfügbar\n"
        
        protocol += f"""
## Hinweise
- Dieses Protokoll wurde automatisch generiert
- Für bessere Qualität: Ollama-Server mit LLM-Modell verwenden
- Transkription-Länge: {len(transcript)} Zeichen
"""
        
        return protocol