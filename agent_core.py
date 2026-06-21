import streamlit as st
from groq import Groq
from config import Config
from tools import ButlerTools
from voice_engine import VoiceEngine
from memory import ButlerMemory
<<<<<<< HEAD
from planner_agent import PlannerAgent
import re
import time

class AIAgentSystem:
    """
    JARVIS AI Agent System - Core intelligence engine
    Handles: Query processing, tool routing, memory, voice, planning
    """
    
    def __init__(self):
        """Initialize all core services"""
=======
import time
import re

class AIAgentSystem:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            st.error("❌ CRITICAL: GROQ_API_KEY is missing in .env file. Please check your .env file.")
            st.stop()
            
        # Initialize Core Components
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.tools = ButlerTools()
        self.voice = VoiceEngine()
        self.memory = ButlerMemory()
<<<<<<< HEAD
        self.planner = PlannerAgent()
        
        # Tool patterns for quick detection
        self._setup_tool_patterns()
    
    def _setup_tool_patterns(self):
        """Setup regex patterns for tool detection"""
        self.TOOL_PATTERNS = {
            'time': [
                r'\bwhat time\b', r'\bcurrent time\b', r'\btime kya hai\b',
                r'\bkitne baje\b', r'\baaj ki date\b', r'\bdate kya hai\b',
                r'\btoday.*date\b', r'\bdate.*today\b'
            ],
            'weather': [
                r'\bweather\b', r'\bmausam\b', r'\btemperature outside\b',
                r'\bbaahar ka mausam\b', r'\bmousam\b', r'\bweather.*like\b'
            ],
            'search': [
                r'\bsearch for\b', r'\bgoogle this\b', r'\bfind on web\b',
                r'\bsearch\b.*\bon\b', r'\blook up\b'
            ],
            'news': [
                r'\bnews\b', r'\bkhabar\b', r'\blatest news\b',
                r'\btoday.*news\b', r'\bnews.*today\b'
            ],
            'calculator': [
                r'\bcalculate\b', r'\bcalc\b', r'\bkitna hoga\b',
                r'\bhow much\b', r'\bwhat is\b.*[\d\+\-\*\/]'
            ]
            # ✅ GMAIL REMOVED: Handled by dedicated UI tool in features.py to avoid OAuth conflicts
        }
    
    def process_query(self, user_message: str, messages: list, use_voice: bool = False, 
                      custom_prompt: str = None, voice_settings: dict = None) -> dict:
        """
        Main query processing pipeline
        Returns: {'response', 'audio_path', 'agent_used', 'model_used', 'response_time'}
        """
        result = {
            'response': '',
            'audio_path': None,
            'agent_used': 'AI',
            'model_used': 'Fast (8B)',
=======
        
    def process_query(self, user_message: str, messages: list, use_voice: bool = False, custom_prompt: str = None) -> dict:
        result = {
            'response': '', 
            'audio_path': None, 
            'agent_used': 'AI', 
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            'response_time': 0
        }
        
        start_time = time.time()
        
        try:
<<<<<<< HEAD
            # ✅ STRICT CONTEXT MANAGEMENT (Last 8 messages to avoid 413 errors)
            context_messages = messages[-8:] if len(messages) > 8 else messages
            
            # 1. Determine Complexity & Model Selection
            is_complex = self._is_complex_query(user_message)
            model = Config.SMART_MODEL if is_complex else Config.FAST_MODEL
            result['model_used'] = "Smart (70B)" if is_complex else "Fast (8B)"

            # 2. Routing Logic - Decide which agent/tool to use
            if is_complex and self._is_planning_query(user_message):
                # Use Planner Agent for complex tasks
                result['response'] = self._handle_planning(user_message, model, custom_prompt)
                result['agent_used'] = 'Planner'
            else:
                # Check for direct tool usage
                tool_res = self._check_tools_directly(user_message)
                
                if tool_res:
                    result['response'] = tool_res
                    result['agent_used'] = 'Tool'
                else:
                    # Normal AI conversation with memory
                    memories = self.memory.get_relevant_memories(user_message)
                    context = "\n".join(memories) if memories else ""
                    result['response'] = self._get_ai_response(
                        context_messages, context, model, custom_prompt
                    )

            # 3. Memory Save (Silent failure)
            try:
                self.memory.save_interaction(user_message, result['response'])
            except Exception as e:
                print(f"Memory save error: {e}")
            
            # 4. Voice Generation with Settings
            if use_voice and result['response']:
                result['audio_path'] = self._generate_voice(
                    result['response'], voice_settings
                )
                    
=======
            # 1. FAST PATH: Check if user wants a specific tool (Time, Weather, News, Calc)
            tool_result = self._check_tools(user_message)
            if tool_result:
                result['response'] = tool_result
                result['agent_used'] = 'Tool'
                result['response_time'] = round(time.time() - start_time, 2)
                # Tools don't need memory saving usually, but we can save it
                self.memory.save_interaction(user_message, tool_result)
                return result

            # 2. SLOW PATH: AI Processing
            # Keep only last 6 messages to save tokens and prevent crashes
            context_messages = messages[-6:] if len(messages) > 6 else messages
            
            # Prepare System Prompt
            system_content = custom_prompt if custom_prompt else Config.SYSTEM_PROMPT
            
            # Inject Long-Term Memory
            relevant_memories = self.memory.get_relevant_memories(user_message)
            if relevant_memories:
                system_content += "\n\n--- Relevant Past Memories ---\n" + "\n".join(relevant_memories)

            # Format messages for Groq API
            final_messages = [{"role": "system", "content": system_content}]
            for msg in context_messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    final_messages.append({"role": msg["role"], "content": msg["content"]})

            # Call Groq API
            response = self.client.chat.completions.create(
                model=Config.SMART_MODEL,
                messages=final_messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
            
            ai_text = response.choices[0].message.content
            result['response'] = ai_text
            result['agent_used'] = 'AI'

            # 3. Voice Generation (If enabled)
            if use_voice and ai_text:
                audio_path = self.voice.text_to_speech(ai_text, lang='en')
                if audio_path:
                    self.voice.play_audio(audio_path)
                    result['audio_path'] = audio_path

            # 4. Save to Memory
            self.memory.save_interaction(user_message, ai_text)
            
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            result['response_time'] = round(time.time() - start_time, 2)
            return result
            
        except Exception as e:
            return {
<<<<<<< HEAD
                'response': f"⚠️ System Error: {str(e)}",
                'audio_path': None,
                'agent_used': 'Error',
                'model_used': 'N/A',
                'response_time': round(time.time() - start_time, 2)
            }
    
    def _is_complex_query(self, message: str) -> bool:
        """Determine if query requires smart model"""
        complex_keywords = ['plan', 'schedule', 'compare', 'analyze', 'code', 'explain']
        word_count = len(message.split())
        return any(w in message.lower() for w in complex_keywords) or word_count > 15
    
    def _is_planning_query(self, message: str) -> bool:
        """Check if query needs planning agent"""
        planning_keywords = ['plan', 'schedule', 'organize', 'breakdown']
        return any(w in message.lower() for w in planning_keywords)
    
    def _handle_planning(self, user_message: str, model: str, custom_prompt: str) -> str:
        """Handle complex planning queries"""
        try:
            plan = self.planner.create_plan(user_message)
            steps = []
            
            for step in plan:
                tool_name = step.get('tool_name', 'general_chat')
                params = step.get('params', {})
                
                if tool_name == 'general_chat':
                    # AI conversation step
                    clean_msgs = [{"role": "user", "content": params.get('prompt', '')}]
                    steps.append(self._get_ai_response(clean_msgs, "", model, custom_prompt))
                else:
                    # Tool execution step
                    func = getattr(self.tools, tool_name, None)
                    if func:
                        result = func(**params) if params else func()
                        steps.append(result)
                    else:
                        steps.append(f"❌ Tool '{tool_name}' not found")
            
            return "\n\n---\n\n".join(steps)
            
        except Exception as e:
            print(f"Planner Fallback: {e}")
            # Fallback to normal AI
            return self._get_ai_response([], "", model, custom_prompt)
    
    def _generate_voice(self, text: str, voice_settings: dict = None) -> str:
        """Generate voice response with settings"""
        try:
            lang = voice_settings.get('lang', 'en') if voice_settings else 'en'
            speed = voice_settings.get('speed', 'normal') if voice_settings else 'normal'
            
            path = self.voice.text_to_speech(text, lang=lang, speed=speed)
            if path:
                self.voice.play_audio(path)
                return path
            return None
        except Exception as e:
            print(f"Voice generation error: {e}")
            return None
    
    def generate_chat_title(self, first_message: str) -> str:
        """Generate a short title for the chat"""
=======
                'response': f"⚠️ System Error: {str(e)}", 
                'audio_path': None, 
                'agent_used': 'Error', 
                'response_time': 0
            }

    def _check_tools(self, msg: str) -> str:
        """Strict tool detection to prevent false triggers"""
        m = msg.lower().strip()
        
        # Time & Date
        time_patterns = ["what time", "time kya", "kitne baje", "current time", "aaj ki date", "what's the time"]
        if any(pattern in m for pattern in time_patterns):
            return self.tools.get_time_date()
        
        # Weather (Only if explicitly asked)
        weather_patterns = ["weather", "mausam", "temperature outside", "baahar ka mausam", "is it raining"]
        if any(pattern in m for pattern in weather_patterns):
            # Default to Delhi, or we could add city extraction logic later
            return self.tools.get_weather("Delhi")
            
        # News
        if "news" in m and any(w in m for w in ["latest", "today", "headlines"]):
            return self.tools.get_news()
            
        # Calculator (Simple math)
        calc_patterns = ["calculate", "calc", "solve", "kitna hoga"]
        if any(pattern in m for pattern in calc_patterns):
            # Extract numbers and operators
            expr = re.findall(r'[\d\+\-\*\/\.\(\)]+', msg)
            if expr:
                return self.tools.calculate("".join(expr))
        
        return ""

    def generate_chat_title(self, first_message: str) -> str:
        """Generates a short title for the chat"""
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
        try:
            response = self.client.chat.completions.create(
                model=Config.FAST_MODEL,
                messages=[
<<<<<<< HEAD
                    {
                        "role": "system",
                        "content": "Generate a short 3-5 word title for this conversation. Return ONLY the title, no quotes."
                    },
                    {"role": "user", "content": first_message}
                ],
                max_tokens=20,
                temperature=0.3
            )
            title = response.choices[0].message.content.strip().replace('"', '')
            return title if title else "New Chat"
        except Exception as e:
            print(f"Title generation error: {e}")
            # Fallback: use first few words
            words = first_message.split()[:5]
            return " ".join(words) if words else "New Chat"
    
    def _check_tools_directly(self, msg: str) -> str:
        """
        Strict tool detection using regex patterns
        Prevents false triggers on normal chat
        """
        m = msg.lower().strip()
        
        # ✅ TIME/DATE
        if self._matches_pattern(m, self.TOOL_PATTERNS['time']):
            return self.tools.get_time_date()
        
        # ✅ WEATHER
        if self._matches_pattern(m, self.TOOL_PATTERNS['weather']):
            city = self._extract_city(msg)
            return self.tools.get_weather(city)
        
        # ✅ SEARCH
        if self._matches_pattern(m, self.TOOL_PATTERNS['search']):
            query = self._extract_search_query(msg)
            return self.tools.search_web(query)
        
        # ✅ NEWS
        if self._matches_pattern(m, self.TOOL_PATTERNS['news']):
            return self.tools.get_news()
        
        # ✅ CALCULATOR
        if self._matches_pattern(m, self.TOOL_PATTERNS['calculator']):
            expr = self._extract_math_expression(msg)
            if expr:
                return self.tools.calculate(expr)
        
        # ✅ GMAIL HANDLED IN FEATURES.PY (To avoid OAuth UI conflicts)
        # If user asks about email in normal chat, guide them to the tool
        if self._matches_pattern(m, [r'\bemail\b', r'\bgmail\b', r'\binbox\b']):
            return "📧 Please use the **Gmail Summarizer** tool from the sidebar to check your emails securely!"
        
        return ""
    
    def _matches_pattern(self, text: str, patterns: list) -> bool:
        """Check if text matches any regex pattern"""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def _extract_city(self, msg: str) -> str:
        """Extract city name from weather query"""
        words = msg.lower().split()
        city = "Delhi"  # Default
        
        for i, word in enumerate(words):
            if word in ["in", "of", "at", "ka", "ke", "ki"] and i+1 < len(words):
                # Check if next word looks like a city name
                next_word = words[i+1].capitalize()
                if len(next_word) > 2 and next_word.isalpha():
                    city = next_word
                    break
        
        return city
    
    def _extract_search_query(self, msg: str) -> str:
        """Extract search query from message"""
        # Remove common search phrases
        query = msg.lower()
        phrases_to_remove = [
            'search for', 'google this', 'find on web',
            'search', 'look up', 'google'
        ]
        
        for phrase in phrases_to_remove:
            query = query.replace(phrase, '')
        
        return query.strip()
    
    def _extract_math_expression(self, msg: str) -> str:
        """Extract mathematical expression from message"""
        # Find all numbers and operators
        expr_parts = re.findall(r'[\d\+\-\*\/\.\(\)]+', msg)
        if expr_parts:
            return "".join(expr_parts)
        return ""
    
    def _get_ai_response(self, messages: list, context: str, model: str, 
                         custom_prompt: str = None) -> str:
        """Get streaming AI response from Groq"""
        system_content = custom_prompt if custom_prompt else Config.SYSTEM_PROMPT
        
        # Add memory context if available
        if context:
            system_content += f"\n\nRelevant Memory:\n{context[:500]}"
        
        # Clean messages
        clean_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
            if isinstance(msg, dict) and "role" in msg
        ]
        
        final_msgs = [{"role": "system", "content": system_content}, *clean_messages]
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=final_msgs,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                stream=True
            )
            
            full_response = ""
            placeholder = st.empty()
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            return full_response
            
        except Exception as e:
            error_msg = f"⚠️ API Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        return {
            'model_fast': Config.FAST_MODEL,
            'model_smart': Config.SMART_MODEL,
            'tools_available': list(self.tools.get_available_tools().keys()),
            'memory_enabled': self.memory is not None,
            'voice_enabled': self.voice is not None,
            'planner_enabled': self.planner is not None
        }
=======
                    {"role": "system", "content": "Generate a short 3-5 word title for this conversation. Return ONLY the title."},
                    {"role": "user", "content": first_message}
                ],
                max_tokens=20
            )
            title = response.choices[0].message.content.strip().replace('"', '')
            return title if title else "New Chat"
        except:
            return first_message.split()[:4] if len(first_message.split()) > 4 else "New Chat"

            
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
