import speech_recognition as sr
import asyncio
import threading
import time
import tempfile
import logging
import openai
from config import OPENAI_API_KEY
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ShadowSTT:
    """
    Unified Speech-to-Text (STT) system for Shadow AI.
    Uses OpenAI Whisper API for accurate transcription.
    """

    def __init__(self,
                 energy_threshold: int = 300,
                 pause_threshold: float = 0.8,
                 language: str = "en"):
        """
        language: STT language code (e.g. "en", "ur", "ps")
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = None
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self._stop_listening = None
        self._is_listening = False

        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            logger.info("🎤 Microphone initialized successfully")
        except Exception as e:
            logger.warning(f"🎤 Microphone initialization failed: {e}")
            self.microphone = None

        # Configure OpenAI API for Whisper
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            logger.info("🔧 OpenAI Whisper API configured")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found - Whisper API will not work")

    # ------------------------------
    # Utility Methods
    # ------------------------------
    def check_microphone(self) -> bool:
        """Ensure microphone is initialized before use."""
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone()
                logger.info("✅ Microphone reinitialized successfully")
                return True
            except Exception as e:
                logger.error(f"❌ Microphone check failed: {e}")
                return False
        return True

    def set_language(self, lang_code: str = "en"):
        """Change STT language dynamically."""
        self.language = lang_code
        logger.info(f"🌍 STT language switched to {lang_code}")

    # ------------------------------
    # Transcription Methods
    # ------------------------------
    def _transcribe_with_whisper_api(self, audio_file_path: str) -> str:
        """Transcribe using OpenAI Whisper API (most accurate)."""
        try:
            if not OPENAI_API_KEY:
                logger.error("❌ OpenAI API key not configured")
                return ""
                
            with open(audio_file_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.language,
                    response_format="text"
                )
            return str(transcript).strip()
        except Exception as e:
            logger.error(f"❌ OpenAI Whisper transcription failed: {e}")
            return ""

    # ------------------------------
    # Core Listening Methods
    # ------------------------------
    async def listen_once_async(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Async single-shot listen -> return recognized text."""
        if not self.check_microphone():
            return ""

        def recognize():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                    
                    # Save audio to file and use Whisper API
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        audio_data = audio.get_wav_data()
                        with open(tmp.name, "wb") as f:
                            f.write(audio_data)
                        return self._transcribe_with_whisper_api(tmp.name)
                        
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                logger.error(f"❌ Recognition error: {e}")
                return ""

        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(self.thread_pool, recognize)
            if text:
                logger.info(f"🎯 Recognized: {text}")
            return text
        except Exception as e:
            logger.error(f"❌ Async listen error: {e}")
            return ""

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Blocking single-shot listen -> return recognized text."""
        if not self.check_microphone():
            return ""

        try:
            with self.microphone as source:
                logger.info(f"🎤 Listening... (timeout: {timeout}s)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                # Save audio to file and use Whisper API
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    audio_data = audio.get_wav_data()
                    with open(tmp.name, "wb") as f:
                        f.write(audio_data)
                    return self._transcribe_with_whisper_api(tmp.name)
                    
        except sr.WaitTimeoutError:
            logger.info("⏰ Listening timed out")
            return ""
        except Exception as e:
            logger.error(f"❌ Listen error: {e}")
            return ""

    # ------------------------------
    # Continuous Listening
    # ------------------------------
    def listen_continuous(self, callback, event_loop=None, timeout: int = 5, phrase_time_limit: int = 10):
        """Start continuous listening in background. Returns stop() function."""
        if not self.check_microphone():
            return lambda: None

        stop_flag = threading.Event()
        self._is_listening = True

        def listen_worker():
            while not stop_flag.is_set() and self._is_listening:
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = self.recognizer.listen(
                                source,
                                timeout=2,
                                phrase_time_limit=phrase_time_limit
                            )
                            
                            # Transcribe using Whisper API
                            text = ""
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                audio_data = audio.get_wav_data()
                                with open(tmp.name, "wb") as f:
                                    f.write(audio_data)
                                text = self._transcribe_with_whisper_api(tmp.name)

                            if text:
                                logger.info(f"🎯 Continuous recognition: {text}")

                                # Stop command check
                                if text.lower().strip() in ["stop listening", "exit", "stop", "quit"]:
                                    logger.info("🛑 Stop command detected")
                                    stop_flag.set()
                                    break

                                # Execute callback
                                if callback:
                                    if event_loop and event_loop.is_running():
                                        if asyncio.iscoroutinefunction(callback):
                                            asyncio.run_coroutine_threadsafe(callback(text), event_loop)
                                        else:
                                            # Wrap sync callback in async
                                            async def async_wrapper():
                                                try:
                                                    callback(text)
                                                except Exception as e:
                                                    logger.error(f"❌ Callback error: {e}")
                                            asyncio.run_coroutine_threadsafe(async_wrapper(), event_loop)
                                    else:
                                        try:
                                            callback(text)
                                        except Exception as e:
                                            logger.error(f"❌ Callback error: {e}")
                                            
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"❌ Listen error: {e}")
                            continue

                except Exception as e:
                    logger.error(f"❌ Worker error: {e}")
                    if not stop_flag.is_set():
                        time.sleep(0.1)

            logger.info("✅ Continuous listening stopped")

        worker_thread = threading.Thread(target=listen_worker, daemon=True)
        worker_thread.start()

        def stop_listening():
            logger.info("🛑 Stopping continuous listening...")
            stop_flag.set()
            self._is_listening = False
            try:
                worker_thread.join(timeout=2.0)
            except Exception:
                pass
            self._stop_listening = None

        self._stop_listening = stop_listening
        logger.info(f"🔊 Continuous STT started (language: {self.language})")
        return stop_listening

    # ------------------------------
    # Control Methods
    # ------------------------------
    def stop(self):
        """Stop any ongoing listening."""
        if self._stop_listening:
            try:
                self._stop_listening()
            except Exception as e:
                logger.error(f"❌ Stop failed: {e}")
            finally:
                self._stop_listening = None
                self._is_listening = False

    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._is_listening

    # ------------------------------
    # Test Methods
    # ------------------------------
    async def test_microphone(self) -> bool:
        """Test if microphone is working."""
        if not self.check_microphone():
            return False
        try:
            text = await self.listen_once_async(timeout=2)
            return text != ""
        except Exception as e:
            logger.error(f"❌ Microphone test failed: {e}")
            return False

    def get_mode_info(self) -> dict:
        """Get information about current STT configuration."""
        return {
            "mode": "openai_whisper",
            "language": self.language,
            "microphone_available": self.microphone is not None,
            "is_listening": self._is_listening,
            "openai_configured": OPENAI_API_KEY is not None
        }


# ------------------------------
# Quick Utility Function
# ------------------------------
async def quick_listen(timeout: int = 3) -> str:
    """Quick utility for simple speech recognition using Whisper API."""
    try:
        stt = ShadowSTT()
        return await stt.listen_once_async(timeout=timeout)
    except Exception as e:
        logger.error(f"❌ Quick listen failed: {e}")
        return ""