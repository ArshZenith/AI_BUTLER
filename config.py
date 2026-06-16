import os
from dotenv import load_dotenv

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