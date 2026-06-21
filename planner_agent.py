import json
import re
from config import Config
from groq import Groq

class PlannerAgent:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
    
    def create_plan(self, user_query: str, chat_history_summary: str = "") -> list:
        system_prompt = """You are JARVIS's Planning Core. Break down complex requests into executable steps.

RULES:
1. ALWAYS return valid JSON array. No markdown, no explanations.
2. Available tools: 'get_weather', 'search_web', 'get_news', 'get_time_date', 'calculate', 'general_chat'.
3. For 'general_chat', use params: {"prompt": "detailed instruction"}.
4. If user asks for schedule/plan, include 'general_chat' step at end to format final answer.
5. Keep steps logical and sequential.

Example Output:
[{"tool_name": "get_time_date", "params": {}}, {"tool_name": "general_chat", "params": {"prompt": "Create weekly schedule..."}}]"""

        user_content = f"User Query: {user_query}\n\nChat Context: {chat_history_summary}" if chat_history_summary else f"User Query: {user_query}"
        
        try:
            response = self.client.chat.completions.create(
                model=Config.SMART_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            raw_json = response.choices[0].message.content
            json_match = re.search(r'\[\s*\{.*\}\s*\]', raw_json, re.DOTALL)
            clean_json = json_match.group(0) if json_match else raw_json
            plan = json.loads(clean_json)
            
            if not isinstance(plan, list):
                raise ValueError("Plan is not a list")
            return plan
            
        except Exception as e:
            print(f"Planner failed: {e}")
            return [{"tool_name": "general_chat", "params": {"prompt": f"User asked: '{user_query}'. Provide helpful response directly."}}]