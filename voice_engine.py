import os
import time
import re
import platform
import threading

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

class VoiceEngine:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def text_to_speech(self, text: str, lang: str = "en", speed: str = "normal") -> str:
        if not HAS_GTTS:
            print("⚠️ gTTS not installed. Run: pip install gTTS")
            return None
            
        try:
            # Clean text to remove emojis/special chars that break TTS
            clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', text)
            if not clean_text.strip():
                return None
            
            # gTTS only supports slow=True (slow) or slow=False (normal/fast)
            is_slow = True if speed == "slow" else False
            
            tts = gTTS(text=clean_text, lang=lang, slow=is_slow)
            filename = f"jarvis_{int(time.time())}.mp3"
            path = os.path.join(self.temp_dir, filename)
            tts.save(path)
            return path
            
        except Exception as e:
            print(f"TTS Generation Error: {e}")
            return None

    def play_audio(self, path: str):
        if not path or not os.path.exists(path):
            print(f"Audio file not found at: {path}")
            return
            
        def _play():
            try:
                system = platform.system()
                if system == "Windows":
                    # Native Windows playback (No console popup)
                    os.startfile(path)
                elif system == "Darwin":  # macOS
                    os.system(f'afplay "{path}" &')
                else:  # Linux
                    os.system(f'mpg123 "{path}" &')
            except Exception as e:
                print(f"Audio Playback Error: {e}")
        
        # Run in background thread so app doesn't freeze
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()