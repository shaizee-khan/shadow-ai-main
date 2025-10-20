# build_all.py
"""
Build Shadow AI for Windows GUI
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check platform
    if platform.system() != 'Windows':
        print("❌ This build is for Windows only!")
        print("💡 Please run on Windows 10/11")
        return False
    
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
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for missing in missing_files:
            print(f"   - {missing}")
        return False
    
    print("✅ All requirements met")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Install from requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        
        # Install build tools
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True, capture_output=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

def build_windows_gui():
    """Build Windows GUI application"""
    print("🏗️ Building Windows GUI Application...")
    
    try:
        # PyInstaller command for single executable
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
        
        print(f"🔧 Running: {' '.join(pyinstaller_cmd)}")
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Windows GUI application built successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_distribution_package():
    """Create final distribution package"""
    print("📦 Creating Distribution Package...")
    
    try:
        # Create distribution folder
        dist_folder = "ShadowAI_Windows"
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        os.makedirs(dist_folder)
        
        # Copy executable
        if not os.path.exists("dist/ShadowAI.exe"):
            print("❌ Executable not found in dist folder")
            return False
        
        shutil.copy2("dist/ShadowAI.exe", f"{dist_folder}/ShadowAI.exe")
        
        # Create configuration file
        config_content = '''# Shadow AI Configuration
# Required: Get your OpenAI API key from https://platform.openai.com/api-keys

OPENAI_API_KEY = "your-openai-api-key-here"

# Optional: Weather API (get from https://openweathermap.org/api)
OPENWEATHER_API_KEY = "your-weather-api-key-here"

# Note: Replace the placeholder text with your actual API keys
# The application requires a valid OpenAI API key to function
'''
        with open(f"{dist_folder}/config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        # Copy documentation
        if os.path.exists("README.md"):
            shutil.copy2("README.md", f"{dist_folder}/README.md")
        if os.path.exists("LICENSE"):
            shutil.copy2("LICENSE", f"{dist_folder}/LICENSE")
        
        # Create launcher script
        launcher_content = '''@echo off
chcp 65001 >nul
echo.
echo ========================================
echo           Shadow AI Launcher
echo ========================================
echo.
echo Requirements:
echo - OpenAI API key in config.py
echo - Internet connection
echo - Microphone (for voice features)
echo.
echo Press any key to configure and launch...
pause >nul
echo.
echo Opening configuration file...
notepad config.py
echo.
echo Press any key to launch Shadow AI...
pause >nul
echo.
echo Starting Shadow AI...
ShadowAI.exe
'''
        with open(f"{dist_folder}/Launch_ShadowAI.bat", "w", encoding="utf-8") as f:
            f.write(launcher_content)
        
        # Create ZIP package
        shutil.make_archive("ShadowAI_Windows_GUI", 'zip', dist_folder)
        
        print("✅ Distribution package created: ShadowAI_Windows_GUI.zip")
        return True
        
    except Exception as e:
        print(f"❌ Package creation failed: {e}")
        return False

def cleanup():
    """Clean up build artifacts"""
    print("🧹 Cleaning up...")
    
    try:
        # Remove build directory
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        # Remove .spec files
        for spec_file in Path(".").glob("*.spec"):
            spec_file.unlink()
        
        # Clean __pycache__
        for pycache in Path(".").rglob("__pycache__"):
            shutil.rmtree(pycache)
            
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def build_for_windows():
    """Build specifically for Windows"""
    print(f"💻 Building for Windows {platform.release()}...")
    
    # Build pipeline
    pipeline = [
        ("Requirements Check", check_requirements),
        ("Dependency Installation", install_dependencies),
        ("GUI Application Build", build_windows_gui),
        ("Distribution Package", create_distribution_package),
        ("Cleanup", cleanup)
    ]
    
    success = True
    for step_name, step_function in pipeline:
        print(f"\n📍 {step_name}")
        print("-" * 30)
        
        if not step_function():
            print(f"❌ {step_name} failed!")
            success = False
            break
    
    return success

def main():
    """Main build function"""
    print("🚀 Shadow AI - Windows GUI Build System")
    print("=" * 50)
    print(f"🏷️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print()
    
    # Build for current platform (Windows only)
    success = build_for_windows()
    
    # Final result
    print("\n" + "=" * 50)
    if success:
        print("🎉 Build completed successfully!")
        print()
        print("📦 Generated Files:")
        print("   - dist/ShadowAI.exe (Main application)")
        print("   - ShadowAI_Windows/ (Distribution folder)")
        print("   - ShadowAI_Windows_GUI.zip (Ready to share)")
        print()
        print("🚀 Distribution Ready:")
        print("   1. Share ShadowAI_Windows_GUI.zip")
        print("   2. Users extract and run Launch_ShadowAI.bat")
        print("   3. Follow configuration guide")
        print()
        print("🎯 Features Included:")
        print("   - Voice recognition with Whisper")
        print("   - GPT-4 conversations")
        print("   - Text-to-speech responses")
        print("   - Weather integration")
        print("   - Modern GUI interface")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()