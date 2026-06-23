import json
import re
from config import Config
from groq import Groq

class PlannerAgent:
    """Advanced Planning Core for breaking down complex queries"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        
        # Define available tools and their descriptions for the planner
        self.TOOL_DEFINITIONS = {
            "get_weather": {"desc": "Get current weather for a city", "params": {"city": "string"}},
            "search_web": {"desc": "Search internet for real-time info", "params": {"query": "string"}},
            "get_news": {"desc": "Fetch latest tech/general news", "params": {}},
            "get_time_date": {"desc": "Get current time and date", "params": {}},
            "calculate": {"desc": "Perform math calculations", "params": {"expression": "string"}},
            "general_chat": {"desc": "Converse or synthesize final answer", "params": {"prompt": "string"}}
        }
    
    def create_plan(self, user_query: str, chat_history_summary: str = "") -> list:
        """Create an executable plan from user query"""
        
        system_prompt = f"""You are JARVIS's Strategic Planning Core. Your job is to break complex user requests into a sequence of executable tool calls.

AVAILABLE TOOLS:
{json.dumps(self.TOOL_DEFINITIONS, indent=2)}

CRITICAL RULES:
1. Return ONLY a valid JSON array of objects. No markdown formatting, no explanations.
2. Each object MUST have 'tool_name' (string) and 'params' (object).
3. Use 'general_chat' when you need to synthesize information from previous steps or provide a conversational response.
4. For 'general_chat', always include a detailed 'prompt' in params explaining what to say based on previous context.
5. If the query requires scheduling, planning, or multi-step reasoning, end with a 'general_chat' step to format the final output nicely.
6. Keep the plan logical, sequential, and minimal. Don't over-plan simple queries.

EXAMPLE OUTPUT FORMAT:
[
  {{"tool_name": "get_time_date", "params": {{}}}},
  {{"tool_name": "search_web", "params": {{"query": "best python frameworks 2024"}}}},
  {{"tool_name": "general_chat", "params": {{"prompt": "Based on the search results and current time, suggest the best framework for a beginner."}}}}
]"""

        user_content = f"User Query: {user_query}"
        if chat_history_summary:
            user_content += f"\n\nChat Context Summary: {chat_history_summary}"
        
        try:
            response = self.client.chat.completions.create(
                model=Config.SMART_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,  # Low temp for deterministic planning
                max_tokens=1500
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Robust JSON extraction
            plan = self._extract_json_array(raw_content)
            
            # Validate plan structure
            if not isinstance(plan, list):
                raise ValueError("Plan is not a list")
                
            for step in plan:
                if not isinstance(step, dict) or "tool_name" not in step:
                    raise ValueError(f"Invalid step structure: {step}")
                if "params" not in step:
                    step["params"] = {}
                    
            return plan
            
        except Exception as e:
            print(f"⚠️ Planner failed: {e}. Falling back to direct chat.")
            # Safe fallback: Let AI handle it directly
            return [{"tool_name": "general_chat", "params": {"prompt": f"User asked: '{user_query}'. Provide a comprehensive and helpful response directly."}}]

    def _extract_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response with multiple fallback strategies"""
        # Strategy 1: Direct parse
        try:
            return json.loads(text)
        except:
            pass
            
        # Strategy 2: Find JSON array with regex
        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
                
        # Strategy 3: Try to fix common JSON issues (trailing commas, etc.)
        try:
            fixed_text = text.replace(",]", "]").replace(",}", "}")
            return json.loads(fixed_text)
        except:
            pass
            
        # Strategy 4: Last resort - wrap in array if it looks like a single object
        if text.strip().startswith("{"):
            try:
                return [json.loads(text)]
            except:
                pass
        
        raise ValueError("Could not extract valid JSON array from response")