import requests
import datetime
import pytz
import re

class ButlerTools:
    def get_time_date(self):
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.datetime.now(ist)
        return f"Current time in India is {now.strftime('%I:%M %p')} on {now.strftime('%A, %d %B %Y')}."

    def get_weather(self, city="Delhi"):
        try:
            # Using Open-Meteo (Free, No API Key required)
            # Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_res = requests.get(geo_url, timeout=5).json()
            
            if "results" not in geo_res:
                return f"Could not find weather data for {city}."
            
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            
            # Weather
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_res = requests.get(weather_url, timeout=5).json()
            
            temp = weather_res["current_weather"]["temperature"]
            return f"The current temperature in {city} is {temp}°C."
        except Exception as e:
            return f"Unable to fetch weather for {city} at the moment."

    def get_news(self):
        try:
            from duckduckgo_search import DDGS
            results = DDGS().news("latest technology news", max_results=3)
            news_list = []
            for r in results:
                news_list.append(f"- **{r['title']}** ({r['source']})")
            return "\n".join(news_list) if news_list else "No news found."
        except Exception:
            return "News service is currently unavailable."

    def calculate(self, expression):
        try:
            # Safe evaluation
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "Invalid characters in expression."
            result = eval(expression)
            return f"The result is {result}."
        except Exception:
            return "Could not calculate that expression."

    def search_web(self, query):
        try:
            from duckduckgo_search import DDGS
            results = DDGS().text(query, max_results=3)
            summary = []
            for r in results:
                summary.append(f"- {r['title']}: {r['href']}")
            return "\n".join(summary) if summary else "No results found."
        except Exception:
            return "Web search is currently unavailable."