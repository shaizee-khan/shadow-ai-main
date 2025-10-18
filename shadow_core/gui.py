# shadow_core/gui.py
import customtkinter as ctk
from datetime import datetime
import psutil
import threading
import time
from typing import Optional, Callable

# ========== THEME SETUP ==========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ========== MAIN APP ==========
class ShadowGUI(ctk.CTk):
    def __init__(self, on_user_input_callback: Optional[Callable] = None):
        super().__init__()

        self.on_user_input = on_user_input_callback
        self.title("SHADOW AI Interface")
        self.geometry("1200x700")
        self.configure(fg_color="#0b0f19")
        
        # Prevent window from being resizable to avoid layout issues
        self.resizable(True, True)

        # Configure grid weights for proper scaling
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()
        self._start_background_tasks()

    def _create_widgets(self):
        # Top Bar
        self.top_frame = ctk.CTkFrame(self, height=40, fg_color="#111827", corner_radius=0)
        self.top_frame.pack(fill="x", side="top")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.top_frame, text="SHADOW AI | OpenAI GPT-4 & Whisper", 
                                      font=("Consolas", 16, "bold"))
        self.title_label.pack(side="left", padx=20)

        self.time_label = ctk.CTkLabel(self.top_frame, text="", font=("Consolas", 14))
        self.time_label.pack(side="right", padx=20)

        # Main Layout (3 Columns)
        self.main_frame = ctk.CTkFrame(self, fg_color="#0b0f19")
        self.main_frame.pack(expand=True, fill="both", padx=15, pady=10)

        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # ========== LEFT PANEL ==========
        self._create_left_panel()
        
        # ========== CENTER PANEL ==========
        self._create_center_panel()
        
        # ========== RIGHT PANEL ==========
        self._create_right_panel()

    def _create_left_panel(self):
        self.left_panel = ctk.CTkFrame(self.main_frame, fg_color="#111827", corner_radius=15)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.left_panel.grid_propagate(False)

        # System Status
        ctk.CTkLabel(self.left_panel, text="System Status", font=("Consolas", 14, "bold")).pack(pady=10)

        self.cpu_label = ctk.CTkLabel(self.left_panel, text="CPU: --%", font=("Consolas", 12))
        self.cpu_label.pack(pady=5)

        self.mem_label = ctk.CTkLabel(self.left_panel, text="Memory: --%", font=("Consolas", 12))
        self.mem_label.pack(pady=5)

        # AI Status
        ctk.CTkLabel(self.left_panel, text="\nAI Status", font=("Consolas", 14, "bold")).pack(pady=(20, 10))
        self.ai_status_label = ctk.CTkLabel(self.left_panel, text="🟢 ONLINE", text_color="#10b981", 
                                          font=("Consolas", 12, "bold"))
        self.ai_status_label.pack(pady=5)

        self.model_label = ctk.CTkLabel(self.left_panel, text="GPT-4 | Whisper | TTS", font=("Consolas", 10))
        self.model_label.pack(pady=2)

        # Weather Section - ADDED THIS SECTION
        ctk.CTkLabel(self.left_panel, text="\nLive Weather", 
                    font=("Consolas", 14, "bold")).pack(pady=(20, 10))
        
        self.weather_label = ctk.CTkLabel(
            self.left_panel, 
            text="🌡️ Loading weather...",
            font=("Consolas", 10),
            justify="left",
            wraplength=250
        )
        self.weather_label.pack(pady=5, padx=10)

        # Refresh Weather Button
        self.weather_btn = ctk.CTkButton(
            self.left_panel, 
            text="🔄 Refresh Weather", 
            command=self._refresh_weather,
            fg_color="#059669",
            hover_color="#047857",
            height=30
        )
        self.weather_btn.pack(pady=5, fill="x", padx=10)

        # Quick Actions
        ctk.CTkLabel(self.left_panel, text="\nQuick Actions", font=("Consolas", 14, "bold")).pack(pady=(20, 10))
        
        self.voice_btn = ctk.CTkButton(self.left_panel, text="🎙 Start Voice", command=self._start_voice, 
                                      fg_color="#3b82f6", hover_color="#2563eb")
        self.voice_btn.pack(pady=5, fill="x", padx=10)

        self.clear_btn = ctk.CTkButton(self.left_panel, text="🗑 Clear Chat", command=self._clear_chat,
                                      fg_color="#6b7280", hover_color="#4b5563")
        self.clear_btn.pack(pady=5, fill="x", padx=10)

    def _create_center_panel(self):
        self.center_panel = ctk.CTkFrame(self.main_frame, fg_color="#0f172a", corner_radius=15)
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        self.center_label = ctk.CTkLabel(self.center_panel, text="SHADOW AI", font=("Orbitron", 36, "bold"))
        self.center_label.pack(pady=80)

        # Status circle
        self.circle_canvas = ctk.CTkCanvas(self.center_panel, width=200, height=200, bg="#0f172a", 
                                         highlightthickness=0)
        self.circle_canvas.pack()
        self._draw_circle("ACTIVE", "#10b981")

        # Status text
        self.status_text = ctk.CTkLabel(self.center_panel, text="Ready for commands", 
                                      font=("Consolas", 12), text_color="#9ca3af")
        self.status_text.pack(pady=10)

        # Voice recording indicator
        self.voice_indicator = ctk.CTkLabel(self.center_panel, text="", font=("Consolas", 14), 
                                          text_color="#f59e0b")
        self.voice_indicator.pack(pady=5)

    def _create_right_panel(self):
        self.right_panel = ctk.CTkFrame(self.main_frame, fg_color="#111827", corner_radius=15)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)

        ctk.CTkLabel(self.right_panel, text="Conversation", font=("Consolas", 14, "bold")).pack(pady=10)

        # Chat box with scrollbar
        self.chat_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.chat_box = ctk.CTkTextbox(self.chat_frame, wrap="word", font=("Consolas", 11))
        self.chat_box.pack(fill="both", expand=True)
        self.chat_box.configure(state="disabled")

        # Input area
        self.input_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=10)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message here...", 
                                      font=("Consolas", 11))
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self._send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", command=self._send_message, width=80)
        self.send_btn.pack(side="right")

        # Initial message
        self._write_shadow("🌌 Shadow AI Online")
        self._write_shadow("🔧 OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
        self._write_shadow("🌤️  OpenWeather API Integrated")
        self._write_shadow("💡 Click Voice button or type your message")
        self._write_shadow("=" * 40)

    def _draw_circle(self, text, color):
        """Draw status circle with text"""
        self.circle_canvas.delete("all")
        self.circle_canvas.create_oval(30, 30, 170, 170, outline=color, width=4)
        self.circle_canvas.create_text(100, 100, text=text, fill=color, 
                                     font=("Consolas", 14, "bold"))

    def _write_shadow(self, message: str):
        """Add a message from Shadow to the chat box"""
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"🤖 {message}\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def write_shadow(self, message: str):
        """Public method to write Shadow messages (for external calls)"""
        self._write_shadow(message)

    def _write_user(self, message: str):
        """Add a user message to the chat box"""
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"👤 {message}\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def _send_message(self):
        """Send text message to Shadow AI"""
        user_msg = self.input_entry.get().strip()
        if user_msg:
            self._write_user(user_msg)
            self.input_entry.delete(0, "end")
            
            # Disable input while processing
            self.input_entry.configure(state="disabled")
            self.send_btn.configure(state="disabled")
            
            # Call the callback function if provided
            if self.on_user_input:
                self.on_user_input(user_msg)

    def _start_voice(self):
        """Start voice input"""
        if self.on_user_input:
            self.on_user_input("voice")

    def _refresh_weather(self):
        """Refresh weather data"""
        if hasattr(self, 'on_weather_refresh'):
            self.on_weather_refresh()
        else:
            self.weather_label.configure(text="🔄 Refreshing weather...")
            # This will be handled by the main application

    def set_weather(self, weather_text: str):
        """Update weather display from external source"""
        self.weather_label.configure(text=weather_text)

    def set_voice_recording(self, recording: bool):
        """Update voice recording status"""
        if recording:
            self.voice_indicator.configure(text="🎤 Recording... Speak now")
            self.voice_btn.configure(text="🛑 Stop Voice", fg_color="#ef4444", hover_color="#dc2626")
            self.status_text.configure(text="Listening...", text_color="#f59e0b")
            self._draw_circle("LISTENING", "#f59e0b")
        else:
            self.voice_indicator.configure(text="")
            self.voice_btn.configure(text="🎙 Start Voice", fg_color="#3b82f6", hover_color="#2563eb")
            self.status_text.configure(text="Ready for commands", text_color="#9ca3af")
            self._draw_circle("ACTIVE", "#10b981")

    def set_thinking(self, thinking: bool):
        """Update thinking status"""
        if thinking:
            self.status_text.configure(text="Processing...", text_color="#3b82f6")
            self._draw_circle("THINKING", "#3b82f6")
        else:
            self.status_text.configure(text="Ready for commands", text_color="#9ca3af")
            self._draw_circle("ACTIVE", "#10b981")

    def _clear_chat(self):
        """Clear the chat history"""
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        
        # Add back initial messages
        self._write_shadow("Chat cleared")
        self._write_shadow("Ready for new conversation")

    def enable_input(self):
        """Re-enable input after processing"""
        self.input_entry.configure(state="normal")
        self.send_btn.configure(state="normal")
        self.input_entry.focus_set()
        self.set_thinking(False)

    def _start_background_tasks(self):
        """Start background update threads"""
        threading.Thread(target=self._update_stats, daemon=True).start()
        threading.Thread(target=self._update_time, daemon=True).start()

    def _update_stats(self):
        """Update system statistics"""
        while True:
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                self.cpu_label.configure(text=f"CPU: {cpu:.1f}%")
                self.mem_label.configure(text=f"Memory: {mem:.1f}%")
            except Exception:
                pass
            time.sleep(2)

    def _update_time(self):
        """Update time display"""
        while True:
            try:
                now = datetime.now().strftime("%I:%M:%S %p  |  %b %d, %Y")
                self.time_label.configure(text=now)
            except Exception:
                pass
            time.sleep(1)

    def run(self):
        """Start the GUI application"""
        try:
            self.mainloop()
        except Exception as e:
            print(f"GUI Error: {e}")


# Simple test function
if __name__ == "__main__":
    def test_callback(text):
        print(f"User input: {text}")
        if text.lower() == "voice":
            print("Voice command received")
        else:
            print(f"Text message: {text}")

    app = ShadowGUI(on_user_input_callback=test_callback)
    app.run()