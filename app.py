import streamlit as st
import os
import pytz
import requests
from datetime import datetime, timedelta
import time
import json
from config import Config 

# --- CORE IMPORTS (Lazy Loading for Speed) ---
# Heavy libraries are imported only when needed inside functions
# This ensures app starts in < 2 seconds

# --- CONFIG & STATE INITIALIZATION ---
def initialize_state():
    """Centralized state management to prevent undefined variables"""
    if "butler" not in st.session_state:
        from agent_core import AIAgentSystem
        st.session_state.butler = AIAgentSystem()
        
    if "chat_manager" not in st.session_state:
        from chat_manager import ChatManager
        st.session_state.chat_manager = ChatManager()
        
    if "current_chat_id" not in st.session_state:
        cm = st.session_state.chat_manager
        all_chats = cm.chats
        st.session_state.current_chat_id = list(all_chats.keys())[0] if all_chats else cm.create_new_chat("👑 Royal Session")
        
    if "active_mode" not in st.session_state:
        st.session_state.active_mode = "butler"
        
    if "last_processed_audio" not in st.session_state:
        st.session_state.last_processed_audio = None
        
    if "toast_message" not in st.session_state:
        st.session_state.toast_message = None
        
    if "matrix_mode" not in st.session_state:
        st.session_state.matrix_mode = False
        
    if "timer_minutes" not in st.session_state:
        st.session_state.timer_minutes = 25
        
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
        
    if "timer_end_time" not in st.session_state:
        st.session_state.timer_end_time = None
        
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = "💬 Normal Chat"
        
    # Konami Code State
    if "konami_sequence" not in st.session_state:
        st.session_state.konami_sequence = []
    if "secret_unlocked" not in st.session_state:
        st.session_state.secret_unlocked = False

initialize_state()

# --- LUXURY UI ENGINE ---
def render_luxury_ui(active_mode, matrix_mode=False, secret_unlocked=False):
    """Dynamic theme injection with glassmorphism and animations"""
    themes = {
        "butler": {"primary": "#FFD700", "secondary": "#B8860B", "bg": "#0a0a0f", "accent": "#FFD700"},
        "roast": {"primary": "#FF4500", "secondary": "#8B0000", "bg": "#1a0505", "accent": "#FF6347"},
        "code": {"primary": "#00FF88", "secondary": "#008B45", "bg": "#0a1410", "accent": "#00FF88"},
        "zen": {"primary": "#A78BFA", "secondary": "#6B46C1", "bg": "#0f0f1a", "accent": "#A78BFA"}
    }
    
    t = themes.get(active_mode, themes["butler"])
    
    # Secret Mode Override
    if secret_unlocked:
        bg_color = "#000000"
        primary_color = "#00FF00"
        secondary_color = "#008800"
    elif matrix_mode:
        bg_color = "#000000"
        primary_color = "#00FF00"
        secondary_color = "#008800"
    else:
        bg_color = t['bg']
        primary_color = t['primary']
        secondary_color = t['secondary']
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        /* Global Reset */
        .main {{ background: linear-gradient(135deg, {bg_color} 0%, #000000 100%) !important; font-family: 'Inter', sans-serif; }}
        
        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(20,20,30,0.95) 0%, rgba(10,10,15,0.98) 100%) !important;
            backdrop-filter: blur(20px);
            border-right: 2px solid {primary_color}40 !important;
            max-height: 100vh;
            overflow-y: auto !important;
        }}
        
        /* Boot Sequence Animation */
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
        
        /* Matrix Rain Canvas */
        #matrix-canvas {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 9998; pointer-events: none; opacity: 0.3;
        }}
        
        /* Chat Message Styling */
        .stChatMessage {{
            background: linear-gradient(135deg, rgba(30,30,40,0.8) 0%, rgba(20,20,30,0.9) 100%) !important;
            border: 1px solid {primary_color}30 !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 30px {primary_color}10 !important;
            animation: messageSlide 0.4s ease-out;
            transition: all 0.3s ease;
        }}
        .stChatMessage:hover {{
            border-color: {primary_color}60 !important;
            box-shadow: 0 4px 30px rgba(0,0,0,0.4), 0 0 40px {primary_color}20 !important;
        }}
        @keyframes messageSlide {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        /* Input Fields */
        div[data-baseweb="base-input"] > div {{
            background: rgba(20,20,30,0.8) !important;
            border: 2px solid {primary_color}40 !important;
            border-radius: 14px !important;
            transition: all 0.3s ease;
        }}
        div[data-baseweb="base-input"]:focus-within > div {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 30px {primary_color}30 !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%) !important;
            color: #000 !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px {primary_color}40 !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px {primary_color}60 !important;
        }}
        
        /* Sidebar Mode Buttons */
        div[data-testid="stSidebar"] button[kind="secondary"] {{
            height: 80px !important;
            background: rgba(20, 20, 30, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            transition: all 0.3s ease !important;
            color: #fff !important;
            font-weight: bold !important;
            margin-bottom: 10px !important;
        }}
        div[data-testid="stSidebar"] button[kind="secondary"]:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.4) !important;
            border-color: #FFD700 !important;
            background: rgba(40, 40, 50, 0.8) !important;
        }}

        /* Agent Badge */
        .agent-badge {{
            background: linear-gradient(135deg, {primary_color}20, {secondary_color}20);
            color: {primary_color};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            display: inline-block;
            margin-bottom: 12px;
            border: 1px solid {primary_color}50;
            box-shadow: 0 0 20px {primary_color}20;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        /* Stat Cards */
        .stat-card {{
            background: linear-gradient(135deg, rgba(30,30,40,0.8), rgba(20,20,30,0.9));
            border: 1px solid {primary_color}30;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
            text-align: center;
        }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; color: {primary_color}; }}
        .stat-label {{ font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
        
        /* Toast Notification */
        .toast {{
            position: fixed; bottom: 100px; right: 30px;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: #000; padding: 15px 25px; border-radius: 10px;
            font-weight: 600; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            z-index: 10000; animation: toastSlide 0.4s ease-out;
        }}
        @keyframes toastSlide {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a0f; }}
        ::-webkit-scrollbar-thumb {{ background: {primary_color}60; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {primary_color}; }}
        
        /* Hide Streamlit Branding */
        #MainMenu, footer {{ visibility: hidden; }}
        
        /* Market Ticker Card */
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
        
        /* Dropdown Styling */
        div[data-baseweb="select"] > div {{
            background: rgba(20,20,30,0.8) !important;
            border: 2px solid {primary_color}40 !important;
            border-radius: 10px !important;
        }}
    </style>
    
    <!-- Boot Overlay -->
    <div id="boot-overlay">
        <div class="boot-crown">👑</div>
        <div class="boot-text">INITIALIZING JARVIS</div>
        <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
    
    <!-- Matrix Canvas -->
    <canvas id="matrix-canvas"></canvas>
    
    <!-- Matrix Rain Script -->
    <script>
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = Array(Math.floor(columns)).fill(1);
        
        let matrixActive = false;
        
        function drawMatrix() {{
            if (!matrixActive) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                return;
            }}
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';
            
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
    </script>
    """, unsafe_allow_html=True)

# --- CACHED FUNCTIONS FOR SPEED ---
@st.cache_resource
def get_groq_client():
    """Initialize Groq client once and reuse"""
    from groq import Groq
    from config import Config
    return Groq(api_key=Config.GROQ_API_KEY)

@st.cache_data(ttl=300)
def get_market_data():
    """Fetch market data every 5 minutes only"""
    try:
        import yfinance as yf
        tickers = {"Bitcoin": "BTC-USD", "Apple": "AAPL", "Google": "GOOGL"}
        data = {}
        for name, symbol in tickers.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                data[name] = f"${info.last_price:,.2f}"
            except:
                data[name] = "N/A"
        return data
    except:
        return {"Error": "Install yfinance"}

# --- KONAMI CODE EASTER EGG ---
def check_konami_code():
    """Listen for Up Up Down Down Left Right B A sequence"""
    keys = st.query_params.get_all("key")
    if keys:
        st.session_state.konami_sequence.extend(keys)
        # Keep only last 8 keys
        st.session_state.konami_sequence = st.session_state.konami_sequence[-8:]
        
        konami = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", 
                  "ArrowLeft", "ArrowRight", "b", "a"]
        
        if st.session_state.konami_sequence == konami:
            st.session_state.secret_unlocked = True
            st.session_state.toast_message = "🎮 SECRET MATRIX MODE UNLOCKED!"
            st.rerun()

# --- SIDEBAR CONTROL DECK ---
def render_sidebar():
    """Complete sidebar with modes, tools, timer, and chat management"""
    with st.sidebar:
        # Header
        st.markdown("<h1 style='text-align:center; color:#FFD700; font-family:Playfair Display;'>👑 JARVIS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; font-size:0.8rem;'>Royal AI Experience</p>", unsafe_allow_html=True)
        st.divider()
        
        # 4-Mode Reality Grid
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
        
        # Super Tools Selector (22 Tools)
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
            "📧 Email Optimizer"
        ]
        
        selected_tool = st.selectbox(
            "Select Feature:",
            options=tool_options,
            index=tool_options.index(st.session_state.selected_tool),
            key="tool_selector"
        )
        
        if selected_tool != st.session_state.selected_tool:
            st.session_state.selected_tool = selected_tool
            st.rerun()
        
        st.divider()
        
        # Live Market Ticker (Cached)
        st.markdown("<h4 style='color:#FFD700;'>📈 LIVE MARKETS</h4>", unsafe_allow_html=True)
        market_data = get_market_data()
        for name, price in market_data.items():
            st.markdown(f'<div class="ticker-card"><span class="ticker-symbol">{name}</span><span class="ticker-price">{price}</span></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Matrix Rain Toggle
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
        
        # Focus Timer
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
        
        # Voice Toggle
        st.toggle("🔊 Voice Response", value=False, key="voice_toggle")
        
        st.divider()
        
        # Chat History Manager
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
            with col1:
                is_selected = chat_id == st.session_state.current_chat_id
                btn_type = "primary" if is_selected else "secondary"
                title = chat_data.get("title", "Chat")
                if chat_data.get("pinned"): title = f"📌 {title}"
                if st.button(title, key=f"btn_{chat_id}", use_container_width=True, type=btn_type):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("📌", key=f"pin_{chat_id}"):
                    st.session_state.chat_manager.pin_chat(chat_id)
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    st.session_state.chat_manager.delete_chat(chat_id)
                    remaining = list(st.session_state.chat_manager.chats.keys())
                    st.session_state.current_chat_id = remaining[0] if remaining else st.session_state.chat_manager.create_new_chat("New Chat")
                    st.session_state.toast_message = "Chat deleted"
                    st.rerun()
        
        st.divider()
        
        # System Stats
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
        
        # More Settings
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

# --- FEATURE ROUTING LOGIC ---
def route_features():
    """Dispatch to correct feature module based on selection"""
    core_features = [
        "📺 YouTube Summarizer", "📄 PDF Chat", "✍️ Quick Writer", 
        "💻 Code Helper", "📰 Daily Briefing"
    ]
    extra_features = [
        "🔍 Web Search", "📄 Article Summarizer", "🃏 Flashcard Generator", 
        "📝 Quiz Generator", "🌐 Translator", "📊 Text Analyzer", 
        "💡 Idea Generator", "🐙 GitHub Analyzer", "📄 Resume Analyzer", 
        "📋 Meeting Notes", "🔐 Password Generator", "📱 QR Code Generator", 
        "🍳 Recipe Generator"
    ]
    advanced_features = [
        "📊 CSV Data Analyzer", "✍️ Text to Handwriting", 
        "🎨 Color Palette", "📧 Email Optimizer"
    ]
    
    selected = st.session_state.selected_tool
    
    if selected == "💬 Normal Chat":
        return False  # Continue to main chat
        
    try:
        if selected in core_features or selected in extra_features or selected in advanced_features:
            from features import render_selected_tool
            result = render_selected_tool(selected)
            if result == "feature_rendered":
                return True  # Stop rendering main chat
        else:
            st.error(f"❌ Unknown tool: {selected}")
            return True
            
    except ImportError as e:
        st.error(f"❌ Missing module: {str(e)}")
        st.info("💡 Run: `pip install -r requirements.txt`")
        return True
    except Exception as e:
        st.error(f"❌ Feature Error: {str(e)[:100]}")
        return True

# --- MAIN CHAT INTERFACE ---
def render_main_chat():
    """Render the primary chat interface with voice and streaming"""
    current_mode_config = Config.MODES.get(st.session_state.active_mode, Config.MODES["butler"])
    
    # Dynamic Greeting
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    hour = now.hour
    if 5 <= hour < 12: greeting = "Good Morning"
    elif 12 <= hour < 17: greeting = "Good Afternoon"
    elif 17 <= hour < 21: greeting = "Good Evening"
    else: greeting = "Good Night"

    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px; padding: 20px; background: rgba(20,20,30,0.4); border-radius: 15px; border: 1px solid {current_mode_config['color']}30;'>
        <h1 style='font-family:Playfair Display; color:{current_mode_config['color']}; margin-bottom:5px;'>{greeting}, Arsh. 👑</h1>
        <p style='color:#888; font-size:1.1rem;'>{now.strftime("%A, %d %B %Y")} | {now.strftime("%I:%M %p")} IST</p>
        <p style='color:#aaa; font-size:0.9rem;'>Mode: {current_mode_config['name']} | Royal Systems Online</p>
    </div>
    """, unsafe_allow_html=True)

    # Toast Notification
    if st.session_state.toast_message:
        st.markdown(f'<div class="toast">{st.session_state.toast_message}</div>', unsafe_allow_html=True)
        st.session_state.toast_message = None

    # Display Messages
    current_messages = st.session_state.chat_manager.get_chat_messages(st.session_state.current_chat_id)
    for msg in current_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input Area
    st.markdown("<div style='margin-top: 40px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    col_voice, col_text = st.columns([1, 5])
    with col_voice:
        audio_input = st.audio_input("🎤", label_visibility="collapsed")
    with col_text:
        prompt = st.chat_input("Ask Jarvis anything...", key="main_chat_input")

    # Processing Logic
    final_prompt = prompt

    # Handle Voice Input
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

# --- APP ENTRY POINT ---
def main():
    # Check Konami Code
    check_konami_code()
    
    # Render Luxury UI
    render_luxury_ui(
        st.session_state.active_mode, 
        st.session_state.matrix_mode,
        st.session_state.secret_unlocked
    )
    
    # Render Sidebar
    render_sidebar()
    
    # Route Features or Show Chat
    feature_rendered = route_features()
    
    if not feature_rendered:
        render_main_chat()

if __name__ == "__main__":
    main()