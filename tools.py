import requests
import re
import os
from datetime import datetime, timezone, timedelta

# Safe imports for optional tools
try:
    from gmail_tools import GmailSummarizer
except ImportError:
    GmailSummarizer = None

class ButlerTools:
    """
    JARVIS Butler Tools - All utility functions for the AI Butler
    Includes: Weather, Web Search, News, Time/Date, Calculator, Gmail
    """
    
    def __init__(self):
        """Initialize all tool services"""
        if GmailSummarizer:
            self.gmail_service = GmailSummarizer()
        else:
            self.gmail_service = None
            
        self._setup_constants()
    
    def _setup_constants(self):
        """Setup constants for API calls"""
        self.TIMEOUT = 5  # seconds
        self.IST_OFFSET = timedelta(hours=5, minutes=30)
        self.WEATHER_CONDITIONS = {
            0: "Clear Sky ☀️",
            1: "Mainly Clear 🌤️",
            2: "Partly Cloudy ⛅",
            3: "Overcast ☁️",
            45: "Foggy 🌫️",
            48: "Rime Fog 🌫️",
            51: "Light Drizzle 🌦️",
            53: "Moderate Drizzle 🌦️",
            55: "Dense Drizzle 🌧️",
            61: "Light Rain 🌧️",
            63: "Moderate Rain 🌧️",
            65: "Heavy Rain 🌧️",
            71: "Light Snow ❄️",
            73: "Moderate Snow ❄️",
            75: "Heavy Snow ❄️",
            77: "Snow Grains ❄️",
            80: "Light Showers 🌦️",
            81: "Moderate Showers 🌧️",
            82: "Violent Showers ⛈️",
            85: "Light Snow Showers 🌨️",
            86: "Heavy Snow Showers 🌨️",
            95: "Thunderstorm ⛈️",
            96: "Thunderstorm with Hail ⛈️",
            99: "Thunderstorm with Heavy Hail ⛈️"
        }
    
    # ========================================
    # 🌤️ WEATHER TOOL
    # ========================================
    def get_weather(self, city: str = "Delhi") -> str:
        """Get current weather for a city using Open-Meteo API (No API Key)"""
        try:
            # Step 1: Get coordinates
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_res = requests.get(geo_url, timeout=self.TIMEOUT).json()
            
            if not geo_res.get('results'):
                return f"❌ Could not find location: {city}"
            
            lat = geo_res['results'][0]['latitude']
            lon = geo_res['results'][0]['longitude']
            
            # Step 2: Get weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=auto"
            res = requests.get(weather_url, timeout=self.TIMEOUT).json()
            
            # Step 3: Extract data
            current = res['current']
            temp = current['temperature_2m']
            code = current['weather_code']
            humidity = current.get('relative_humidity_2m', 'N/A')
            wind_speed = current.get('wind_speed_10m', 'N/A')
            
            condition = self.WEATHER_CONDITIONS.get(code, 'Unknown')
            
            return f"""🌤️ **Weather in {city}**
            
🌡️ Temperature: {temp}°C
☁️ Condition: {condition}
💧 Humidity: {humidity}%
💨 Wind Speed: {wind_speed} km/h"""
            
        except requests.exceptions.Timeout:
            return f"⚠️ Weather service timeout for {city}"
        except Exception as e:
            return f"⚠️ Weather Error: {str(e)}"
    
    # ========================================
    # 🔍 WEB SEARCH TOOL
    # ========================================
    def search_web(self, query: str) -> str:
        """Search the web using DuckDuckGo Instant Answer API (No API Key)"""
        try:
            url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json"
            res = requests.get(url, timeout=self.TIMEOUT).json()
            
            # Try to get abstract (direct answer)
            if res.get('AbstractText'):
                return f"**{res.get('Heading', query)}**\n\n{res['AbstractText']}\n\n_Source: {res.get('AbstractSource', 'DuckDuckGo')}_"
            
            # Try related topics
            elif res.get('RelatedTopics'):
                results = []
                for topic in res['RelatedTopics'][:5]:
                    if 'Text' in topic:
                        results.append(f"• {topic['Text']}")
                
                if results:
                    return f"**Search Results for '{query}':**\n\n" + "\n".join(results)
            
            # Try definition
            elif res.get('Definition'):
                return f"**Definition:** {res['Definition']}\n\n_Source: {res.get('DefinitionSource', 'DuckDuckGo')}_"
            
            return f"ℹ️ No direct results found for '{query}'. Try rephrasing your query."
            
        except requests.exceptions.Timeout:
            return "⚠️ Search service timeout"
        except Exception as e:
            return f"⚠️ Search Error: {str(e)}"
    
    # ========================================
    # 📰 NEWS TOOL
    # ========================================
    def get_news(self, category: str = "tech") -> str:
        """Get latest news from Hacker News API (No API Key)"""
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            ids = requests.get(url, timeout=self.TIMEOUT).json()[:5]
            
            news = []
            for i, story_id in enumerate(ids, 1):
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", 
                    timeout=self.TIMEOUT
                ).json()
                title = item.get('title', 'No title')
                url_link = item.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                score = item.get('score', 0)
                
                news.append(f"{i}. **{title}**\n   Score: {score} | [Read more]({url_link})")
            
            return "📰 **Top Tech News (Hacker News)**\n\n" + "\n\n".join(news)
            
        except requests.exceptions.Timeout:
            return "⚠️ News service timeout"
        except Exception as e:
            return f"⚠️ News Error: {str(e)}"
    
    # ========================================
    # 🕐 TIME & DATE TOOL
    # ========================================
    def get_time_date(self) -> str:
        """Get current date and time in IST (Indian Standard Time)"""
        try:
            ist = timezone(self.IST_OFFSET)
            now = datetime.now(ist)
            
            return f"""🕐 **Current Date & Time (IST)**
            
📅 Date: {now.strftime('%A, %B %d, %Y')}
⏰ Time: {now.strftime('%I:%M %p')}
🌍 Timezone: IST (UTC+5:30)"""
            
        except Exception as e:
            return f"⚠️ Time Error: {str(e)}"
    
    # ========================================
    # 🧮 CALCULATOR TOOL
    # ========================================
    def calculate(self, expression: str) -> str:
        """Safe mathematical calculator (Only allows digits and basic operators)"""
        try:
            # Security check - only allow safe characters
            allowed_pattern = re.compile(r'^[\d\+\-\*\/\.\(\)\s]+$')
            
            if not allowed_pattern.match(expression):
                return "❌ Invalid expression. Only numbers and +, -, *, /, (, ) allowed."
            
            # Check for division by zero
            if '/0' in expression.replace(' ', ''):
                return "❌ Cannot divide by zero!"
            
            # Evaluate safely
            result = eval(expression)
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 4)
            
            return f"🧮 **Calculation**\n\n`{expression}` = **{result}**"
            
        except ZeroDivisionError:
            return "❌ Cannot divide by zero!"
        except SyntaxError:
            return "❌ Invalid mathematical expression. Check your syntax."
        except Exception as e:
            return f"⚠️ Calculation Error: {str(e)}"
    
    # ========================================
    # 📧 GMAIL SUMMARIZER TOOL
    # ========================================
    def summarize_gmails(self, max_results: int = 10, hours_back: int = 24) -> str:
        """Fetch and summarize recent Gmail emails (Requires credentials.json)"""
        if not self.gmail_service:
            return "⚠️ Gmail tools not installed. Please install required dependencies."
            
        try:
            # Check if credentials exist
            if not os.path.exists('credentials.json'):
                return """⚠️ **Gmail Not Connected**

To enable Gmail summarization:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` and place it in this folder
5. Restart the app and try again"""
            
            # Fetch and summarize emails
            summary = self.gmail_service.get_email_summary(
                max_results=max_results, 
                hours_back=hours_back
            )
            
            if not summary or "No recent emails" in summary:
                return f"📭 **No new emails** found in the last {hours_back} hours."
            
            return summary
            
        except Exception as e:
            return f"⚠️ Gmail Error: {str(e)}"
    
    def check_gmail_auth_status(self) -> dict:
        """Check if Gmail is authenticated"""
        if not self.gmail_service:
            return {'authenticated': False, 'message': 'Gmail tools not installed'}
            
        try:
            if not os.path.exists('credentials.json'):
                return {'authenticated': False, 'message': 'credentials.json not found'}
            
            if not os.path.exists('token.json'):
                return {'authenticated': False, 'message': 'Not authenticated yet'}
            
            # Try to authenticate silently
            success, msg = self.gmail_service.authenticate()
            return {'authenticated': success, 'message': msg}
            
        except Exception as e:
            return {'authenticated': False, 'message': str(e)}
    
    # ========================================
    # 🛠️ UTILITY METHODS
    # ========================================
    def get_available_tools(self) -> dict:
        """Get list of all available tools with descriptions"""
        tools = {
            "get_weather": "Get current weather for a city (params: city)",
            "search_web": "Search the internet for information (params: query)",
            "get_news": "Get latest tech news from Hacker News (no params)",
            "get_time_date": "Get current date and time in IST (no params)",
            "calculate": "Perform mathematical calculations (params: expression)"
        }
        
        if self.gmail_service:
            tools["summarize_gmails"] = "Fetch and summarize recent Gmail emails (params: max_results, hours_back)"
            
        return tools
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters (Central dispatcher)"""
        tool_map = {
            'get_weather': self.get_weather,
            'search_web': self.search_web,
            'get_news': self.get_news,
            'get_time_date': self.get_time_date,
            'calculate': self.calculate,
            'summarize_gmails': self.summarize_gmails
        }
        
        if tool_name not in tool_map:
            return f"❌ Tool '{tool_name}' not found"
        
        try:
            return tool_map[tool_name](**kwargs)
        except TypeError as e:
            return f"❌ Invalid parameters for {tool_name}: {str(e)}"
        except Exception as e:
            return f"⚠️ Tool execution error: {str(e)}"