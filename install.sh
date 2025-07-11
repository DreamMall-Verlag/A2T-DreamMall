#!/bin/bash
# A2T-DreamMall Installation Script for Linux/Mac

echo "🚀 A2T-DreamMall Installation Script"
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '3\.\d+')
if [[ "$python_version" != "3.10" ]]; then
    echo "⚠️ Python 3.10.x ist erforderlich. Gefunden: $python_version"
    echo "Bitte installieren Sie Python 3.10.x von https://www.python.org"
    exit 1
fi

echo "✅ Python $python_version gefunden"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Erstelle Virtual Environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Aktiviere Virtual Environment..."
source venv/bin/activate

# Install PyTorch first
echo "🔥 Installiere PyTorch (CPU Version)..."
pip install -r requirements-pytorch.txt

# Install other dependencies
echo "📚 Installiere weitere Dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️ Erstelle .env Konfiguration..."
    cp .env.example .env
    echo "✏️ Bitte bearbeiten Sie .env für Ihre Konfiguration"
fi

# Create necessary directories
echo "📁 Erstelle notwendige Verzeichnisse..."
mkdir -p temp/uploads
mkdir -p temp/processed
mkdir -p logs

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "🚀 Zum Starten:"
echo "   source venv/bin/activate"
echo "   python src/api/app.py"
echo ""
echo "🌐 Web-Interface: http://localhost:5000/web"
echo ""
echo "📝 Nächste Schritte:"
echo "   1. .env Datei bearbeiten (optional HuggingFace Token)"
echo "   2. FFmpeg installieren für Audio-Verarbeitung"
echo "   3. Ollama installieren für Protokoll-Generierung (optional)"
