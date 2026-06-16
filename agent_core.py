import streamlit as st
from groq import Groq
from config import Config
from tools import ButlerTools
from voice_engine import VoiceEngine
from memory import ButlerMemory
import time
import re

class AIAgentSystem:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            st.error("❌ CRITICAL: GROQ_API_KEY is missing in .env file. Please check your .env file.")
            st.stop()
            
        # Initialize Core Components
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.tools = ButlerTools()
        self.voice = VoiceEngine()
        self.memory = ButlerMemory()
        
    def process_query(self, user_message: str, messages: list, use_voice: bool = False, custom_prompt: str = None) -> dict:
        result = {
            'response': '', 
            'audio_path': None, 
            'agent_used': 'AI', 
            'response_time': 0
        }
        
        start_time = time.time()
        
        try:
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
            
            result['response_time'] = round(time.time() - start_time, 2)
            return result
            
        except Exception as e:
            return {
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
        try:
            response = self.client.chat.completions.create(
                model=Config.FAST_MODEL,
                messages=[
                    {"role": "system", "content": "Generate a short 3-5 word title for this conversation. Return ONLY the title."},
                    {"role": "user", "content": first_message}
                ],
                max_tokens=20
            )
            title = response.choices[0].message.content.strip().replace('"', '')
            return title if title else "New Chat"
        except:
            return first_message.split()[:4] if len(first_message.split()) > 4 else "New Chat"

            