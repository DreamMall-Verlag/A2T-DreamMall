# A2T-DreamMall Audio-zu-Text Meeting Protocol Generator

## 🎯 Überblick

Der A2T-DreamMall Service ist eine vollständig funktionsfähige Audio-zu-Text Pipeline, die Audiodateien von Meetings automatisch in strukturierte Protokolle umwandelt. Das System kombiniert modernste KI-Technologien für Transkription, Speaker Diarization und intelligente Protokoll-Generierung.

## ✅ Vollständig implementierte Features

### 🎵 Audio-Processing
- **Whisper AI** für hochqualitative deutsche Sprachtranskription
- **FFmpeg + Librosa** Integration für Audio-Format-Unterstützung
- **Robuste Fehlerbehandlung** mit Fallback-Mechanismen
- **Zeitstempel-Segmente** für präzise Transkript-Navigation

### 🗣️ Speaker Diarization (Optional)
- **PyAnnote.Audio** für automatische Sprecher-Erkennung
- **HuggingFace Integration** mit Token-basierter Authentifizierung
- **Graceful Fallback** wenn Speaker Diarization nicht verfügbar
- **Speaker-Farbcodierung** im Web-Interface

### 🤖 Intelligente Protokoll-Generierung
- **Ollama LLM Integration** für strukturierte Meeting-Protokolle
- **Deutsche Sprachoptimierung** für Business-Kontext
- **Automatische Extraktion** von Agenda-Punkten, Entscheidungen, Action Items
- **On-Demand-Generierung** per Klick (nicht automatisch)

### 🌐 Moderne Web-Interface & API
- **🎨 Völlig neue Web-UI** mit modernem Design und UX
- **📊 Dashboard-Übersicht** mit Dauer, Speaker-Anzahl, Sprache
- **📝 Transkript-Anzeige** mit Zeitstempeln und Speaker-Farbcodierung
- **🎛️ Interactive Features** (Zeitstempel ein/ausblenden, Speaker-Legend)
- **🤖 KI-Protokoll-Button** für On-Demand-Protokoll-Generierung
- **📄 Download-Funktion** für Protokolle als Text-Datei
- **📡 REST API** für programmatische Integration
- **⏱️ Echtzeit-Status-Updates** mit Progress Bar und Loading-Animations
- **⚡ Asynchrone Job-Verarbeitung** mit Background-Tasks

## 🛠️ Technologie-Stack

```
├── Backend: Flask + Python 3.10/3.11
├── AI/ML: Whisper, PyAnnote, Ollama, Librosa
├── Audio: FFmpeg, Librosa, PyDub
├── Frontend: HTML5, JavaScript, Tailwind CSS, Chart.js
└── Integration: DreamMall Backend/Frontend Ready
```

## 📋 Erfolgreiche Tests

✅ **Audio-Upload**: Multi-Format-Unterstützung (MP3, WAV, M4A, MP4, WebM)  
✅ **Deutsche Transkription**: Business-Meeting perfekt transkribiert  
✅ **Zeitstempel-Segmente**: Präzise Navigation durch Gespräch  
✅ **Speaker-Erkennung**: Automatische Sprecher-Identifikation  
✅ **Protokoll-Generierung**: Strukturierte Ausgabe mit Action Items  
✅ **Moderne Web-Interface**: Benutzerfreundliche, responsive Bedienung  
✅ **API-Endpunkte**: Vollständig funktional mit erweiterten Datenstrukturen  
✅ **Fehlerbehandlung**: Robuste Error-Recovery mit Fallback-Mechanismen  

## 🚀 Quick Start

### 1. Installation
```bash
cd A2T-Service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Konfiguration
```bash
# .env Datei erstellen (bereits vorhanden)
cp .env.example .env

# Optional: HuggingFace Token für Speaker Diarization
HUGGINGFACE_TOKEN=your_token_here
```

### 3. Starten
```bash
python src/api/app.py
```

### 4. Verwenden
- **🌐 Web-Interface**: http://localhost:5000/web
- **🔍 API Health Check**: http://localhost:5000/health
- **📤 Upload API**: POST http://localhost:5000/api/v1/transcribe

## 🎨 Neue Web-UI Features

### 📊 Dashboard-Übersicht
- **Dauer**: Automatische Erkennung der Audio-Länge
- **Speaker**: Anzahl identifizierter Sprecher
- **Sprache**: Erkannte Sprache (DE/EN/etc.)

### 📝 Transkript-Anzeige
- **Zeitstempel**: Ein-/ausblendbar per Klick
- **Speaker-Farbcodierung**: Bis zu 6 verschiedene Farben pro Sprecher
- **Speaker-Legend**: Übersicht aller identifizierten Sprecher
- **Scrollbare Segmente**: Übersichtliche Darstellung langer Gespräche

### 🤖 KI-Protokoll-Generierung
- **On-Demand**: Protokoll wird erst nach Klick generiert
- **Loading-Animation**: Visuelles Feedback während Generierung
- **Download-Funktion**: Protokoll als .txt-Datei herunterladen
- **Strukturierte Ausgabe**: Agenda, Entscheidungen, Action Items

## 📊 Beispiel-Ergebnis

Das System generiert strukturierte Meeting-Protokolle wie:

```markdown
# Meeting-Protokoll

## Teilnehmer
- Vera Becker (neue Assistentin)
- Mia Storm (Designerin)

## Agenda-Punkte
- Verteilung der wichtigsten Aufgaben für neue Kollektion
- Vertrieb, Besuch von Simon Götz

## Wichtige Entscheidungen
- Entscheidung für Baumwollstoffe bei der neuen Kollektion
- Bestellung von Stoffmustern bis Ende nächster Woche

## Action Items
- [ ] Stoffmuster bestellen - Eva Schilling - Ende nächster Woche
- [ ] Kontakt mit neuem Lieferanten - Frau Becker
```

## 🔗 Integration

### DreamMall Backend Integration
```javascript
// API-Aufruf für Meeting-Protokoll
const response = await fetch('/api/v1/transcribe', {
  method: 'POST',
  body: formData
});
```

### Status-Monitoring
```javascript
// Job-Status abfragen
const status = await fetch(`/api/v1/status/${jobId}`);
```

## 📝 Entwicklungsstand

**Status**: ✅ **VOLLSTÄNDIG FUNKTIONSFÄHIG**  
**Qualität**: Produktionstauglich  
**Testing**: End-to-End Tests erfolgreich  
**Integration**: DreamMall-Ready  

---

Entwickelt für das DreamMall-Ecosystem | Audio-zu-Text Meeting Protocol Generator
