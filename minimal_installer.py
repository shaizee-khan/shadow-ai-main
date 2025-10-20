# minimal_installer.py
"""
Minimal installer for Shadow AI - Fast and efficient
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import os
import shutil
import sys
import subprocess
import threading
from pathlib import Path
import webbrowser

class MinimalInstaller:
    """Minimal installer for Shadow AI"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.install_dir = Path.home() / "ShadowAI"
        self.setup_window()
        self.setup_gui()
        
    def setup_window(self):
        """Setup window"""
        self.root.title("Shadow AI - Quick Installer")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.center_window()
        
    def center_window(self):
        """Center window"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self):
        """Setup installer GUI"""
        # Main container
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="🤖 Shadow AI",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Voice-Enabled AI Assistant",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        ).pack()
        
        # Features
        features_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features = [
            "🎤 Voice recognition with OpenAI Whisper",
            "🤖 GPT-4 powered conversations", 
            "🔊 Text-to-speech responses",
            "🌤️ Live weather updates",
            "🎨 Modern dark theme GUI"
        ]
        
        for feature in features:
            ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(size=12),
                justify="left"
            ).pack(anchor="w", pady=2)
        
        # Installation directory
        dir_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dir_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ctk.CTkLabel(dir_frame, text="Installation Directory:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(dir_frame, text=str(self.install_dir), text_color="lightblue").pack(anchor="w", pady=(5, 0))
        
        # Progress area
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_label = ctk.CTkLabel(
            progress_frame, 
            text="Ready to install Shadow AI",
            text_color="lightgreen"
        )
        self.status_label.pack()
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Install button
        self.install_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Install Shadow AI",
            command=self.start_installation,
            width=200,
            height=45,
            fg_color="#2E8B57",
            hover_color="#3CB371",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.install_btn.pack(pady=5)
        
        # Documentation link
        ctk.CTkButton(
            button_frame,
            text="📚 View Documentation",
            command=self.open_docs,
            width=200,
            height=35,
            fg_color="transparent",
            border_width=2,
            border_color="#3B82F6"
        ).pack(pady=5)
        
    def open_docs(self):
        """Open documentation"""
        webbrowser.open("https://github.com/yourusername/shadow-ai")
        
    def start_installation(self):
        """Start installation in separate thread"""
        self.install_btn.configure(state="disabled")
        thread = threading.Thread(target=self.install)
        thread.daemon = True
        thread.start()
        
    def update_progress(self, value, text):
        """Update progress bar and status"""
        self.progress['value'] = value
        self.status_label.configure(text=text)
        self.root.update_idletasks()
        
    def install(self):
        """Main installation process"""
        try:
            self.update_progress(10, "Creating installation directory...")
            
            # Create installation directory
            self.install_dir.mkdir(exist_ok=True)
            
            self.update_progress(20, "Copying application files...")
            
            # Copy current directory files
            current_dir = Path(__file__).parent
            files_to_copy = [
                "run_shadow_gui.py",
                "main.py", 
                "config.example.py",
                "requirements.txt",
                "README.md",
                "LICENSE"
            ]
            
            for file in files_to_copy:
                source = current_dir / file
                if source.exists():
                    shutil.copy2(source, self.install_dir / file)
            
            self.update_progress(40, "Creating application structure...")
            
            # Copy shadow_core directory
            shadow_core_src = current_dir / "shadow_core"
            shadow_core_dest = self.install_dir / "shadow_core"
            if shadow_core_src.exists():
                if shadow_core_dest.exists():
                    shutil.rmtree(shadow_core_dest)
                shutil.copytree(shadow_core_src, shadow_core_dest)
            
            self.update_progress(60, "Creating configuration...")
            
            # Create config file from example
            config_example = self.install_dir / "config.example.py"
            config_file = self.install_dir / "config.py"
            if config_example.exists() and not config_file.exists():
                shutil.copy2(config_example, config_file)
            
            self.update_progress(80, "Creating launchers...")
            
            # Create Windows batch launcher
            batch_content = f'''@echo off
chcp 65001 >nul
echo.
echo 🤖 Shadow AI - Starting...
echo.
echo 📁 Location: {self.install_dir}
echo.
echo ⚠️  Make sure to configure your OpenAI API key in config.py
echo.
cd /d "{self.install_dir}"
python run_shadow_gui.py
pause
'''
            (self.install_dir / "Start Shadow AI.bat").write_text(batch_content, encoding='utf-8')
            
            # Create Python launcher script
            launcher_content = '''#!/usr/bin/env python3
"""
Shadow AI Launcher
"""

import os
import sys
from pathlib import Path

def main():
    """Launch Shadow AI"""
    install_dir = Path(__file__).parent
    os.chdir(install_dir)
    
    print("🤖 Shadow AI Launcher")
    print("====================")
    print(f"📁 Directory: {install_dir}")
    print()
    
    # Check if config exists
    config_file = install_dir / "config.py"
    if not config_file.exists():
        print("⚠️  Warning: config.py not found!")
        print("   Please copy config.example.py to config.py")
        print("   and add your OpenAI API key.")
        print()
    
    # Check requirements
    try:
        import customtkinter
        import openai
        import pygame
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        input("Press Enter to exit...")
        return
    
    # Launch application
    try:
        print("🚀 Starting Shadow AI...")
        from run_shadow_gui import main
        main()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
            (self.install_dir / "launcher.py").write_text(launcher_content)
            
            self.update_progress(100, "Installation complete!")
            
            # Show success message
            self.root.after(0, self.show_success)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
            
    def show_success(self):
        """Show success message"""
        messagebox.showinfo(
            "Installation Complete!", 
            f"🤖 Shadow AI has been successfully installed!\n\n"
            f"📁 Location: {self.install_dir}\n\n"
            f"Next steps:\n"
            f"1. Edit {self.install_dir}/config.py\n"
            f"2. Add your OpenAI API key\n" 
            f"3. Run 'Start Shadow AI.bat'\n\n"
            f"Enjoy your AI assistant! 🎉"
        )
        
        # Enable install button and change text
        self.install_btn.configure(
            state="normal", 
            text="✅ Installed - Run Again?",
            fg_color="#3B82F6"
        )
        
    def show_error(self, error_msg):
        """Show error message"""
        messagebox.showerror(
            "Installation Failed", 
            f"Installation failed:\n\n{error_msg}\n\n"
            f"Please check your permissions and try again."
        )
        self.install_btn.configure(state="normal")
        self.status_label.configure(text="Installation failed", text_color="red")
        
    def run(self):
        """Run installer"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        installer = MinimalInstaller()
        installer.run()
    except Exception as e:
        print(f"Installer error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()