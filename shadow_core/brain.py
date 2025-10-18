# shadow_core/brain.py
"""
OPENAI GPT-4 BRAIN - ALWAYS ONLINE
Uses OpenAI GPT-4 for superior reasoning and conversation
"""

import logging
import asyncio
import openai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time

logger = logging.getLogger(__name__)

class ShadowBrain:
    """
    OpenAI GPT-4 Brain - Superior reasoning and conversation
    """
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.conversation_history = []
        self.max_history = 10
        self.request_timestamps = []
        self.daily_requests = 0
        self.last_reset_time = time.time()
        
        # Rate limiting (reasonable limits)
        self.requests_per_minute = 55  # Stay under 60/minute
        self.requests_per_day = 1400   # Reasonable daily limit
        
        # Model configuration - Using GPT-4
        self.model_name = "gpt-4"
        
        # Initialize OpenAI
        if self.api_key and self.api_key != 'your_openai_api_key_here':
            try:
                openai.api_key = self.api_key
                self.available = True
                logger.info(f"🎯 OpenAI GPT-4 Brain initialized - Model: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ OpenAI initialization failed: {e}")
                self.available = False
                raise Exception(f"OpenAI API failed: {e}")
        else:
            logger.error("❌ No OpenAI API key found in .env file")
            raise Exception("Missing OPENAI_API_KEY in .env file")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """
        Get response from OpenAI GPT-4 - Superior reasoning
        """
        try:
            # Check rate limits
            if not self._check_rate_limits():
                return "I've reached my API limit for now. Please try again in a minute."
            
            # Update request tracking
            current_time = time.time()
            self.request_timestamps.append(current_time)
            self.daily_requests += 1
            
            # Clean old timestamps
            two_minutes_ago = current_time - 120
            self.request_timestamps = [ts for ts in self.request_timestamps if ts > two_minutes_ago]
            
            # Get response from OpenAI GPT-4
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=0.8
                )
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Update conversation history
            last_user_message = self._get_last_user_message(messages)
            self._update_conversation_history(last_user_message, response_text)
            
            logger.info(f"🚀 OpenAI GPT-4 response (Daily: {self.daily_requests}/1400)")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return f"I'm experiencing a temporary issue with the AI service. Please try again in a moment. Error: {str(e)}"
    
    def _get_last_user_message(self, messages: List[Dict[str, str]]) -> str:
        """Extract the last user message"""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Reset daily counter if new day
        if current_time - self.last_reset_time > 86400:
            self.daily_requests = 0
            self.last_reset_time = current_time
        
        # Check daily limit
        if self.daily_requests >= self.requests_per_day:
            logger.warning("Daily limit reached")
            return False
        
        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = [ts for ts in self.request_timestamps if ts > minute_ago]
        
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning("Minute rate limit reached")
            return False
        
        return True
    
    def _update_conversation_history(self, user_message: str, ai_response: str):
        """Update conversation history"""
        self.conversation_history.append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_time = time.time()
        minute_ago = current_time - 60
        recent_requests = len([ts for ts in self.request_timestamps if ts > minute_ago])
        
        return {
            "model": self.model_name,
            "daily_requests": self.daily_requests,
            "recent_requests": recent_requests,
            "remaining_daily": max(0, self.requests_per_day - self.daily_requests),
            "remaining_minute": max(0, self.requests_per_minute - recent_requests),
            "status": "openai_gpt4_online"
        }

# Legacy fallback class for compatibility (but it should never be used)
class FallbackBrain:
    """
    LEGACY - This should not be used anymore
    Shadow AI uses OpenAI GPT-4
    """
    
    def __init__(self):
        logger.error("❌ FALLBACK BRAIN SHOULD NOT BE USED - Shadow AI uses OpenAI GPT-4")
        raise Exception("FallbackBrain should not be used. Shadow AI uses OpenAI GPT-4.")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        raise Exception("FallbackBrain should not be used. Check your OpenAI API configuration.")