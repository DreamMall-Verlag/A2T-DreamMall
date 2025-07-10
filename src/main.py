"""
Main entry point for A2T-DreamMall Standalone Application
This file is used as the entry point for PyInstaller
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = Path(sys.executable).parent
    src_path = base_path / 'src'
else:
    # Running as script
    base_path = Path(__file__).parent
    src_path = base_path / 'src'

sys.path.insert(0, str(src_path))

# Setup logging for standalone mode
def setup_logging():
    """Configure logging for standalone application"""
    log_dir = base_path / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'a2t-dreammall.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('A2T-DreamMall')
    logger.info(f"Starting A2T-DreamMall from: {base_path}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Frozen mode: {getattr(sys, 'frozen', False)}")
    
    return logger

def setup_environment():
    """Setup environment variables for standalone mode"""
    
    # Set base paths
    os.environ['A2T_BASE_PATH'] = str(base_path)
    os.environ['A2T_SRC_PATH'] = str(src_path)
    
    # Set model paths if bundled
    models_path = base_path / 'models'
    if models_path.exists():
        os.environ['A2T_MODELS_PATH'] = str(models_path)
        os.environ['WHISPER_CACHE_DIR'] = str(models_path / 'whisper')
        os.environ['PYANNOTE_CACHE_DIR'] = str(models_path / 'pyannote')
    
    # Set web assets path
    web_path = base_path / 'web'
    if web_path.exists():
        os.environ['A2T_WEB_PATH'] = str(web_path)
    
    # Set upload directory
    uploads_path = base_path / 'uploads'
    uploads_path.mkdir(exist_ok=True)
    os.environ['A2T_UPLOADS_PATH'] = str(uploads_path)
    
    # Set configuration path
    config_path = base_path / 'config'
    if config_path.exists():
        os.environ['A2T_CONFIG_PATH'] = str(config_path)
    
    # FFmpeg path for bundled executable
    if sys.platform.startswith('win'):
        ffmpeg_path = base_path / 'bin' / 'ffmpeg.exe'
    else:
        ffmpeg_path = base_path / 'bin' / 'ffmpeg'
    
    if ffmpeg_path.exists():
        os.environ['FFMPEG_BINARY'] = str(ffmpeg_path)

def check_dependencies():
    """Check if all required dependencies are available"""
    logger = logging.getLogger('A2T-DreamMall.Dependencies')
    
    required_modules = [
        'flask',
        'whisper', 
        'torch',
        'librosa',
        'soundfile',
        'requests'
    ]
    
    # Optional modules - only check in development mode
    optional_modules = []
    
    # Skip PyAnnote check in standalone mode (frozen executable)
    if not getattr(sys, 'frozen', False):
        optional_modules = [
            'pyannote.audio'  # Speaker diarization - optional feature
        ]
    else:
        logger.info("[STANDALONE] Skipping PyAnnote check - using fallback speaker detection")
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"[OK] {module} imported successfully")
        except ImportError as e:
            logger.error(f"[ERROR] Failed to import {module}: {e}")
            missing_modules.append(module)
    
    # Check optional modules
    missing_optional = []
    for module in optional_modules:
        try:
            __import__(module)
            logger.info(f"[OK] {module} imported successfully (optional)")
        except ImportError as e:
            logger.warning(f"[WARN] Optional module {module} not available: {e}")
            missing_optional.append(module)
    
    if missing_optional:
        logger.warning(f"Optional features unavailable: {missing_optional}")
        logger.info("Application will run with reduced functionality")
    
    if missing_modules:
        logger.error(f"Missing required modules: {missing_modules}")
        return False
    
    return True

def main():
    """Main entry point for A2T-DreamMall"""
    
    # Setup logging
    logger = setup_logging()
    logger.info("[STARTUP] Starting A2T-DreamMall Standalone Application")
    
    try:
        # Setup environment
        setup_environment()
        logger.info("[OK] Environment setup complete")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("[ERROR] Dependency check failed")
            input("Press Enter to exit...")
            return 1
        
        logger.info("[OK] All dependencies available")
        
        # Import and run the Flask application
        from api.app import create_app
        
        app = create_app()
        
        # Get configuration
        host = os.environ.get('A2T_HOST', '127.0.0.1')
        port = int(os.environ.get('A2T_PORT', 5000))
        debug = os.environ.get('A2T_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"[WEB] Starting web server on http://{host}:{port}")
        logger.info("[UI] Check the web interface for audio processing")
        
        # Open browser automatically if not in debug mode
        if not debug:
            import webbrowser
            import threading
            
            def open_browser():
                import time
                time.sleep(1.5)  # Wait for server to start
                webbrowser.open(f'http://{host}:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Start Flask development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader in standalone mode
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("[STOP] Application stopped by user")
        return 0
        
    except Exception as e:
        logger.error(f"[FATAL] Fatal error: {e}", exc_info=True)
        input("Press Enter to exit...")
        return 1

if __name__ == '__main__':
    sys.exit(main())
