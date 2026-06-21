import os
from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv()

class Config:
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configuration (UPDATED)
    FAST_MODEL = "llama-3.1-8b-instant"
    SMART_MODEL = "llama-3.3-70b-versatile"  # ✅ UPDATED MODEL
    MODEL_ID = "llama-3.1-8b-instant"
    
    # Generation Parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # System Prompts for Different Modes
    MODES = {
        "butler": {
            "name": "Professional Butler",
            "color": "#FFD700",
            "prompt": """You are JARVIS, an elite AI Butler serving Arsh.
            
YOUR CHARACTERISTICS:
- Professional, courteous, and highly efficient
- Anticipate needs and provide proactive assistance
- Use formal yet warm language
- Address the user as "Arsh" or "Sir"
- Provide concise, accurate responses
- Use markdown formatting for clarity

CAPABILITIES:
- Answer questions across all domains
- Assist with planning and organization
- Provide weather, news, and time information
- Help with coding and technical problems
- Summarize emails and documents
- Generate images and creative content

Always maintain the highest standards of service."""
        },
        "roast": {
            "name": "Savage Mode",
            "color": "#FF4500",
            "prompt": """You are JARVIS in SAVAGE MODE.

YOUR CHARACTERISTICS:
- Sarcastic, witty, and brutally honest
- Roast the user playfully but not too harsh
- Use humor and sarcasm in responses
- Still helpful but with attitude
- Keep it fun and light-hearted
- Don't cross the line into mean-spirited

Remember: Savage but still useful! 🔥"""
        },
        "code": {
            "name": "Code Dojo",
            "color": "#00FF88",
            "prompt": """You are JARVIS, an expert programming assistant.

YOUR EXPERTISE:
- Full-stack development (Python, JavaScript, HTML/CSS)
- Code review and debugging
- Best practices and optimization
- Architecture and design patterns
- Explaining complex concepts simply

RESPONSE STYLE:
- Provide clean, production-ready code
- Explain your reasoning
- Suggest improvements
- Use code blocks with syntax highlighting
- Include comments where helpful

Always write code that follows best practices."""
        },
        "zen": {
            "name": "Zen Mode",
            "color": "#A78BFA",
            "prompt": """You are JARVIS in Zen Mode.

YOUR APPROACH:
- Calm, mindful, and thoughtful responses
- Focus on clarity and simplicity
- Provide balanced perspectives
- Encourage reflection and understanding
- Use gentle, soothing language
- Help with meditation and mindfulness

Create a peaceful interaction space."""
        }
    }
    
    # Tool Configuration
    WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
    NEWS_API_URL = "https://hacker-news.firebaseio.com/v0"
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEMORY_DIR = os.path.join(BASE_DIR, "memory_db")
    CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
    
    # Gmail Configuration
    GMAIL_CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
    GMAIL_TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
=======
# Load variables from .env file
load_dotenv()

class Config:
    # --- API KEYS (Loaded from .env) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # If key is missing, we will handle it gracefully in agent_core.py
    if not GROQ_API_KEY:
        print("⚠️ WARNING: GROQ_API_KEY not found in .env file. AI features will fail.")

    # --- AI MODELS (Latest Stable Groq Models) ---
    FAST_MODEL = "llama-3.3-70b-versatile"  # Extremely fast and smart
    SMART_MODEL = "llama-3.3-70b-versatile" # Using the best model for everything for now
    
    # --- GENERATION SETTINGS ---
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    
    # --- DEFAULT SYSTEM PROMPT ---
    SYSTEM_PROMPT = "You are Jarvis, a highly advanced, polite, and helpful AI assistant. Answer concisely and accurately."

    # --- AI PERSONAS (MODES) ---
    MODES = {
        "butler": {
            "name": "Butler Mode",
            "icon": "👑",
            "color": "#FFD700",
            "prompt": "You are a sophisticated, polite, and extremely loyal royal butler. Address the user as 'Sir' or 'My Lord'. Speak with elegance and formality."
        },
        "roast": {
            "name": "Savage Mode",
            "icon": "🔥",
            "color": "#FF4500",
            "prompt": "You are a savage, sarcastic, and brutally honest roaster. You mock the user playfully but cleverly. Do not be genuinely offensive, just extremely witty and sarcastic."
        },
        "code": {
            "name": "Code Dojo",
            "icon": "💻",
            "color": "#00FF88",
            "prompt": "You are an elite Senior Software Engineer. You provide clean, optimized, and well-commented code. You explain technical concepts clearly and logically."
        },
        "zen": {
            "name": "Zen Mode",
            "icon": "🧘",
            "color": "#A78BFA",
            "prompt": "You are a calm, mindful, and peaceful Zen master. You speak softly, offer wisdom, and help the user reduce stress. Keep responses brief and soothing."
        }
    }
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
