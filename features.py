import streamlit as st
import requests
import secrets
import string
import os
from io import BytesIO
from datetime import datetime
import pytz

# ==========================================
# CORE HELPER
# ==========================================
def get_groq_client():
    try:
        from groq import Groq
        from config import Config
        if not Config.GROQ_API_KEY:
            st.error("🔑 GROQ_API_KEY missing!")
            return None
        return Groq(api_key=Config.GROQ_API_KEY)
    except ImportError:
        st.error("❌ Run: `pip install groq`")
        return None

def safe_ai_call(messages, max_tokens=800, system_role="You are a helpful expert.", model="llama-3.3-70b-versatile"):
    client = get_groq_client()
    if not client: return None
    final_msgs = [{"role": "system", "content": system_role}] + messages
    try:
        response = client.chat.completions.create(model=model, messages=final_msgs, temperature=0.7, max_tokens=max_tokens)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ AI Error: {str(e)[:100]}")
        return None

# ==========================================
# TOOLS 1-22 (COMPACTED FOR SPACE BUT FULLY FUNCTIONAL)
# ==========================================
def render_youtube_summarizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📺 YouTube Summarizer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_yt"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    url = st.text_input("YouTube URL:", key="yt_url")
    if st.button("Summarize", key="yt_btn", type="primary"):
        if not url: st.warning("Enter URL"); return
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            video_id = url.split('v=')[-1].split('&')[0] if 'v=' in url else url.split('youtu.be/')[-1].split('?')[0]
            with st.spinner("Fetching transcript..."):
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
                text = " ".join([t['text'] for t in transcript])
            with st.spinner("AI Summarizing..."):
                summary = safe_ai_call([{"role": "user", "content": f"Summarize:\n{text[:10000]}"}], max_tokens=1000)
            if summary: st.markdown(summary)
        except Exception as e: st.error(f"Error: {e}")

def render_pdf_chat():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 PDF Chat</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_pdf"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_up")
    if uploaded_file:
        question = st.text_area("Ask question:", key="pdf_q")
        if st.button("Ask", key="pdf_btn", type="primary"):
            if not question: st.warning("Ask something!"); return
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "".join([p.extract_text() for p in reader.pages])
                with st.spinner("Reading PDF..."):
                    answer = safe_ai_call([{"role": "user", "content": f"Context:\n{text[:8000]}\n\nQ: {question}"}])
                if answer: st.markdown(answer)
            except Exception as e: st.error(f"Error: {e}")

def render_quick_writer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>✍️ Quick Writer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_writer"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    topic = st.text_area("Topic:", key="writer_topic")
    tone = st.selectbox("Tone:", ["Professional", "Friendly", "Formal"], key="writer_tone")
    if st.button("Write", key="writer_btn", type="primary"):
        if not topic: st.warning("Enter topic!"); return
        with st.spinner("Writing..."):
            result = safe_ai_call([{"role": "user", "content": f"Write a {tone} piece about: {topic}"}])
        if result: st.markdown(result)

def render_code_helper():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>💻 Code Helper</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_code"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    code = st.text_area("Paste Code:", height=200, key="code_in")
    task = st.selectbox("Task:", ["Explain", "Debug", "Optimize"], key="code_task")
    if st.button("Analyze", key="code_btn", type="primary"):
        if not code: st.warning("Paste code!"); return
        with st.spinner("Analyzing..."):
            result = safe_ai_call([{"role": "user", "content": f"{task} this code:\n{code}"}], max_tokens=1000)
        if result: st.markdown(result)

def render_web_search():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🔍 Web Search</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_ws"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    query = st.text_input("Search:", key="ws_q")
    if st.button("Search", key="ws_btn", type="primary"):
        if not query: st.warning("Enter query!"); return
        try:
            from duckduckgo_search import DDGS
            with st.spinner("Searching..."):
                results = DDGS().text(query, max_results=5)
                text = "\n".join([f"{r['title']}: {r['body']}" for r in results])
            with st.spinner("Summarizing..."):
                summary = safe_ai_call([{"role": "user", "content": f"Summarize these results for '{query}':\n{text}"}])
            if summary: st.markdown(summary)
        except Exception as e: st.error(f"Error: {e}")

def render_article_summarizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 Article Summarizer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_as"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    url = st.text_input("URL:", key="as_url")
    if st.button("Summarize", key="as_btn", type="primary"):
        if not url: st.warning("Enter URL!"); return
        try:
            from bs4 import BeautifulSoup
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = " ".join([p.get_text() for p in soup.find_all('p')])
            with st.spinner("Summarizing..."):
                summary = safe_ai_call([{"role": "user", "content": f"Summarize:\n{text[:5000]}"}])
            if summary: st.markdown(summary)
        except Exception as e: st.error(f"Error: {e}")

def render_flashcard_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🃏 Flashcards</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_fg"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    text = st.text_area("Notes:", key="fg_text")
    if st.button("Generate", key="fg_btn", type="primary"):
        if not text: st.warning("Enter notes!"); return
        with st.spinner("Creating..."):
            result = safe_ai_call([{"role": "user", "content": f"Create 5 flashcards (Q/A format) from:\n{text[:3000]}"}])
        if result: st.markdown(result)

def render_quiz_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📝 Quiz Generator</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_qg"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    text = st.text_area("Source:", key="qg_text")
    if st.button("Generate Quiz", key="qg_btn", type="primary"):
        if not text: st.warning("Enter source!"); return
        with st.spinner("Creating..."):
            result = safe_ai_call([{"role": "user", "content": f"Create 5 MCQs from:\n{text[:3000]}"}])
        if result: st.markdown(result)

def render_translator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🌐 Translator</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_tr"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    text = st.text_area("Text:", key="tr_text")
    c1, c2 = st.columns(2)
    with c1: src = st.selectbox("From:", ["English", "Hindi", "Spanish"], key="tr_src")
    with c2: tgt = st.selectbox("To:", ["Hindi", "English", "Spanish"], key="tr_tgt")
    if st.button("Translate", key="tr_btn", type="primary"):
        if not text: st.warning("Enter text!"); return
        with st.spinner("Translating..."):
            result = safe_ai_call([{"role": "user", "content": f"Translate from {src} to {tgt}:\n{text}"}])
        if result: st.markdown(result)

def render_text_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📊 Text Analyzer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_ta"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    text = st.text_area("Text:", key="ta_text")
    if st.button("Analyze", key="ta_btn", type="primary"):
        if not text: st.warning("Enter text!"); return
        words = len(text.split())
        st.metric("Words", words)
        with st.spinner("Analyzing..."):
            result = safe_ai_call([{"role": "user", "content": f"Analyze sentiment and tone of:\n{text[:2000]}"}])
        if result: st.markdown(result)

def render_idea_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>💡 Idea Generator</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_ig"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    topic = st.text_input("Topic:", key="ig_topic")
    if st.button("Generate Ideas", key="ig_btn", type="primary"):
        if not topic: st.warning("Enter topic!"); return
        with st.spinner("Brainstorming..."):
            result = safe_ai_call([{"role": "user", "content": f"Give 10 ideas for: {topic}"}])
        if result: st.markdown(result)

def render_github_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🐙 GitHub Analyzer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_gh"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    username = st.text_input("Username:", key="gh_user")
    if st.button("Analyze", key="gh_btn", type="primary"):
        if not username: st.warning("Enter username!"); return
        try:
            data = requests.get(f"https://api.github.com/users/{username}").json()
            st.image(data.get('avatar_url'), width=100)
            st.markdown(f"**{data.get('name')}** - {data.get('bio')}")
            st.metric("Repos", data.get('public_repos'))
            st.metric("Followers", data.get('followers'))
        except Exception as e: st.error(f"Error: {e}")

def render_resume_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 Resume Scanner</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_ra"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    file = st.file_uploader("Upload PDF", type=["pdf"], key="ra_pdf")
    jd = st.text_area("Job Description:", key="ra_jd")
    if st.button("Scan", key="ra_btn", type="primary"):
        if not file: st.warning("Upload resume!"); return
        try:
            import PyPDF2
            text = "".join([p.extract_text() for p in PyPDF2.PdfReader(file).pages])
            with st.spinner("Scanning..."):
                result = safe_ai_call([{"role": "user", "content": f"Score this resume (1-100) for this JD:\nJD: {jd}\nResume: {text[:5000]}"}])
            if result: st.markdown(result)
        except Exception as e: st.error(f"Error: {e}")

def render_meeting_notes():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📋 Meeting Notes</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_mn"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    notes = st.text_area("Raw Notes:", key="mn_notes")
    if st.button("Structure", key="mn_btn", type="primary"):
        if not notes: st.warning("Enter notes!"); return
        with st.spinner("Processing..."):
            result = safe_ai_call([{"role": "user", "content": f"Structure these notes into Action Items and Decisions:\n{notes}"}])
        if result: st.markdown(result)

def render_password_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🔐 Password Gen</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_pg"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    length = st.slider("Length:", 8, 32, 16, key="pg_len")
    if st.button("Generate", key="pg_btn", type="primary"):
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = "".join(secrets.choice(chars) for _ in range(length))
        st.code(pwd)

def render_qr_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📱 QR Generator</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_qr"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    data = st.text_input("URL/Text:", key="qr_data")
    if st.button("Generate QR", key="qr_btn", type="primary"):
        if not data: st.warning("Enter data!"); return
        try:
            import qrcode
            img = qrcode.make(data)
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue())
        except Exception as e: st.error(f"Error: {e}")

def render_recipe_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🍳 Recipe Gen</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_rg"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    ingredients = st.text_area("Ingredients:", key="rg_ing")
    if st.button("Find Recipes", key="rg_btn", type="primary"):
        if not ingredients: st.warning("Enter ingredients!"); return
        with st.spinner("Cooking..."):
            result = safe_ai_call([{"role": "user", "content": f"Give 3 recipes using: {ingredients}"}])
        if result: st.markdown(result)

def render_csv_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📊 CSV Analyzer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_csv"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    file = st.file_uploader("Upload CSV", type=["csv"], key="csv_file")
    question = st.text_input("Question:", key="csv_q")
    if st.button("Analyze", key="csv_btn", type="primary"):
        if not file or not question: st.warning("Upload and ask!"); return
        try:
            import pandas as pd
            df = pd.read_csv(file)
            st.dataframe(df.head())
            with st.spinner("Analyzing..."):
                result = safe_ai_call([{"role": "user", "content": f"Data:\n{df.head().to_string()}\n\nQ: {question}"}])
            if result: st.markdown(result)
        except Exception as e: st.error(f"Error: {e}")

def render_handwriting():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>✍️ Handwriting</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_hw"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    text = st.text_area("Text:", key="hw_text")
    if st.button("Convert", key="hw_btn", type="primary"):
        if not text: st.warning("Enter text!"); return
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 400), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), text[:200], fill='black')
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue())
        except Exception as e: st.error(f"Error: {e}")

def render_color_palette():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🎨 Color Palette</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_cp"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    theme = st.text_input("Theme:", key="cp_theme")
    if st.button("Generate", key="cp_btn", type="primary"):
        if not theme: st.warning("Enter theme!"); return
        with st.spinner("Mixing..."):
            result = safe_ai_call([{"role": "user", "content": f"Give 5 hex colors for '{theme}'. Format: #XXXXXX, #XXXXXX..."}])
        if result: st.markdown(f"Colors: {result}")

def render_email_optimizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📧 Email Optimizer</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_eo"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    body = st.text_area("Email Body:", key="eo_body")
    if st.button("Optimize", key="eo_btn", type="primary"):
        if not body: st.warning("Enter body!"); return
        with st.spinner("Optimizing..."):
            result = safe_ai_call([{"role": "user", "content": f"Give 3 better subject lines for:\n{body}"}])
        if result: st.markdown(result)

# ==========================================
# 23. AI IMAGE STUDIO
# ==========================================
def render_image_studio():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🎨 AI Image Studio</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_is"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    prompt = st.text_area("Describe Image:", key="is_prompt")
    if st.button("Generate", key="is_btn", type="primary"):
        if not prompt: st.warning("Describe something!"); return
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true"
            with st.spinner("Generating..."):
                resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                st.image(resp.content)
                st.download_button("Download", data=resp.content, file_name="art.png")
            else: st.error("Failed")
        except Exception as e: st.error(f"Error: {e}")

# ==========================================
# 24. MAGIC VISION (FIXED MODEL)
# ==========================================
def render_magic_vision():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📸 Magic Vision</h2>", unsafe_allow_html=True)
    if st.button("← Back", key="back_mv"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    uploaded_file = st.file_uploader("Upload Image:", type=["png", "jpg", "jpeg"], key="mv_upload")
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded", use_container_width=True)
        
        task = st.selectbox("Task:", ["Describe", "Extract Text (OCR)", "Answer Question"], key="mv_task")
        question = ""
        if task == "Answer Question":
            question = st.text_input("Your Question:", key="mv_q")
            
        if st.button("Analyze", key="mv_btn", type="primary"):
            try:
                from groq import Groq
                from config import Config
                import base64
                
                client = Groq(api_key=Config.GROQ_API_KEY)
                img_bytes = uploaded_file.getvalue()
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                
                prompt_text = ""
                if task == "Describe": prompt_text = "Describe this image in detail."
                elif task == "Extract Text (OCR)": prompt_text = "Extract all text from this image."
                elif task == "Answer Question": prompt_text = f"Answer this question about the image: {question}"
                
                with st.spinner("Analyzing..."):
                    # FIXED: Using correct model name
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",  # <-- FIXED MODEL
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }],
                        temperature=0.3, max_tokens=1000
                    )
                    result = response.choices[0].message.content
                st.markdown("### Result:")
                st.markdown(result)
            except Exception as e: st.error(f"Error: {str(e)[:150]}")

# ==========================================
# 25. AI DEBATE PARTNER (NEW!)
# ==========================================
def render_debate_partner():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🗣️ AI Debate Partner</h2>", unsafe_allow_html=True)
    st.caption("Challenge your views! AI will argue against you.")
    if st.button("← Back", key="back_dp"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    topic = st.text_input("Your Stance:", placeholder="e.g., AI will replace all jobs", key="dp_topic")
    if st.button("Start Debate", key="dp_btn", type="primary"):
        if not topic: st.warning("State your stance!"); return
        with st.spinner("AI is preparing counterarguments..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"I believe: {topic}. Give me 3 strong counterarguments to challenge my view."}],
                system_role="You are a skilled debater. Be respectful but firm."
            )
        if result: st.markdown(result)

# ==========================================
# 26. DREAM INTERPRETER (NEW!)
# ==========================================
def render_dream_interpreter():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🌙 Dream Interpreter</h2>", unsafe_allow_html=True)
    st.caption("Unlock the hidden meanings of your dreams.")
    if st.button("← Back", key="back_di"): st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    dream = st.text_area("Describe your dream:", height=150, key="di_dream")
    if st.button("Interpret", key="di_btn", type="primary"):
        if not dream: st.warning("Describe your dream!"); return
        with st.spinner("Analyzing symbols..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Interpret this dream psychologically and symbolically:\n{dream}"}],
                system_role="You are an expert dream analyst and psychologist."
            )
        if result: st.markdown(result)

# ==========================================
# ROUTER
# ==========================================
def render_selected_tool(tool_name):
    tools_map = {
        "📺 YouTube Summarizer": render_youtube_summarizer,
        "📄 PDF Chat": render_pdf_chat,
        "✍️ Quick Writer": render_quick_writer,
        "💻 Code Helper": render_code_helper,
        "🔍 Web Search": render_web_search,
        "📄 Article Summarizer": render_article_summarizer,
        "🃏 Flashcard Generator": render_flashcard_generator,
        "📝 Quiz Generator": render_quiz_generator,
        "🌐 Translator": render_translator,
        "📊 Text Analyzer": render_text_analyzer,
        "💡 Idea Generator": render_idea_generator,
        "🐙 GitHub Analyzer": render_github_analyzer,
        "📄 Resume Analyzer": render_resume_analyzer,
        "📋 Meeting Notes": render_meeting_notes,
        "🔐 Password Generator": render_password_generator,
        "📱 QR Code Generator": render_qr_generator,
        "🍳 Recipe Generator": render_recipe_generator,
        "📊 CSV Data Analyzer": render_csv_analyzer,
        "✍️ Text to Handwriting": render_handwriting,
        "🎨 Color Palette": render_color_palette,
        "📧 Email Optimizer": render_email_optimizer,
        "🎨 AI Image Studio": render_image_studio,
        "📸 Magic Vision": render_magic_vision,
        "🗣️ AI Debate Partner": render_debate_partner,
        "🌙 Dream Interpreter": render_dream_interpreter
    }
    
    if tool_name in tools_map:
        tools_map[tool_name]()
    else:
        st.error(f"❌ Tool '{tool_name}' not found.")
    return "feature_rendered"