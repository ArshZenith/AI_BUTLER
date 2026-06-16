import json
import os
import uuid
from datetime import datetime
import streamlit as st

class ChatManager:
    def __init__(self):
        # 1. Unique User ID Generate Karna (Har Device Ke Liye Alag)
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())[:8]
        
        # 2. File Path Ko User-Specific Banana
        self.file_path = f"chats_{st.session_state.user_id}.json"
        self.chats = {}
        self.load_chats()

    def load_chats(self):
        """Chats ko user-specific JSON file se load karta hai"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
            except Exception:
                self.chats = {}
        else:
            # Agar nayi file hai toh pehli chat auto-create kar do
            self.create_new_chat("👑 Welcome Session")

    def save_chats(self):
        """Changes ko user-specific JSON file mein save karta hai"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chats for user {st.session_state.user_id}: {e}")

    def create_new_chat(self, title="New Chat"):
        chat_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.chats[chat_id] = {
            "title": title,
            "messages": [],
            "pinned": False,
            "created_at": datetime.now().isoformat()
        }
        self.save_chats()
        return chat_id

    def delete_chat(self, chat_id):
        if chat_id in self.chats:
            del self.chats[chat_id]
            self.save_chats()

    def pin_chat(self, chat_id):
        if chat_id in self.chats:
            self.chats[chat_id]["pinned"] = not self.chats[chat_id]["pinned"]
            self.save_chats()

    def rename_chat(self, chat_id, new_title):
        if chat_id in self.chats:
            self.chats[chat_id]["title"] = new_title
            self.save_chats()

    def add_message(self, chat_id, role, content):
        if chat_id in self.chats:
            self.chats[chat_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.save_chats()

    def get_chat_messages(self, chat_id):
        if chat_id in self.chats:
            return self.chats[chat_id]["messages"]
        return []

    def search_chats(self, query):
        query = query.lower()
        return [cid for cid, data in self.chats.items() 
                if query in data["title"].lower()]

    def export_chat(self, chat_id, format="txt"):
        if chat_id not in self.chats:
            return ""
        
        messages = self.chats[chat_id]["messages"]
        if format == "txt":
            text = ""
            for msg in messages:
                text += f"[{msg['role'].upper()}]: {msg['content']}\n\n"
            return text
        return ""

    def get_stats(self, chat_id):
        if chat_id not in self.chats:
            return {}
        messages = self.chats[chat_id]["messages"]
        total_words = sum(len(msg["content"].split()) for msg in messages)
        return {
            "total_messages": len(messages),
            "total_words": total_words
        }