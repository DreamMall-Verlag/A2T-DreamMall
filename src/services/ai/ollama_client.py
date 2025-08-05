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
        """Protokoll-Generierung via Ollama mit erweiterten Prompt-Strategien"""
        
        if not self.available:
            print("⚠️ Ollama not available - using fallback protocol generation")
            return self._generate_fallback_protocol(transcript, speakers)
        
        print(f"🤖 [OLLAMA] Using model: {model}")
        
        # Enhanced speaker information with names
        speaker_info = ""
        if speakers:
            unique_speakers = {}
            for speaker in speakers:
                speaker_id = speaker.get('speaker', speaker.get('original_id', 'Unknown'))
                speaker_name = speaker.get('name', f"Person {len(unique_speakers) + 1}")
                if speaker_id not in unique_speakers:
                    unique_speakers[speaker_id] = speaker_name
            
            speaker_info = "TEILNEHMER:\n" + "\n".join([
                f"- {name} (als {speaker_id} erkannt)" 
                for speaker_id, name in unique_speakers.items()
            ])
        else:
            speaker_info = "TEILNEHMER:\n- Ein Sprecher erkannt"
        
        # Vereinfachter und direkter Prompt für bessere Ergebnisse
        prompt = f"""Analysiere das folgende Meeting-Transkript und erstelle ein strukturiertes Protokoll.

{speaker_info}

TRANSKRIPT:
{transcript}

Erstelle GENAU dieses Format - NUR die 9 Punkte, keine zusätzlichen Informationen:

# Meeting-Protokoll

**1. Anwesende:**
[Namen der Teilnehmer]

**2. Thema des Gesprächs:**
[Hauptthema in 1-2 Sätzen]

**3. Terminabsprachen:**
[Termine und Deadlines oder "—"]

**4. Vereinbarungen:**
[Getroffene Entscheidungen oder "—"]

**5. Übereinkünfte:**
[Absprachen oder "—"]

**6. Besprochene Probleme:**
[Diskutierte Probleme oder "—"]

**7. Offene Punkte für das nächste Gespräch:**
[Vertage Themen oder "—"]

**8. Nächster Termin zum Treffen:**
[Folgetermine oder "—"]

**9. Aufgaben:**
[Wer macht was bis wann oder "—"]

WICHTIG: 
- NUR diese 9 Punkte
- Keine Zeitstempel
- Keine wörtlichen Zitate  
- Kurze Stichpunkte
- Bei leeren Punkten: "—"
- Verwende die echten Namen der Teilnehmer"""
        
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
        """Fallback-Protokoll ohne LLM - mit strukturiertem 9-Punkte-Format"""
        
        # Einfache Textanalyse für Fallback
        words = transcript.lower().split()
        
        # Keywords für verschiedene Kategorien
        decision_keywords = ["entscheidung", "beschluss", "beschließen", "entscheiden", "beschlossen"]
        action_keywords = ["aufgabe", "todo", "erledigen", "zuständig", "verantwortlich", "bis", "deadline"]
        time_keywords = ["termin", "deadline", "bis", "nächste woche", "montag", "dienstag", "mittwoch"]
        
        # Speaker-Liste erstellen
        unique_speakers = list(set([s['speaker'] for s in speakers])) if speakers else ["Sprecher 1"]
        speaker_names = []
        
        # Versuche Sprecher-Namen zu extrahieren, falls verfügbar
        for speaker in speakers:
            if 'name' in speaker and speaker['name']:
                speaker_names.append(speaker['name'])
        
        if not speaker_names:
            speaker_names = unique_speakers
        
        speaker_list = ", ".join(speaker_names)
        
        # Einfache Struktur generieren im 9-Punkte-Format
        protocol = f"""# Meeting-Protokoll

**1. Anwesende:**
{speaker_list}

**2. Thema des Gesprächs:**
Meeting-Diskussion (automatisch erkannt aus Audio-Transkription)

**3. Terminabsprachen:**
{self._extract_simple_info(transcript, time_keywords, "—")}

**4. Vereinbarungen:**
{self._extract_simple_info(transcript, decision_keywords, "—")}

**5. Übereinkünfte:**
—

**6. Besprochene Probleme:**
—

**7. Offene Punkte für das nächste Gespräch:**
—

**8. Nächster Termin zum Treffen:**
—

**9. Aufgaben:**
{self._extract_simple_info(transcript, action_keywords, "—")}

---

⚠️ **Hinweis**: Automatisch generiertes Basis-Protokoll. Für detaillierte KI-Analyse bitte Ollama-Server mit LLM-Modell verwenden.
"""
        
        return protocol
    
    def _extract_simple_info(self, transcript: str, keywords: List[str], default: str) -> str:
        """Einfache Keyword-basierte Extraktion für Fallback"""
        sentences = transcript.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in keywords):
                relevant_sentences.append(f"• {sentence}")
                if len(relevant_sentences) >= 3:  # Maximal 3 Punkte
                    break
        
        return "\n".join(relevant_sentences) if relevant_sentences else default
    
    def get_structured_protocol_prompt(self, transcript: str, speakers: List[Dict]) -> Dict:
        """Gibt einen strukturierten JSON-Prompt für das 9-Punkte-Protokoll zurück"""
        
        # Enhanced speaker information with names
        speaker_info = ""
        if speakers:
            unique_speakers = {}
            for speaker in speakers:
                speaker_id = speaker.get('speaker', speaker.get('original_id', 'Unknown'))
                speaker_name = speaker.get('name', f"Person {len(unique_speakers) + 1}")
                if speaker_id not in unique_speakers:
                    unique_speakers[speaker_id] = speaker_name
            
            speaker_info = "TEILNEHMER:\n" + "\n".join([
                f"- {name} (als {speaker_id} erkannt)" 
                for speaker_id, name in unique_speakers.items()
            ])
        else:
            speaker_info = "TEILNEHMER:\n- Ein Sprecher erkannt"
        
        # Strukturierter JSON-Prompt
        prompt_content = f"""Du bist ein professioneller Meeting-Protokollant. Fasse das folgende Transkript sehr kompakt in ein strukturiertes Ergebnisprotokoll mit maximal 9 Punkten zusammen:

{speaker_info}

TRANSKRIPTION:
{transcript}

STRUKTUR:
1. Anwesende
2. Thema des Gesprächs
3. Terminabsprachen
4. Vereinbarungen
5. Übereinkünfte
6. Besprochene Probleme
7. Offene Punkte für das nächste Gespräch
8. Nächster Termin zum Treffen
9. Aufgaben die erledigt werden müssen und von wem

REGELN:
- Keine wörtlichen Zitate
- Kein Fließtext
- Keine Wiederholung unwichtiger Aussagen
- Nur das Wesentliche extrahieren
- Verwende die echten Namen der Teilnehmer
- Wenn ein Punkt nicht relevant ist, schreibe "—" oder "nicht besprochen"
- Maximal 3-5 Stichpunkte pro Kategorie

Erstelle nur das strukturierte Protokoll, keine zusätzlichen Kommentare."""
        
        return {
            "role": "system",
            "content": prompt_content,
            "format": "9-point-structured-protocol",
            "transcript_length": len(transcript),
            "speaker_count": len(speakers) if speakers else 1,
            "expected_sections": [
                "Anwesende",
                "Thema des Gesprächs", 
                "Terminabsprachen",
                "Vereinbarungen",
                "Übereinkünfte",
                "Besprochene Probleme",
                "Offene Punkte für das nächste Gespräch",
                "Nächster Termin zum Treffen",
                "Aufgaben"
            ]
        }