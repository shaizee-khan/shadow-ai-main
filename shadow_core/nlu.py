# shadow_core/nlu.py
"""
Simplified but Stronger NLU (Natural Language Understanding) system for Shadow AI
Fast, reliable intent recognition with improved pattern matching
"""

import logging
import re
import asyncio
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IntentResult:
    """Structured result from intent classification"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    original_text: str

class NLU:
    """
    Stronger NLU system with enhanced pattern matching and entity extraction
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.patterns = self._initialize_enhanced_patterns()
        logger.info("🚀 Stronger NLU system initialized")
    
    def _initialize_enhanced_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize enhanced patterns for better intent recognition"""
        
        patterns = {
            "send_message": [
                {
                    "pattern": r"(?:send|text|message)\s+(?:to\s+)?(\w+)(?:\s+on\s+(whatsapp|sms|telegram))?(?:\s+(.+))?",
                    "groups": ["contact", "platform", "message"]
                },
                {
                    "pattern": r"whatsapp\s+(?:to\s+)?(\w+)(?:\s+(.+))?",
                    "groups": ["contact", "message"]
                },
                {
                    "pattern": r"message\s+(\w+)\s+(.+)",
                    "groups": ["contact", "message"]
                }
            ],
            
            "get_weather": [
                {
                    "pattern": r"(?:weather|forecast|temperature)(?:\s+in\s+|\s+for\s+)?([\w\s]+)?",
                    "groups": ["location"]
                },
                {
                    "pattern": r"(?:how's|what's)\s+the\s+weather(?:\s+in\s+([\w\s]+))?",
                    "groups": ["location"]
                },
                {
                    "pattern": r"is it\s+(?:raining|sunny|cold|hot)(?:\s+in\s+([\w\s]+))?",
                    "groups": ["location"]
                }
            ],
            
            "get_stock": [
                {
                    "pattern": r"(?:stock|share|price)\s+(?:of\s+)?([A-Z]{1,5})",
                    "groups": ["symbol"]
                },
                {
                    "pattern": r"how much is\s+([A-Z]{1,5})\s+(?:stock|share)",
                    "groups": ["symbol"]
                },
                {
                    "pattern": r"([A-Z]{1,5})\s+(?:stock|price)",
                    "groups": ["symbol"]
                }
            ],
            
            "search_web": [
                {
                    "pattern": r"(?:search|look up|find|google)\s+(.+)",
                    "groups": ["query"]
                },
                {
                    "pattern": r"what is\s+(.+)",
                    "groups": ["query"]
                },
                {
                    "pattern": r"tell me about\s+(.+)",
                    "groups": ["query"]
                },
                {
                    "pattern": r"information about\s+(.+)",
                    "groups": ["query"]
                }
            ],
            
            "set_reminder": [
                {
                    "pattern": r"(?:remind|set reminder)\s+(?:me\s+)?(?:to\s+)?(.+?)\s+(?:in\s+)?(\d+)\s*(minute|min|hour|hr)s?",
                    "groups": ["message", "duration", "unit"]
                },
                {
                    "pattern": r"set timer for\s+(\d+)\s*(minute|min|hour|hr|second|sec)s?",
                    "groups": ["duration", "unit"]
                },
                {
                    "pattern": r"alarm for\s+(.+) at\s+(\d+:\d+\s*(?:am|pm)?)",
                    "groups": ["message", "time"]
                }
            ],
            
            "get_time": [
                {
                    "pattern": r"(?:what'?s?|tell me)\s+(?:the\s+)?time(?:\s+now)?",
                    "groups": []
                },
                {
                    "pattern": r"current time",
                    "groups": []
                },
                {
                    "pattern": r"time please",
                    "groups": []
                }
            ],
            
            "get_date": [
                {
                    "pattern": r"(?:what'?s?|tell me)\s+(?:the\s+)?date(?:\s+today)?",
                    "groups": []
                },
                {
                    "pattern": r"today'?s? date",
                    "groups": []
                },
                {
                    "pattern": r"current date",
                    "groups": []
                }
            ],
            
            "calculation": [
                {
                    "pattern": r"(?:calculate|what is|how much is)\s+(.+)",
                    "groups": ["expression"]
                },
                {
                    "pattern": r"(\d+(?:\s*[+\-*/]\s*\d+)+)",
                    "groups": ["expression"]
                }
            ],
            
            "joke": [
                {
                    "pattern": r"(?:tell|say)\s+(?:me\s+)?a? joke",
                    "groups": []
                },
                {
                    "pattern": r"make me laugh",
                    "groups": []
                },
                {
                    "pattern": r"funny joke",
                    "groups": []
                }
            ],
            
            "fact": [
                {
                    "pattern": r"(?:tell|give)\s+(?:me\s+)?a? fact(?:\s+about\s+(.+))?",
                    "groups": ["topic"]
                },
                {
                    "pattern": r"interesting fact(?:\s+about\s+(.+))?",
                    "groups": ["topic"]
                }
            ],
            
            "greeting": [
                {
                    "pattern": r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening)",
                    "groups": ["type"]
                },
                {
                    "pattern": r"how are you",
                    "groups": []
                }
            ],
            
            "farewell": [
                {
                    "pattern": r"^(bye|goodbye|see you|farewell|quit|exit)",
                    "groups": []
                }
            ],
            
            "help": [
                {
                    "pattern": r"help(?:\s+me)?",
                    "groups": []
                },
                {
                    "pattern": r"what can you do",
                    "groups": []
                },
                {
                    "pattern": r"show commands",
                    "groups": []
                }
            ]
        }
        return patterns

    async def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Stronger intent classification with improved accuracy
        Returns: (intent, entities)
        """
        if not text or not text.strip():
            return "chat", {}

        text_lower = text.lower().strip()
        original_text = text.strip()

        # Step 1: Quick high-confidence pattern matching
        quick_result = self._quick_pattern_match(text_lower, original_text)
        if quick_result.confidence >= 0.9:
            logger.info(f"🎯 NLU Quick Match: {quick_result.intent} ({quick_result.confidence:.2f})")
            return quick_result.intent, quick_result.entities

        # Step 2: Enhanced pattern matching
        pattern_result = self._enhanced_pattern_matching(text_lower, original_text)
        if pattern_result.confidence >= 0.7:
            logger.info(f"🎯 NLU Pattern Match: {pattern_result.intent} ({pattern_result.confidence:.2f})")
            return pattern_result.intent, pattern_result.entities

        # Step 3: Contextual keyword analysis
        keyword_result = self._contextual_keyword_analysis(text_lower, original_text)
        if keyword_result.confidence >= 0.6:
            logger.info(f"🎯 NLU Keyword Match: {keyword_result.intent} ({keyword_result.confidence:.2f})")
            return keyword_result.intent, keyword_result.entities

        # Step 4: AI fallback (if available)
        if self.brain:
            ai_result = await self._ai_fallback_classification(text)
            if ai_result.confidence >= 0.7:
                logger.info(f"🎯 NLU AI Match: {ai_result.intent} ({ai_result.confidence:.2f})")
                return ai_result.intent, ai_result.entities

        # Default to chat
        logger.info("💬 NLU Default: chat")
        return "chat", {}

    def _quick_pattern_match(self, text_lower: str, original_text: str) -> IntentResult:
        """Quick high-confidence pattern matching for common intents"""
        
        # Greetings (high confidence)
        if re.match(r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening)', text_lower):
            return IntentResult("greeting", 0.95, {"type": "greeting"}, original_text)
        
        # Farewells (high confidence)
        if re.match(r'^(bye|goodbye|see you|farewell|quit|exit)', text_lower):
            return IntentResult("farewell", 0.95, {}, original_text)
        
        # Time queries
        if re.match(r'^(what time|current time|time please|tell me the time)', text_lower):
            return IntentResult("get_time", 0.9, {}, original_text)
        
        # Date queries
        if re.match(r'^(what date|today\'s date|current date|tell me the date)', text_lower):
            return IntentResult("get_date", 0.9, {}, original_text)
        
        # Help requests
        if re.match(r'^(help|what can you do|show commands)', text_lower):
            return IntentResult("help", 0.9, {}, original_text)
        
        return IntentResult("unknown", 0.0, {}, original_text)

    def _enhanced_pattern_matching(self, text_lower: str, original_text: str) -> IntentResult:
        """Enhanced pattern matching with better entity extraction"""
        best_match = None
        highest_confidence = 0.0
        
        for intent, patterns in self.patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                groups = pattern_info["groups"]
                
                match = re.search(pattern, text_lower)
                if match:
                    confidence = self._calculate_enhanced_confidence(match, text_lower, intent)
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        entities = self._extract_enhanced_entities(match, groups, original_text, intent)
                        best_match = IntentResult(intent, confidence, entities, original_text)
        
        if best_match and highest_confidence >= 0.7:
            return best_match
        
        return IntentResult("chat", 0.0, {}, original_text)

    def _contextual_keyword_analysis(self, text_lower: str, original_text: str) -> IntentResult:
        """Contextual keyword analysis with weighted scoring"""
        
        keyword_weights = {
            "send_message": {
                "send": 3, "message": 3, "whatsapp": 4, "text": 2, "sms": 3, "telegram": 3
            },
            "get_weather": {
                "weather": 4, "temperature": 3, "forecast": 3, "rain": 2, "sunny": 2, "cloudy": 2
            },
            "get_stock": {
                "stock": 4, "price": 3, "share": 3, "crypto": 3, "bitcoin": 3, "ethereum": 3
            },
            "search_web": {
                "search": 3, "google": 3, "look up": 4, "find": 2, "information": 2, "what is": 3
            },
            "set_reminder": {
                "remind": 4, "reminder": 4, "timer": 3, "alarm": 3, "schedule": 2
            },
            "calculation": {
                "calculate": 4, "math": 3, "what is": 2, "how much": 2, "+": 1, "-": 1, "*": 1, "/": 1
            },
            "joke": {
                "joke": 4, "funny": 3, "laugh": 2, "humor": 2
            },
            "fact": {
                "fact": 4, "interesting": 2, "did you know": 3
            }
        }
        
        intent_scores = {}
        
        for intent, keywords in keyword_weights.items():
            score = 0
            total_weight = sum(keywords.values())
            
            for keyword, weight in keywords.items():
                if keyword in text_lower:
                    score += weight
            
            if score > 0:
                # Normalize and apply confidence curve
                normalized_score = score / total_weight
                confidence = min(normalized_score * 1.5, 1.0)  # Boost confidence
                intent_scores[intent] = confidence
        
        if intent_scores:
            best_intent, confidence = max(intent_scores.items(), key=lambda x: x[1])
            entities = self._extract_entities_from_context(best_intent, text_lower, original_text)
            return IntentResult(best_intent, confidence, entities, original_text)
        
        return IntentResult("chat", 0.0, {}, original_text)

    async def _ai_fallback_classification(self, text: str) -> IntentResult:
        """AI-powered classification fallback"""
        try:
            if not self.brain:
                return IntentResult("chat", 0.5, {}, text)
            
            prompt = f"""
            Analyze this user query and classify the intent. Be concise.
            
            Query: "{text}"
            
            Respond with ONLY the intent name from this list:
            - send_message (sending messages)
            - get_weather (weather queries)
            - get_stock (stock prices)
            - search_web (web searches)
            - set_reminder (reminders/timers)
            - get_time (current time)
            - get_date (current date)
            - calculation (math calculations)
            - joke (tell a joke)
            - fact (share a fact)
            - greeting (hello/hi)
            - farewell (goodbye)
            - help (help request)
            - chat (general conversation)
            
            Intent:
            """
            
            response = await self.brain.ask([{"role": "user", "content": prompt}])
            intent = response.strip().lower()
            
            # Validate intent
            valid_intents = self.get_supported_intents()
            if intent in valid_intents:
                return IntentResult(intent, 0.8, {}, text)
            else:
                return IntentResult("chat", 0.7, {}, text)
                
        except Exception as e:
            logger.error(f"❌ AI classification error: {e}")
            return IntentResult("chat", 0.5, {}, text)

    def _calculate_enhanced_confidence(self, match: re.Match, text: str, intent: str) -> float:
        """Calculate enhanced confidence score"""
        match_length = match.end() - match.start()
        text_length = len(text)
        
        coverage = match_length / text_length
        
        # Base confidence on coverage
        if coverage > 0.9:
            base_confidence = 0.95
        elif coverage > 0.7:
            base_confidence = 0.85
        elif coverage > 0.5:
            base_confidence = 0.75
        else:
            base_confidence = 0.65
        
        # Boost for specific high-confidence intents
        high_confidence_intents = ["get_time", "get_date", "greeting", "farewell", "help"]
        if intent in high_confidence_intents:
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        return base_confidence

    def _extract_enhanced_entities(self, match: re.Match, groups: List[str], original_text: str, intent: str) -> Dict[str, Any]:
        """Extract enhanced entities with context awareness"""
        entities = {}
        
        # Extract from match groups
        for i, group_name in enumerate(groups, 1):
            if i <= len(match.groups()):
                value = match.group(i)
                if value and value.strip():
                    entities[group_name] = value.strip()
        
        # Intent-specific entity enhancement
        entities.update(self._enhance_entities_by_intent(intent, original_text, entities))
        
        return entities

    def _extract_entities_from_context(self, intent: str, text_lower: str, original_text: str) -> Dict[str, Any]:
        """Extract entities based on intent context"""
        entities = {}
        
        if intent == "send_message":
            # Extract contact and message
            if "to" in text_lower:
                parts = text_lower.split("to", 1)
                if len(parts) > 1:
                    contact_part = parts[1].strip()
                    contact_match = re.match(r'^(\w+)', contact_part)
                    if contact_match:
                        entities["contact"] = contact_match.group(1)
            
            # Extract platform
            if "whatsapp" in text_lower:
                entities["platform"] = "whatsapp"
            elif "sms" in text_lower:
                entities["platform"] = "sms"
            elif "telegram" in text_lower:
                entities["platform"] = "telegram"
            else:
                entities["platform"] = "whatsapp"  # default
        
        elif intent == "get_weather":
            # Extract location using multiple patterns
            location_patterns = [
                r'in\s+([\w\s]+)',
                r'for\s+([\w\s]+)',
                r'at\s+([\w\s]+)'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities["location"] = match.group(1).strip()
                    break
            else:
                entities["location"] = "current location"
        
        elif intent == "calculation":
            # Extract math expression
            math_patterns = [
                r'calculate\s+(.+)',
                r'what is\s+(.+)',
                r'how much is\s+(.+)',
                r'(\d+(?:\s*[+\-*/]\s*\d+)+)'
            ]
            
            for pattern in math_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities["expression"] = match.group(1).strip()
                    break
        
        return entities

    def _enhance_entities_by_intent(self, intent: str, original_text: str, current_entities: Dict) -> Dict[str, Any]:
        """Enhance entities based on specific intent patterns"""
        enhanced = {}
        
        if intent == "set_reminder" and "message" not in current_entities:
            # Try to extract reminder message
            message_patterns = [
                r'remind me to (.+?) in',
                r'reminder for (.+?) at',
                r'set reminder for (.+)'
            ]
            
            for pattern in message_patterns:
                match = re.search(pattern, original_text.lower())
                if match:
                    enhanced["message"] = match.group(1).strip()
                    break
        
        return enhanced

    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        return list(self.patterns.keys()) + ["chat"]

    def get_intent_description(self, intent: str) -> str:
        """Get description of an intent"""
        descriptions = {
            "send_message": "Send messages via WhatsApp/SMS/Telegram",
            "get_weather": "Get weather information for locations",
            "get_stock": "Get stock and cryptocurrency prices",
            "search_web": "Search the web for information",
            "set_reminder": "Set reminders, timers, and alarms",
            "get_time": "Get current time",
            "get_date": "Get current date",
            "calculation": "Perform mathematical calculations",
            "joke": "Tell jokes and funny stories",
            "fact": "Share interesting facts",
            "greeting": "Greet the user",
            "farewell": "Say goodbye",
            "help": "Provide help information",
            "chat": "General conversation"
        }
        return descriptions.get(intent, "General conversation")


# Ultra-simple NLU for minimal dependency
class SimpleNLU:
    """Ultra-simple NLU for basic usage"""
    
    def __init__(self):
        self.patterns = {
            "greeting": [r'hi|hello|hey|greetings'],
            "farewell": [r'bye|goodbye|see you|exit|quit'],
            "get_time": [r'time|what time|current time'],
            "get_date": [r'date|what date|today'],
            "help": [r'help|what can you do']
        }
        logger.info("🔧 Simple NLU initialized")
    
    async def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Ultra-simple classification"""
        if not text:
            return "chat", {}
            
        text_lower = text.lower().strip()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent, {}
        
        return "chat", {}