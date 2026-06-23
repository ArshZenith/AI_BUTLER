import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized Configuration for Jarvis Butler"""
    
    # ========================================
    # 🔑 API KEYS
    # ========================================
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        print("⚠️ WARNING: GROQ_API_KEY not found in .env file. AI features will fail.")
    
    # ========================================
    # 🤖 MODEL CONFIGURATION
    # ========================================
    FAST_MODEL = "llama-3.3-70b-versatile"   # Extremely fast and smart
    SMART_MODEL = "llama-3.3-70b-versatile"  # Using the best model for everything
    VISION_MODEL = "llama-3.2-11b-vision-preview"  # For image analysis
    MODEL_ID = "llama-3.3-70b-versatile"     # Alias for backward compatibility
    
    # Generation Parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Default System Prompt (Fallback)
    SYSTEM_PROMPT = "You are Jarvis, a highly advanced, polite, and helpful AI assistant. Answer concisely and accurately."
    
    # ========================================
    # 🎭 MODE PROMPTS & SETTINGS
    # ========================================
    MODES = {
        "butler": {
            "name": "Professional Butler",
            "icon": "👑",
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
            "icon": "🔥",
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
            "icon": "💻",
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
            "icon": "🧘",
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
    
    # ========================================
    # 🛠️ TOOL & SYSTEM CONFIG
    # ========================================
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
    
    # ========================================
    # 🆕 HELPER METHODS
    # ========================================
    
    @classmethod
    def validate(cls):
        """Validate that all required configurations are present"""
        errors = []
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is missing")
        
        if cls.GROQ_API_KEY and len(cls.GROQ_API_KEY) < 10:
            errors.append("GROQ_API_KEY appears to be invalid (too short)")
        
        if not os.path.exists(cls.BASE_DIR):
            errors.append(f"BASE_DIR does not exist: {cls.BASE_DIR}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def get_model_for_complexity(cls, message: str) -> str:
        """Select appropriate model based on query complexity"""
        complex_keywords = ['plan', 'schedule', 'compare', 'analyze', 'code', 'explain', 'detailed']
        word_count = len(message.split())
        
        is_complex = any(w in message.lower() for w in complex_keywords) or word_count > 15
        return cls.SMART_MODEL if is_complex else cls.FAST_MODEL
    
    @classmethod
    def get_mode_config(cls, mode_name: str) -> dict:
        """Safely get mode configuration with fallback"""
        return cls.MODES.get(mode_name, cls.MODES["butler"])
    
    @classmethod
    def get_system_prompt(cls, mode_name: str = None) -> str:
        """Get system prompt for a mode with fallback"""
        if mode_name and mode_name in cls.MODES:
            return cls.MODES[mode_name]["prompt"]
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary for debugging"""
        print(f"\n{'='*50}")
        print(f"🤖 Jarvis Butler Configuration")
        print(f"{'='*50}")
        print(f"✅ API Key: {'Set' if cls.GROQ_API_KEY else '❌ Missing'}")
        print(f"🚀 Fast Model: {cls.FAST_MODEL}")
        print(f"🧠 Smart Model: {cls.SMART_MODEL}")
        print(f"👁️  Vision Model: {cls.VISION_MODEL}")
        print(f"🌡️  Temperature: {cls.TEMPERATURE}")
        print(f"📝 Max Tokens: {cls.MAX_TOKENS}")
        print(f"📂 Base Dir: {cls.BASE_DIR}")
        print(f"🎭 Modes: {', '.join(cls.MODES.keys())}")
        print(f"{'='*50}\n")