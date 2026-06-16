import streamlit as st
from groq import Groq
from config import Config
from tools import ButlerTools
from voice_engine import VoiceEngine
import json
import re

class AIButler:
    """Integrated AI Butler with Smart Tool Usage"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.tools = ButlerTools()
        self.voice = VoiceEngine()
        
        # Define available tools for AI
        self.available_tools = {
            "get_weather": "Get current weather for a city",
            "search_web": "Search the internet for information",
            "get_news": "Get latest news updates",
            "calculate": "Perform mathematical calculations",
            "get_time_date": "Get current time and date"
        }
    
    def process_query(self, user_message: str, messages: list, use_voice: bool = False) -> dict:
        """Main processing function with integrated tool usage"""
        result = {'response': '', 'audio_path': None, 'tool_used': None}
        
        try:
            # Step 1: Check if AI wants to use a tool
            tool_call = self._detect_tool_intent(messages)
            
            if tool_call:
                # Execute the tool
                tool_result = self._execute_tool(tool_call, user_message)
                result['response'] = tool_result
                result['tool_used'] = tool_call['name']
            else:
                # Normal AI conversation
                result['response'] = self._get_ai_response(messages)
            
            # Step 2: Generate voice if enabled
            if use_voice and result['response']:
                result['audio_path'] = self.voice.text_to_speech(result['response'])
            
            return result
            
        except Exception as e:
            return {'response': f"⚠️ System Error: {str(e)}", 'audio_path': None, 'tool_used': None}

    def _detect_tool_intent(self, messages: list) -> dict:
        """Detect if user wants to use a tool using AI"""
        try:
            # Ask AI to decide if a tool is needed
            decision_prompt = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast model for decision making
                messages=[
                    {"role": "system", "content": self._get_tool_decision_system()},
                    {"role": "user", "content": messages[-1]["content"] if messages else ""}
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
                    elif ":" in line and not line.startswith("reason:"):
                        key, value = line.split(":", 1)
                        params[key.strip()] = value.strip()
                
                if tool_name and tool_name in self.available_tools:
                    return {"name": tool_name, "params": params}
            
            return None
            
        except Exception as e:
            print(f"Tool detection error: {e}")
            return None

    def _execute_tool(self, tool_call: dict, user_message: str) -> str:
        """Execute the detected tool"""
        tool_name = tool_call['name']
        params = tool_call['params']
        
        try:
            if tool_name == "get_weather":
                city = params.get('city', 'London')
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
            
            return "Tool not found."
            
        except Exception as e:
            return f"Tool execution failed: {str(e)}"

    def _get_ai_response(self, messages: list) -> str:
        """Get response from Groq AI with tool awareness"""
        try:
            # Enhanced system prompt that knows about tools
            enhanced_messages = [
                {"role": "system", "content": self._get_enhanced_system_prompt()},
                *messages
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
            raise Exception(f"Groq API Error: {str(e)}")

    def _get_tool_decision_system(self) -> str:
        """System prompt for tool detection"""
        return """You are a tool detector. Analyze the user's message and decide if they need a tool.

Available tools:
- get_weather: For weather information (needs: city)
- search_web: For searching internet (needs: query)
- get_news: For latest news (no params needed)
- calculate: For math calculations (needs: expression)
- get_time_date: For current time/date (no params needed)

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
        return f"""You are JARVIS, an elite AI Butler with integrated tools.

YOUR CAPABILITIES:
- You have access to real-time tools for weather, web search, news, calculations, and time
- When users ask about weather, time, news, or calculations, you can use tools
- For general conversation, use your knowledge
- Always be professional, helpful, and concise

AVAILABLE TOOLS (used automatically):
- Weather information (current conditions)
- Web search (latest information)
- News updates (technology and general)
- Calculator (mathematical operations)
- Time and date (current)

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
            return f"File analysis failed: {str(e)}"