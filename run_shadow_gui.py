# run_shadow_gui.py
import sys
import os
import asyncio
import threading
import time
import pyaudio
import wave
import numpy as np
import tempfile
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual GUI from shadow_core
try:
    from shadow_core.gui import ShadowGUI
    from main import SHADOW, BG_LOOP
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("💡 Make sure you have:")
    print("   - shadow_core/gui.py")
    print("   - main.py with SHADOW and BG_LOOP")
    GUI_AVAILABLE = False

class WeatherService:
    """OpenWeather API service for weather data"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.last_update = None
        self.cache_duration = 600  # 10 minutes cache
        
    def get_weather(self, city="London", country_code="GB"):
        """Get current weather data"""
        try:
            if not self.api_key:
                return {"error": "OpenWeather API key not configured"}
            
            # Construct API URL
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city},{country_code}",
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'updated': datetime.now().strftime("%H:%M")
            }
            
            self.last_update = time.time()
            return weather_info
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}
        except KeyError as e:
            return {"error": f"Invalid weather data format: {str(e)}"}
        except Exception as e:
            return {"error": f"Weather service error: {str(e)}"}
    
    def get_weather_icon(self, icon_code):
        """Convert OpenWeather icon code to emoji"""
        icon_map = {
            '01d': '☀️',  # clear sky day
            '01n': '🌙',  # clear sky night
            '02d': '⛅',  # few clouds day
            '02n': '☁️',  # few clouds night
            '03d': '☁️',  # scattered clouds
            '03n': '☁️',
            '04d': '☁️',  # broken clouds
            '04n': '☁️',
            '09d': '🌧️',  # shower rain
            '09n': '🌧️',
            '10d': '🌦️',  # rain day
            '10n': '🌧️',  # rain night
            '11d': '⛈️',  # thunderstorm
            '11n': '⛈️',
            '13d': '❄️',  # snow
            '13n': '❄️',
            '50d': '🌫️',  # mist
            '50n': '🌫️'
        }
        return icon_map.get(icon_code, '🌈')
    
    def format_weather_text(self, weather_data):
        """Format weather data for display"""
        if 'error' in weather_data:
            return weather_data['error']
        
        icon = self.get_weather_icon(weather_data['icon'])
        return (
            f"{icon} {weather_data['temperature']}°C\n"
            f"{weather_data['description']}\n"
            f"Feels like: {weather_data['feels_like']}°C\n"
            f"Humidity: {weather_data['humidity']}%\n"
            f"Wind: {weather_data['wind_speed']} m/s\n"
            f"📍 {weather_data['city']}, {weather_data['country']}\n"
            f"Updated: {weather_data['updated']}"
        )

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
            try:
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                max_amplitude = np.max(np.abs(audio_data))
                
                if max_amplitude > self.silence_threshold:
                    self.last_sound_time = time.time()
            except:
                pass
        
        return (in_data, pyaudio.paContinue)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.audio.terminate()
        except:
            pass

class ShadowGUIApp:
    def __init__(self):
        if not GUI_AVAILABLE:
            raise ImportError("Required modules not available")
            
        self.gui = ShadowGUI(on_user_input_callback=self._on_user_input)
        self.weather_service = WeatherService()
        self._setup_gui()
        self.voice_recorder = None
        
        # Start weather updates
        self._start_weather_updates()
    
    def _setup_gui(self):
        """Setup initial GUI state"""
        self.gui.write_shadow("🌌 Shadow AI Online")
        self.gui.write_shadow("🔧 OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
        self.gui.write_shadow("💡 Click Voice button or type your message")
        self.gui.write_shadow("🎤 Voice: Auto-stops when you stop speaking")
        self.gui.write_shadow("🌤️  Weather: Auto-updates every 10 minutes")
        self.gui.write_shadow("=" * 40)
        
        # Set initial weather
        self._update_weather_display()
    
    def _start_weather_updates(self):
        """Start background weather updates"""
        def weather_worker():
            while True:
                try:
                    self._update_weather_display()
                    time.sleep(600)  # Update every 10 minutes
                except Exception as e:
                    print(f"Weather update error: {e}")
                    time.sleep(60)  # Retry after 1 minute on error
        
        threading.Thread(target=weather_worker, daemon=True).start()
    
    def _update_weather_display(self):
        """Update weather display in GUI"""
        try:
            # Get weather data (default to London)
            weather_data = self.weather_service.get_weather("London", "GB")
            weather_text = self.weather_service.format_weather_text(weather_data)
            
            # Update GUI if it has a weather label
            if hasattr(self.gui, 'weather_label'):
                self.gui.weather_label.configure(text=weather_text)
            else:
                print(f"Weather: {weather_text.split(chr(10))[0]}")  # Print first line to console
                
        except Exception as e:
            error_text = f"🌡️ Weather unavailable\nCheck API key"
            if hasattr(self.gui, 'weather_label'):
                self.gui.weather_label.configure(text=error_text)
    
    def _on_user_input(self, text):
        """Handle all user input from GUI"""
        text = text.strip()
        if not text:
            return
            
        if text.lower() == "voice":
            self._handle_voice_input()
        elif text.lower().startswith("weather"):
            self._handle_weather_query(text)
        else:
            self._handle_text_input(text)
    
    def _handle_weather_query(self, text):
        """Handle weather-related queries"""
        try:
            # Extract city from query (e.g., "weather London" or "weather in Paris")
            city = "London"  # default
            if "weather" in text.lower():
                parts = text.lower().split("weather")[1].strip()
                if parts.startswith("in"):
                    parts = parts[2:].strip()
                if parts:
                    city = parts.split()[0].title()
            
            self.gui.write_shadow(f"🌤️  Checking weather for {city}...")
            
            # Get weather for specified city
            weather_data = self.weather_service.get_weather(city)
            weather_text = self.weather_service.format_weather_text(weather_data)
            
            if 'error' in weather_data:
                self.gui.write_shadow(f"❌ {weather_data['error']}")
            else:
                self.gui.write_shadow(f"🌤️  Weather in {city}:\n{weather_text}")
                
        except Exception as e:
            self.gui.write_shadow(f"❌ Weather query error: {e}")
        finally:
            self.gui.enable_input()
    
    def _handle_voice_input(self):
        """Start voice input processing"""
        try:
            self.gui.set_voice_recording(True)
            
            # Run voice processing in background
            asyncio.run_coroutine_threadsafe(
                self._process_voice(), 
                BG_LOOP
            )
        except Exception as e:
            self.gui.write_shadow(f"❌ Voice start error: {e}")
            self.gui.set_voice_recording(False)
    
    def _handle_text_input(self, text):
        """Start text input processing"""
        self.gui.set_thinking(True)
        
        # Run text processing in background
        asyncio.run_coroutine_threadsafe(
            self._process_text(text), 
            BG_LOOP
        )
    
    async def _process_voice(self):
        """Process voice input"""
        recorder = None
        try:
            # Initialize voice recorder
            recorder = VoiceRecorder()
            self.gui.write_shadow("🎤 Recording... Speak now")
            
            # Start recording
            recorder.start_recording()
            start_time = time.time()
            
            # Wait for auto-stop or timeout
            while recorder.is_recording and (time.time() - start_time) < 10:
                await asyncio.sleep(0.1)
            
            # Stop recording
            audio_file = recorder.stop_recording()
            
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                self.gui.write_shadow("✅ Processing audio...")
                
                # Use Shadow AI to process voice
                await SHADOW.process_voice_input(audio_file, self.gui)
                
                # Cleanup
                try:
                    os.remove(audio_file)
                except:
                    pass
            else:
                self.gui.write_shadow("❌ No audio detected. Please try again.")
                    
        except Exception as e:
            self.gui.write_shadow(f"❌ Voice processing error: {e}")
        finally:
            # Cleanup recorder
            if recorder:
                try:
                    recorder.cleanup()
                except:
                    pass
            self.gui.set_voice_recording(False)
            self.gui.enable_input()
    
    async def _process_text(self, text):
        """Process text input"""
        try:
            await SHADOW.process_text_input(text, self.gui)
        except Exception as e:
            self.gui.write_shadow(f"❌ Text processing error: {e}")
        finally:
            self.gui.enable_input()
    
    def run(self):
        """Start the application"""
        try:
            self.gui.run()
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            # Cleanup on exit
            if self.voice_recorder:
                self.voice_recorder.cleanup()

def check_microphone():
    """Check if microphone is available"""
    try:
        audio = pyaudio.PyAudio()
        
        # Check for available microphones
        info = audio.get_default_input_device_info()
        if info:
            print(f"🎤 Microphone found: {info.get('name', 'Unknown')}")
            audio.terminate()
            return True
        else:
            print("❌ No microphone found")
            audio.terminate()
            return False
    except Exception as e:
        print(f"❌ Microphone check failed: {e}")
        return False

def main():
    """Main entry point"""
    if not GUI_AVAILABLE:
        print("❌ Cannot start GUI - required modules missing")
        return
    
    print("🚀 Starting Shadow AI GUI...")
    print("🔧 OPENAI WHISPER STT | GPT-4 | OPENAI TTS")
    print("🌤️  OpenWeather API Integration")
    print("💡 Make sure your OPENAI_API_KEY is set in config.py")
    print("💡 Optional: Set OPENWEATHER_API_KEY for weather features")
    
    # Check microphone
    if not check_microphone():
        print("⚠️  No microphone detected. Voice features will not work.")
    
    # Check weather API
    if not os.getenv('OPENWEATHER_API_KEY'):
        print("⚠️  OPENWEATHER_API_KEY not set. Weather features will be limited.")
    
    try:
        app = ShadowGUIApp()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start Shadow AI: {e}")
    finally:
        print("👋 Shadow AI closed")

if __name__ == "__main__":
    main()