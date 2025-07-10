# WSL-Ollama für Windows A2T-Service konfigurieren

## ✅ UPDATE: Ollama läuft direkt in Windows!

**Status**: Ollama ist bereits in Windows installiert und läuft auf `localhost:11434`!

```bash
# Verfügbare Modelle:
ollama list
# NAME             ID              SIZE      MODIFIED
# llama3:latest    365c0bd3c000    4.7 GB    2 weeks ago
```

**Test erfolgreich**:
```bash
curl http://localhost:11434/api/tags
# ✅ Funktioniert! JSON-Response mit verfügbaren Modellen
```

**Konfiguration**: 
- ✅ `.env` bereits korrekt: `OLLAMA_BASE_URL=http://localhost:11434`
- ✅ A2T-Service kann direkt auf Ollama zugreifen
- ✅ Keine WSL-Konfiguration erforderlich!

---

## WSL-Konfiguration (nicht mehr nötig)

Die folgenden Schritte sind nur relevant, wenn Sie Ollama ausschließlich in WSL betreiben möchten:

### Schritt 1: Ollama in WSL für externe Verbindungen konfigurieren

```bash
# In WSL-Terminal:
export OLLAMA_HOST=0.0.0.0:11434
```

### Schritt 2: Ollama neu starten
```bash
# Ollama stoppen (falls läuft)
pkill ollama

# Ollama mit neuer Konfiguration starten
ollama serve
```

### Schritt 3: WSL-IP ermitteln
```bash
# In WSL:
ip route show | grep default
# Oder:
hostname -I
```

### Schritt 4: Windows A2T-Service konfigurieren
In `A2T-Service\.env` die WSL-IP eintragen:
```bash
OLLAMA_BASE_URL=http://172.19.231.68:11434
```

### Schritt 5: Testen
```bash
# Von Windows aus testen:
curl http://172.19.231.68:11434/api/tags
```

## Alternative: Ollama direkt in Windows installieren

Wenn WSL-Konfiguration zu komplex ist:
1. Ollama für Windows herunterladen: https://ollama.ai/download/windows
2. Installieren und `ollama pull llama3` ausführen
3. In `.env` belassen: `OLLAMA_BASE_URL=http://localhost:11434`

## Aktueller Status
- ✅ Ollama läuft in WSL mit `llama3` und `mistral-nemo`
- ❌ Nicht für Windows-Python-App erreichbar
- ✅ Fallback-Protokolle funktionieren ohne Ollama

## Test-Kommandos

### WSL-Seite testen:
```bash
# In WSL:
curl http://localhost:11434/api/tags
```

### Windows-Seite testen:
```bash
# In Windows PowerShell:
curl http://172.19.231.68:11434/api/tags
```

Sollte JSON mit verfügbaren Modellen zurückgeben.
