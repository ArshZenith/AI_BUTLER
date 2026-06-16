import streamlit as st
import json
from datetime import datetime

def export_chat(messages: list, format: str = "txt") -> str:
    """Export chat history"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        return json.dumps(messages, indent=2)
    else:
        text = f"Chat Export - {timestamp}\n" + "="*50 + "\n\n"
        for msg in messages:
            if msg['role'] != 'system':
                text += f"{msg['role'].upper()}: {msg['content']}\n\n"
        return text

def get_file_icon(file_type: str) -> str:
    """Get emoji icon for file type"""
    icons = {
        'pdf': '📄',
        'txt': '📝',
        'csv': '📊',
        'xlsx': '📈',
        'doc': '📃',
        'py': '🐍',
        'js': '🌐',
        'html': '🌐',
        'json': '📋'
    }
    return icons.get(file_type.lower(), '📎')

def format_bytes(size: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024