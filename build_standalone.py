#!/usr/bin/env python3
"""
A2T-DreamMall Standalone Build Script
Creates platform-specific standalone executables with all dependencies
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

class A2TBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.platform = platform.system().lower()
        self.dist_dir = self.base_dir / "dist"
        self.build_dir = self.base_dir / "build"
        
    def check_requirements(self):
        """Check if all build requirements are available"""
        print("🔍 Checking build requirements...")
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller not found!")
            print("💡 Install with: pip install pyinstaller")
            return False
        
        # Check core dependencies
        required = ['flask', 'whisper', 'torch', 'librosa', 'soundfile']
        for req in required:
            try:
                __import__(req)
                print(f"✅ {req}: available")
            except ImportError:
                print(f"❌ {req}: missing")
                return False
        
        return True
    
    def download_models(self):
        """Download Whisper models for offline use"""
        print("📥 Downloading Whisper models...")
        
        try:
            import whisper
            models = ['tiny', 'base', 'small']  # Essential models
            
            for model in models:
                print(f"📥 Downloading Whisper model: {model}")
                whisper.load_model(model)
                print(f"✅ {model} model downloaded")
                
        except Exception as e:
            print(f"⚠️ Model download failed: {e}")
            print("💡 Models will be downloaded on first use")
    
    def prepare_ffmpeg(self):
        """Check FFmpeg availability"""
        print("🔍 Checking FFmpeg...")
        
        ffmpeg_cmd = 'ffmpeg.exe' if self.platform == 'windows' else 'ffmpeg'
        
        if shutil.which(ffmpeg_cmd):
            print(f"✅ FFmpeg found in PATH")
            return True
        
        # Check local bin directory
        bin_dir = self.base_dir / 'bin'
        local_ffmpeg = bin_dir / ffmpeg_cmd
        
        if local_ffmpeg.exists():
            print(f"✅ FFmpeg found locally: {local_ffmpeg}")
            return True
        
        print(f"⚠️ FFmpeg not found!")
        print(f"💡 Please install FFmpeg or place {ffmpeg_cmd} in /bin/ folder")
        print("💡 Download from: https://ffmpeg.org/download.html")
        
        # Create bin directory for user
        bin_dir.mkdir(exist_ok=True)
        print(f"📁 Created bin directory: {bin_dir}")
        
        return False
    
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous builds...")
        
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print(f"🧹 Removed: {self.dist_dir}")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"🧹 Removed: {self.build_dir}")
    
    def build_executable(self):
        """Build the standalone executable"""
        print("🔨 Building standalone executable...")
        
        spec_file = self.base_dir / "A2T-DreamMall-Standalone.spec"
        
        if not spec_file.exists():
            print(f"❌ Spec file not found: {spec_file}")
            return False
        
        # Run PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]
        
        print(f"🔨 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.base_dir, check=True)
            print("✅ Build completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed with error code: {e.returncode}")
            return False
    
    def test_executable(self):
        """Test the built executable"""
        print("🧪 Testing executable...")
        
        if self.platform == 'windows':
            exe_path = self.dist_dir / "A2T-DreamMall.exe"
        else:
            exe_path = self.dist_dir / "A2T-DreamMall"
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        print(f"✅ Executable found: {exe_path}")
        print(f"📏 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        return True
    
    def create_distribution(self):
        """Create distribution package"""
        print("📦 Creating distribution package...")
        
        # Create distribution folder structure
        dist_name = f"A2T-DreamMall-{self.platform}"
        dist_package = self.base_dir / "releases" / dist_name
        dist_package.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        if self.platform == 'windows':
            exe_file = "A2T-DreamMall.exe"
        else:
            exe_file = "A2T-DreamMall"
        
        src_exe = self.dist_dir / exe_file
        dst_exe = dist_package / exe_file
        
        if src_exe.exists():
            shutil.copy2(src_exe, dst_exe)
            print(f"✅ Copied executable to: {dst_exe}")
        
        # Copy documentation
        docs = ['README.md', 'CRITICAL_FIXES.md']
        for doc in docs:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                shutil.copy2(doc_path, dist_package / doc)
                print(f"✅ Copied: {doc}")
        
        # Create README for distribution
        dist_readme = dist_package / "STANDALONE_README.md"
        with open(dist_readme, 'w', encoding='utf-8') as f:
            f.write(f"""# A2T-DreamMall Standalone

## 🚀 Quick Start

1. **Run the executable**: `{exe_file}`
2. **Open browser**: http://127.0.0.1:5000/web
3. **Upload audio**: Drag & drop your meeting audio file
4. **Get transcript**: Audio will be processed automatically

## ✅ Features

- ✅ **Offline Audio Transcription** (Whisper AI)
- ✅ **Speaker Recognition** (when available)
- ✅ **Web Interface** (user-friendly)
- ✅ **Multiple Audio Formats** (MP3, WAV, M4A, etc.)
- ✅ **No Internet Required** (100% offline)

## ⚙️ System Requirements

- **Windows 10/11** (64-bit) or **Linux** or **macOS**
- **4GB RAM** minimum (8GB recommended)
- **2GB disk space** for models and processing

## 🔧 Troubleshooting

### Audio Processing Fails
- Ensure audio file is valid and not corrupted
- Try converting to WAV format first
- Check file size (max 100MB recommended)

### Web Interface Not Loading
- Check if port 5000 is available
- Try http://localhost:5000/web instead
- Restart the application

### Performance Issues
- Use smaller Whisper models (tiny/base)
- Close other applications to free RAM
- Process shorter audio files (<30 minutes)

## 📞 Support

For technical issues, check the logs in the console window.

---

**Version**: Standalone {platform.system()} Build  
**Built**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
""")
        
        print(f"✅ Distribution package created: {dist_package}")
        return dist_package
    
    def build_all(self):
        """Complete build process"""
        print("="*60)
        print("🚀 A2T-DreamMall Standalone Builder")
        print("="*60)
        print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("")
        
        # Step 1: Check requirements
        if not self.check_requirements():
            print("❌ Build requirements not met!")
            return False
        
        # Step 2: Download models
        self.download_models()
        
        # Step 3: Check FFmpeg
        ffmpeg_ok = self.prepare_ffmpeg()
        if not ffmpeg_ok:
            print("⚠️ FFmpeg missing - audio processing may be limited")
        
        # Step 4: Clean previous builds
        self.clean_build()
        
        # Step 5: Build executable
        if not self.build_executable():
            print("❌ Build failed!")
            return False
        
        # Step 6: Test executable
        if not self.test_executable():
            print("❌ Executable test failed!")
            return False
        
        # Step 7: Create distribution
        dist_package = self.create_distribution()
        
        print("")
        print("="*60)
        print("✅ BUILD SUCCESSFUL!")
        print("="*60)
        print(f"📦 Distribution: {dist_package}")
        print("")
        print("🎯 Next Steps:")
        print(f"1. Test the executable: {dist_package}")
        print("2. Share the distribution folder with users")
        print("3. Users just run the executable - no installation needed!")
        print("")
        
        return True

if __name__ == "__main__":
    builder = A2TBuilder()
    success = builder.build_all()
    
    if not success:
        sys.exit(1)
    
    print("🎉 Ready for distribution!")
