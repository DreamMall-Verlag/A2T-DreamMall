# A2T-DreamMall Installation Script for Windows
# PowerShell Script

Write-Host "🚀 A2T-DreamMall Installation Script" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check Python version
try {
    $pythonVersion = python --version 2>&1 | Out-String
    if ($pythonVersion -notmatch "3\.10") {
        Write-Host "⚠️ Python 3.10.x ist erforderlich. Gefunden: $pythonVersion" -ForegroundColor Yellow
        Write-Host "Bitte installieren Sie Python 3.10.x von https://www.python.org" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Python 3.10.x gefunden" -ForegroundColor Green
} catch {
    Write-Host "❌ Python nicht gefunden. Bitte installieren Sie Python 3.10.x" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "📦 Erstelle Virtual Environment..." -ForegroundColor Blue
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔌 Aktiviere Virtual Environment..." -ForegroundColor Blue
& .\venv\Scripts\Activate.ps1

# Install PyTorch first
Write-Host "🔥 Installiere PyTorch (CPU Version)..." -ForegroundColor Blue
pip install -r requirements-pytorch.txt

# Install other dependencies
Write-Host "📚 Installiere weitere Dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Create .env if not exists
if (!(Test-Path ".env")) {
    Write-Host "⚙️ Erstelle .env Konfiguration..." -ForegroundColor Blue
    Copy-Item .env.example .env
    Write-Host "✏️ Bitte bearbeiten Sie .env für Ihre Konfiguration" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "📁 Erstelle notwendige Verzeichnisse..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "temp\uploads"
New-Item -ItemType Directory -Force -Path "temp\processed"
New-Item -ItemType Directory -Force -Path "logs"

Write-Host ""
Write-Host "✅ Installation abgeschlossen!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Zum Starten:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python src\api\app.py" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Web-Interface: http://localhost:5000/web" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Nächste Schritte:" -ForegroundColor Cyan
Write-Host "   1. .env Datei bearbeiten (optional HuggingFace Token)" -ForegroundColor White
Write-Host "   2. FFmpeg installieren für Audio-Verarbeitung" -ForegroundColor White
Write-Host "   3. Ollama installieren für Protokoll-Generierung (optional)" -ForegroundColor White
