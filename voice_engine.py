import os
import time
import re
import platform
<<<<<<< HEAD
=======
import threading
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

class VoiceEngine:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(self.temp_dir, exist_ok=True)
    
<<<<<<< HEAD
    def text_to_speech(self, text: str, lang: str = "en", speed: str = "normal") -> str:
        if not HAS_GTTS:
            print("⚠️ gTTS not installed. Run: pip install gTTS")
            return None
            
        try:
            # Clean text to remove emojis/special chars that break TTS
=======
    def text_to_speech(self, text: str, lang: str = "en") -> str:
        if not HAS_GTTS:
            return None
            
        try:
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', text)
            if not clean_text.strip():
                return None
            
<<<<<<< HEAD
            # gTTS only supports slow=True (slow) or slow=False (normal/fast)
            is_slow = True if speed == "slow" else False
            
            tts = gTTS(text=clean_text, lang=lang, slow=is_slow)
=======
            tts = gTTS(text=clean_text, lang=lang, slow=False)
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            filename = f"jarvis_{int(time.time())}.mp3"
            path = os.path.join(self.temp_dir, filename)
            tts.save(path)
            return path
<<<<<<< HEAD
            
        except Exception as e:
            print(f"TTS Generation Error: {e}")
=======
        except Exception as e:
            print(f"TTS Error: {e}")
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            return None

    def play_audio(self, path: str):
        if not path or not os.path.exists(path):
<<<<<<< HEAD
            print(f"Audio file not found at: {path}")
            return
            
        try:
            system = platform.system()
            if system == "Windows":
                # Native Windows playback (No console popup)
                os.startfile(path)
            elif system == "Darwin": # macOS
                os.system(f'afplay "{path}" &')
            else: # Linux
                os.system(f'mpg123 "{path}" &')
        except Exception as e:
            print(f"Audio Playback Error: {e}")
=======
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
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
