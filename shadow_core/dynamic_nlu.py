# shadow_core/dynamic_nlu.py
"""
Ultra-simple NLU system that directly understands intent - No JSON, No Complexity
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DirectIntent:
    action: str
    target: str
    confidence: float
    language: str
    raw_text: str

class DirectInterpreter:
    """
    Direct interpreter - understands natural language instantly
    No complex parsing, no JSON, just direct understanding
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.conversation_memory = []
        logger.info("🚀 Direct Interpreter initialized")
    
    async def understand(self, text: str) -> DirectIntent:
        """
        Direct understanding - instant intent recognition
        Returns simple, actionable intent
        """
        if not text or not text.strip():
            return self._create_intent("chat", "user", 0.8, "en", text)
        
        # Clean text
        clean_text = text.strip().lower()
        
        # Step 1: Ultra-fast direct pattern matching
        direct_intent = self._instant_pattern_match(clean_text, text)
        if direct_intent.confidence > 0.9:
            logger.info(f"🎯 Direct match: {direct_intent.action} -> {direct_intent.target}")
            return direct_intent
        
        # Step 2: Smart AI understanding (if brain available)
        if self.brain:
            ai_intent = await self._ai_quick_understand(clean_text, text)
            if ai_intent.confidence > 0.7:
                logger.info(f"🎯 AI understood: {ai_intent.action} -> {ai_intent.target}")
                return ai_intent
        
        # Step 3: Context-aware fallback
        context_intent = self._context_aware_fallback(clean_text, text)
        logger.info(f"💬 Context fallback: {context_intent.action}")
        return context_intent
    
    def _instant_pattern_match(self, clean_text: str, original_text: str) -> DirectIntent:
        """Ultra-fast direct pattern matching"""
        
        # Greetings
        if any(word in clean_text for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
            return self._create_intent("greet", "user", 0.98, self._detect_lang(original_text), original_text)
        
        # Goodbyes
        if any(word in clean_text for word in ['bye', 'goodbye', 'see you', 'exit', 'quit']):
            return self._create_intent("farewell", "user", 0.97, self._detect_lang(original_text), original_text)
        
        # Weather
        if any(word in clean_text for word in ['weather', 'temperature', 'forecast', 'rain', 'sunny']):
            location = self._extract_location(clean_text)
            return self._create_intent("get_weather", location, 0.95, self._detect_lang(original_text), original_text)
        
        # Messages
        if any(word in clean_text for word in ['send', 'message', 'whatsapp', 'text', 'tell']):
            contact = self._extract_contact(clean_text)
            return self._create_intent("send_message", contact, 0.94, self._detect_lang(original_text), original_text)
        
        # Reminders
        if any(word in clean_text for word in ['remind', 'reminder', 'timer', 'alarm']):
            task = self._extract_task(clean_text)
            return self._create_intent("set_reminder", task, 0.96, self._detect_lang(original_text), original_text)
        
        # Time
        if any(word in clean_text for word in ['time', 'what time', 'current time']):
            return self._create_intent("get_time", "current", 0.99, self._detect_lang(original_text), original_text)
        
        # Date
        if any(word in clean_text for word in ['date', 'what date', 'today']):
            return self._create_intent("get_date", "today", 0.99, self._detect_lang(original_text), original_text)
        
        # Help
        if any(word in clean_text for word in ['help', 'assist', 'support']):
            return self._create_intent("provide_help", "user", 0.93, self._detect_lang(original_text), original_text)
        
        # Search
        if any(word in clean_text for word in ['search', 'find', 'look up', 'google']):
            query = self._extract_query(clean_text)
            return self._create_intent("search_web", query, 0.92, self._detect_lang(original_text), original_text)
        
        # Calculations
        if any(word in clean_text for word in ['calculate', 'math', 'what is', 'how much']):
            expression = self._extract_math(clean_text)
            return self._create_intent("calculate", expression, 0.91, self._detect_lang(original_text), original_text)
        
        # Jokes
        if any(word in clean_text for word in ['joke', 'funny', 'make me laugh']):
            return self._create_intent("tell_joke", "user", 0.90, self._detect_lang(original_text), original_text)
        
        return self._create_intent("chat", "user", 0.8, self._detect_lang(original_text), original_text)
    
    async def _ai_quick_understand(self, clean_text: str, original_text: str) -> DirectIntent:
        """AI-powered quick understanding"""
        try:
            prompt = f"""
            Understand this user message in one word - what do they want?
            
            User: "{original_text}"
            
            Respond with JUST the action word from:
            greet, farewell, weather, message, reminder, time, date, help, search, calculate, joke, chat
            
            Action:
            """
            
            response = await self.brain.ask([{"role": "user", "content": prompt}])
            action = response.strip().lower()
            
            # Map to our actions
            action_map = {
                "greet": ("greet", "user", 0.95),
                "farewell": ("farewell", "user", 0.96),
                "weather": ("get_weather", self._extract_location(clean_text), 0.94),
                "message": ("send_message", self._extract_contact(clean_text), 0.93),
                "reminder": ("set_reminder", self._extract_task(clean_text), 0.95),
                "time": ("get_time", "current", 0.98),
                "date": ("get_date", "today", 0.98),
                "help": ("provide_help", "user", 0.92),
                "search": ("search_web", self._extract_query(clean_text), 0.91),
                "calculate": ("calculate", self._extract_math(clean_text), 0.90),
                "joke": ("tell_joke", "user", 0.89),
                "chat": ("chat", "user", 0.85)
            }
            
            action_data = action_map.get(action, ("chat", "user", 0.8))
            
            return self._create_intent(
                action_data[0], 
                action_data[1], 
                action_data[2],
                self._detect_lang(original_text),
                original_text
            )
            
        except Exception as e:
            logger.error(f"AI understanding failed: {e}")
            return self._create_intent("chat", "user", 0.7, self._detect_lang(original_text), original_text)
    
    def _context_aware_fallback(self, clean_text: str, original_text: str) -> DirectIntent:
        """Context-aware fallback understanding"""
        
        # Check recent conversation for context
        if self.conversation_memory:
            last_intent = self.conversation_memory[-1]
            
            # If last was weather query and this seems related
            if last_intent.action == "get_weather" and any(word in clean_text for word in ['tomorrow', 'week', 'cold', 'hot']):
                location = self._extract_location(clean_text) or last_intent.target
                return self._create_intent("get_weather", location, 0.88, self._detect_lang(original_text), original_text)
            
            # If last was message and this continues
            if last_intent.action == "send_message" and any(word in clean_text for word in ['yes', 'no', 'ok', 'send']):
                return self._create_intent("send_message", last_intent.target, 0.87, self._detect_lang(original_text), original_text)
        
        # Question detection
        if any(word in clean_text for word in ['what', 'how', 'when', 'where', 'why', 'who', 'which']):
            return self._create_intent("answer_question", "user", 0.86, self._detect_lang(original_text), original_text)
        
        # Command detection
        if clean_text.startswith(('open ', 'start ', 'launch ', 'show ', 'play ')):
            target = clean_text.split(' ', 1)[1] if ' ' in clean_text else "something"
            return self._create_intent("open_app", target, 0.89, self._detect_lang(original_text), original_text)
        
        return self._create_intent("chat", "user", 0.8, self._detect_lang(original_text), original_text)
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        locations = ['new york', 'london', 'paris', 'tokyo', 'karachi', 'islamabad', 'lahore']
        for location in locations:
            if location in text:
                return location
        return "current location"
    
    def _extract_contact(self, text: str) -> str:
        """Extract contact from message text"""
        # Simple extraction - look for names after "to"
        if ' to ' in text:
            parts = text.split(' to ', 1)
            if len(parts) > 1:
                name_part = parts[1].split(' ', 1)[0]
                return name_part
        return "someone"
    
    def _extract_task(self, text: str) -> str:
        """Extract task from reminder text"""
        if ' to ' in text:
            parts = text.split(' to ', 1)
            if len(parts) > 1:
                return parts[1]
        elif ' about ' in text:
            parts = text.split(' about ', 1)
            if len(parts) > 1:
                return parts[1]
        return "something"
    
    def _extract_query(self, text: str) -> str:
        """Extract search query"""
        for prefix in ['search for ', 'find ', 'look up ', 'google ']:
            if text.startswith(prefix):
                return text[len(prefix):]
        return text
    
    def _extract_math(self, text: str) -> str:
        """Extract math expression"""
        # Look for numbers and operators
        import re
        math_pattern = r'(\d+(?:\s*[+\-*/]\s*\d+)+)'
        match = re.search(math_pattern, text)
        if match:
            return match.group(1)
        
        # Extract after calculate/what is
        for prefix in ['calculate ', 'what is ', 'how much is ']:
            if text.startswith(prefix):
                return text[len(prefix):]
        
        return text
    
    def _detect_lang(self, text: str) -> str:
        """Simple language detection"""
        text_lower = text.lower()
        
        # Urdu indicators
        urdu_words = ['aap', 'mujhe', 'kyun', 'kya', 'hai', 'ho', 'ہے', 'کیا']
        if any(word in text_lower for word in urdu_words):
            return 'ur'
        
        # Pashto indicators  
        pashto_words = ['sta', 'kaw', 'de', 'da', 'pa', 'komak']
        if any(word in text_lower for word in pashto_words):
            return 'ps'
        
        return 'en'
    
    def _create_intent(self, action: str, target: str, confidence: float, language: str, raw_text: str) -> DirectIntent:
        """Create a DirectIntent object"""
        intent = DirectIntent(
            action=action,
            target=target,
            confidence=confidence,
            language=language,
            raw_text=raw_text
        )
        
        # Store in memory (keep last 10)
        self.conversation_memory.append(intent)
        if len(self.conversation_memory) > 10:
            self.conversation_memory.pop(0)
        
        return intent
    
    def get_conversation_summary(self) -> str:
        """Get simple conversation summary"""
        if not self.conversation_memory:
            return "No conversation yet"
        
        recent = self.conversation_memory[-3:]  # Last 3 intents
        summary = " → ".join([f"{intent.action}({intent.target})" for intent in recent])
        return summary

# Ultra-simple version for minimal usage
class QuickUnderstand:
    """Ultra-simple understanding for basic needs"""
    
    def __init__(self):
        logger.info("🔧 Quick Understand initialized")
    
    async def understand(self, text: str) -> DirectIntent:
        """Ultra-simple understanding"""
        if not text:
            return DirectIntent("chat", "user", 0.8, "en", "")
        
        clean_text = text.lower().strip()
        
        # Very basic pattern matching
        if any(word in clean_text for word in ['hello', 'hi', 'hey']):
            return DirectIntent("greet", "user", 0.95, "en", text)
        elif any(word in clean_text for word in ['weather', 'temperature']):
            return DirectIntent("get_weather", "current", 0.9, "en", text)
        elif any(word in clean_text for word in ['time', 'what time']):
            return DirectIntent("get_time", "current", 0.98, "en", text)
        elif any(word in clean_text for word in ['bye', 'exit', 'quit']):
            return DirectIntent("farewell", "user", 0.96, "en", text)
        else:
            return DirectIntent("chat", "user", 0.8, "en", text)

# Usage examples:
async def demo():
    """Demo the direct interpreter"""
    interpreter = DirectInterpreter()
    
    test_messages = [
        "hello",
        "what's the weather like?",
        "send message to John",
        "remind me to buy milk",
        "what time is it?",
        "calculate 25 + 17",
        "tell me a joke"
    ]
    
    for message in test_messages:
        intent = await interpreter.understand(message)
        print(f"'{message}' → {intent.action}({intent.target}) [{intent.confidence:.2f}]")

if __name__ == "__main__":
    asyncio.run(demo())