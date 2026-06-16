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
    
    def text_to_speech(self, text: str, lang: str = "en") -> str:
        if not HAS_GTTS:
            return None
            
        try:
            clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', text)
            if not clean_text.strip():
                return None
            
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            filename = f"jarvis_{int(time.time())}.mp3"
            path = os.path.join(self.temp_dir, filename)
            tts.save(path)
            return path
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    def play_audio(self, path: str):
        if not path or not os.path.exists(path):
            return
            
        def _play():
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(path)
                elif system == "Darwin":
                    os.system(f'afplay "{path}" &')
                else:
                    os.system(f'mpg123 "{path}" &')
            except Exception as e:
                print(f"Playback Error: {e}")
        
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()