# main.py
import asyncio
import sys
import threading
import time
import os
from typing import Dict, Optional, Tuple

# Suppress verbose logging
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------
# Core Modules
# ------------------------------
from shadow_core.voice import ShadowVoice
from shadow_core.gui import ShadowGUI

# OpenAI imports
import openai
from config import OPENAI_API_KEY

# Configure logging - Only show errors, suppress info and httpx logs
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# ------------------------------
# Shadow AI Class (OpenAI Only)
# ------------------------------
class Shadow:
    """Shadow AI using OpenAI GPT-4, Whisper, and TTS"""
    
    def __init__(self):
        """Initialize Shadow AI with OpenAI components"""
        logger.info("Initializing Shadow AI with OpenAI...")
        
        # Initialize voice components
        self.voice = ShadowVoice()
        
        logger.info("🤖 SHADOW AI - OPENAI GPT-4, WHISPER & TTS ONLINE")
        
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                )
            return str(transcript).strip()
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return ""

    async def get_gpt4_response(self, prompt: str) -> str:
        """Get response from OpenAI GPT-4"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are Shadow, a helpful AI assistant. Provide clear, concise responses."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"GPT-4 request failed: {e}")
            return "I apologize, but I'm having trouble processing your request right now."

    async def speak_text(self, text: str):
        """Speak text using OpenAI TTS - Direct speech without file creation"""
        if not text:
            return
            
        try:
            # Generate speech using OpenAI TTS
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.audio.speech.create(
                    model="tts-1",
                    voice="alloy",  # You can change to: alloy, echo, fable, onyx, nova, shimmer
                    input=text
                )
            )
            
            # Get audio data and play directly
            audio_data = response.content
            
            # Play audio directly using pygame
            await self.play_audio_directly(audio_data)
                
        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            # Fallback to system TTS if available
            self.fallback_tts(text)

    async def play_audio_directly(self, audio_data: bytes):
        """Play audio data directly without saving to file"""
        try:
            import pygame
            import io
            
            # Initialize pygame mixer
            pygame.mixer.init()
            
            # Create a file-like object from audio data
            audio_file = io.BytesIO(audio_data)
            
            # Load and play the audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Direct audio playback failed: {e}")
            # Fallback to saving temporary file
            await self.fallback_audio_playback(audio_data)

    async def fallback_audio_playback(self, audio_data: bytes):
        """Fallback method to play audio via temporary file"""
        try:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_file.write(audio_data)
            temp_file.close()
            
            # Play using platform-specific player
            await self.play_audio_file(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
        except Exception as e:
            logger.error(f"Fallback audio playback failed: {e}")

    async def play_audio_file(self, audio_file: str):
        """Play audio file using platform-specific player"""
        try:
            if sys.platform == "win32":
                os.system(f"start wmplayer {audio_file} 2>nul")
            elif sys.platform == "darwin":  # macOS
                os.system(f"afplay {audio_file} 2>/dev/null")
            else:  # Linux
                os.system(f"mpv {audio_file} --no-video --quiet 2>/dev/null")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")

    def fallback_tts(self, text: str):
        """Fallback TTS using pyttsx3 if OpenAI TTS fails"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"Fallback TTS also failed: {e}")
            print(f"🤖 [Text Response]: {text}")

    async def process_voice_input(self, audio_file_path: str, gui=None) -> str:
        """Process voice input and return response"""
        # Step 1: Transcribe audio with Whisper
        if gui:
            gui.write_shadow("🎤 Transcribing speech...")
        
        transcribed_text = await self.transcribe_audio(audio_file_path)
        
        if not transcribed_text:
            error_msg = "Sorry, I couldn't understand the audio."
            if gui:
                gui.write_shadow(error_msg)
            await self.speak_text(error_msg)
            return error_msg
        
        if gui:
            gui.write_shadow(f"👤 User: {transcribed_text}")
        else:
            print(f"👤 User: {transcribed_text}")
        
        # Step 2: Get GPT-4 response
        if gui:
            gui.write_shadow("🤖 Thinking...")
        
        response = await self.get_gpt4_response(transcribed_text)
        
        # Step 3: Display and speak response
        if gui:
            gui.write_shadow(f"🤖 Shadow: {response}")
        else:
            print(f"🤖 Shadow: {response}")
        
        # Speak the response
        await self.speak_text(response)
        
        return response

    async def process_text_input(self, text: str, gui=None) -> str:
        """Process text input and return response"""
        if not text.strip():
            error_msg = "Please provide some input."
            if gui:
                gui.write_shadow(error_msg)
            await self.speak_text(error_msg)
            return error_msg
        
        if gui:
            gui.write_shadow(f"👤 User: {text}")
        else:
            print(f"👤 User: {text}")
        
        response = await self.get_gpt4_response(text)
        
        if gui:
            gui.write_shadow(f"🤖 Shadow: {response}")
        else:
            print(f"🤖 Shadow: {response}")
        
        # Speak the response
        await self.speak_text(response)
        
        return response

    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down Shadow AI...")

# ------------------------------
# Global Shadow Instance
# ------------------------------
SHADOW = Shadow()

# ------------------------------
# Background asyncio loop
# ------------------------------
def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

BG_LOOP = asyncio.new_event_loop()
_bg_thread = threading.Thread(target=start_background_loop, args=(BG_LOOP,), daemon=True)
_bg_thread.start()
time.sleep(0.05)

# ------------------------------
# Voice Recording Function (Auto-stop version)
# ------------------------------
import pyaudio
import wave
import threading

class VoiceRecorder:
    """Voice recorder with auto-stop functionality"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.silence_threshold = 500  # Adjust based on microphone sensitivity
        self.silence_duration = 2.0   # Stop after 2 seconds of silence
        self.last_sound_time = None
    
    def start_recording(self):
        """Start recording audio with auto-stop"""
        self.frames = []
        self.is_recording = True
        self.last_sound_time = time.time()
        
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.callback
        )
        
        self.stream.start_stream()
        
        # Start silence detection thread
        self.silence_thread = threading.Thread(target=self._detect_silence, daemon=True)
        self.silence_thread.start()
    
    def _detect_silence(self):
        """Detect silence and auto-stop recording"""
        while self.is_recording:
            if time.time() - self.last_sound_time > self.silence_duration:
                self.is_recording = False
                break
            time.sleep(0.1)
    
    def stop_recording(self) -> str:
        """Stop recording and save to file"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Save to file
        filename = f"temp_audio_{int(time.time())}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        return filename
    
    def callback(self, in_data, frame_count, time_info, status):
        """Audio callback with silence detection"""
        if self.is_recording:
            self.frames.append(in_data)
            
            # Check for sound (simple amplitude-based detection)
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            
            if max_amplitude > self.silence_threshold:
                self.last_sound_time = time.time()
        
        return (in_data, pyaudio.paContinue)
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio.terminate()

# ------------------------------
# Query Handlers
# ------------------------------
async def handle_voice_input(gui=None):
    """Handle voice input with auto-stop recording"""
    recorder = VoiceRecorder()
    
    try:
        if gui:
            gui.write_shadow("🎤 Recording... (Auto-stop when silent)")
        else:
            print("🎤 Recording... (Speak now - auto-stops when silent)")
        
        # Start recording
        recorder.start_recording()
        
        # Wait for auto-stop (max 10 seconds)
        start_time = time.time()
        while recorder.is_recording and (time.time() - start_time) < 10:
            await asyncio.sleep(0.1)
        
        # Stop recording
        audio_file = recorder.stop_recording()
        
        if gui:
            gui.write_shadow("✅ Audio recorded, processing...")
        else:
            print("✅ Processing...")
        
        # Process the audio
        await SHADOW.process_voice_input(audio_file, gui)
        
        # Clean up temp file
        try:
            os.remove(audio_file)
        except:
            pass
            
    except Exception as e:
        error_msg = f"Error processing voice input: {e}"
        if gui:
            gui.write_shadow(error_msg)
        else:
            print(error_msg)
        await SHADOW.speak_text(error_msg)
    finally:
        recorder.cleanup()

async def handle_text_input(text: str, gui=None):
    """Handle text input"""
    return await SHADOW.process_text_input(text, gui)

# ------------------------------
# CLI Mode
# ------------------------------
def run_cli_mode():
    print("🌌 Shadow CLI Online")
    print("🔧 Mode: OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
    print("💡 Commands: 'voice', 'exit'")
    print("🎤 Voice: Auto-stops when you stop speaking")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("exit", "quit"):
                print("👋 Goodbye!")
                asyncio.run_coroutine_threadsafe(SHADOW.shutdown(), BG_LOOP)
                break
            
            if user_input.lower() == "voice":
                # Handle voice input with auto-stop
                asyncio.run_coroutine_threadsafe(handle_voice_input(), BG_LOOP).result(timeout=60)
                continue
            
            # Handle text input
            response = asyncio.run_coroutine_threadsafe(
                handle_text_input(user_input), 
                BG_LOOP
            ).result(timeout=60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"\n❌ Error: {e}")

# ------------------------------
# GUI Mode
# ------------------------------
def run_gui_mode():
    gui = ShadowGUI(on_user_input_callback=None)
    gui.write_shadow("🌌 Shadow AI Online")
    gui.write_shadow("🔧 OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
    gui.write_shadow("💡 Click Voice button or type your message")

    def on_user_input(text):
        if text.strip().lower() == "voice":
            # Start voice input in background
            asyncio.run_coroutine_threadsafe(handle_voice_input(gui), BG_LOOP)
        else:
            # Handle text input
            asyncio.run_coroutine_threadsafe(handle_text_input(text, gui), BG_LOOP)

    gui.on_user_input = on_user_input
    gui.run()

# ------------------------------
# Main Async Entry Point
# ------------------------------
async def main():
    """Main async entry point"""
    try:
        # Determine mode
        mode = "cli"
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()

        print(f"🚀 Starting Shadow AI in {mode.upper()} mode...")
        print("🔧 OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
        
        if mode == "gui":
            run_gui_mode()
        else:
            run_cli_mode()
            
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"❌ Fatal error: {e}")
    finally:
        await SHADOW.shutdown()

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    # Import numpy for silence detection
    import numpy as np
    
    # Run the main async function
    asyncio.run(main())