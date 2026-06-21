import streamlit as st
import os
import pytz
import requests
<<<<<<< HEAD
import base64
import json
from datetime import datetime, timedelta
from pathlib import Path
from config import Config
from agent_core import AIAgentSystem
from chat_manager import ChatManager

# ========================================
# 🎨 ULTIMATE UI WITH ALL FEATURES
# ========================================
def render_ultimate_ui(active_mode, matrix_mode=False, theme_mode="dark", current_theme="royal"):
    """Render ultimate UI with all enhancements"""
    
    # Theme definitions (Dark & Light modes)
    themes = {
        "dark": {
            "royal": {
                "butler": {"primary": "#FFD700", "secondary": "#B8860B", "bg": "#0a0a0f", "text": "#ffffff", "card_bg": "rgba(30,30,40,0.9)"},
                "roast": {"primary": "#FF4500", "secondary": "#8B0000", "bg": "#1a0505", "text": "#ffffff", "card_bg": "rgba(40,20,20,0.9)"},
                "code": {"primary": "#00FF88", "secondary": "#008B45", "bg": "#0a1410", "text": "#ffffff", "card_bg": "rgba(20,40,30,0.9)"},
                "zen": {"primary": "#A78BFA", "secondary": "#6B46C1", "bg": "#0f0f1a", "text": "#ffffff", "card_bg": "rgba(30,20,50,0.9)"}
            },
            "cyberpunk": {
                "butler": {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0a0a1a", "text": "#ffffff", "card_bg": "rgba(20,20,50,0.9)"},
                "roast": {"primary": "#FF0066", "secondary": "#CC0033", "bg": "#1a0510", "text": "#ffffff", "card_bg": "rgba(50,10,20,0.9)"},
                "code": {"primary": "#00FF66", "secondary": "#00CC33", "bg": "#0a1a10", "text": "#ffffff", "card_bg": "rgba(10,40,20,0.9)"},
                "zen": {"primary": "#FFCC00", "secondary": "#CC9900", "bg": "#1a1a0a", "text": "#ffffff", "card_bg": "rgba(40,40,10,0.9)"}
            },
            "neon": {
                "butler": {"primary": "#FF1493", "secondary": "#FF69B4", "bg": "#0a0005", "text": "#ffffff", "card_bg": "rgba(40,10,30,0.9)"},
                "roast": {"primary": "#FF4500", "secondary": "#FF6347", "bg": "#1a0500", "text": "#ffffff", "card_bg": "rgba(50,20,10,0.9)"},
                "code": {"primary": "#39FF14", "secondary": "#7FFF00", "bg": "#001a00", "text": "#ffffff", "card_bg": "rgba(10,40,10,0.9)"},
                "zen": {"primary": "#00FFFF", "secondary": "#40E0D0", "bg": "#001a1a", "text": "#ffffff", "card_bg": "rgba(10,40,40,0.9)"}
            },
            "ocean": {
                "butler": {"primary": "#00BFFF", "secondary": "#1E90FF", "bg": "#000a1a", "text": "#ffffff", "card_bg": "rgba(10,30,60,0.9)"},
                "roast": {"primary": "#FF6347", "secondary": "#FF4500", "bg": "#1a0505", "text": "#ffffff", "card_bg": "rgba(60,20,20,0.9)"},
                "code": {"primary": "#00CED1", "secondary": "#20B2AA", "bg": "#001a1a", "text": "#ffffff", "card_bg": "rgba(10,40,40,0.9)"},
                "zen": {"primary": "#87CEEB", "secondary": "#4682B4", "bg": "#001020", "text": "#ffffff", "card_bg": "rgba(10,30,50,0.9)"}
            },
            "forest": {
                "butler": {"primary": "#32CD32", "secondary": "#228B22", "bg": "#001a00", "text": "#ffffff", "card_bg": "rgba(10,40,10,0.9)"},
                "roast": {"primary": "#FF8C00", "secondary": "#FF4500", "bg": "#1a0a00", "text": "#ffffff", "card_bg": "rgba(50,30,10,0.9)"},
                "code": {"primary": "#9ACD32", "secondary": "#6B8E23", "bg": "#0a1a00", "text": "#ffffff", "card_bg": "rgba(30,40,10,0.9)"},
                "zen": {"primary": "#90EE90", "secondary": "#3CB371", "bg": "#001a0a", "text": "#ffffff", "card_bg": "rgba(10,40,20,0.9)"}
            }
        },
        "light": {
            "royal": {
                "butler": {"primary": "#B8860B", "secondary": "#FFD700", "bg": "#f5f5f5", "text": "#1a1a1a", "card_bg": "rgba(255,255,255,0.95)"},
                "roast": {"primary": "#8B0000", "secondary": "#FF4500", "bg": "#fff5f5", "text": "#1a1a1a", "card_bg": "rgba(255,240,240,0.95)"},
                "code": {"primary": "#008B45", "secondary": "#00FF88", "bg": "#f0fff4", "text": "#1a1a1a", "card_bg": "rgba(240,255,245,0.95)"},
                "zen": {"primary": "#6B46C1", "secondary": "#A78BFA", "bg": "#faf5ff", "text": "#1a1a1a", "card_bg": "rgba(250,245,255,0.95)"}
            },
            "cyberpunk": {
                "butler": {"primary": "#0099AA", "secondary": "#00FFFF", "bg": "#e8f9ff", "text": "#1a1a1a", "card_bg": "rgba(230,250,255,0.95)"},
                "roast": {"primary": "#CC0033", "secondary": "#FF0066", "bg": "#fff0f5", "text": "#1a1a1a", "card_bg": "rgba(255,240,245,0.95)"},
                "code": {"primary": "#00AA44", "secondary": "#00FF66", "bg": "#f0fff4", "text": "#1a1a1a", "card_bg": "rgba(240,255,245,0.95)"},
                "zen": {"primary": "#CC9900", "secondary": "#FFCC00", "bg": "#fffef0", "text": "#1a1a1a", "card_bg": "rgba(255,255,240,0.95)"}
            },
            "neon": {
                "butler": {"primary": "#CC0066", "secondary": "#FF3399", "bg": "#fff0f5", "text": "#1a1a1a", "card_bg": "rgba(255,240,245,0.95)"},
                "roast": {"primary": "#CC3300", "secondary": "#FF6633", "bg": "#fff5f0", "text": "#1a1a1a", "card_bg": "rgba(255,245,240,0.95)"},
                "code": {"primary": "#00CC00", "secondary": "#33FF33", "bg": "#f0fff0", "text": "#1a1a1a", "card_bg": "rgba(240,255,240,0.95)"},
                "zen": {"primary": "#00CCCC", "secondary": "#33FFFF", "bg": "#f0ffff", "text": "#1a1a1a", "card_bg": "rgba(240,255,255,0.95)"}
            },
            "ocean": {
                "butler": {"primary": "#0099CC", "secondary": "#33BBFF", "bg": "#f0f8ff", "text": "#1a1a1a", "card_bg": "rgba(240,248,255,0.95)"},
                "roast": {"primary": "#CC6633", "secondary": "#FF9966", "bg": "#fff5f0", "text": "#1a1a1a", "card_bg": "rgba(255,245,240,0.95)"},
                "code": {"primary": "#00AAAA", "secondary": "#33CCCC", "bg": "#f0ffff", "text": "#1a1a1a", "card_bg": "rgba(240,255,255,0.95)"},
                "zen": {"primary": "#6699CC", "secondary": "#99BBFF", "bg": "#f5f8ff", "text": "#1a1a1a", "card_bg": "rgba(245,248,255,0.95)"}
            },
            "forest": {
                "butler": {"primary": "#00AA00", "secondary": "#33CC33", "bg": "#f0fff0", "text": "#1a1a1a", "card_bg": "rgba(240,255,240,0.95)"},
                "roast": {"primary": "#CC6600", "secondary": "#FF9933", "bg": "#fff5f0", "text": "#1a1a1a", "card_bg": "rgba(255,245,240,0.95)"},
                "code": {"primary": "#66AA00", "secondary": "#99CC33", "bg": "#f5fff0", "text": "#1a1a1a", "card_bg": "rgba(245,255,240,0.95)"},
                "zen": {"primary": "#33AA66", "secondary": "#66CC99", "bg": "#f0fff5", "text": "#1a1a1a", "card_bg": "rgba(240,255,245,0.95)"}
            }
        }
    }
    
    t = themes.get(theme_mode, themes["dark"]).get(current_theme, themes["dark"]["royal"]).get(active_mode, themes["dark"]["royal"]["butler"])
    
    if matrix_mode:
        bg_color, primary_color, text_color = "#000000", "#00FF00", "#00FF00"
    else:
        bg_color, primary_color, text_color = t['bg'], t['primary'], t['text']
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;600;800&family=Fira+Code:wght@400;600&display=swap');
        
        * {{
            cursor: none;
        }}
        
        .custom-cursor {{
            position: fixed;
            width: 25px;
            height: 25px;
            border: 3px solid {primary_color};
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            transition: all 0.1s ease;
            box-shadow: 0 0 30px {primary_color}80, 0 0 60px {primary_color}40;
            background: {primary_color}20;
            backdrop-filter: blur(5px);
        }}
        
        .cursor-trail {{
            position: fixed;
            width: 10px;
            height: 10px;
            background: {primary_color};
            border-radius: 50%;
            pointer-events: none;
            z-index: 99998;
            opacity: 0.6;
            box-shadow: 0 0 15px {primary_color};
        }}
        
        .main {{ 
            background: linear-gradient(135deg, {bg_color} 0%, {theme_mode == 'light' and '#ffffff' or '#000000'} 100%) !important; 
            font-family: 'Inter', sans-serif;
            color: {text_color} !important;
            overflow-x: hidden;
        }}
        
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {theme_mode == 'light' and 'rgba(255,255,255,0.98)' or 'rgba(20,20,30,0.98)'} 0%, {theme_mode == 'light' and 'rgba(245,245,245,0.99)' or 'rgba(10,10,15,0.99)'} 100%) !important;
            backdrop-filter: blur(30px) saturate(180%);
            border-right: 2px solid {primary_color}40 !important;
            box-shadow: 5px 0 30px {primary_color}20 !important;
            max-height: 100vh;
            overflow-y: auto !important;
            color: {text_color} !important;
        }}
        
        #particles-js {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }}
        
        @keyframes bootFade {{ 
            0% {{ opacity: 1; transform: scale(1); }} 
            80% {{ opacity: 1; transform: scale(1.05); }} 
            100% {{ opacity: 0; visibility: hidden; transform: scale(1.1); }} 
        }}
        
        #boot-overlay {{
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100vw; 
            height: 100vh;
            background: radial-gradient(circle at center, #1a1a2e 0%, #000000 100%);
            z-index: 99999; 
            display: flex; 
            flex-direction: column;
            justify-content: center; 
            align-items: center;
            animation: bootFade 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards; 
            pointer-events: none;
        }}
        
        .boot-crown {{ 
            font-size: 5rem; 
            margin-bottom: 30px; 
            animation: crownFloat 2s ease-in-out infinite, crownGlow 2s ease-in-out infinite; 
            color: {primary_color};
            text-shadow: 0 0 50px {primary_color}80;
        }}
        
        @keyframes crownFloat {{ 
            0%, 100% {{ transform: translateY(0) rotate(0deg); }} 
            50% {{ transform: translateY(-20px) rotate(5deg); }} 
        }}
        
        @keyframes crownGlow {{
            0%, 100% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.5); }}
        }}
        
        .boot-text {{ 
            font-size: 2rem; 
            color: {primary_color}; 
            font-family: 'Playfair Display', serif; 
            letter-spacing: 5px; 
            animation: textGlow 2s ease-in-out infinite;
            text-shadow: 0 0 30px {primary_color}80;
        }}
        
        @keyframes textGlow {{
            0%, 100% {{ text-shadow: 0 0 30px {primary_color}80; }}
            50% {{ text-shadow: 0 0 60px {primary_color}80, 0 0 80px {primary_color}80; }}
        }}
        
        .boot-sub {{ 
            font-size: 1rem; 
            color: #888; 
            margin-top: 15px; 
            letter-spacing: 3px; 
            animation: fadeInUp 1s ease-out;
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .progress-bar {{ 
            width: 350px; 
            height: 4px; 
            background: #333; 
            margin-top: 40px; 
            border-radius: 4px; 
            overflow: hidden; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }}
        
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, {primary_color}, {t['secondary']}, {primary_color});
            background-size: 200% 100%;
            box-shadow: 0 0 30px {primary_color}80; 
            animation: load 2s ease-out forwards, gradientShift 3s ease-in-out infinite;
        }}
        
        @keyframes load {{ 
            0% {{ width: 0%; }} 
            100% {{ width: 100%; }} 
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        #matrix-canvas {{
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%;
            z-index: 9998; 
            pointer-events: none; 
            opacity: 0.3;
        }}
        
        #royal-grid {{
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, {primary_color}10 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, {t['secondary']}10 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, {primary_color}08 0%, transparent 40%);
            pointer-events: none; 
            z-index: -1;
            animation: gridPulse 4s ease-in-out infinite;
        }}
        
        @keyframes gridPulse {{
            0%, 100% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
        }}
        
        .stChatMessage {{
            background: {t['card_bg']} !important;
            border: 1px solid {primary_color}30 !important;
            border-radius: 20px !important;
            padding: 25px !important;
            margin-bottom: 20px !important;
            backdrop-filter: blur(20px) saturate(180%);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 40px {primary_color}15 !important;
            animation: messageSlide 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: {text_color} !important;
        }}
        
        .stChatMessage:hover {{
            border-color: {primary_color}60 !important;
            box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 60px {primary_color}25 !important;
            transform: translateY(-2px);
        }}
        
        @keyframes messageSlide {{ 
            from {{ opacity: 0; transform: translateY(30px) scale(0.95); }} 
            to {{ opacity: 1; transform: translateY(0) scale(1); }} 
        }}
        
        div[data-baseweb="base-input"] > div,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: {theme_mode == 'light' and 'rgba(255,255,255,0.9)' or 'rgba(20,20,30,0.8)'} !important;
            border: 2px solid {primary_color}40 !important;
            border-radius: 14px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            color: {text_color} !important;
        }}
        
        div[data-baseweb="base-input"]:focus-within > div,
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 40px {primary_color}40 !important;
            transform: translateY(-2px);
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {primary_color} 0%, {t['secondary']} 100%) !important;
            color: {theme_mode == 'light' and '#000000' or '#000000'} !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 12px 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 20px {primary_color}50 !important;
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}
        
        .stButton > button:hover::before {{
            width: 300px;
            height: 300px;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 35px {primary_color}70 !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(-1px) scale(0.98) !important;
        }}
        
        div[data-testid="stSidebar"] button[kind="secondary"] {{
            height: 90px !important;
            background: {theme_mode == 'light' and 'rgba(255,255,255,0.8)' or 'rgba(20, 20, 30, 0.7)'} !important;
            border: 2px solid {primary_color}20 !important;
            border-radius: 16px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            color: {text_color} !important;
            font-weight: 700 !important;
            margin-bottom: 12px !important;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}
        
        div[data-testid="stSidebar"] button[kind="secondary"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, {primary_color}30, transparent);
            transition: left 0.5s;
        }}
        
        div[data-testid="stSidebar"] button[kind="secondary"]:hover::before {{
            left: 100%;
        }}
        
        div[data-testid="stSidebar"] button[kind="secondary"]:hover {{
            transform: translateY(-5px) scale(1.03) !important;
            box-shadow: 0 10px 40px {primary_color}50 !important;
            border-color: {primary_color} !important;
            background: {theme_mode == 'light' and 'rgba(240,240,240,0.95)' or 'rgba(40, 40, 50, 0.9)'} !important;
        }}
        
        .agent-badge {{
            background: linear-gradient(135deg, {primary_color}25, {t['secondary']}25);
            color: {primary_color};
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            display: inline-block;
            margin-bottom: 15px;
            border: 2px solid {primary_color}60;
            box-shadow: 0 0 30px {primary_color}40, inset 0 0 20px {primary_color}20;
            font-weight: 700;
            letter-spacing: 1px;
            animation: badgePulse 2s ease-in-out infinite;
            backdrop-filter: blur(10px);
        }}
        
        @keyframes badgePulse {{
            0%, 100% {{ box-shadow: 0 0 30px {primary_color}40, inset 0 0 20px {primary_color}20; }}
            50% {{ box-shadow: 0 0 50px {primary_color}60, inset 0 0 30px {primary_color}30; }}
        }}
        
        .stat-card {{
            background: {t['card_bg']};
            border: 2px solid {primary_color}30;
            border-radius: 16px;
            padding: 20px;
            margin: 15px 0;
            backdrop-filter: blur(20px);
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px) scale(1.02);
            border-color: {primary_color}60;
            box-shadow: 0 12px 48px {primary_color}30;
        }}
        
        .stat-value {{ 
            font-size: 2rem; 
            font-weight: 800; 
            color: {primary_color};
            text-shadow: 0 0 20px {primary_color}80;
            animation: statGlow 2s ease-in-out infinite;
        }}
        
        @keyframes statGlow {{
            0%, 100% {{ text-shadow: 0 0 20px {primary_color}80; }}
            50% {{ text-shadow: 0 0 40px {primary_color}80, 0 0 60px {primary_color}80; }}
        }}
        
        .stat-label {{ 
            font-size: 0.85rem; 
            color: {theme_mode == 'light' and '#666' or '#888'}; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            margin-top: 8px;
        }}
        
        .toast {{
            position: fixed; 
            bottom: 120px; 
            right: 40px;
            background: linear-gradient(135deg, {primary_color}, {t['secondary']});
            color: {theme_mode == 'light' and '#000' or '#000'}; 
            padding: 18px 30px; 
            border-radius: 14px;
            font-weight: 700; 
            box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 60px {primary_color}60;
            z-index: 10000; 
            animation: toastSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1), toastFloat 3s ease-in-out infinite;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.2);
        }}
        
        @keyframes toastSlideIn {{ 
            from {{ transform: translateX(150%) rotate(5deg); opacity: 0; }} 
            to {{ transform: translateX(0) rotate(0deg); opacity: 1; }} 
        }}
        
        @keyframes toastFloat {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}
        
        ::-webkit-scrollbar {{ 
            width: 10px; 
        }}
        
        ::-webkit-scrollbar-track {{ 
            background: {theme_mode == 'light' and '#f0f0f0' or '#0a0a0f'}; 
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{ 
            background: linear-gradient(180deg, {primary_color}, {t['secondary']}); 
            border-radius: 10px;
            box-shadow: 0 0 20px {primary_color}80;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{ 
            background: {primary_color};
            box-shadow: 0 0 30px {primary_color}80;
        }}
        
        #MainMenu, footer, header {{ 
            visibility: hidden; 
            display: none !important;
        }}
        
        .ticker-card {{
            background: {t['card_bg']};
            border: 2px solid {primary_color}30;
            border-radius: 14px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(20px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        .ticker-card:hover {{
            transform: translateX(5px);
            border-color: {primary_color}60;
            box-shadow: 0 6px 30px {primary_color}30;
        }}
        
        .ticker-symbol {{ 
            font-weight: 700; 
            color: {primary_color}; 
            font-size: 1rem;
            text-shadow: 0 0 10px {primary_color}80;
        }}
        
        .ticker-price {{ 
            font-size: 1.2rem; 
            font-weight: 800;
            color: {t['secondary']};
            text-shadow: 0 0 15px {primary_color}80;
        }}
        
        .image-gen-box {{
            background: {t['card_bg']};
            border: 2px solid {primary_color}30;
            border-radius: 16px;
            padding: 20px;
            margin: 15px 0;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .image-gen-box:hover {{
            border-color: {primary_color}60;
            box-shadow: 0 12px 48px {primary_color}30;
        }}
        
        div[data-baseweb="select"] > div {{
            background: {theme_mode == 'light' and 'rgba(255,255,255,0.9)' or 'rgba(20,20,30,0.8)'} !important;
            border: 2px solid {primary_color}40 !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: {text_color} !important;
        }}
        
        div[data-baseweb="select"]:focus-within > div {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 30px {primary_color}30 !important;
            transform: translateY(-2px);
        }}
        
        .search-box {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: {t['card_bg']};
            border: 3px solid {primary_color};
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 0 100px {primary_color}80;
            z-index: 99999;
            min-width: 500px;
            backdrop-filter: blur(20px);
            display: none;
        }}
        
        .search-box.active {{
            display: block;
            animation: searchBoxSlide 0.3s ease-out;
        }}
        
        @keyframes searchBoxSlide {{
            from {{ opacity: 0; transform: translate(-50%, -60%); }}
            to {{ opacity: 1; transform: translate(-50%, -50%); }}
        }}
        
        .rename-input {{
            background: {theme_mode == 'light' and '#fff' or '#1a1a2e'} !important;
            border: 2px solid {primary_color} !important;
            padding: 10px !important;
            border-radius: 8px !important;
            color: {text_color} !important;
            width: 100% !important;
        }}
        
        .suggestion-chip {{
            display: inline-block;
            background: {primary_color}20;
            border: 2px solid {primary_color}40;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: {primary_color};
            font-size: 0.9em;
        }}
        
        .suggestion-chip:hover {{
            background: {primary_color}40;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px {primary_color}40;
        }}
        
        .folder-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: {primary_color}10;
            border: 1px solid {primary_color}20;
        }}
        
        .folder-item:hover {{
            background: {primary_color}20;
            transform: translateX(5px);
        }}
        
        .folder-icon {{
            margin-right: 8px;
            font-size: 1.2em;
        }}
        
        .folder-name {{
            flex-grow: 1;
            font-weight: 600;
        }}
        
        .folder-count {{
            background: {primary_color}30;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: 700;
        }}
    </style>
    
    <div class="custom-cursor" id="customCursor"></div>
    
    <div id="boot-overlay">
        <div class="boot-crown">👑</div>
        <div class="boot-text">INITIALIZING JARVIS</div>
        <div class="boot-sub">ULTIMATE AI EXPERIENCE</div>
        <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
    
    <div id="particles-js"></div>
    <canvas id="matrix-canvas"></canvas>
    <div id="royal-grid"></div>
    
    <script>
        const cursor = document.getElementById('customCursor');
        let mouseX = 0, mouseY = 0;
        let cursorX = 0, cursorY = 0;
        
        document.addEventListener('mousemove', (e) => {{
            mouseX = e.clientX;
            mouseY = e.clientY;
        }});
        
        function animateCursor() {{
            cursorX += (mouseX - cursorX) * 0.1;
            cursorY += (mouseY - cursorY) * 0.1;
            cursor.style.left = cursorX - 12.5 + 'px';
            cursor.style.top = cursorY - 12.5 + 'px';
            requestAnimationFrame(animateCursor);
        }}
        
        animateCursor();
        
        const trailElements = [];
        for (let i = 0; i < 10; i++) {{
            const trail = document.createElement('div');
            trail.className = 'cursor-trail';
            document.body.appendChild(trail);
            trailElements.push(trail);
        }}
        
        function animateTrail() {{
            trailElements.forEach((trail, index) => {{
                const prev = index === 0 ? {{ x: mouseX, y: mouseY }} : {{
                    x: parseFloat(trailElements[index - 1].style.left) + 5 || mouseX,
                    y: parseFloat(trailElements[index - 1].style.top) + 5 || mouseY
                }};
                
                trail.style.left = prev.x - 5 + 'px';
                trail.style.top = prev.y - 5 + 'px';
                trail.style.opacity = 0.6 - (index * 0.06);
            }});
            requestAnimationFrame(animateTrail);
        }}
        
        animateTrail();
        
        if ('ontouchstart' in window) {{
            cursor.style.display = 'none';
            document.querySelectorAll('.cursor-trail').forEach(trail => trail.style.display = 'none');
            document.body.style.cursor = 'auto';
        }}
        
        const particlesContainer = document.getElementById('particles-js');
        for (let i = 0; i < 50; i++) {{
            const particle = document.createElement('div');
            const duration = 10 + Math.random() * 10;
            const delay = Math.random() * 5;
            const size = 2 + Math.random() * 4;
            const opacity = 0.2 + Math.random() * 0.5;
            
            particle.style.position = 'absolute';
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.background = '{primary_color}';
            particle.style.borderRadius = '50%';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.opacity = opacity;
            particle.style.pointerEvents = 'none';
            particle.style.boxShadow = `0 0 20px {primary_color}`;
            particle.style.animation = `particleFloat ${{duration}}s ease-in-out infinite`;
            particle.style.animationDelay = `${{delay}}s`;
            particlesContainer.appendChild(particle);
        }}
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes particleFloat {{
                0%, 100% {{ transform: translateY(0) translateX(0); }}
                25% {{ transform: translateY(-30px) translateX(15px); }}
                50% {{ transform: translateY(-15px) translateX(-15px); }}
                75% {{ transform: translateY(-45px) translateX(10px); }}
            }}
        `;
        document.head.appendChild(style);
        
=======
from datetime import datetime, timedelta
import time
import json
from config import Config 

# ==========================================
# CONFIG & STATE INITIALIZATION
# ==========================================
def initialize_state():
    """Centralized state management to prevent undefined variables"""
    defaults = {
        "butler": None,
        "chat_manager": None,
        "current_chat_id": None,
        "active_mode": "butler",
        "last_processed_audio": None,
        "toast_message": None,
        "matrix_mode": False,
        "timer_minutes": 25,
        "timer_running": False,
        "timer_end_time": None,
        "selected_tool": "💬 Normal Chat",
        "username": "Guest",
        "konami_sequence": [],
        "secret_unlocked": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Lazy load heavy objects only once
    if st.session_state.butler is None:
        from agent_core import AIAgentSystem
        st.session_state.butler = AIAgentSystem()
        
    if st.session_state.chat_manager is None:
        from chat_manager import ChatManager
        st.session_state.chat_manager = ChatManager()
        
    if st.session_state.current_chat_id is None:
        cm = st.session_state.chat_manager
        all_chats = cm.chats
        st.session_state.current_chat_id = list(all_chats.keys())[0] if all_chats else cm.create_new_chat("👑 Royal Session")

initialize_state()

# ==========================================
# LUXURY UI ENGINE
# ==========================================
def render_luxury_ui(active_mode, matrix_mode=False, secret_unlocked=False):
    """Dynamic theme injection with glassmorphism and animations"""
    themes = {
        "butler": {"primary": "#FFD700", "secondary": "#B8860B", "bg": "#0a0a0f"},
        "roast": {"primary": "#FF4500", "secondary": "#8B0000", "bg": "#1a0505"},
        "code": {"primary": "#00FF88", "secondary": "#008B45", "bg": "#0a1410"},
        "zen": {"primary": "#A78BFA", "secondary": "#6B46C1", "bg": "#0f0f1a"}
    }
    
    t = themes.get(active_mode, themes["butler"])
    
    if secret_unlocked or matrix_mode:
        bg_color, primary_color, secondary_color = "#000000", "#00FF00", "#008800"
    else:
        bg_color, primary_color, secondary_color = t['bg'], t['primary'], t['secondary']
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        .main {{ background: linear-gradient(135deg, {bg_color} 0%, #000000 100%) !important; font-family: 'Inter', sans-serif; }}
        
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(20,20,30,0.95) 0%, rgba(10,10,15,0.98) 100%) !important;
            backdrop-filter: blur(20px);
            border-right: 2px solid {primary_color}40 !important;
            max-height: 100vh;
            overflow-y: auto !important;
        }}
        
        @keyframes bootFade {{ 0% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; visibility: hidden; }} }}
        #boot-overlay {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: radial-gradient(circle at center, #1a1a2e 0%, #000000 100%);
            z-index: 9999; display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            animation: bootFade 2s ease-out forwards; pointer-events: none;
        }}
        .boot-crown {{ font-size: 4rem; margin-bottom: 20px; animation: crownFloat 2s ease-in-out infinite; color: {primary_color}; }}
        @keyframes crownFloat {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
        .boot-text {{ font-size: 1.5rem; color: {primary_color}; font-family: 'Playfair Display', serif; letter-spacing: 3px; }}
        .progress-bar {{ width: 300px; height: 3px; background: #333; margin-top: 30px; border-radius: 2px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, {primary_color}, {secondary_color}); box-shadow: 0 0 20px {primary_color}; animation: load 1.5s ease-out forwards; }}
        @keyframes load {{ 0% {{ width: 0%; }} 100% {{ width: 100%; }} }}
        
        #matrix-canvas {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9998; pointer-events: none; opacity: 0.3; }}
        
        .stChatMessage {{
            background: linear-gradient(135deg, rgba(30,30,40,0.8) 0%, rgba(20,20,30,0.9) 100%) !important;
            border: 1px solid {primary_color}30 !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 30px {primary_color}10 !important;
            animation: messageSlide 0.4s ease-out;
        }}
        @keyframes messageSlide {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%) !important;
            color: #000 !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px {primary_color}40 !important;
        }}
        .stButton > button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 6px 25px {primary_color}60 !important; }}
        
        .agent-badge {{
            background: linear-gradient(135deg, {primary_color}20, {secondary_color}20);
            color: {primary_color};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            display: inline-block;
            margin-bottom: 12px;
            border: 1px solid {primary_color}50;
            font-weight: 600;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(30,30,40,0.8), rgba(20,20,30,0.9));
            border: 1px solid {primary_color}30;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
        }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; color: {primary_color}; }}
        .stat-label {{ font-size: 0.8rem; color: #888; text-transform: uppercase; }}
        
        .toast {{
            position: fixed; bottom: 100px; right: 30px;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: #000; padding: 15px 25px; border-radius: 10px;
            font-weight: 600; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            z-index: 10000; animation: toastSlide 0.4s ease-out;
        }}
        @keyframes toastSlide {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }}
        
        #MainMenu, footer {{ visibility: hidden; }}
        
        .ticker-card {{
            background: linear-gradient(135deg, rgba(30,30,40,0.8), rgba(20,20,30,0.9));
            border: 1px solid {primary_color}30;
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .ticker-symbol {{ font-weight: bold; color: {primary_color}; font-size: 0.9rem; }}
        .ticker-price {{ font-size: 1.1rem; font-weight: 700; }}
    </style>
    
    <div id="boot-overlay">
        <div class="boot-crown"></div>
        <div class="boot-text">INITIALIZING JARVIS</div>
        <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
    
    <canvas id="matrix-canvas"></canvas>
    
    <script>
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
<<<<<<< HEAD
        
=======
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = Array(Math.floor(columns)).fill(1);
        let matrixActive = false;
<<<<<<< HEAD
        
        function drawMatrix() {{
            if (!matrixActive) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                return;
            }}
=======
        function drawMatrix() {{
            if (!matrixActive) {{ ctx.clearRect(0, 0, canvas.width, canvas.height); return; }}
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';
<<<<<<< HEAD
            
            for (let i = 0; i < drops.length; i++) {{
                const text = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975)
                    drops[i] = 0;
                drops[i]++;
            }}
        }}
        
        setInterval(drawMatrix, 35);
        
        window.addEventListener('message', (event) => {{
            if (event.data.type === 'matrix_toggle') {{
                matrixActive = event.data.active;
            }}
        }});
        
        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});
        
        document.addEventListener('keydown', (e) => {{
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {{
                e.preventDefault();
                window.parent.postMessage({{type: 'open_search'}}, '*');
            }}
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {{
                e.preventDefault();
                window.parent.postMessage({{type: 'new_chat'}}, '*');
            }}
        }});
    </script>
    """, unsafe_allow_html=True)

# ========================================
# 📁 USER DATA MANAGEMENT
# ========================================
def get_user_data_path(username):
    """Get user-specific data directory"""
    base_path = Path("user_data")
    user_path = base_path / username.lower().replace(" ", "_")
    user_path.mkdir(parents=True, exist_ok=True)
    return user_path

def load_user_settings(username):
    """Load user-specific settings"""
    settings_path = get_user_data_path(username) / "settings.json"
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    return {
        "theme_mode": "dark",
        "current_theme": "royal",
        "language": "en"
    }

def save_user_settings(username, settings):
    """Save user-specific settings"""
    settings_path = get_user_data_path(username) / "settings.json"
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

def load_user_stats(username):
    """Load user statistics"""
    stats_path = get_user_data_path(username) / "stats.json"
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            return json.load(f)
    return {
        "total_chats": 0,
        "total_messages": 0,
        "tools_used": {},
        "last_active": None
    }

def save_user_stats(username, stats):
    """Save user statistics"""
    stats_path = get_user_data_path(username) / "stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

def update_user_stats(username, action, tool_name=None):
    """Update user statistics"""
    stats = load_user_stats(username)
    
    if action == "new_chat":
        stats["total_chats"] += 1
    elif action == "message":
        stats["total_messages"] += 1
    elif action == "tool" and tool_name:
        stats["tools_used"][tool_name] = stats["tools_used"].get(tool_name, 0) + 1
    
    stats["last_active"] = datetime.now().isoformat()
    save_user_stats(username, stats)
    return stats

# ========================================
# 💾 STATE INITIALIZATION
# ========================================
if "butler" not in st.session_state:
    st.session_state.butler = AIAgentSystem()

if "username" not in st.session_state:
    st.session_state.username = "Guest"

if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False

# Load user settings after authentication
if st.session_state.user_authenticated:
    user_settings = load_user_settings(st.session_state.username)
    
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = user_settings.get("theme_mode", "dark")
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = user_settings.get("current_theme", "royal")
    if "language" not in st.session_state:
        st.session_state.language = user_settings.get("language", "en")

if "chat_manager" not in st.session_state:
    if st.session_state.user_authenticated:
        user_path = get_user_data_path(st.session_state.username)
        st.session_state.chat_manager = ChatManager(str(user_path))
    else:
        st.session_state.chat_manager = ChatManager()

if "current_chat_id" not in st.session_state:
    all_chats = st.session_state.chat_manager.chats
    st.session_state.current_chat_id = list(all_chats.keys())[0] if all_chats else st.session_state.chat_manager.create_new_chat("👑 Royal Session")

if "active_mode" not in st.session_state:
    st.session_state.active_mode = "butler"
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "toast_message" not in st.session_state:
    st.session_state.toast_message = None
if "matrix_mode" not in st.session_state:
    st.session_state.matrix_mode = False
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""
if "voice_speed" not in st.session_state:
    st.session_state.voice_speed = "normal"
if "voice_lang" not in st.session_state:
    st.session_state.voice_lang = "en"
if "timer_minutes" not in st.session_state:
    st.session_state.timer_minutes = 25
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_end_time" not in st.session_state:
    st.session_state.timer_end_time = None
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "💬 Normal Chat"
if "gmail_authenticated" not in st.session_state:
    st.session_state.gmail_authenticated = False
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "default"
if "renaming_chat_id" not in st.session_state:
    st.session_state.renaming_chat_id = None
if "current_folder" not in st.session_state:
    st.session_state.current_folder = "all"

# ========================================
# 🔐 USER LOGIN SCREEN
# ========================================
# ========================================
# 🔐 NEURAL LINK LOGIN SCREEN
# ========================================
if not st.session_state.user_authenticated:
    st.markdown("""
    <div style='text-align: center; padding: 80px 20px;'>
        <h1 style='font-family: Playfair Display; color: #FFD700; font-size: 3.5rem; margin-bottom: 10px;'>👑 JARVIS BUTLER</h1>
        <p style='color: #888; font-size: 1.1rem; letter-spacing: 2px;'>ULTIMATE AI EXPERIENCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #FFD700;'>Initialize Secure Handshake</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #aaa; margin-bottom: 20px;'>Enter your Comm-Link to access the mainframe</p>", unsafe_allow_html=True)
        
        email_input = st.text_input(
            "ENTER COMM-LINK (Email):",
            placeholder="operator@domain.com",
            key="login_email"
        )
        
        if st.button("🚀 INITIALIZE SECURE HANDSHAKE", type="primary", use_container_width=True):
            if email_input and "@" in email_input:
                # Extract username from email (e.g., arsh@gmail.com -> Arsh)
                raw_name = email_input.split('@')[0]
                clean_name = raw_name.replace('.', ' ').replace('_', ' ').title()
                
                st.session_state.username = clean_name
                st.session_state.user_email = email_input # Save email for future use
                st.session_state.user_authenticated = True
                
                # Initialize user data with safe folder name
                safe_folder_name = email_input.lower().replace('@', '_at_').replace('.', '_')
                user_path = get_user_data_path(safe_folder_name)
                st.session_state.chat_manager = ChatManager(str(user_path))
                
                # Load settings
                user_settings = load_user_settings(safe_folder_name)
                st.session_state.theme_mode = user_settings.get("theme_mode", "dark")
                st.session_state.current_theme = user_settings.get("current_theme", "royal")
                
                update_user_stats(safe_folder_name, "login")
                
                st.success(f"✅ Handshake Successful! Welcome, {clean_name}.")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Invalid Comm-Link format. Please enter a valid email.")
    
    st.stop()
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px;'>
        <h1 style='font-family: Playfair Display; color: #FFD700; font-size: 4rem; margin-bottom: 20px;'>👑 JARVIS</h1>
        <p style='color: #888; font-size: 1.2rem; letter-spacing: 3px;'>ULTIMATE AI EXPERIENCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #FFD700;'>Enter Your Name to Continue</h3>", unsafe_allow_html=True)
        
        username_input = st.text_input(
            "Username:",
            placeholder="Enter your name (e.g., Arsh)",
            key="login_username"
        )
        
        if st.button("🚀 Enter Jarvis", type="primary", use_container_width=True):
            if username_input and len(username_input.strip()) >= 2:
                st.session_state.username = username_input.strip()
                st.session_state.user_authenticated = True
                
                # Initialize user data
                user_path = get_user_data_path(st.session_state.username)
                st.session_state.chat_manager = ChatManager(str(user_path))
                
                # Load or create default settings
                user_settings = load_user_settings(st.session_state.username)
                st.session_state.theme_mode = user_settings.get("theme_mode", "dark")
                st.session_state.current_theme = user_settings.get("current_theme", "royal")
                st.session_state.language = user_settings.get("language", "en")
                
                # Update stats
                update_user_stats(st.session_state.username, "login")
                
                st.success(f"Welcome, {st.session_state.username}! 👑")
                st.rerun()
            else:
                st.error("Please enter a valid name (at least 2 characters)")
    
    st.stop()

# Render UI after authentication
render_ultimate_ui(
    st.session_state.active_mode, 
    st.session_state.matrix_mode,
    st.session_state.theme_mode,
    st.session_state.current_theme
)

# ========================================
# 🎛️ ULTIMATE SIDEBAR
# ========================================
with st.sidebar:
    # User Profile Header
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 0; border-bottom: 2px solid {st.session_state.theme_mode == 'dark' and '#FFD700' or '#B8860B'}40; margin-bottom: 20px;'>
        <div style='width: 60px; height: 60px; background: linear-gradient(135deg, #FFD700, #B8860B); border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 2rem;'>👑</div>
        <h2 style='font-family: Playfair Display; color: {st.session_state.theme_mode == 'dark' and '#FFD700' or '#B8860B'}; margin: 0; font-size: 1.8rem;'>{st.session_state.username}</h2>
        <p style='color: #888; font-size: 0.85rem; margin: 5px 0 0 0;'>Royal Member</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>⚡ QUICK ACTIONS</h4>", unsafe_allow_html=True)
    
    col_qa1, col_qa2 = st.columns(2)
    with col_qa1:
        if st.button("➕ New", key="new_chat_btn", use_container_width=True):
            st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("💬 New Chat", st.session_state.current_folder)
            update_user_stats(st.session_state.username, "new_chat")
            st.session_state.toast_message = "New chat created! ✨"
            st.rerun()
    
    with col_qa2:
        theme_mode = "Light ☀️" if st.session_state.theme_mode == "dark" else "Dark 🌙"
        if st.button(theme_mode, key="theme_toggle", use_container_width=True):
            st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
            user_settings = load_user_settings(st.session_state.username)
            user_settings["theme_mode"] = st.session_state.theme_mode
            save_user_settings(st.session_state.username, user_settings)
            st.session_state.toast_message = f"Switched to {st.session_state.theme_mode} mode!"
            st.rerun()
    
    st.divider()
    
    # Theme Selector
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>🎨 THEME</h4>", unsafe_allow_html=True)
    theme_options = {
        "royal": "👑 Royal Gold",
        "cyberpunk": "🤖 Cyberpunk",
        "neon": "🌸 Neon Glow",
        "ocean": "🌊 Ocean Blue",
        "forest": "🌲 Forest Green"
    }
    
    selected_theme = st.selectbox(
        "Choose theme:",
        options=list(theme_options.keys()),
        format_func=lambda x: theme_options[x],
        index=list(theme_options.keys()).index(st.session_state.current_theme),
        key="theme_selector"
    )
    
    if selected_theme != st.session_state.current_theme:
        st.session_state.current_theme = selected_theme
        user_settings = load_user_settings(st.session_state.username)
        user_settings["current_theme"] = selected_theme
        save_user_settings(st.session_state.username, user_settings)
        st.session_state.toast_message = f"Theme: {theme_options[selected_theme]}!"
        st.rerun()
    
    st.divider()
    
    # Mode Selection
    st.markdown("<h4 style='color:#FFD700; text-align:center; margin-bottom: 15px;'>⚡ SELECT MODE</h4>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👑\nButler", key="p_butler", use_container_width=True, type="secondary"):
            st.session_state.active_mode = "butler"
            st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("👑 Butler Session", st.session_state.current_folder)
            update_user_stats(st.session_state.username, "new_chat")
            st.session_state.toast_message = "Butler Mode! 👑"
            st.rerun()
    with c2:
        if st.button("🔥\nSavage", key="p_savage", use_container_width=True, type="secondary"):
            st.session_state.active_mode = "roast"
            st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("🔥 Savage Session", st.session_state.current_folder)
            update_user_stats(st.session_state.username, "new_chat")
            st.session_state.toast_message = "Savage Mode! 🔥"
            st.rerun()

    c3, c4 = st.columns(2)
    with c3:
        if st.button("💻\nCode", key="p_code", use_container_width=True, type="secondary"):
            st.session_state.active_mode = "code"
            st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("💻 Code Dojo", st.session_state.current_folder)
            update_user_stats(st.session_state.username, "new_chat")
            st.session_state.toast_message = "Code Dojo! 💻"
            st.rerun()
    with c4:
        if st.button("🧘\nZen", key="p_zen", use_container_width=True, type="secondary"):
            st.session_state.active_mode = "zen"
            st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("🧘 Zen Mode", st.session_state.current_folder)
            update_user_stats(st.session_state.username, "new_chat")
            st.session_state.toast_message = "Zen Mode! 🧘"
            st.rerun()
            
    st.divider()
    
    # AI Personas
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>🎭 AI PERSONA</h4>", unsafe_allow_html=True)
    persona_options = {
        "default": "🤖 Default",
        "professor": "🎓 Professor",
        "business": "💼 Business",
        "friendly": "😎 Friendly"
    }
    
    selected_persona = st.selectbox(
        "Choose persona:",
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x],
        index=list(persona_options.keys()).index(st.session_state.current_persona),
        key="persona_selector"
    )
    
    if selected_persona != st.session_state.current_persona:
        st.session_state.current_persona = selected_persona
        st.session_state.toast_message = f"Persona: {persona_options[selected_persona]}!"
        st.rerun()
    
    st.divider()
    
    # Tools
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>🛠️ SUPER TOOLS (30)</h4>", unsafe_allow_html=True)
    
    tool_options = [
        "💬 Normal Chat", #"📧 Gmail Summarizer",
         "💻 GitHub Assistant", "👤 GitHub Profile Analyzer",
        "📺 YouTube Summarizer", "📄 PDF Chat", "✍️ Quick Writer", "💻 Code Helper", "📰 Daily Briefing",
        "🔍 Web Search", "📄 Article Summarizer", "🃏 Flashcard Generator", "📝 Quiz Generator",
        "🌐 Translator", "📊 Text Analyzer", "💡 Idea Generator", "🐙 GitHub Analyzer",
        "📄 Resume Analyzer", "📋 Meeting Notes", "🔐 Password Generator", "📱 QR Code Generator",
        "🍳 Recipe Generator", "📊 CSV Data Analyzer", "✍️ Text to Handwriting", "🎨 Color Palette",
        "📧 Email Optimizer", "🎨 AI Image Studio", "📸 Magic Vision", "🗣️ AI Debate Partner", "🌙 Dream Interpreter"
    ]
    
    if st.session_state.selected_tool not in tool_options:
        st.session_state.selected_tool = "💬 Normal Chat"
    
    selected_tool = st.selectbox(
        "Select tool:",
        options=tool_options,
        index=tool_options.index(st.session_state.selected_tool),
        key="tool_selector"
    )
    
    if selected_tool != st.session_state.selected_tool:
        st.session_state.selected_tool = selected_tool
        update_user_stats(st.session_state.username, "tool", selected_tool)
        st.session_state.toast_message = f"Tool: {selected_tool}!"
        st.rerun()
    
    st.divider()
    
    # Market Ticker
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>📈 MARKETS</h4>", unsafe_allow_html=True)
    try:
        import yfinance as yf
        tickers = {"Bitcoin": "BTC-USD", "Apple": "AAPL", "Google": "GOOGL", "Tesla": "TSLA"}
        
=======
            for (let i = 0; i < drops.length; i++) {{
                const text = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }}
        }}
        setInterval(drawMatrix, 35);
        window.addEventListener('message', (event) => {{ if (event.data.type === 'matrix_toggle') matrixActive = event.data.active; }});
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# CACHED FUNCTIONS
# ==========================================
@st.cache_resource
def get_groq_client():
    from groq import Groq
    from config import Config
    return Groq(api_key=Config.GROQ_API_KEY)

@st.cache_data(ttl=300)
def get_market_data():
    try:
        import yfinance as yf
        tickers = {"Bitcoin": "BTC-USD", "Apple": "AAPL", "Google": "GOOGL"}
        data = {}
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
        for name, symbol in tickers.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
<<<<<<< HEAD
                current_price = info.last_price
                st.markdown(f"""
                <div class="ticker-card">
                    <span class="ticker-symbol">{name}</span>
                    <span class="ticker-price">${current_price:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
    except:
        pass
    
    st.divider()
    
    # Matrix Mode
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>🟢 MATRIX</h4>", unsafe_allow_html=True)
    matrix_toggle = st.toggle("Matrix Rain", value=st.session_state.matrix_mode, key="matrix_toggle")
    if matrix_toggle != st.session_state.matrix_mode:
        st.session_state.matrix_mode = matrix_toggle
        st.session_state.toast_message = "Matrix mode! 🟢" if matrix_toggle else "Matrix off"
        st.rerun()
    
    st.components.v1.html(f"""
    <script>
        window.parent.postMessage({{type: 'matrix_toggle', active: {str(matrix_toggle).lower()}}}, '*');
    </script>
    """, height=0)
    
    st.divider()
    
    # Timer
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>⏱️ TIMER</h4>", unsafe_allow_html=True)
    
    timer_mins = st.number_input(
        "Minutes:", 
        min_value=1, 
        max_value=120, 
        value=st.session_state.timer_minutes, 
        key="timer_input",
        disabled=st.session_state.timer_running
    )
    
    if timer_mins != st.session_state.timer_minutes and not st.session_state.timer_running:
        st.session_state.timer_minutes = timer_mins
    
    col_timer1, col_timer2 = st.columns(2)
    with col_timer1:
        if st.button("▶️", key="start_timer", use_container_width=True, disabled=st.session_state.timer_running):
            st.session_state.timer_end_time = datetime.now() + timedelta(minutes=timer_mins)
            st.session_state.timer_running = True
            st.session_state.toast_message = f"Timer: {timer_mins}min ⏱️"
            st.rerun()
    
    with col_timer2:
        if st.button("⏹️", key="stop_timer", use_container_width=True, disabled=not st.session_state.timer_running):
            st.session_state.timer_running = False
            st.session_state.toast_message = "Timer stopped"
            st.rerun()
    
    if st.session_state.timer_running and st.session_state.timer_end_time:
        remaining = st.session_state.timer_end_time - datetime.now()
        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            st.markdown(f"<div style='text-align:center; font-size:2rem; font-weight:800; color:#FFD700; padding: 15px;'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        else:
            st.balloons()
            st.session_state.toast_message = "⏰ Timer Complete!"
            st.session_state.timer_running = False
            st.rerun()
    
    st.divider()
    
    # Chat Folders
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>📁 CHAT FOLDERS</h4>", unsafe_allow_html=True)
    
    folders = st.session_state.chat_manager.get_folders()
    for folder_id, folder_data in folders.items():
        if folder_data.get("is_system", False) or folder_id == "all":
            continue
            
        folder_chats = st.session_state.chat_manager.get_folder_chats(folder_id)
        is_selected = st.session_state.current_folder == folder_id
        
        col_f1, col_f2 = st.columns([4, 1])
        with col_f1:
            if st.button(
                f"{folder_data['icon']} {folder_data['name']}",
                key=f"folder_{folder_id}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.current_folder = folder_id
                st.rerun()
        with col_f2:
            if st.button("🗑️", key=f"del_folder_{folder_id}"):
                st.session_state.chat_manager.delete_folder(folder_id)
                if st.session_state.current_folder == folder_id:
                    st.session_state.current_folder = "all"
                st.rerun()
    
    # Create new folder
    new_folder_name = st.text_input("New Folder:", key="new_folder_name", label_visibility="collapsed")
    if st.button("➕ Create Folder", key="create_folder_btn", use_container_width=True):
        if new_folder_name.strip():
            st.session_state.chat_manager.create_folder(new_folder_name.strip())
            st.session_state.toast_message = f"Folder '{new_folder_name}' created!"
            st.rerun()
    
    st.divider()
    
    # Chats with Rename
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>📜 CHATS</h4>", unsafe_allow_html=True)
    
    search_query = st.text_input("🔍 Search...", key="chat_search", label_visibility="collapsed")
    
    # Get chats based on current folder
    if st.session_state.current_folder == "all":
        chat_ids = list(st.session_state.chat_manager.chats.keys())
    elif st.session_state.current_folder == "pinned":
        chat_ids = list(st.session_state.chat_manager.get_pinned_chats().keys())
    else:
        chat_ids = st.session_state.chat_manager.get_folder_chats(st.session_state.current_folder)
    
    pinned_chats = [cid for cid in chat_ids if st.session_state.chat_manager.chats[cid].get("pinned")]
    other_chats = [cid for cid in chat_ids if not st.session_state.chat_manager.chats[cid].get("pinned")]
    
    if search_query:
        chat_ids = st.session_state.chat_manager.search_chats(search_query)
    else:
        chat_ids = pinned_chats + other_chats
    
    for chat_id in chat_ids[:15]:
        chat_data = st.session_state.chat_manager.chats.get(chat_id, {})
        
        if st.session_state.renaming_chat_id == chat_id:
            # Rename mode
            new_name = st.text_input(
                "New name:",
                value=chat_data.get("title", "Chat"),
                key=f"rename_{chat_id}"
            )
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("✅", key=f"save_rename_{chat_id}", use_container_width=True):
                    st.session_state.chat_manager.rename_chat(chat_id, new_name)
                    st.session_state.renaming_chat_id = None
                    st.session_state.toast_message = "Chat renamed! ✏️"
                    st.rerun()
            with col_r2:
                if st.button("❌", key=f"cancel_rename_{chat_id}", use_container_width=True):
                    st.session_state.renaming_chat_id = None
                    st.rerun()
        else:
            # Normal mode
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
=======
                data[name] = f"${info.last_price:,.2f}"
            except:
                data[name] = "N/A"
        return data
    except:
        return {"Error": "Install yfinance"}

# ==========================================
# KONAMI CODE
# ==========================================
def check_konami_code():
    keys = st.query_params.get_all("key")
    if keys:
        st.session_state.konami_sequence.extend(keys)
        st.session_state.konami_sequence = st.session_state.konami_sequence[-8:]
        konami = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "b", "a"]
        if st.session_state.konami_sequence == konami:
            st.session_state.secret_unlocked = True
            st.session_state.toast_message = "🎮 SECRET MATRIX MODE UNLOCKED!"
            st.rerun()

# ==========================================
# SIDEBAR
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:#FFD700; font-family:Playfair Display;'>👑 JARVIS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; font-size:0.8rem;'>Royal AI Experience</p>", unsafe_allow_html=True)
        st.divider()
        
        st.session_state.username = st.text_input(
            "Your Name:", 
            value=st.session_state.get("username", "Guest"),
            key="username_input"
        )
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700; text-align:center;'>SELECT REALITY</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👑\nButler", key="p_butler", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "butler"
                st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("👑 Butler Session")
                st.session_state.toast_message = "Welcome to Butler Mode"
                st.rerun()
        with c2:
            if st.button("🔥\nSavage", key="p_savage", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "roast"
                st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("🔥 Savage Session")
                st.session_state.toast_message = "Savage Mode Activated"
                st.rerun()

        c3, c4 = st.columns(2)
        with c3:
            if st.button("💻\nCode", key="p_code", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "code"
                st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("💻 Code Dojo")
                st.session_state.toast_message = "Code Dojo Ready"
                st.rerun()
        with c4:
            if st.button("🧘\nZen", key="p_zen", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "zen"
                st.session_state.current_chat_id = st.session_state.chat_manager.create_new_chat("🧘 Zen Mode")
                st.session_state.toast_message = "Zen Mode Active"
                st.rerun()
                
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>🛠️ SUPER TOOLS</h4>", unsafe_allow_html=True)
        
        tool_options = [
            "💬 Normal Chat",
            "📺 YouTube Summarizer",
            "📄 PDF Chat",
            "✍️ Quick Writer",
            "💻 Code Helper",
            "📰 Daily Briefing",
            "🔍 Web Search",
            "📄 Article Summarizer",
            "🃏 Flashcard Generator",
            "📝 Quiz Generator",
            "🌐 Translator",
            "📊 Text Analyzer",
            "💡 Idea Generator",
            "🐙 GitHub Analyzer",
            "📄 Resume Analyzer",
            "📋 Meeting Notes",
            "🔐 Password Generator",
            "📱 QR Code Generator",
            "🍳 Recipe Generator",
            "📊 CSV Data Analyzer",
            "✍️ Text to Handwriting",
            "🎨 Color Palette",
            "📧 Email Optimizer",
            "🎨 AI Image Studio",
            "📸 Magic Vision",
            "🗣️ AI Debate Partner",
            "🌙 Dream Interpreter",
            "🐉 Jarvis RPG"
        ]
        
        current_tool = st.session_state.selected_tool
        safe_index = 0
        if current_tool in tool_options:
            safe_index = tool_options.index(current_tool)
        else:
            st.session_state.selected_tool = "💬 Normal Chat"
            safe_index = 0
        
        selected_tool = st.selectbox(
            "Select Feature:",
            options=tool_options,
            index=safe_index,
            key="tool_selector"
        )
        
        if selected_tool != st.session_state.selected_tool:
            st.session_state.selected_tool = selected_tool
            st.rerun()
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>📈 LIVE MARKETS</h4>", unsafe_allow_html=True)
        market_data = get_market_data()
        for name, price in market_data.items():
            st.markdown(f'<div class="ticker-card"><span class="ticker-symbol">{name}</span><span class="ticker-price">{price}</span></div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>🟢 MATRIX MODE</h4>", unsafe_allow_html=True)
        matrix_toggle = st.toggle("Activate Matrix Rain", value=st.session_state.matrix_mode, key="matrix_toggle")
        if matrix_toggle != st.session_state.matrix_mode:
            st.session_state.matrix_mode = matrix_toggle
            st.rerun()
        
        st.components.v1.html(f"""
        <script>
            window.parent.postMessage({{type: 'matrix_toggle', active: {str(matrix_toggle).lower()}}}, '*');
        </script>
        """, height=0)
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>⏱️ FOCUS TIMER</h4>", unsafe_allow_html=True)
        
        timer_mins = st.number_input(
            "Minutes:", 
            min_value=1, 
            max_value=120, 
            value=st.session_state.timer_minutes, 
            key="timer_input",
            disabled=st.session_state.timer_running
        )
        
        if timer_mins != st.session_state.timer_minutes and not st.session_state.timer_running:
            st.session_state.timer_minutes = timer_mins
        
        col_timer1, col_timer2 = st.columns(2)
        with col_timer1:
            if st.button("▶️ Start", key="start_timer", use_container_width=True, disabled=st.session_state.timer_running):
                st.session_state.timer_end_time = datetime.now() + timedelta(minutes=timer_mins)
                st.session_state.timer_running = True
                st.session_state.toast_message = f"Timer started: {timer_mins} minutes"
                st.rerun()
        
        with col_timer2:
            if st.button("⏹️ Stop", key="stop_timer", use_container_width=True, disabled=not st.session_state.timer_running):
                st.session_state.timer_running = False
                st.session_state.toast_message = "Timer stopped"
                st.rerun()
        
        if st.session_state.timer_running and st.session_state.timer_end_time:
            remaining = st.session_state.timer_end_time - datetime.now()
            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                st.markdown(f"<div style='text-align:center; font-size:2rem; font-weight:bold; color:#FFD700;'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            else:
                st.balloons()
                st.session_state.toast_message = "⏰ Timer Complete! Great work!"
                st.session_state.timer_running = False
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:2rem; font-weight:bold; color:#888;'>{st.session_state.timer_minutes:02d}:00</div>", unsafe_allow_html=True)
        
        st.divider()
        
        st.toggle("🔊 Voice Response", value=False, key="voice_toggle")
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700; margin-top:10px;'>📜 CHATS</h4>", unsafe_allow_html=True)
        search_query = st.text_input("🔍 Search chats...", key="chat_search")
        
        chat_ids = list(st.session_state.chat_manager.chats.keys())
        pinned_chats = [cid for cid in chat_ids if st.session_state.chat_manager.chats[cid].get("pinned")]
        other_chats = [cid for cid in chat_ids if not st.session_state.chat_manager.chats[cid].get("pinned")]
        
        if search_query:
            chat_ids = st.session_state.chat_manager.search_chats(search_query)
        else:
            chat_ids = pinned_chats + other_chats
        
        for chat_id in chat_ids[:10]:
            chat_data = st.session_state.chat_manager.chats.get(chat_id, {})
            col1, col2, col3 = st.columns([5, 1, 1])
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
            with col1:
                is_selected = chat_id == st.session_state.current_chat_id
                btn_type = "primary" if is_selected else "secondary"
                title = chat_data.get("title", "Chat")
<<<<<<< HEAD
                if chat_data.get("pinned"): 
                    title = f"📌 {title}"
=======
                if chat_data.get("pinned"): title = f"📌 {title}"
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
                if st.button(title, key=f"btn_{chat_id}", use_container_width=True, type=btn_type):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
<<<<<<< HEAD
                if st.button("✏️", key=f"rename_{chat_id}"):
                    st.session_state.renaming_chat_id = chat_id
                    st.rerun()
            with col3:
                if st.button("📌", key=f"pin_{chat_id}"):
                    st.session_state.chat_manager.pin_chat(chat_id)
                    st.rerun()
            with col4:
=======
                if st.button("📌", key=f"pin_{chat_id}"):
                    st.session_state.chat_manager.pin_chat(chat_id)
                    st.rerun()
            with col3:
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
                if st.button("🗑️", key=f"del_{chat_id}"):
                    st.session_state.chat_manager.delete_chat(chat_id)
                    remaining = list(st.session_state.chat_manager.chats.keys())
                    st.session_state.current_chat_id = remaining[0] if remaining else st.session_state.chat_manager.create_new_chat("New Chat")
                    st.session_state.toast_message = "Chat deleted"
                    st.rerun()
<<<<<<< HEAD
    
    st.divider()
    
    # Usage Stats
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>📊 YOUR STATS</h4>", unsafe_allow_html=True)
    user_stats = load_user_stats(st.session_state.username)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{user_stats.get('total_chats', 0)}</div>
            <div class="stat-label">Chats</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{user_stats.get('total_messages', 0)}</div>
            <div class="stat-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Settings
    st.markdown("<h4 style='color:#FFD700; margin-bottom: 15px;'>🔧 SETTINGS</h4>", unsafe_allow_html=True)
    st.toggle("🔊 Voice", value=False, key="voice_toggle")
    
    # Export options
    export_format = st.selectbox(
        "Export Format:",
        ["txt", "json", "markdown", "html"],
        key="export_format"
    )
    
    if st.button("📥 Export Chat", use_container_width=True):
        content = st.session_state.chat_manager.export_chat(st.session_state.current_chat_id, export_format)
        file_ext = {"txt": "txt", "json": "json", "markdown": "md", "html": "html"}[export_format]
        st.download_button(
            "⬇️ Download", 
            content, 
            file_name=f"chat_export.{file_ext}", 
            use_container_width=True
        )
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_manager.chats[st.session_state.current_chat_id]["messages"] = []
        st.session_state.chat_manager.save_chats()
        st.session_state.toast_message = "Chat cleared"
        st.rerun()
    
    if st.button("🧠 Clear Memory", use_container_width=True):
        st.session_state.butler.memory.clear_memory()
        st.session_state.toast_message = "Memory cleared"
        st.rerun()
    
    if st.button("🚪 Logout", use_container_width=True):
        # Clear all session state for proper logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Feature routing
if st.session_state.selected_tool != "💬 Normal Chat":
    try:
        from features import render_selected_tool
        result = render_selected_tool(st.session_state.selected_tool)
        if result == "feature_rendered":
            st.stop()
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Main chat interface
current_mode_config = Config.MODES.get(st.session_state.active_mode, Config.MODES["butler"])

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
hour = now.hour
greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 17 else "Good Evening" if 17 <= hour < 21 else "Good Night"

st.markdown(f"""
<div style='text-align: center; margin-bottom: 30px; padding: 30px; background: {st.session_state.theme_mode == 'dark' and 'linear-gradient(135deg, rgba(30,30,40,0.6), rgba(20,20,30,0.8))' or 'linear-gradient(135deg, rgba(255,255,255,0.8), rgba(245,245,245,0.9))'}; border-radius: 20px; border: 2px solid {current_mode_config['color']}40; backdrop-filter: blur(20px);'>
    <h1 style='font-family: Playfair Display; color: {current_mode_config['color']}; margin-bottom:10px; font-size: 2.5rem;'>{greeting}, {st.session_state.username}. 👑</h1>
    <p style='color:{st.session_state.theme_mode == 'dark' and '#888' or '#666'}; font-size:1.2rem; margin: 10px 0;'>{now.strftime("%A, %d %B %Y")} | {now.strftime("%I:%M %p")} IST</p>
    <p style='color:{st.session_state.theme_mode == 'dark' and '#aaa' or '#888'}; font-size:1rem; margin: 10px 0 0 0;'>Mode: {current_mode_config['name']} | Persona: {persona_options[st.session_state.current_persona]}</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.toast_message:
    st.markdown(f'<div class="toast">{st.session_state.toast_message}</div>', unsafe_allow_html=True)
    st.session_state.toast_message = None

current_messages = st.session_state.chat_manager.get_chat_messages(st.session_state.current_chat_id)
for msg in current_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.markdown("<div style='margin-top: 50px; margin-bottom: 30px;'></div>", unsafe_allow_html=True)

col_voice, col_text = st.columns([1, 5])
with col_voice:
    audio_input = st.audio_input("🎤", label_visibility="collapsed")
with col_text:
    prompt = st.chat_input("Ask Jarvis anything...", key="main_chat_input")

final_prompt = prompt

if audio_input is not None:
    audio_hash = hash(audio_input.getvalue())
    if audio_hash != st.session_state.get("last_processed_audio"):
        try:
            transcript = st.session_state.butler.client.audio.transcriptions.create(
                file=("recording.webm", audio_input.getvalue()),
                model="whisper-large-v3",
                response_format="text"
            )
            final_prompt = transcript
            st.session_state.last_processed_audio = audio_hash
        except Exception as e:
            st.session_state.toast_message = f"Voice error: {str(e)[:50]}"
            final_prompt = None

if final_prompt:
    st.session_state.chat_manager.add_message(st.session_state.current_chat_id, "user", final_prompt)
    update_user_stats(st.session_state.username, "message")
    
    with st.chat_message("user"):
        st.markdown(final_prompt)
    
    user_msg_count = sum(1 for m in current_messages if m["role"] == "user")
    if user_msg_count == 0:
        title = st.session_state.butler.generate_chat_title(final_prompt)
        st.session_state.chat_manager.rename_chat(st.session_state.current_chat_id, title)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            voice_settings = {'lang': st.session_state.voice_lang, 'speed': st.session_state.voice_speed}
            res = st.session_state.butler.process_query(
                final_prompt,
                current_messages,
                st.session_state.voice_toggle,
                custom_prompt=current_mode_config["prompt"],
                voice_settings=voice_settings
            )
        
        agent = res.get('agent_used', 'AI')
        model = res.get('model_used', 'Fast')
        response_time = res.get('response_time', 0)
        response_text = res.get('response', '')
        
        if agent != 'AI':
            st.markdown(f'<div class="agent-badge">⚡ {agent} | {model} | ⏱️ {response_time}s</div>', unsafe_allow_html=True)
        
        audio_path = res.get('audio_path')
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format="audio/mp3", autoplay=True)
        
        if response_text and response_text.strip():
            st.markdown(response_text)
            st.session_state.chat_manager.add_message(st.session_state.current_chat_id, "assistant", response_text)
            update_user_stats(st.session_state.username, "message")
            
            # AI Smart Suggestions
            st.markdown("---")
            st.markdown("**💡 You might also want to ask:**")
            suggestions = [
                f"Explain this in simpler terms",
                f"Give me more examples",
                f"What are the pros and cons?",
                f"How can I apply this practically?"
            ]
            cols = st.columns(4)
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                        st.session_state.chat_manager.add_message(st.session_state.current_chat_id, "user", suggestion)
                        st.rerun()
            
            st.rerun()

st.markdown(f"""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: {st.session_state.theme_mode == 'dark' and '#666' or '#999'}; font-size: 0.9rem; border-top: 1px solid {current_mode_config['color']}30;'>
    <p>Powered by Groq AI | Built with ❤️ by {st.session_state.username}</p>
</div>
""", unsafe_allow_html=True)
=======
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>📊 SYSTEM STATS</h4>", unsafe_allow_html=True)
        stats = st.session_state.chat_manager.get_stats(st.session_state.current_chat_id)
        if stats:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_messages', 0)}</div>
                <div class="stat-label">Messages</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("<h4 style='color:#FFD700;'>🔧 MORE SETTINGS</h4>", unsafe_allow_html=True)
        
        if st.button("📥 Export Chat (TXT)", use_container_width=True, type="primary"):
            content = st.session_state.chat_manager.export_chat(st.session_state.current_chat_id, "txt")
            st.download_button("⬇️ Download", content, file_name="chat.txt", use_container_width=True)
        
        if st.button("🗑️ Clear Chat", use_container_width=True, type="primary"):
            st.session_state.chat_manager.chats[st.session_state.current_chat_id]["messages"] = []
            st.session_state.chat_manager.save_chats()
            st.session_state.toast_message = "Chat cleared"
            st.rerun()
            
        if st.button("🧠 Clear Memory", use_container_width=True, type="primary"):
            st.session_state.butler.memory.clear_memory()
            st.session_state.toast_message = "Memory cleared"
            st.rerun()

# ==========================================
# FEATURE ROUTING
# ==========================================
def route_features():
    selected = st.session_state.selected_tool
    
    if "Normal Chat" in selected:
        return False
    
    if "Jarvis RPG" in selected:
        try:
            from rpg_engine import render_rpg_tool
            result = render_rpg_tool()
            return result == "feature_rendered"
        except Exception as e:
            st.error(f"❌ RPG Error: {str(e)[:100]}")
            return True
    
    try:
        from features import render_selected_tool
        result = render_selected_tool(selected)
        return result == "feature_rendered"
    except Exception as e:
        st.error(f"❌ Feature Error: {str(e)[:100]}")
        return True

# ==========================================
# MAIN CHAT
# ==========================================
def render_main_chat():
    current_mode_config = Config.MODES.get(st.session_state.active_mode, Config.MODES["butler"])
    
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    hour = now.hour
    if 5 <= hour < 12: greeting = "Good Morning"
    elif 12 <= hour < 17: greeting = "Good Afternoon"
    elif 17 <= hour < 21: greeting = "Good Evening"
    else: greeting = "Good Night"

    username = st.session_state.get("username", "Guest")
    if username == "Guest" and "user_id" in st.session_state:
        username = f"User-{st.session_state.user_id}"

    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px; padding: 20px; background: rgba(20,20,30,0.4); border-radius: 15px; border: 1px solid {current_mode_config['color']}30;'>
        <h1 style='font-family:Playfair Display; color:{current_mode_config['color']}; margin-bottom:5px;'>{greeting}, {username}. 👑</h1>
        <p style='color:#888; font-size:1.1rem;'>{now.strftime("%A, %d %B %Y")} | {now.strftime("%I:%M %p")} IST</p>
        <p style='color:#aaa; font-size:0.9rem;'>Mode: {current_mode_config['name']} | Royal Systems Online</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.toast_message:
        st.markdown(f'<div class="toast">{st.session_state.toast_message}</div>', unsafe_allow_html=True)
        st.session_state.toast_message = None

    current_messages = st.session_state.chat_manager.get_chat_messages(st.session_state.current_chat_id)
    for msg in current_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    st.markdown("<div style='margin-top: 40px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    col_voice, col_text = st.columns([1, 5])
    with col_voice:
        audio_input = st.audio_input("🎤", label_visibility="collapsed")
    with col_text:
        prompt = st.chat_input("Ask Jarvis anything...", key="main_chat_input")

    final_prompt = prompt

    if audio_input is not None:
        audio_hash = hash(audio_input.getvalue())
        if audio_hash != st.session_state.get("last_processed_audio"):
            try:
                transcript = st.session_state.butler.client.audio.transcriptions.create(
                    file=("recording.webm", audio_input.getvalue()),
                    model="whisper-large-v3",
                    response_format="text"
                )
                final_prompt = transcript
                st.session_state.last_processed_audio = audio_hash
            except Exception as e:
                st.session_state.toast_message = f"Voice error: {str(e)[:50]}"
                final_prompt = None
        else:
            final_prompt = None

    if final_prompt:
        st.session_state.chat_manager.add_message(st.session_state.current_chat_id, "user", final_prompt)
        
        with st.chat_message("user"):
            st.markdown(final_prompt)
        
        user_msg_count = sum(1 for m in current_messages if m["role"] == "user")
        if user_msg_count == 0:
            title = st.session_state.butler.generate_chat_title(final_prompt)
            st.session_state.chat_manager.rename_chat(st.session_state.current_chat_id, title)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = st.session_state.butler.process_query(
                    final_prompt,
                    current_messages,
                    st.session_state.voice_toggle,
                    custom_prompt=current_mode_config["prompt"]
                )
            
            agent = res.get('agent_used', 'AI')
            model = res.get('model_used', 'Fast')
            response_time = res.get('response_time', 0)
            response_text = res.get('response', '')
            
            if agent != 'AI':
                st.markdown(f'<div class="agent-badge">⚡ {agent} | {model} | ⏱️ {response_time}s</div>', unsafe_allow_html=True)
            
            audio_path = res.get('audio_path')
            if audio_path and os.path.exists(audio_path):
                st.audio(audio_path, format="audio/mp3", autoplay=True)
            
            if response_text and response_text.strip():
                st.markdown(response_text)
                st.session_state.chat_manager.add_message(st.session_state.current_chat_id, "assistant", response_text)
                st.rerun()
            else:
                st.warning("⚠️ Empty response. Try again.")
                st.session_state.toast_message = "Empty response"

# ==========================================
# APP ENTRY POINT
# ==========================================
def main():
    check_konami_code()
    render_luxury_ui(
        st.session_state.active_mode, 
        st.session_state.matrix_mode,
        st.session_state.secret_unlocked
    )
    render_sidebar()
    feature_rendered = route_features()
    if not feature_rendered:
        render_main_chat()

if __name__ == "__main__":
    main()
>>>>>>> 649d5aef0355dffa597cb4cfaa2f8d7bfed2e668
