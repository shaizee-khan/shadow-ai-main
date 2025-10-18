# shadow_core/stt_multilingual.py
"""
Multilingual Speech-to-Text module with OpenAI Whisper API for Urdu, Pashto, and English
"""

import logging
import asyncio
import re
import tempfile
import openai
from typing import Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import soundfile as sf
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class MultilingualSTT:
    """
    Multilingual Speech-to-Text using OpenAI Whisper API for superior Urdu, Pashto, and English recognition
    """
    
    def __init__(self, multilingual_manager):
        self.multilingual_manager = multilingual_manager
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Set OpenAI API key for Whisper API
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            logger.info("🔧 OpenAI Whisper API configured")
        else:
            logger.warning("❌ OpenAI API key not found - Whisper API will not work")
        
        # Initialize microphone for quick listening
        try:
            self.microphone = sr.Microphone()
            self.recognizer = sr.Recognizer()
            logger.info("🎤 Microphone initialized for quick listening")
        except Exception as e:
            logger.warning(f"🎤 Microphone initialization failed: {e}")
            self.microphone = None
            self.recognizer = None
        
        # Language codes mapping
        self.language_codes = {
            'ur': 'ur',  # Whisper supports Urdu directly
            'ps': 'ps',  # Whisper supports Pashto directly  
            'en': 'en',
            'hi': 'hi',
            'ar': 'ar'
        }
        
        # Roman script detection patterns
        self.roman_urdu_patterns = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'thi', 'the', 'kyun', 'kahan', 'kaun',
            'acha', 'theek', 'bilkul', 'zaroor', 'salam', 'alaikum'
        ]
        
        self.roman_pashto_patterns = [
            'sta', 'yast', 'kaw', 'kawi', 'kawam', 'kawalai', 'kawale', 
            'sham', 'dera', 'khaire', 'kha', 'manana', 'mehrbani', 'sara',
            'lag', 'de', 'da', 'pa', 'po', 'kaw', 'ka', 'komak', 'murajat'
        ]

    async def _transcribe_with_whisper_api(self, audio_file_path: str, language: str = None) -> str:
        """Transcribe using OpenAI Whisper API (most accurate)"""
        try:
            if not OPENAI_API_KEY:
                logger.error("❌ OpenAI API key not configured")
                return ""
                
            with open(audio_file_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
            return str(transcript).strip()
        except Exception as e:
            logger.error(f"❌ OpenAI Whisper API failed: {e}")
            return ""

    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> str:
        """Record audio and save to temporary file"""
        try:
            logger.info(f"🎤 Recording audio for {duration} seconds...")
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )
            sd.wait()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, recording, sample_rate)
                return tmp.name
                
        except Exception as e:
            logger.error(f"❌ Audio recording failed: {e}")
            return ""

    async def _quick_listen_sr(self, timeout: int = 3) -> Optional[str]:
        """Quick listening using speech_recognition (fallback)"""
        if not self.microphone or not self.recognizer:
            return None
            
        try:
            def recognize():
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=timeout)
                        # Save to file and use Whisper API
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                            audio_data = audio.get_wav_data()
                            with open(tmp.name, "wb") as f:
                                f.write(audio_data)
                            return self._transcribe_with_whisper_api(tmp.name)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        return None
                    except Exception as e:
                        logger.error(f"Quick listen error: {e}")
                        return None
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.thread_pool, recognize)
        except Exception as e:
            logger.error(f"Quick listen failed: {e}")
            return None

    async def listen(self, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen for speech and convert to text with automatic language detection
        Uses OpenAI Whisper API for superior multilingual recognition
        Returns: (text, detected_language)
        """
        try:
            logger.info("🎤 Listening for speech...")
            
            # Record audio
            audio_file = self.record_audio(duration=min(timeout, 10))
            if not audio_file:
                return None, None
            
            # Use Whisper API with automatic language detection
            text = await self._transcribe_with_whisper_api(audio_file)
            
            if text:
                # Detect language from text
                detected_lang = await self._detect_language_from_text(text)
                logger.info(f"🎯 Recognized: {text} (Language: {detected_lang})")
                return text, detected_lang
            
            logger.info("❌ No speech recognized")
            return None, None
            
        except Exception as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return None, None

    async def listen_with_language_hint(self, language: str, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen with specific language preference using Whisper API
        """
        try:
            logger.info(f"🎤 Listening for {language}...")
            
            # Record audio
            audio_file = self.record_audio(duration=min(timeout, 10))
            if not audio_file:
                return None, None
            
            # Get Whisper language code
            whisper_lang = self.language_codes.get(language, None)
            
            # Transcribe with language hint using Whisper API
            text = await self._transcribe_with_whisper_api(audio_file, whisper_lang)
            
            if text:
                logger.info(f"🎯 Recognized {language}: {text}")
                return text, language
            
            return None, None
            
        except Exception as e:
            logger.error(f"❌ Language-specific STT error: {e}")
            return None, None

    async def listen_simple(self, language: str = 'en') -> Optional[str]:
        """
        Simple speech recognition using Whisper API
        """
        try:
            audio_file = self.record_audio(duration=5)
            if not audio_file:
                return None
            
            whisper_lang = self.language_codes.get(language, None)
            text = await self._transcribe_with_whisper_api(audio_file, whisper_lang)
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Simple listen error: {e}")
            return None

    async def _detect_language_from_text(self, text: str) -> str:
        """Detect language from transcribed text"""
        if not text:
            return 'en'
        
        text_lower = text.lower()
        
        # Check for Urdu patterns
        urdu_score = sum(1 for pattern in self.roman_urdu_patterns if pattern in text_lower)
        if urdu_score >= 2:
            return 'ur'
        
        # Check for Pashto patterns
        pashto_score = sum(1 for pattern in self.roman_pashto_patterns if pattern in text_lower)
        if pashto_score >= 2:
            return 'ps'
        
        # Check script characters
        if self._contains_urdu_script(text):
            return 'ur'
        if self._contains_pashto_script(text):
            return 'ps'
        if self._contains_hindi_script(text):
            return 'hi'
        
        # Default to English
        return 'en'

    def _contains_urdu_script(self, text: str) -> bool:
        """Check if text contains Urdu script characters"""
        return bool(re.search(r'[\u0600-\u06FF]', text))
    
    def _contains_pashto_script(self, text: str) -> bool:
        """Check if text contains Pashto script characters"""
        return bool(re.search(r'[\u0600-\u06FF\u0671-\u06D3]', text))
    
    def _contains_hindi_script(self, text: str) -> bool:
        """Check if text contains Hindi script characters"""
        return bool(re.search(r'[\u0900-\u097F]', text))

    def _urdu_to_roman(self, urdu_text: str) -> str:
        """Convert Urdu script to Roman Urdu"""
        urdu_roman_map = {
            'میں': 'main', 'ہوں': 'hoon', 'ہے': 'hai', 'ہیں': 'hain',
            'آپ': 'aap', 'کیسے': 'kaise', 'ہو': 'ho', 'ٹھیک': 'theek',
            'شکریہ': 'shukriya', 'کیا': 'kya', 'کر': 'kar', 'سکتے': 'sakte',
            'میری': 'meri', 'مدد': 'madad', 'سن': 'sun', 'رہے': 'rahe',
            'جواب': 'jawab', 'دو': 'do', 'السلام': 'salam', 'علیکم': 'alaikum',
        }
        
        roman_text = urdu_text
        for urdu, roman in urdu_roman_map.items():
            roman_text = roman_text.replace(urdu, roman)
        
        return roman_text
    
    def _pashto_to_roman(self, pashto_text: str) -> str:
        """Convert Pashto script to Roman Pashto"""
        pashto_roman_map = {
            'سته': 'sta', 'یاست': 'yast', 'کولی': 'kaw', 'کولی شم': 'kawam',
            'شئ': 'she', 'مه': 'ma', 'ته': 'ta', 'دی': 'de', 'مو': 'mo',
            'ستا': 'sta', 'زما': 'zma', 'د': 'da', 'په': 'pa', 'کې': 'ke',
            'نه': 'na', 'سلام': 'salam', 'مننه': 'manana', 'مهرباني': 'mehrbani',
        }
        
        roman_text = pashto_text
        for pashto, roman in pashto_roman_map.items():
            roman_text = roman_text.replace(pashto, roman)
        
        return roman_text

    async def is_roman_input(self, text: str) -> bool:
        """Check if input appears to be in Roman script"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for Roman patterns
        urdu_score = sum(1 for pattern in self.roman_urdu_patterns if pattern in text_lower)
        pashto_score = sum(1 for pattern in self.roman_pashto_patterns if pattern in text_lower)
        
        # Check for absence of native script characters
        has_native_script = (
            self._contains_urdu_script(text) or 
            self._contains_pashto_script(text) or
            self._contains_hindi_script(text)
        )
        
        return (urdu_score >= 1 or pashto_score >= 1) and not has_native_script

    def get_available_languages(self) -> list:
        """Get list of available languages for speech recognition"""
        return [
            {'code': 'ur', 'name': 'Urdu', 'whisper_support': True},
            {'code': 'ps', 'name': 'Pashto', 'whisper_support': True},
            {'code': 'en', 'name': 'English', 'whisper_support': True},
            {'code': 'hi', 'name': 'Hindi', 'whisper_support': True},
            {'code': 'ar', 'name': 'Arabic', 'whisper_support': True}
        ]

    async def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            # Quick test recording
            audio_file = self.record_audio(duration=2)
            if audio_file:
                # Try to transcribe (even if no speech)
                text = await self._transcribe_with_whisper_api(audio_file)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Microphone test failed: {e}")
            return False

    def get_capabilities(self) -> dict:
        """Get STT capabilities information"""
        return {
            "primary_engine": "OpenAI Whisper API",
            "supported_languages": ["ur", "ps", "en", "hi", "ar"],
            "automatic_language_detection": True,
            "api_configured": OPENAI_API_KEY is not None
        }


# Utility function for quick speech recognition
async def quick_listen(timeout: int = 5) -> Optional[str]:
    """
    Quick utility function for simple speech recognition using Whisper API
    """
    try:
        # Create a temporary instance
        stt = MultilingualSTT(None)
        text, lang = await stt.listen(timeout=timeout)
        return text
    except Exception as e:
        logger.warning(f"❌ Quick listen failed: {e}")
        return None