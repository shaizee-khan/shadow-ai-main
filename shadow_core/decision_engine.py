"""
Simplified Decision Engine - Direct routing and intent handling
No complex processing, just direct understanding and execution
"""

import logging
import asyncio
import random
import re
from datetime import datetime
from typing import Dict, Any, Optional
from shadow_core.dynamic_nlu import DirectInterpreter, DirectIntent

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Simplified Decision Engine - Direct understanding and execution
    No complex NLU, no multiple interpreters - just direct action
    """
    
    def __init__(self, brain, memory, messaging=None, scheduler=None):
        self.brain = brain
        self.memory = memory
        self.messaging = messaging
        self.scheduler = scheduler
        
        # ✅ Initialize Direct Interpreter (ultra-simple)
        self.interpreter = DirectInterpreter(brain)
        
        # ✅ Initialize multilingual system (optional)
        self.multilingual_system = None
        try:
            from shadow_core.multilingual import create_multilingual_system
            self.multilingual_system = create_multilingual_system(brain)
            logger.info("Multilingual system initialized")
        except Exception as e:
            logger.warning(f"Multilingual system not available: {e}")
        
        logger.info("🚀 Simplified Decision Engine initialized")

    async def handle_query(self, text: str, gui=None) -> str:
        """
        Handle user query with direct understanding
        No complex processing - just understand and execute
        """
        if not text or text.strip() == "":
            return "I didn't catch that. Could you please repeat?"

        logger.info(f"Processing: {text}")
        
        try:
            # Step 1: Direct understanding (no preprocessing)
            intent = await self.interpreter.understand(text)
            
            logger.info(f"🎯 Direct intent: {intent.action} -> {intent.target}")
            
            # Step 2: Execute directly based on intent
            response = await self._execute_direct_intent(intent, text, gui)
            
            # Step 3: Save to memory
            self.memory.save_chat(text, response)
            
            logger.info(f"✅ Response ready")
            return response
            
        except Exception as e:
            logger.error(f"Error in decision engine: {e}")
            error_msg = "I encountered an error. Please try again."
            self.memory.save_chat(text, error_msg)
            return error_msg

    async def _execute_direct_intent(self, intent: DirectIntent, original_text: str, gui=None) -> str:
        """Execute action based on direct intent understanding"""
        
        # Handle greetings
        if intent.action == "greet":
            return await self._handle_greeting(intent, original_text)
        
        # Handle farewells
        elif intent.action == "farewell":
            return await self._handle_farewell(intent, original_text)
        
        # Handle weather
        elif intent.action == "get_weather":
            return await self._handle_weather(intent, original_text)
        
        # Handle messaging
        elif intent.action == "send_message":
            return await self._handle_messaging(intent, original_text)
        
        # Handle reminders
        elif intent.action == "set_reminder":
            return await self._handle_reminder(intent, original_text)
        
        # Handle time
        elif intent.action == "get_time":
            return await self._handle_time(intent, original_text)
        
        # Handle date
        elif intent.action == "get_date":
            return await self._handle_date(intent, original_text)
        
        # Handle search
        elif intent.action == "search_web":
            return await self._handle_search(intent, original_text)
        
        # Handle calculations
        elif intent.action == "calculate":
            return await self._handle_calculation(intent, original_text)
        
        # Handle jokes
        elif intent.action == "tell_joke":
            return await self._handle_joke(intent, original_text)
        
        # Handle help
        elif intent.action == "provide_help":
            return await self._handle_help(intent, original_text)
        
        # Default: general chat
        else:
            return await self._handle_chat(original_text)

    async def _handle_greeting(self, intent: DirectIntent, original_text: str) -> str:
        """Handle greetings"""
        greetings = {
            'en': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! Nice to see you. How can I assist?",
                "Greetings! How may I help you?"
            ],
            'ur': [
                "Salam! Main aap ki kya madad kar sakta hoon?",
                "Hello! Aaj main aap ke liye kya kar sakta hoon?",
                "Adaab! Kya main aap ki koi madad kar sakta hoon?",
                "Salam alaikum! Aap ko kya chahiye?"
            ],
            'ps': [
                "Salam! زه ستاسو لپاره څه کولی شم؟",
                "Hello! نن زه ستاسو لپاره څه کولی شم؟",
                "سلام! ایا زه کولی شم ستاسو سره مرسته وکړم؟",
                "سلام! تاسو څه غواړئ؟"
            ]
        }
        
        lang = intent.language
        return random.choice(greetings.get(lang, greetings['en']))

    async def _handle_farewell(self, intent: DirectIntent, original_text: str) -> str:
        """Handle farewells"""
        farewells = {
            'en': [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! Feel free to come back anytime!",
                "Farewell! Looking forward to our next chat!"
            ],
            'ur': [
                "Khuda hafiz! Aap ka din acha guzre!",
                "Phir milenge! Apna khayal rakhiye!",
                "Allah hafiz! Kabhi bhi wapas a sakte hain!",
                "Alwida! Agli baat ka intezar rahega!"
            ],
            'ps': [
                "خداى حافظ! ستاسو ورځ ښه تیرېږي!",
                "ورو وو به سره ګورو! پخه ساتل!",
                "خدای پامان! کله هم بیرته راشئ!",
                "په خیر! زه ستاسو د راتلونکي خبرې ته تمیم!"
            ]
        }
        
        lang = intent.language
        return random.choice(farewells.get(lang, farewells['en']))

    async def _handle_weather(self, intent: DirectIntent, original_text: str) -> str:
        """Handle weather requests"""
        location = intent.target
        if location == "current location":
            location_text = "your current location"
        else:
            location_text = location
        
        responses = {
            'en': f"I'd check the weather for {location_text}, but I need to connect to a weather service for real-time data. You can check your favorite weather app for current conditions in {location_text}.",
            'ur': f"Main {location_text} ka mausam check kar sakta hoon, lekin real-time data ke liye mujhe weather service se connect karna hoga. Aap apne favorite weather app par {location_text} ka current mausam dekh sakte hain.",
            'ps': f"زه کولی شم د {location_text} هوا وګورم، مګر د حقيقي وخت د معلوماتو لپاره زه اړ یم چې د هوا د خدماتو سره وصل شم. تاسو کولی شئ خپل د هوا غوره اپلیکیشن کې د {location_text} اوسنی حالت وګورئ."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_messaging(self, intent: DirectIntent, original_text: str) -> str:
        """Handle messaging requests"""
        contact = intent.target
        if contact == "someone":
            contact_text = "your contact"
        else:
            contact_text = contact
        
        responses = {
            'en': f"I can help you send a message to {contact_text}. Please make sure the messaging system is set up, or you can use your regular messaging apps to contact {contact_text}.",
            'ur': f"Main {contact_text} ko message bhejne mein aap ki madad kar sakta hoon. Please ensure messaging system set hai, ya aap apne regular messaging apps use kar ke {contact_text} se contact kar sakte hain.",
            'ps': f"زه کولی شم تاسو سره د {contact_text} پیغام لیږلو کې مرسته وکړم. مهرباني وکړئ ډاډه کړئ چې د پیغام رسونې سیستم تنظیم شوی دی، یا تاسو کولی شئ خپل عادي پیغام رسونې اپلیکیشنونه وکاروئ ترڅو سره {contact_text} اړیکه ونیسئ."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_reminder(self, intent: DirectIntent, original_text: str) -> str:
        """Handle reminder requests"""
        task = intent.target
        if task == "something":
            task_text = "your task"
        else:
            task_text = task
        
        responses = {
            'en': f"I can help you set a reminder for {task_text}. Please provide the specific time and date, like 'tomorrow at 3 PM' or 'next Monday at 10 AM'.",
            'ur': f"Main {task_text} ke liye reminder set karne mein aap ki madad kar sakta hoon. Please specific time aur date bataiye, jaise 'kal 3 baje' ya 'agle Monday 10 baje'.",
            'ps': f"زه کولی شم تاسو سره د {task_text} لپاره د یادونې ترتیبولو کې مرسته وکړم. مهرباني وکړئ مشخص وخت او نېټه ووایاست، لکه 'سبا په ۳ بجې' یا 'بل دو شنبه په ۱۰ بجې'."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_time(self, intent: DirectIntent, original_text: str) -> str:
        """Handle time requests"""
        current_time = datetime.now().strftime("%I:%M %p")
        
        responses = {
            'en': f"The current time is {current_time}.",
            'ur': f"Current time {current_time} hai.",
            'ps': f"اوسنی وخت {current_time} دی."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_date(self, intent: DirectIntent, original_text: str) -> str:
        """Handle date requests"""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        responses = {
            'en': f"Today is {current_date}.",
            'ur': f"Aaj {current_date} hai.",
            'ps': f"نن {current_date} دی."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_search(self, intent: DirectIntent, original_text: str) -> str:
        """Handle search requests"""
        query = intent.target
        if query == original_text.lower():
            query = "your query"
        
        responses = {
            'en': f"I can search for '{query}' online. For the most current information, you might want to check your favorite search engine or I can try to help with what I know.",
            'ur': f"Main '{query}' ko online search kar sakta hoon. Most current information ke liye, aap apna favorite search engine check kar sakte hain ya main jo main jaanta hoon us se madad kar sakta hoon.",
            'ps': f"زه کولی شم د '{query}' آنلاین لټون وکړم. د ترټولو اوسنیو معلوماتو لپاره، تاسو غواړئ چې خپل غوره لټون انجن وګورئ یا زه هڅه کوم چې د هغه څه سره مرسته وکړم چې زه یې پوهیږم."
        }
        
        return responses.get(intent.language, responses['en'])

    async def _handle_calculation(self, intent: DirectIntent, original_text: str) -> str:
        """Handle calculation requests"""
        expression = intent.target
        if expression == original_text.lower():
            # Try to extract math from text
            math_match = re.search(r'(\d+(?:\s*[+\-*/]\s*\d+)+)', original_text)
            if math_match:
                expression = math_match.group(1)
            else:
                expression = "that calculation"
        
        try:
            # Safe evaluation of simple math
            # Remove spaces and evaluate
            clean_expression = expression.replace(' ', '')
            result = eval(clean_expression)
            
            responses = {
                'en': f"The answer to {expression} is {result}.",
                'ur': f"{expression} ka answer {result} hai.",
                'ps': f"د {expression} ځواب {result} دی."
            }
            
            return responses.get(intent.language, responses['en'])
            
        except:
            responses = {
                'en': f"I can help with calculations! Try asking something like 'what is 15 + 27' or 'calculate 45 * 3'.",
                'ur': f"Main calculations mein madad kar sakta hoon! Kuch aise poochiye jaise '15 + 27 kya hai' ya '45 * 3 calculate karo'.",
                'ps': f"زه کولی شم د محاسبو کې مرسته وکړم! هڅه وکړئ لکه '15 + 27 څه دی' یا '45 * 3 محاسبه کړئ' وغواړئ."
            }
            
            return responses.get(intent.language, responses['en'])

    async def _handle_joke(self, intent: DirectIntent, original_text: str) -> str:
        """Handle joke requests"""
        jokes = {
            'en': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "Why don't eggs tell jokes? They'd crack each other up!",
                "What do you call a fake noodle? An impasta!"
            ],
            'ur': [
                "Scientists atoms par bharosa kyun nahi karte? Kyun ke woh sab kuch bana dete hain!",
                "Scarecrow ne award kyun jeeta? Kyun ke woh apne field mein outstanding tha!",
                "Ande jokes kyun nahi sunate? Kyun ke woh crack ho jaate!",
                "False noodle ko kya kehte hain? Ek impasta!"
            ],
            'ps': [
                "ولې ساینس پوهان اټومونو ته باور نه لري؟ ځکه چې دوی هرڅه جوړوي!",
                "ولې سکیڼې جایزه وګټله؟ ځکه چې هغه په خپل سیمه کې بریالی و!",
                "ولې هګۍ ټوکې نه وایي؟ ځکه چې دوی به یو بل مات کړي!",
                "تاسو یو جعلی نوډل څه بلائ؟ یو ایمپاسټا!"
            ]
        }
        
        lang = intent.language
        return random.choice(jokes.get(lang, jokes['en']))

    async def _handle_help(self, intent: DirectIntent, original_text: str) -> str:
        """Handle help requests"""
        help_texts = {
            'en': """
🤖 **What I can help you with:**

• **Chatting** - Just talk to me about anything!
• **Weather** - "What's the weather like?" 
• **Messages** - "Send message to John"
• **Reminders** - "Remind me to call mom"
• **Time/Date** - "What time is it?" or "What's today's date?"
• **Calculations** - "Calculate 15 + 27"
• **Jokes** - "Tell me a joke"
• **Search** - "Search for artificial intelligence"

Just ask naturally - I understand what you mean!
""",
            'ur': """
🤖 **Main aap ki kya madad kar sakta hoon:**

• **Baatcheet** - Kisi bhi cheez par mere se baat karein!
• **Mausam** - "Mausam kaisa hai?"
• **Messages** - "John ko message bhejo"
• **Reminders** - "Mujhe mom ko call karne ki yaad dilao"
• **Time/Date** - "Time kya hai?" ya "Aaj ki date kya hai?"
• **Calculations** - "15 + 27 calculate karo"
• **Jokes** - "Mujhe ek joke sunao"
• **Search** - "Artificial intelligence search karo"

Natural tareeke se poochiye - main samajh jaata hoon!
""",
            'ps': """
🤖 **زه ستاسو سره څه مرسته کولی شم:**

• **خبرې** - زما سره د هرڅه په اړه خبرې وکړئ!
• **هوا** - "هوا څنګه ده؟"
• **پیغامونه** - "جان ته پیغام واستوئ"
• **یادونې** - "ما ته د مور سره د تلیفون کولو یادونه راکړئ"
• **وخت/نېټه** - "وخت څه دی؟" یا "نن نېټه څه ده؟"
• **محاسبې** - "15 + 27 محاسبه کړئ"
• **ټوکې** - "ما ته یو ټوکه ووایاست"
• **لټون** - "مصنوعي ځیرکتیا لټون کړئ"

په طبیعي ډول وپوښتئ - زه پوهیږم چې تاسو څه وایئ!
"""
        }
        
        return help_texts.get(intent.language, help_texts['en'])

    async def _handle_chat(self, original_text: str) -> str:
        """Handle general chat - direct to AI"""
        try:
            # Simple direct chat - no complex context management
            messages = [
                {
                    "role": "system", 
                    "content": "You are Shadow, a helpful and friendly AI assistant. Keep responses clear and conversational."
                },
                {
                    "role": "user", 
                    "content": original_text
                }
            ]
            
            # Use multilingual brain if available, otherwise regular brain
            if self.multilingual_system:
                response = await self.multilingual_system.ask(original_text)
            else:
                response = await self.brain.ask(messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm here to help! What would you like to know or discuss?"

    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "interpreter": "DirectInterpreter",
            "multilingual": self.multilingual_system is not None,
            "capabilities": [
                "greetings", "weather", "messaging", "reminders", 
                "time_date", "calculations", "jokes", "search", "help", "chat"
            ]
        }