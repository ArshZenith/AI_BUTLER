import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class ChatManager:
    """
    Advanced Chat Manager with multi-user support and folder organization
    """
    
    def __init__(self, user_path: str = None):
        """
        Initialize ChatManager
        
        Args:
            user_path: User-specific data directory path
                      If None, uses default location
        """
        # Setup paths
        if user_path:
            self.base_path = Path(user_path)
        else:
            self.base_path = Path(os.getcwd())
        
        # Create necessary directories
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Database paths
        self.chats_db_path = self.base_path / "chat_history.json"
        self.folders_db_path = self.base_path / "chat_folders.json"
        
        # Load data
        self.chats = self._load_chats()
        self.folders = self._load_folders()
        
        # Default folders if none exist
        if not self.folders:
            self._create_default_folders()
    
    def _load_chats(self) -> Dict[str, Any]:
        """Load chats from JSON file"""
        try:
            if self.chats_db_path.exists():
                with open(self.chats_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading chats: {e}")
        return {}
    
    def _save_chats(self):
        """Save chats to JSON file"""
        try:
            with open(self.chats_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chats: {e}")
    
    def _load_folders(self) -> Dict[str, Any]:
        """Load folder structure from JSON file"""
        try:
            if self.folders_db_path.exists():
                with open(self.folders_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading folders: {e}")
        return {}
    
    def _save_folders(self):
        """Save folder structure to JSON file"""
        try:
            with open(self.folders_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.folders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving folders: {e}")
    
    def _create_default_folders(self):
        """Create default chat folders"""
        self.folders = {
            "all": {
                "id": "all",
                "name": "All Chats",
                "icon": "💬",
                "color": "#FFD700",
                "is_system": True,
                "created": datetime.now().isoformat()
            },
            "pinned": {
                "id": "pinned",
                "name": "Pinned",
                "icon": "📌",
                "color": "#FF4500",
                "is_system": True,
                "created": datetime.now().isoformat()
            },
            "work": {
                "id": "work",
                "name": "Work",
                "icon": "💼",
                "color": "#00FF88",
                "is_system": False,
                "created": datetime.now().isoformat()
            },
            "personal": {
                "id": "personal",
                "name": "Personal",
                "icon": "👤",
                "color": "#A78BFA",
                "is_system": False,
                "created": datetime.now().isoformat()
            },
            "code": {
                "id": "code",
                "name": "Code",
                "icon": "💻",
                "color": "#00FFFF",
                "is_system": False,
                "created": datetime.now().isoformat()
            },
            "study": {
                "id": "study",
                "name": "Study",
                "icon": "📚",
                "color": "#FF69B4",
                "is_system": False,
                "created": datetime.now().isoformat()
            }
        }
        self._save_folders()
    
    # ========================================
    # CHAT MANAGEMENT
    # ========================================
    
    def create_new_chat(
        self, 
        title: str = "New Chat",
        folder_id: str = "all"
    ) -> str:
        """Create a new chat"""
        chat_id = f"chat_{int(datetime.now().timestamp())}_{len(self.chats)}"
        
        self.chats[chat_id] = {
            "id": chat_id,
            "title": title,
            "messages": [],
            "folder_id": folder_id,
            "tags": [],
            "pinned": False,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "metadata": {
                "word_count": 0,
                "message_count": 0,
                "last_activity": datetime.now().isoformat()
            }
        }
        
        self._save_chats()
        return chat_id
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat"""
        if chat_id in self.chats:
            del self.chats[chat_id]
            self._save_chats()
            return True
        return False
    
    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """Rename a chat"""
        if chat_id in self.chats:
            self.chats[chat_id]["title"] = new_title
            self.chats[chat_id]["updated"] = datetime.now().isoformat()
            self._save_chats()
            return True
        return False
    
    def move_chat_to_folder(self, chat_id: str, folder_id: str) -> bool:
        """Move chat to different folder"""
        if chat_id in self.chats and folder_id in self.folders:
            self.chats[chat_id]["folder_id"] = folder_id
            self.chats[chat_id]["updated"] = datetime.now().isoformat()
            self._save_chats()
            return True
        return False
    
    def pin_chat(self, chat_id: str) -> bool:
        """Pin/unpin a chat"""
        if chat_id in self.chats:
            self.chats[chat_id]["pinned"] = not self.chats[chat_id].get("pinned", False)
            self.chats[chat_id]["updated"] = datetime.now().isoformat()
            self._save_chats()
            return True
        return False
    
    def add_tag(self, chat_id: str, tag: str) -> bool:
        """Add tag to chat"""
        if chat_id in self.chats:
            if tag not in self.chats[chat_id].get("tags", []):
                self.chats[chat_id].setdefault("tags", []).append(tag)
                self._save_chats()
            return True
        return False
    
    def remove_tag(self, chat_id: str, tag: str) -> bool:
        """Remove tag from chat"""
        if chat_id in self.chats:
            tags = self.chats[chat_id].get("tags", [])
            if tag in tags:
                tags.remove(tag)
                self._save_chats()
            return True
        return False
    
    def add_message(self, chat_id: str, role: str, content: str) -> bool:
        """Add message to chat"""
        if chat_id in self.chats:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "tokens": len(content.split())
            }
            
            self.chats[chat_id]["messages"].append(message)
            self.chats[chat_id]["updated"] = datetime.now().isoformat()
            
            # Update metadata
            self.chats[chat_id]["metadata"]["message_count"] += 1
            self.chats[chat_id]["metadata"]["word_count"] += message["tokens"]
            self.chats[chat_id]["metadata"]["last_activity"] = datetime.now().isoformat()
            
            self._save_chats()
            return True
        return False
    
    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a chat"""
        if chat_id in self.chats:
            return self.chats[chat_id].get("messages", [])
        return []
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information without messages"""
        if chat_id in self.chats:
            chat = self.chats[chat_id].copy()
            # Don't return full messages for info
            chat["message_count"] = len(chat.get("messages", []))
            del chat["messages"]
            return chat
        return None
    
    def auto_update_title(self, chat_id: str, first_message: str) -> bool:
        """Auto-generate title from first message"""
        if chat_id in self.chats and self.chats[chat_id]["title"] == "New Chat":
            words = first_message.split()[:6]
            title = " ".join(words)
            if len(first_message) > 40:
                title += "..."
            
            self.chats[chat_id]["title"] = title
            self._save_chats()
            return True
        return False
    
    # ========================================
    # FOLDER MANAGEMENT
    # ========================================
    
    def create_folder(self, name: str, icon: str = "📁", color: str = "#FFD700") -> str:
        """Create a new folder"""
        folder_id = f"folder_{int(datetime.now().timestamp())}"
        
        self.folders[folder_id] = {
            "id": folder_id,
            "name": name,
            "icon": icon,
            "color": color,
            "is_system": False,
            "created": datetime.now().isoformat()
        }
        
        self._save_folders()
        return folder_id
    
    def delete_folder(self, folder_id: str) -> bool:
        """Delete a folder (moves chats to 'all')"""
        if folder_id in self.folders and not self.folders[folder_id].get("is_system", False):
            # Move all chats from this folder to 'all'
            for chat_id, chat_data in self.chats.items():
                if chat_data.get("folder_id") == folder_id:
                    chat_data["folder_id"] = "all"
            
            del self.folders[folder_id]
            self._save_folders()
            self._save_chats()
            return True
        return False
    
    def rename_folder(self, folder_id: str, new_name: str) -> bool:
        """Rename a folder"""
        if folder_id in self.folders and not self.folders[folder_id].get("is_system", False):
            self.folders[folder_id]["name"] = new_name
            self._save_folders()
            return True
        return False
    
    def get_folders(self) -> Dict[str, Any]:
        """Get all folders"""
        return self.folders
    
    def get_folder_chats(self, folder_id: str) -> List[str]:
        """Get all chat IDs in a folder"""
        return [
            chat_id for chat_id, chat_data in self.chats.items()
            if chat_data.get("folder_id") == folder_id
        ]
    
    # ========================================
    # SEARCH & FILTER
    # ========================================
    
    def search_chats(self, query: str) -> List[str]:
        """Search chats by title or message content"""
        results = []
        query_lower = query.lower()
        
        for chat_id, chat_data in self.chats.items():
            # Search in title
            if query_lower in chat_data["title"].lower():
                results.append(chat_id)
                continue
            
            # Search in messages
            for msg in chat_data.get("messages", []):
                if query_lower in msg.get("content", "").lower():
                    results.append(chat_id)
                    break
        
        return results
    
    def get_chats_by_folder(self, folder_id: str) -> Dict[str, Any]:
        """Get all chats in a specific folder"""
        folder_chats = {}
        for chat_id, chat_data in self.chats.items():
            if chat_data.get("folder_id") == folder_id:
                folder_chats[chat_id] = chat_data
        return folder_chats
    
    def get_pinned_chats(self) -> Dict[str, Any]:
        """Get all pinned chats"""
        return {
            chat_id: chat_data 
            for chat_id, chat_data in self.chats.items()
            if chat_data.get("pinned", False)
        }
    
    def get_recent_chats(self, limit: int = 10) -> List[str]:
        """Get most recently updated chats"""
        sorted_chats = sorted(
            self.chats.items(),
            key=lambda x: x[1].get("updated", x[1].get("created", "")),
            reverse=True
        )
        return [chat_id for chat_id, _ in sorted_chats[:limit]]
    
    # ========================================
    # EXPORT FUNCTIONS
    # ========================================
    
    def export_chat(self, chat_id: str, format: str = "txt") -> str:
        """Export chat in various formats"""
        if chat_id not in self.chats:
            return ""
        
        chat = self.chats[chat_id]
        
        if format == "txt":
            return self._export_txt(chat)
        elif format == "json":
            return json.dumps(chat, indent=2, ensure_ascii=False)
        elif format == "markdown":
            return self._export_markdown(chat)
        elif format == "html":
            return self._export_html(chat)
        
        return ""
    
    def _export_txt(self, chat: Dict[str, Any]) -> str:
        """Export as plain text"""
        content = f"Chat: {chat['title']}\n"
        content += f"Created: {chat.get('created', 'Unknown')}\n"
        content += f"Messages: {len(chat.get('messages', []))}\n"
        content += "=" * 60 + "\n\n"
        
        for msg in chat.get("messages", []):
            role = msg["role"].upper()
            timestamp = msg.get("timestamp", "")[:19]
            content += f"[{timestamp}] {role}: {msg['content']}\n\n"
        
        return content
    
    def _export_markdown(self, chat: Dict[str, Any]) -> str:
        """Export as Markdown"""
        content = f"# {chat['title']}\n\n"
        content += f"**Created:** {chat.get('created', 'Unknown')[:10]}\n"
        content += f"**Messages:** {len(chat.get('messages', []))}\n\n"
        content += "---\n\n"
        
        for msg in chat.get("messages", []):
            role = "**You**" if msg["role"] == "user" else "**AI**"
            content += f"{role}: {msg['content']}\n\n"
        
        return content
    
    def _export_html(self, chat: Dict[str, Any]) -> str:
        """Export as HTML (for PDF conversion)"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{chat['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #FFD700; padding-bottom: 20px; }}
        .message {{ margin: 15px 0; padding: 15px; border-radius: 10px; }}
        .user {{ background: #E3F2FD; margin-left: 50px; }}
        .assistant {{ background: #F5F5F5; margin-right: 50px; }}
        .timestamp {{ font-size: 0.8em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{chat['title']}</h1>
        <p>Created: {chat.get('created', 'Unknown')[:10]}</p>
    </div>
"""
        
        for msg in chat.get("messages", []):
            role_class = "user" if msg["role"] == "user" else "assistant"
            role_name = "You" if msg["role"] == "user" else "AI"
            timestamp = msg.get("timestamp", "")[:19]
            
            html += f"""
    <div class="message {role_class}">
        <div class="timestamp">{role_name} - {timestamp}</div>
        <div>{msg['content']}</div>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    # ========================================
    # STATISTICS
    # ========================================
    
    def get_stats(self, chat_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a chat"""
        if chat_id not in self.chats:
            return {}
        
        chat = self.chats[chat_id]
        messages = chat.get("messages", [])
        
        user_msgs = [m for m in messages if m["role"] == "user"]
        ai_msgs = [m for m in messages if m["role"] == "assistant"]
        
        total_words = sum(len(m["content"].split()) for m in messages)
        user_words = sum(len(m["content"].split()) for m in user_msgs)
        ai_words = sum(len(m["content"].split()) for m in ai_msgs)
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_msgs),
            "ai_messages": len(ai_msgs),
            "total_words": total_words,
            "user_words": user_words,
            "ai_words": ai_words,
            "avg_message_length": total_words // max(len(messages), 1),
            "created": chat.get("created", "Unknown"),
            "updated": chat.get("updated", "Unknown"),
            "folder": chat.get("folder_id", "all"),
            "tags": chat.get("tags", []),
            "pinned": chat.get("pinned", False)
        }
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get overall user statistics"""
        total_chats = len(self.chats)
        total_messages = sum(len(chat.get("messages", [])) for chat in self.chats.values())
        total_words = sum(
            sum(len(m["content"].split()) for m in chat.get("messages", []))
            for chat in self.chats.values()
        )
        
        # Get folder distribution
        folder_counts = {}
        for chat in self.chats.values():
            folder_id = chat.get("folder_id", "all")
            folder_counts[folder_id] = folder_counts.get(folder_id, 0) + 1
        
        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "total_words": total_words,
            "folder_distribution": folder_counts,
            "pinned_chats": sum(1 for chat in self.chats.values() if chat.get("pinned", False))
        }
    
    # ========================================
    # UTILITY FUNCTIONS
    # ========================================
    
    def clear_all_chats(self):
        """Clear all chats (dangerous!)"""
        self.chats = {}
        self._save_chats()
    
    def merge_chats(self, chat_id_1: str, chat_id_2: str) -> Optional[str]:
        """Merge two chats into one"""
        if chat_id_1 not in self.chats or chat_id_2 not in self.chats:
            return None
        
        # Combine messages
        merged_messages = (
            self.chats[chat_id_1]["messages"] + 
            self.chats[chat_id_2]["messages"]
        )
        
        # Sort by timestamp
        merged_messages.sort(key=lambda x: x.get("timestamp", ""))
        
        # Create new chat with merged content
        new_chat_id = self.create_new_chat(
            title=f"Merged: {self.chats[chat_id_1]['title']} + {self.chats[chat_id_2]['title']}"
        )
        
        self.chats[new_chat_id]["messages"] = merged_messages
        self._save_chats()
        
        # Delete original chats
        self.delete_chat(chat_id_1)
        self.delete_chat(chat_id_2)
        
        return new_chat_id
    
    def duplicate_chat(self, chat_id: str) -> Optional[str]:
        """Duplicate a chat"""
        if chat_id not in self.chats:
            return None
        
        original = self.chats[chat_id]
        new_chat_id = self.create_new_chat(
            title=f"Copy: {original['title']}",
            folder_id=original.get("folder_id", "all")
        )
        
        # Copy messages
        self.chats[new_chat_id]["messages"] = original["messages"].copy()
        self.chats[new_chat_id]["tags"] = original.get("tags", []).copy()
        self._save_chats()
        
        return new_chat_id