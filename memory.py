import json
import os

class ButlerMemory:
    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        self.memories = []
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except Exception:
                self.memories = []

    def save_memory(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def save_interaction(self, user_msg, ai_msg):
        # Simple logic: save short, important looking interactions
        if len(user_msg.split()) < 50: 
            self.memories.append({"user": user_msg, "ai": ai_msg[:100]})
            if len(self.memories) > 50: # Keep only last 50 memories to save space
                self.memories = self.memories[-50:]
            self.save_memory()

    def get_relevant_memories(self, query):
        # Simple keyword matching for memory retrieval
        query_words = set(query.lower().split())
        relevant = []
        for mem in self.memories[-10:]: # Check last 10 memories
            mem_words = set(mem["user"].lower().split())
            if query_words.intersection(mem_words):
                relevant.append(f"User previously asked: {mem['user']}")
        return relevant

    def clear_memory(self):
        self.memories = []
        self.save_memory()