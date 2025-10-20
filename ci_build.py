# ci_build.py
"""
Build script optimized for CI/CD environments - GUI Only Version
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def detect_ci_environment():
    """Detect CI environment and adjust build accordingly"""
    ci_vars = {
        'GITHUB_ACTIONS': 'GitHub Actions',
        'GITLAB_CI': 'GitLab CI', 
        'TRAVIS': 'Travis CI',
        'CIRCLECI': 'CircleCI',
        'CI': 'Generic CI'
    }
    
    for var, name in ci_vars.items():
        if os.getenv(var):
            return name
    return 'Local'

def verify_project_structure():
    """Verify all required files exist for GUI build"""
    required_files = [
        'run_shadow_gui.py',
        'shadow_core/gui.py',
        'shadow_core/brain.py',
        'config.example.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("🔍 Verifying project structure...")
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for missing in missing_files:
            print(f"   - {missing}")
        return False
    
    print("✅ All required files present")
    return True

def install_dependencies():
    """Install required dependencies for GUI build"""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Install from requirements
        if os.path.exists('requirements.txt'):
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True, capture_output=True)
        
        # Install build tools
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True, capture_output=True)
        
        # Install GUI-specific dependencies
        gui_deps = ['customtkinter', 'pygame', 'psutil', 'requests']
        for dep in gui_deps:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                          check=True, capture_output=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

def test_gui_imports():
    """Test that all GUI modules can be imported"""
    print("🧪 Testing GUI imports...")
    
    test_code = """
import sys
sys.path.append('.')

try:
    # Core dependencies
    import customtkinter
    import openai
    import pygame
    import psutil
    import requests
    import asyncio
    import threading
    
    # Project modules
    from shadow_core.gui import ShadowGUI
    from shadow_core.brain import ShadowBrain
    
    print("SUCCESS: All imports working")
    sys.exit(0)
    
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"OTHER_ERROR: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run([sys.executable, '-c', test_code], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ All GUI imports successful")
            return True
        else:
            print(f"❌ Import test failed: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Import test timed out")
        return False

def build_gui_application():
    """Build the GUI application with PyInstaller"""
    current_platform = platform.system().lower()
    print(f"🏗️ Building GUI application for {current_platform}...")
    
    # Common PyInstaller arguments for GUI
    common_args = [
        '--clean', '--noconfirm', '--onefile', '--windowed',
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
        '--hidden-import=queue'
    ]
    
    # Platform-specific adjustments
    if current_platform == 'windows':
        pass  # Use common args as-is
    elif current_platform == 'darwin':  # macOS
        common_args.extend(['--icon=assets/icon.icns'])
    else:  # Linux
        common_args[4] = '--name=shadow-ai'  # Change name for Linux
    
    # Add the main script
    common_args.append('run_shadow_gui.py')
    
    try:
        print(f"🔧 Running: python -m PyInstaller {' '.join(common_args)}")
        result = subprocess.run([sys.executable, '-m', 'PyInstaller'] + common_args,
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ GUI application built successfully")
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
    print("📦 Creating distribution package...")
    
    dist_folder = "ShadowAI-GUI-Windows"
    
    try:
        # Clean previous distribution
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        
        # Create distribution folder
        os.makedirs(dist_folder, exist_ok=True)
        
        # Copy executable
        if os.path.exists("dist/ShadowAI.exe"):
            shutil.copy2("dist/ShadowAI.exe", f"{dist_folder}/ShadowAI.exe")
        else:
            print("❌ Executable not found in dist folder")
            return False
        
        # Copy configuration and docs
        files_to_copy = [
            ('config.example.py', 'config.py'),
            ('README.md', 'README.md'),
            ('LICENSE', 'LICENSE'),
            ('requirements.txt', 'requirements.txt')
        ]
        
        for src, dst in files_to_copy:
            if os.path.exists(src):
                shutil.copy2(src, f"{dist_folder}/{dst}")
        
        # Create simple README
        readme_content = f"""# Shadow AI - GUI Application

Build Date: {subprocess.getoutput('date /t')}
Python Version: {platform.python_version()}

## Quick Start

1. Edit config.py with your OpenAI API key
2. Run ShadowAI.exe
3. Enjoy your AI assistant!

## Features

- Voice recognition with OpenAI Whisper
- GPT-4 conversations
- Text-to-speech responses
- Weather integration
- Modern GUI interface

## Configuration

Get your API key from: https://platform.openai.com/api-keys
Then edit config.py:

OPENAI_API_KEY = "your-api-key-here"

## Support

Visit: https://github.com/{os.getenv('GITHUB_REPOSITORY', 'your-repo')}
"""
        
        with open(f"{dist_folder}/README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # Create ZIP package
        shutil.make_archive(dist_folder, 'zip', '.', dist_folder)
        
        print(f"✅ Distribution package created: {dist_folder}.zip")
        return True
        
    except Exception as e:
        print(f"❌ Package creation failed: {e}")
        return False

def cleanup():
    """Clean up build artifacts"""
    print("🧹 Cleaning up...")
    
    # Remove build artifacts but keep dist folder
    folders_to_remove = ['build', '__pycache__']
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Clean pycache in subdirectories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("✅ Cleanup completed")

def main():
    """Main CI build function for GUI application"""
    print("🚀 Shadow AI - GUI CI Build System")
    print("=" * 50)
    
    ci_env = detect_ci_environment()
    print(f"🏭 Environment: {ci_env}")
    print(f"🐍 Python: {platform.python_version()}")
    print(f"💻 Platform: {platform.system()} {platform.release()}")
    print()
    
    # Build pipeline
    steps = [
        ("Project Structure Check", verify_project_structure),
        ("Dependency Installation", install_dependencies),
        ("Import Testing", test_gui_imports),
        ("GUI Application Build", build_gui_application),
        ("Distribution Package", create_distribution_package),
        ("Cleanup", cleanup)
    ]
    
    success = True
    for step_name, step_function in steps:
        print(f"\n📍 {step_name}")
        print("-" * 30)
        
        if not step_function():
            print(f"❌ {step_name} failed!")
            success = False
            break
    
    # Final result
    print("\n" + "=" * 50)
    if success:
        print("🎉 CI Build completed successfully!")
        print("📦 Artifacts:")
        print("   - dist/ShadowAI.exe (GUI Application)")
        print("   - ShadowAI-GUI-Windows.zip (Distribution Package)")
    else:
        print("❌ CI Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()