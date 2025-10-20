# build_with_installer.py
"""
Build Shadow AI GUI with graphical installer
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    current_dir = Path(__file__).parent
    
    # Check required files
    required_files = [
        'run_shadow_gui.py',
        'shadow_core/gui.py',
        'shadow_core/brain.py',
        'config.example.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for missing in missing_files:
            print(f"   - {missing}")
        return False
    
    # Check if we're on Windows
    if platform.system() != 'Windows':
        print("⚠️  Warning: This installer is optimized for Windows")
    
    print("✅ All prerequisites met")
    return True

def build_gui_application():
    """Build the main GUI application"""
    print("📦 Building Shadow AI GUI application...")
    
    current_dir = Path(__file__).parent
    
    try:
        # PyInstaller command for GUI application
        pyinstaller_cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--onefile',
            '--windowed',
            '--name=ShadowAI',
            '--add-data=shadow_core;shadow_core',
            '--add-data=config.example.py;.',
            '--hidden-import=customtkinter',
            '--hidden-import=openai',
            '--hidden-import=pygame',
            '--hidden-import=psutil',
            '--hidden-import=requests',
            '--hidden-import=asyncio',
            '--hidden-import=threading',
            '--hidden-import=concurrent.futures',
            'run_shadow_gui.py'
        ]
        
        # Add icon if available
        icon_path = current_dir / 'assets' / 'icon.ico'
        if icon_path.exists():
            pyinstaller_cmd.extend(['--icon', str(icon_path)])
        
        print(f"🔧 Running: {' '.join(pyinstaller_cmd)}")
        result = subprocess.run(
            pyinstaller_cmd,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ GUI application built successfully")
            return True
        else:
            print(f"❌ Application build failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_installer_package():
    """Create installer package with all necessary files"""
    print("📁 Creating installer package...")
    
    current_dir = Path(__file__).parent
    dist_dir = current_dir / "dist"
    package_dir = current_dir / "ShadowAI_Installer_Package"
    
    try:
        # Clean previous package
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        
        # Copy the main executable
        main_exe = dist_dir / "ShadowAI.exe"
        if not main_exe.exists():
            print("❌ Main executable not found")
            return False
        
        shutil.copy2(main_exe, package_dir / "ShadowAI.exe")
        
        # Copy configuration files - FIXED: Use config.example.py as template
        config_files = [
            ('config.example.py', 'config.example.py'),  # Keep as example
            ('README.md', 'README.md'),
            ('LICENSE', 'LICENSE'),
            ('requirements.txt', 'requirements.txt')
        ]
        
        for src_name, dest_name in config_files:
            src_path = current_dir / src_name
            if src_path.exists():
                shutil.copy2(src_path, package_dir / dest_name)
        
        # Create a proper config.py with instructions
        config_content = '''# Shadow AI Configuration
# Get your OpenAI API key from: https://platform.openai.com/api-keys

OPENAI_API_KEY = "your-openai-api-key-here"

# Optional: Weather API (get from https://openweathermap.org/api)
OPENWEATHER_API_KEY = "your-weather-api-key-here"

# Optional: Default settings
DEFAULT_CITY = "London"
DEFAULT_COUNTRY = "GB"

# Note: Replace the placeholder text with your actual API keys
# The application will not work without a valid OpenAI API key
'''
        
        with open(package_dir / "config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        # Create comprehensive README
        readme_content = f"""# Shadow AI - GUI Application

## 🚀 Quick Installation Guide

### Portable Version (Recommended)
1. Extract all files to a folder
2. Edit `config.py` with your OpenAI API key
3. Run `ShadowAI.exe` to start the application

### Configuration Steps
1. Get your OpenAI API key from: https://platform.openai.com/api-keys
2. Open `config.py` in a text editor
3. Replace `"your-openai-api-key-here"` with your actual API key
4. Save the file and run `ShadowAI.exe`

## 🎯 Features

- 🎤 Voice recognition with OpenAI Whisper
- 🤖 GPT-4 powered conversations
- 🔊 Text-to-speech responses
- 🌤️ Live weather updates (optional)
- 🎨 Modern dark theme GUI
- 🌍 Multilingual support (English, Urdu, Pashto)

## 🔧 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Audio**: Microphone and speakers
- **Internet**: Required for AI services

## 🆘 Troubleshooting

### Application won't start:
- Ensure `config.py` has a valid OpenAI API key
- Check internet connection
- Run as Administrator if needed

### Voice not working:
- Check microphone permissions in Windows Settings
- Ensure microphone is not muted
- Test microphone with other applications

### No audio output:
- Check speaker volume
- Verify default audio output device

## 📄 License

MIT License - See LICENSE file for details.

---
**Build Date**: {subprocess.getoutput('date /t')}
**Python Version**: {platform.python_version()}
"""
        
        with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # Create batch configuration helper
        batch_content = """@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    Shadow AI - Configuration Helper
echo ========================================
echo.
echo This helper will guide you through configuration.
echo.
echo IMPORTANT: You need an OpenAI API key to use Shadow AI.
echo Get your key from: https://platform.openai.com/api-keys
echo.
echo Press any key to open the configuration file...
pause >nul
notepad config.py
echo.
echo Please replace "your-openai-api-key-here" with your actual API key.
echo Save the file and then press any key to launch Shadow AI...
pause >nul
echo.
echo Launching Shadow AI...
ShadowAI.exe
"""
        
        with open(package_dir / "Configure_And_Run.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        
        # Create ZIP package
        print("🗜️ Creating ZIP package...")
        shutil.make_archive(
            str(current_dir / "ShadowAI-GUI-Windows"),
            'zip',
            package_dir
        )
        
        print("✅ Installer package created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Package creation failed: {e}")
        return False

def cleanup_build_artifacts():
    """Clean up temporary build files"""
    print("🧹 Cleaning up build artifacts...")
    
    current_dir = Path(__file__).parent
    
    # Remove build directory but keep dist
    build_dir = current_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Clean .spec files
    for spec_file in current_dir.glob("*.spec"):
        spec_file.unlink()
    
    # Clean __pycache__ directories
    for pycache_dir in current_dir.rglob("__pycache__"):
        shutil.rmtree(pycache_dir)
    
    print("✅ Cleanup completed")

def main():
    """Main build function for Shadow AI GUI with installer"""
    print("🚀 Shadow AI - GUI Build with Installer")
    print("=" * 50)
    print(f"🐍 Python: {platform.python_version()}")
    print(f"💻 Platform: {platform.system()} {platform.release()}")
    print()
    
    # Build pipeline
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("GUI Application Build", build_gui_application),
        ("Installer Package Creation", create_installer_package),
        ("Cleanup", cleanup_build_artifacts)
    ]
    
    success = True
    for step_name, step_function in steps:
        print(f"\n📍 {step_name}")
        print("-" * 30)
        
        if not step_function():
            print(f"❌ {step_name} failed!")
            success = False
            break
        print()
    
    # Final result
    print("=" * 50)
    if success:
        print("🎉 Shadow AI GUI build completed successfully!")
        print()
        print("📦 Generated Files:")
        print("   - dist/ShadowAI.exe (Main application)")
        print("   - ShadowAI-GUI-Windows.zip (Complete package)")
        print("   - ShadowAI_Installer_Package/ (Installation files)")
        print()
        print("🚀 Distribution Ready:")
        print("   1. Share ShadowAI-GUI-Windows.zip with users")
        print("   2. Users extract and run Configure_And_Run.bat")
        print("   3. Follow the configuration guide")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()