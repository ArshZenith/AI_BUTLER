import streamlit as st
from groq import Groq
from config import Config
from tools import ButlerTools
from voice_engine import VoiceEngine
from memory import ButlerMemory
import json
import re
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIButler:
    """Integrated AI Butler with Smart Tool Usage & Memory"""
    
    def __init__(self):
        if not Config.GROQ_API_KEY:
            st.error("❌ CRITICAL: GROQ_API_KEY is missing in .env file.")
            st.stop()
            
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.tools = ButlerTools()
        self.voice = VoiceEngine()
        self.memory = ButlerMemory()
        
        # Define available tools for AI (matches ButlerTools methods)
        self.available_tools = {
            "get_weather": "Get current weather for a city (params: city)",
            "search_web": "Search the internet for information (params: query)",
            "get_news": "Get latest news updates (no params)",
            "calculate": "Perform mathematical calculations (params: expression)",
            "get_time_date": "Get current time and date (no params)"
        }
        
        logger.info("✅ AIButler initialized successfully")
    
    def process_query(self, user_message: str, messages: list, use_voice: bool = False, 
                      custom_prompt: str = None, voice_settings: dict = None) -> dict:
        """Main processing function with integrated tool usage"""
        result = {
            'response': '', 
            'audio_path': None, 
            'tool_used': None,
            'response_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Check if AI wants to use a tool
            tool_call = self._detect_tool_intent(user_message)
            
            if tool_call:
                # Execute the tool
                tool_result = self._execute_tool(tool_call, user_message)
                result['response'] = tool_result
                result['tool_used'] = tool_call['name']
                result['model_used'] = "Tool"
            else:
                # Normal AI conversation with memory
                memories = self.memory.get_relevant_memories(user_message)
                context = "\n".join(memories) if memories else ""
                
                # Limit context to last 8 messages
                context_messages = messages[-8:] if len(messages) > 8 else messages
                
                result['response'] = self._get_ai_response(
                    context_messages, 
                    context, 
                    custom_prompt
                )
                result['model_used'] = Config.MODEL_ID
            
            # Step 2: Save to memory (silent failure)
            try:
                self.memory.save_interaction(user_message, result['response'])
            except Exception as e:
                logger.warning(f"Memory save error: {e}")
            
            # Step 3: Generate voice if enabled
            if use_voice and result['response']:
                lang = voice_settings.get('lang', 'en') if voice_settings else 'en'
                speed = voice_settings.get('speed', 'normal') if voice_settings else 'normal'
                result['audio_path'] = self.voice.text_to_speech(
                    result['response'], 
                    lang=lang, 
                    speed=speed
                )
            
            result['response_time'] = round(time.time() - start_time, 2)
            logger.info(f"Query processed in {result['response_time']}s using {result['tool_used'] or 'AI'}")
            return result
            
        except Exception as e:
            logger.error(f"Process query error: {e}")
            return {
                'response': f"⚠️ System Error: {str(e)}", 
                'audio_path': None, 
                'tool_used': None,
                'response_time': round(time.time() - start_time, 2)
            }

    def _detect_tool_intent(self, user_message: str) -> dict:
        """Detect if user wants to use a tool using AI"""
        try:
            # Ask AI to decide if a tool is needed
            decision_prompt = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast model for decision making
                messages=[
                    {"role": "system", "content": self._get_tool_decision_system()},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=200
            )
            
            decision = decision_prompt.choices[0].message.content.strip()
            
            # Parse the decision
            if "TOOL_NEEDED" in decision:
                # Extract tool name and parameters
                lines = decision.split('\n')
                tool_name = None
                params = {}
                
                for line in lines:
                    if line.startswith("tool:"):
                        tool_name = line.replace("tool:", "").strip()
                    elif ":" in line and not line.startswith("reason:") and not line.startswith("TOOL"):
                        key, value = line.split(":", 1)
                        params[key.strip()] = value.strip()
                
                if tool_name and tool_name in self.available_tools:
                    return {"name": tool_name, "params": params}
            
            return None
            
        except Exception as e:
            logger.error(f"Tool detection error: {e}")
            return None

    def _execute_tool(self, tool_call: dict, user_message: str) -> str:
        """Execute the detected tool using ButlerTools"""
        tool_name = tool_call['name']
        params = tool_call['params']
        
        try:
            # Map tool names to ButlerTools methods
            if tool_name == "get_weather":
                city = params.get('city', 'Delhi')
                return self.tools.get_weather(city)
                
            elif tool_name == "search_web":
                query = params.get('query', user_message)
                return self.tools.search_web(query)
                
            elif tool_name == "get_news":
                return self.tools.get_news()
                
            elif tool_name == "calculate":
                # Extract expression from message or params
                expr = params.get('expression', user_message)
                numbers = re.findall(r'[\d\.\+\-\*\/\(\)]+', expr)
                if numbers:
                    return self.tools.calculate("".join(numbers))
                return "Please provide a mathematical expression to calculate."
                
            elif tool_name == "get_time_date":
                return self.tools.get_time_date()
            
            return f"Tool '{tool_name}' not found."
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return f"Tool execution failed: {str(e)}"

    def _get_ai_response(self, messages: list, context: str, custom_prompt: str = None) -> str:
        """Get response from Groq AI with tool awareness"""
        try:
            system_content = custom_prompt if custom_prompt else self._get_enhanced_system_prompt()
            
            # Add memory context if available
            if context:
                system_content += f"\n\nRelevant Memory:\n{context[:500]}"
            
            # Clean messages
            clean_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
                if isinstance(msg, dict) and "role" in msg and "content" in msg
            ]
            
            enhanced_messages = [
                {"role": "system", "content": system_content},
                *clean_messages
            ]
            
            response = self.client.chat.completions.create(
                model=Config.MODEL_ID,
                messages=enhanced_messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                stream=True
            )
            
            full_response = ""
            placeholder = st.empty()
            
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            return full_response
            
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            raise Exception(f"Groq API Error: {str(e)}")

    def _get_tool_decision_system(self) -> str:
        """System prompt for tool detection"""
        tools_desc = "\n".join([f"- {k}: {v}" for k, v in self.available_tools.items()])
        
        return f"""You are a tool detector. Analyze the user's message and decide if they need a tool.

Available tools:
{tools_desc}

Respond in this format:
TOOL_NEEDED
tool: tool_name
param1: value1
param2: value2
reason: why this tool

Or if no tool needed:
NO_TOOL_NEEDED

Be concise."""

    def _get_enhanced_system_prompt(self) -> str:
        """Enhanced system prompt that mentions available tools"""
        tools_list = ", ".join(self.available_tools.keys())
        
        return f"""You are JARVIS, an elite AI Butler with integrated tools.

YOUR CAPABILITIES:
- You have access to real-time tools: {tools_list}
- When users ask about weather, time, news, or calculations, you can use tools
- For general conversation, use your knowledge
- Always be professional, helpful, and concise

PERSONALITY:
- Professional and courteous
- Efficient and accurate
- Proactive in offering help
- Use markdown formatting

Always identify yourself as Jarvis when appropriate."""

    def analyze_file(self, file_content: str, file_type: str) -> str:
        """Analyze uploaded file"""
        prompt = f"Analyze this {file_type} file and provide clear insights:\n\n{file_content[:2000]}"
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a file analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"File analysis failed: {e}")
            return f"File analysis failed: {str(e)}"