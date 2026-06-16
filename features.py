import streamlit as st
import requests
import re
import secrets
import string
import os
from io import BytesIO
from datetime import datetime
import pytz

# ==========================================
# CORE HELPER FUNCTIONS
# ==========================================
def get_groq_client():
    """Safely initializes Groq client with error checking"""
    try:
        from groq import Groq
        from config import Config
        if not Config.GROQ_API_KEY:
            st.error("🔑 GROQ_API_KEY missing in .env file!")
            return None
        return Groq(api_key=Config.GROQ_API_KEY)
    except ImportError:
        st.error("❌ Groq library not installed. Run: `pip install groq`")
        return None

def safe_ai_call(messages, max_tokens=800, system_role="You are a helpful expert."):
    """Universal AI caller with loading states and error handling"""
    client = get_groq_client()
    if not client: return None
    
    final_msgs = [{"role": "system", "content": system_role}] + messages
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=final_msgs,
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ AI Processing Failed: {str(e)[:100]}")
        return None

# ==========================================
# 1. YOUTUBE SUMMARIZER (PREMIUM)
# ==========================================
def render_youtube_summarizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📺 YouTube Video Summarizer</h2>", unsafe_allow_html=True)
    st.caption("Get concise AI summaries of any educational or informational video.")
    
    if st.button("← Back to Chat", key="back_yt", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...", key="yt_url")
    
    if st.button("🎬 Generate Summary", use_container_width=True, type="primary", key="yt_btn"):
        if not url:
            st.warning("⚠️ Please enter a valid YouTube URL first.")
            return
            
        if 'youtube.com' not in url and 'youtu.be' not in url:
            st.error("❌ Invalid URL format. Please check the link.")
            return

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Extract Video ID robustly
            video_id = None
            if 'v=' in url: video_id = url.split('v=')[-1].split('&')[0]
            elif 'youtu.be/' in url: video_id = url.split('youtu.be/')[-1].split('?')[0]
            
            if not video_id:
                st.error("❌ Could not extract Video ID."); return

            with st.spinner("📥 Fetching transcript (trying English & Hindi)..."):
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi', 'en-US'])
                full_text = " ".join([t['text'] for t in transcript_list])
                
                if len(full_text) < 50:
                    st.warning("⚠️ Transcript is too short. This might be a music video or shorts."); return

            with st.spinner("🧠 AI is analyzing and summarizing..."):
                summary = safe_ai_call(
                    [{"role": "user", "content": f"Summarize this video transcript into 7 detailed bullet points with key takeaways:\n\n{full_text[:15000]}"}],
                    max_tokens=1000,
                    system_role="You are an expert content analyst. Provide structured, high-value summaries."
                )
                
            if summary:
                st.success("✅ Summary Generated Successfully!")
                st.markdown(summary)
                
                # Download option
                st.download_button(
                    "⬇️ Download Summary as TXT", 
                    data=summary, 
                    file_name=f"summary_{video_id}.txt", 
                    mime="text/plain"
                )
                
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install youtube-transcript-api`")
        except Exception as e: 
            st.error(f"❌ Extraction Failed: {str(e)}. Try a video with manual captions.")

# ==========================================
# 2. PDF CHAT (PREMIUM)
# ==========================================
def render_pdf_chat():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 Chat with PDF</h2>", unsafe_allow_html=True)
    st.caption("Upload documents and ask specific questions about their content.")
    
    if st.button("← Back", key="back_pdf", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    uploaded_file = st.file_uploader("📎 Upload PDF Document", type=["pdf"], key="pdf_up")
    
    if uploaded_file:
        st.info(f"📂 Loaded: `{uploaded_file.name}` ({round(uploaded_file.size/1024, 1)} KB)")
        question = st.text_area("Ask your question:", height=100, placeholder="e.g., What are the main conclusions?", key="pdf_q")
        
        if st.button("🔍 Ask Document", use_container_width=True, type="primary", key="pdf_btn"):
            if not question.strip():
                st.warning("⚠️ Please type a question first."); return
                
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded_file)
                text_content = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: text_content += extracted + "\n"
                    
                if len(text_content) < 100:
                    st.error("❌ Could not extract text. PDF might be scanned/image-based."); return
                    
                with st.spinner(" Reading document and generating answer..."):
                    answer = safe_ai_call(
                        [{"role": "user", "content": f"Document Context:\n{text_content[:12000]}\n\nUser Question: {question}"}],
                        max_tokens=800,
                        system_role="You are a precise research assistant. Answer ONLY based on the provided text. If unsure, say so."
                    )
                    
                if answer:
                    st.markdown("### 💬 Answer:")
                    st.markdown(answer)
                    
            except ImportError: 
                st.error("❌ Missing Library: Run `pip install PyPDF2`")
            except Exception as e: 
                st.error(f"❌ Processing Error: {str(e)}")
    else:
        st.info("👆 Upload a PDF file above to start chatting.")

# ==========================================
# 3. QUICK WRITER (PREMIUM)
# ==========================================
def render_quick_writer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>✍️ Professional Quick Writer</h2>", unsafe_allow_html=True)
    st.caption("Generate emails, posts, and letters in seconds with perfect tone.")
    
    if st.button("← Back", key="back_writer", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    with st.form("writer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            content_type = st.selectbox("Content Type:", ["Professional Email", "LinkedIn Post", "Twitter Thread", "Formal Apology", "Cover Letter"])
        with col2:
            tone = st.select_slider("Desired Tone:", options=["Very Formal", "Professional", "Friendly", "Casual", "Urgent", "Persuasive"])
            
        topic = st.text_area("Topic / Key Points:", height=120, placeholder="Describe what you want to write about...", key="writer_topic")
        submitted = st.form_submit_button("✨ Generate Content", use_container_width=True, type="primary")
        
        if submitted:
            if not topic.strip():
                st.warning("⚠️ Please provide some context or topic."); return
                
            with st.spinner("✍️ Crafting your content..."):
                result = safe_ai_call(
                    [{"role": "user", "content": f"Write a {tone} {content_type} about: {topic}. Make it engaging and well-structured."}],
                    max_tokens=600,
                    system_role="You are a world-class copywriter and communication expert."
                )
                
            if result:
                st.markdown("### ✨ Generated Draft:")
                st.text_area("Copy your content below:", value=result, height=350, key="writer_output")
                st.toast("Content generated successfully!", icon="✅")

# ==========================================
# 4. CODE HELPER (PREMIUM)
# ==========================================
def render_code_helper():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>💻 Senior Code Assistant</h2>", unsafe_allow_html=True)
    st.caption("Debug, optimize, explain, or convert code with expert precision.")
    
    if st.button("← Back", key="back_code", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    code = st.text_area("Paste Your Code:", height=250, placeholder="# Paste Python, JS, Java, etc...", key="code_in")
    task = st.selectbox("What do you need?", ["🔍 Explain Step-by-Step", "🐛 Find & Fix Bugs", "✨ Optimize Performance", "📝 Add Detailed Comments", "🔄 Convert to Python"])
    
    if st.button("🚀 Process Code", use_container_width=True, type="primary", key="code_btn"):
        if not code.strip():
            st.warning("⚠️ Please paste some code first."); return
            
        with st.spinner("🧠 Analyzing code structure and logic..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Task: {task}\n\nCode:\n```python\n{code}\n```"}],
                max_tokens=1000,
                system_role="You are a Principal Software Engineer. Provide clean, secure, and efficient solutions."
            )
            
        if result:
            st.markdown("### 💡 Expert Analysis:")
            st.markdown(result)

# ==========================================
# 5. DAILY BRIEFING (PREMIUM)
# ==========================================
def render_daily_briefing():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📰 Royal Daily Briefing</h2>", unsafe_allow_html=True)
    st.caption("Your personalized morning dashboard for productivity and awareness.")
    
    if st.button("← Back", key="back_brief", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    
    if st.button("🔄 Refresh Briefing", use_container_width=True, type="primary", key="brief_btn"):
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        
        # Header Card
        st.markdown(f"""
        <div style='background: rgba(255,215,0,0.1); padding: 20px; border-radius: 10px; border: 1px solid #FFD700; margin-bottom: 20px;'>
            <h3 style='margin:0; color:#FFD700;'>Good Morning, Arsh! 👑</h3>
            <p style='margin:5px 0 0 0; opacity:0.8;'>{now.strftime('%A, %d %B %Y')} | {now.strftime('%I:%M %p')} IST</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🌤️ Time & Weather")
            try:
                from tools import ButlerTools
                t = ButlerTools()
                st.info(t.get_time_date())
            except: st.warning("Weather service syncing...")
            
        with col2:
            st.markdown("#### 📰 Latest Tech News")
            try:
                from tools import ButlerTools
                t = ButlerTools()
                news = t.get_news()
                st.markdown(news if news else "No recent headlines found.")
            except: st.warning("News feed unavailable.")
            
        st.divider()
        st.markdown("#### 🧘 AI Motivation for the Day")
        try:
            quote = safe_ai_call(
                [{"role": "user", "content": "Give me a powerful, unique motivational quote for today."}],
                max_tokens=100,
                system_role="You are a wise philosopher."
            )
            if quote: st.markdown(f"*\"{quote}\"*")
        except: pass
        
        st.toast("Daily briefing updated!", icon="📰")

# ==========================================
# 6. WEB SEARCH (PREMIUM)
# ==========================================
def render_web_search():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🔍 Intelligent Web Research</h2>", unsafe_allow_html=True)
    st.caption("Search the web and get synthesized, ad-free answers.")
    
    if st.button("← Back", key="back_ws", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    query = st.text_input("What are you researching?", placeholder="e.g., Latest advancements in quantum computing 2024", key="ws_q")
    
    if st.button("🔍 Search & Summarize", use_container_width=True, type="primary", key="ws_btn"):
        if not query.strip():
            st.warning("⚠️ Please enter a search query."); return
            
        try:
            from duckduckgo_search import DDGS
            
            with st.spinner("🌐 Scanning the web..."):
                results = DDGS().text(query, max_results=6)
                if not results:
                    st.warning("⚠️ No relevant results found. Try different keywords."); return
                    
                combined_text = "\n\n".join([f"Source {i+1}: {r['title']}\n{r['body']}" for i, r in enumerate(results)])
            
            with st.spinner("🧠 Synthesizing information..."):
                summary = safe_ai_call(
                    [{"role": "user", "content": f"Research Query: {query}\n\nSources:\n{combined_text}\n\nProvide a comprehensive answer citing sources."}],
                    max_tokens=800,
                    system_role="You are an expert researcher. Provide factual, well-cited answers."
                )
                
            if summary:
                st.markdown("### 📊 Research Summary:")
                st.markdown(summary)
                
                with st.expander("📄 View Raw Sources"):
                    for i, r in enumerate(results):
                        st.markdown(f"**{i+1}. [{r['title']}]({r['href']})**\n{r['body'][:200]}...")
                        
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install duckduckgo-search`")
        except Exception as e: 
            st.error(f"❌ Search Failed: {str(e)}")

# ==========================================
# 7. ARTICLE SUMMARIZER (PREMIUM)
# ==========================================
def render_article_summarizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 Long Article Summarizer</h2>", unsafe_allow_html=True)
    st.caption("Extract key insights from long-form web content instantly.")
    
    if st.button("← Back", key="back_as", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    url = st.text_input("Article URL:", placeholder="https://medium.com/...", key="as_url")
    
    if st.button("📖 Read & Summarize", use_container_width=True, type="primary", key="as_btn"):
        if not url.startswith('http'):
            st.error("❌ Please enter a valid URL starting with http/https."); return
            
        try:
            from bs4 import BeautifulSoup
            
            with st.spinner("📥 Scraping article content..."):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                resp = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Remove scripts/styles
                for tag in soup(['script', 'style', 'nav', 'footer']): tag.decompose()
                text = " ".join([p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text()) > 20])
                
            if len(text) < 200:
                st.error("❌ Could not extract meaningful text. Site might block scrapers."); return
                
            with st.spinner("🧠 Condensing information..."):
                summary = safe_ai_call(
                    [{"role": "user", "content": f"Summarize this article into 5 actionable bullet points:\n\n{text[:12000]}"}],
                    max_tokens=600,
                    system_role="You are an expert editor. Focus on clarity and key takeaways."
                )
                
            if summary:
                st.markdown("### 📝 Key Insights:")
                st.markdown(summary)
                
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install beautifulsoup4`")
        except Exception as e: 
            st.error(f"❌ Scraping Failed: {str(e)}")

# ==========================================
# 8. FLASHCARD GENERATOR (PREMIUM)
# ==========================================
def render_flashcard_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🃏 Smart Flashcard Creator</h2>", unsafe_allow_html=True)
    st.caption("Turn raw notes into effective study flashcards automatically.")
    
    if st.button("← Back", key="back_fg", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    text = st.text_area("Paste Study Notes:", height=200, placeholder="Paste your chapter notes or textbook excerpt here...", key="fg_text")
    num_cards = st.slider("Number of Flashcards:", min_value=3, max_value=15, value=5, key="fg_num")
    
    if st.button("🃏 Create Flashcards", use_container_width=True, type="primary", key="fg_btn"):
        if not text.strip():
            st.warning("⚠️ Please paste some study material first."); return
            
        with st.spinner("🧠 Designing optimal Q&A pairs..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Create exactly {num_cards} high-quality flashcards from this text. Format strictly as:\nQ: [Question]\nA: [Answer]\n\nText:\n{text[:5000]}"}],
                max_tokens=800,
                system_role="You are an expert educator specializing in active recall learning."
            )
            
        if result:
            st.markdown("### 📚 Your Study Deck:")
            st.markdown(result.replace("Q:", "**Q:**").replace("A:", "\n> **A:**"))
            st.toast("Flashcards ready for revision!", icon="🃏")

# ==========================================
# 9. QUIZ GENERATOR (PREMIUM)
# ==========================================
def render_quiz_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📝 Auto Quiz Builder</h2>", unsafe_allow_html=True)
    st.caption("Generate MCQs with explanations to test your understanding.")
    
    if st.button("← Back", key="back_qg", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    text = st.text_area("Source Material:", height=200, placeholder="Paste text to generate quiz from...", key="qg_text")
    difficulty = st.selectbox("Difficulty Level:", ["Beginner", "Intermediate", "Advanced"], key="qg_diff")
    
    if st.button("📝 Generate Quiz", use_container_width=True, type="primary", key="qg_btn"):
        if not text.strip():
            st.warning("⚠️ Please provide source material."); return
            
        with st.spinner("🧠 Crafting challenging questions..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Create 5 {difficulty} level MCQs from this text. Include correct answer and brief explanation.\nFormat:\nQ: ...\nA) ...\nB) ...\nC) ...\nD) ...\nCorrect: X\nWhy: ...\n\nText:\n{text[:5000]}"}],
                max_tokens=1000,
                system_role="You are a professional exam creator."
            )
            
        if result:
            st.markdown("### 📋 Practice Quiz:")
            st.markdown(result)

# ==========================================
# 10. TRANSLATOR (PREMIUM)
# ==========================================
def render_translator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🌐 Neural Language Translator</h2>", unsafe_allow_html=True)
    st.caption("Accurate translation preserving context and nuance.")
    
    if st.button("← Back", key="back_tr", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    text = st.text_area("Original Text:", height=150, key="tr_text")
    c1, c2 = st.columns(2)
    with c1: src = st.selectbox("From:", ["English", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese"])
    with c2: tgt = st.selectbox("To:", ["Hindi", "English", "Spanish", "French", "German", "Japanese", "Chinese"])
    
    if st.button("🌐 Translate Now", use_container_width=True, type="primary", key="tr_btn"):
        if not text.strip():
            st.warning("⚠️ Please enter text to translate."); return
            
        with st.spinner("🔄 Translating with cultural context..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Translate the following text from {src} to {tgt}. Maintain original tone and formatting:\n\n{text}"}],
                max_tokens=800,
                system_role="You are a native-level translator for multiple languages."
            )
            
        if result:
            st.markdown(f"### ✅ Translation ({tgt}):")
            st.markdown(f"> {result}")

# ==========================================
# 11. TEXT ANALYZER (PREMIUM)
# ==========================================
def render_text_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📊 Deep Text Analytics</h2>", unsafe_allow_html=True)
    st.caption("Understand sentiment, readability, and core themes of any text.")
    
    if st.button("← Back", key="back_ta", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    text = st.text_area("Analyze This Text:", height=200, key="ta_text")
    
    if st.button("📊 Run Analysis", use_container_width=True, type="primary", key="ta_btn"):
        if not text.strip():
            st.warning("⚠️ Please paste text to analyze."); return
            
        # Basic Stats
        words = len(text.split()); chars = len(text); sentences = text.count('.') + text.count('!') + text.count('?')
        read_time = max(1, round(words / 200))
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Words", words); c2.metric("Characters", chars)
        c3.metric("Sentences", sentences); c4.metric("Read Time", f"~{read_time} min")
        
        st.divider()
        st.markdown("#### 🧠 AI-Powered Insights")
        with st.spinner("Analyzing tone and semantics..."):
            insights = safe_ai_call(
                [{"role": "user", "content": f"Analyze this text for: 1. Overall Sentiment 2. Target Audience 3. Writing Style 4. Main Topic 5. Readability Score (Easy/Med/Hard).\n\nText:\n{text[:3000]}"}],
                max_tokens=500,
                system_role="You are a linguistic analyst."
            )
            
        if insights: st.markdown(insights)

# ==========================================
# 12. IDEA GENERATOR (PREMIUM)
# ==========================================
def render_idea_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>💡 Creative Brainstorm Engine</h2>", unsafe_allow_html=True)
    st.caption("Break creative blocks with diverse, actionable ideas.")
    
    if st.button("← Back", key="back_ig", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    topic = st.text_input("Brainstorm Topic:", placeholder="e.g., Unique YouTube video ideas for tech channel", key="ig_topic")
    category = st.selectbox("Category:", ["General", "Business", "Content Creation", "Problem Solving", "Art & Design"], key="ig_cat")
    
    if st.button("💡 Spark Ideas", use_container_width=True, type="primary", key="ig_btn"):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic."); return
            
        with st.spinner("🧠 Connecting creative dots..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Generate 10 unique, practical, and innovative ideas for '{topic}' in the {category} category. Be specific."}],
                max_tokens=1000,
                system_role="You are a world-class creative director and innovation consultant."
            )
            
        if result:
            st.markdown("### 💡 Your Idea Bank:")
            st.markdown(result)
            st.toast("Ideas generated!", icon="💡")

# ==========================================
# 13. GITHUB ANALYZER (PREMIUM)
# ==========================================
def render_github_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🐙 GitHub Profile Analyzer</h2>", unsafe_allow_html=True)
    st.caption("Deep dive into developer stats, contributions, and top projects.")
    
    if st.button("← Back", key="back_gh", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    username = st.text_input("GitHub Username:", placeholder="e.g., torvalds", key="gh_user")
    
    if st.button("🔍 Analyze Profile", use_container_width=True, type="primary", key="gh_btn"):
        if not username.strip():
            st.warning("⚠️ Please enter a username."); return
            
        with st.spinner("📡 Fetching GitHub data..."):
            try:
                user_res = requests.get(f"https://api.github.com/users/{username}", timeout=10)
                if user_res.status_code != 200:
                    st.error("❌ User not found or API rate limited."); return
                    
                data = user_res.json()
                
                # Profile Header
                col1, col2 = st.columns([1, 3])
                with col1: st.image(data.get('avatar_url'), width=120)
                with col2:
                    st.markdown(f"### {data.get('name', username)} (@{username})")
                    st.caption(data.get('bio', 'No bio available.') or 'No bio available.')
                    st.markdown(f"📍 {data.get('location', 'Unknown')} | 🔗 [{data.get('blog', 'No website')}]({data.get('blog', '#')})")
                    
                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Public Repos", data.get('public_repos', 0))
                m2.metric("Followers", data.get('followers', 0))
                m3.metric("Following", data.get('following', 0))
                m4.metric("Joined", data.get('created_at', '')[:4] if data.get('created_at') else 'N/A')
                
                # Top Repos
                st.divider()
                st.markdown("#### ⭐ Top Starred Repositories")
                repos_res = requests.get(f"https://api.github.com/users/{username}/repos?sort=stars&per_page=5", timeout=10)
                if repos_res.status_code == 200:
                    for repo in repos_res.json():
                        lang = repo.get('language', 'Mixed')
                        st.markdown(f"- **[{repo['name']}]({repo['html_url']})** ({repo['stargazers_count']} ⭐) - {lang}\n  > {repo.get('description', 'No description')}")
                        
            except Exception as e: 
                st.error(f"❌ Network Error: {str(e)}")

# ==========================================
# 14. RESUME ANALYZER (PREMIUM)
# ==========================================
def render_resume_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📄 ATS Resume Scanner</h2>", unsafe_allow_html=True)
    st.caption("Get professional feedback and ATS compatibility score.")
    
    if st.button("← Back", key="back_ra", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    resume_file = st.file_uploader("Upload Resume (PDF):", type=["pdf"], key="ra_pdf")
    job_desc = st.text_area("Paste Job Description (Optional but Recommended):", height=120, placeholder="Paste JD here for better matching...", key="ra_jd")
    
    if st.button("🔍 Scan Resume", use_container_width=True, type="primary", key="ra_btn"):
        if not resume_file:
            st.warning("⚠️ Please upload a resume PDF."); return
            
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(resume_file)
            resume_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            
            if len(resume_text) < 200:
                st.error("❌ Could not extract enough text. Ensure PDF is text-based."); return
                
            with st.spinner("🧠 Evaluating against industry standards..."):
                prompt = f"Resume:\n{resume_text[:8000]}\n\nJob Description:\n{job_desc if job_desc else 'General IT/Corporate Role'}\n\nProvide: 1. ATS Score (/100) 2. Top 3 Strengths 3. Critical Weaknesses 4. Specific Improvement Suggestions"
                
                feedback = safe_ai_call(
                    [{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    system_role="You are a Senior HR Manager and ATS System Expert."
                )
                
            if feedback:
                st.markdown("### 📊 Analysis Report:")
                st.markdown(feedback)
                
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install PyPDF2`")
        except Exception as e: 
            st.error(f"❌ Analysis Failed: {str(e)}")

# ==========================================
# 15. MEETING NOTES (PREMIUM)
# ==========================================
def render_meeting_notes():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📋 Meeting Minutes Processor</h2>", unsafe_allow_html=True)
    st.caption("Transform raw notes into structured action items and decisions.")
    
    if st.button("← Back", key="back_mn", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    notes = st.text_area("Paste Raw Meeting Notes:", height=250, placeholder="Paste unstructured notes here...", key="mn_notes")
    
    if st.button("✨ Structure Notes", use_container_width=True, type="primary", key="mn_btn"):
        if not notes.strip():
            st.warning("⚠️ Please paste meeting notes."); return
            
        with st.spinner("🧠 Organizing discussion points..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Convert these raw notes into: 1. Executive Summary 2. Key Decisions Made 3. Action Items (with owners if mentioned) 4. Open Questions.\n\nNotes:\n{notes}"}],
                max_tokens=1000,
                system_role="You are an expert Executive Assistant."
            )
            
        if result:
            st.markdown("### 📋 Structured Minutes:")
            st.markdown(result)

# ==========================================
# 16. PASSWORD GENERATOR (PREMIUM)
# ==========================================
def render_password_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🔐 Secure Password Vault</h2>", unsafe_allow_html=True)
    st.caption("Generate cryptographically strong passwords locally.")
    
    if st.button("← Back", key="back_pg", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    length = st.slider("Password Length:", min_value=8, max_value=64, value=20, key="pg_len")
    c1, c2 = st.columns(2)
    with c1: include_upper = st.checkbox("ABC (Uppercase)", value=True)
    with c2: include_lower = st.checkbox("abc (Lowercase)", value=True)
    c3, c4 = st.columns(2)
    with c3: include_nums = st.checkbox("123 (Numbers)", value=True)
    with c4: include_syms = st.checkbox("!@# (Symbols)", value=True)
    
    if st.button("🔐 Generate Secure Password", use_container_width=True, type="primary", key="pg_btn"):
        charset = ""
        if include_upper: charset += string.ascii_uppercase
        if include_lower: charset += string.ascii_lowercase
        if include_nums: charset += string.digits
        if include_syms: charset += string.punctuation
        
        if not charset:
            st.warning("⚠️ Select at least one character type."); return
            
        password = "".join(secrets.choice(charset) for _ in range(length))
        
        st.markdown("### ✅ Generated Password:")
        st.code(password, language="text")
        st.info("💡 Copied to clipboard? Save it in a password manager immediately!")

# ==========================================
# 17. QR CODE GENERATOR (PREMIUM)
# ==========================================
def render_qr_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📱 Custom QR Code Studio</h2>", unsafe_allow_html=True)
    st.caption("Create scannable QR codes for URLs, WiFi, or text.")
    
    if st.button("← Back", key="back_qr", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    data = st.text_input("Content (URL, Text, WiFi, etc.):", placeholder="https://yourwebsite.com", key="qr_data")
    
    if st.button("📱 Create QR Code", use_container_width=True, type="primary", key="qr_btn"):
        if not data.strip():
            st.warning("⚠️ Please enter content for the QR code."); return
            
        try:
            import qrcode
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1, 2])
            with col1: st.image(byte_im, caption="Scan Me", use_container_width=True)
            with col2:
                st.markdown("### ⬇️ Download Options")
                st.download_button("Download PNG", data=byte_im, file_name="jarvis_qr.png", mime="image/png", use_container_width=True)
                
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install qrcode[pil]`")

# ==========================================
# 18. RECIPE GENERATOR (PREMIUM)
# ==========================================
def render_recipe_generator():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🍳 AI Personal Chef</h2>", unsafe_allow_html=True)
    st.caption("Discover delicious recipes based on ingredients you already have.")
    
    if st.button("← Back", key="back_rg", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    ingredients = st.text_area("Available Ingredients:", placeholder="Chicken breast, tomatoes, garlic, pasta, cream...", height=100, key="rg_ing")
    cuisine_pref = st.selectbox("Cuisine Preference:", ["Any", "Indian", "Italian", "Asian", "Mexican", "Healthy/Low-Cal"], key="rg_cui")
    
    if st.button("🍳 Find Recipes", use_container_width=True, type="primary", key="rg_btn"):
        if not ingredients.strip():
            st.warning("⚠️ Please list some ingredients."); return
            
        with st.spinner("👨‍ Consulting the recipe database..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Suggest 3 detailed recipes using primarily these ingredients: {ingredients}. Cuisine preference: {cuisine_pref}. Include ingredient list and step-by-step instructions."}],
                max_tokens=1200,
                system_role="You are a Michelin-star chef and nutritionist."
            )
            
        if result:
            st.markdown("### 🍽️ Chef's Recommendations:")
            st.markdown(result)

# ==========================================
# 19. CSV DATA ANALYZER (PREMIUM)
# ==========================================
def render_csv_analyzer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📊 Smart Data Analyst</h2>", unsafe_allow_html=True)
    st.caption("Ask natural language questions about your spreadsheets.")
    
    if st.button("← Back", key="back_csv", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    file = st.file_uploader("Upload Dataset:", type=["csv", "xlsx", "xls"], key="csv_file")
    question = st.text_input("Ask about your data:", placeholder="e.g., Which region had highest sales?", key="csv_q")
    
    if st.button("📈 Analyze Data", use_container_width=True, type="primary", key="csv_btn"):
        if not file or not question.strip():
            st.warning("⚠️ Please upload a file AND ask a question."); return
            
        try:
            import pandas as pd
            
            if file.name.endswith('.csv'): df = pd.read_csv(file)
            else: df = pd.read_excel(file)
            
            st.success(f"✅ Loaded {df.shape[0]} rows × {df.shape[1]} columns")
            st.dataframe(df.head(10), use_container_width=True)
            
            with st.spinner("🧠 Interpreting data patterns..."):
                schema = df.dtypes.to_string()
                sample = df.head(5).to_markdown()
                
                answer = safe_ai_call(
                    [{"role": "user", "content": f"Dataset Schema:\n{schema}\n\nSample Data:\n{sample}\n\nUser Question: {question}\n\nAnswer accurately based on this data."}],
                    max_tokens=800,
                    system_role="You are a Senior Data Scientist. Provide precise analytical answers."
                )
                
            if answer:
                st.markdown("### 💡 Insight:")
                st.markdown(answer)
                
        except ImportError: 
            st.error("❌ Missing Libraries: Run `pip install pandas openpyxl`")
        except Exception as e: 
            st.error(f"❌ Analysis Failed: {str(e)}")

# ==========================================
# 20. TEXT TO HANDWRITING (PREMIUM)
# ==========================================
def render_handwriting():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>✍️ Digital Handwriting Converter</h2>", unsafe_allow_html=True)
    st.caption("Convert typed text into realistic handwritten note images.")
    
    if st.button("← Back", key="back_hw", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    text = st.text_area("Type Your Note:", height=150, placeholder="Dear Teacher, I am writing to inform you...", key="hw_text")
    
    if st.button("✍️ Convert to Handwriting", use_container_width=True, type="primary", key="hw_btn"):
        if not text.strip():
            st.warning("⚠️ Please enter text to convert."); return
            
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create paper-like background
            img = Image.new('RGB', (1200, 1600), color=(255, 253, 240))
            draw = ImageDraw.Draw(img)
            
            # Try to load a handwriting font, fallback to default
            try:
                font = ImageFont.truetype("Caveat-Regular.ttf", 50)
            except:
                font = ImageFont.load_default()
                st.info("ℹ️ Using default font. Install 'Caveat' font for better handwriting effect.")
            
            # Draw text with slight randomness for realism
            y_position = 80
            lines = text.split('\n')
            for line in lines:
                draw.text((60, y_position), line, fill=(20, 30, 80), font=font)
                y_position += 70
                
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.image(byte_im, caption="Your Handwritten Note", use_container_width=True)
            st.download_button("⬇️ Download Image", data=byte_im, file_name="handwritten_note.png", mime="image/png")
            
        except ImportError: 
            st.error("❌ Missing Library: Run `pip install Pillow`")
        except Exception as e: 
            st.error(f"❌ Conversion Failed: {str(e)}")

# ==========================================
# 21. COLOR PALETTE (PREMIUM)
# ==========================================
def render_color_palette():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>🎨 AI Color Palette Generator</h2>", unsafe_allow_html=True)
    st.caption("Generate harmonious color schemes from simple mood descriptions.")
    
    if st.button("← Back", key="back_cp", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    theme = st.text_input("Describe Mood/Theme:", placeholder="e.g., Cyberpunk neon city at night", key="cp_theme")
    
    if st.button("🎨 Generate Palette", use_container_width=True, type="primary", key="cp_btn"):
        if not theme.strip():
            st.warning("⚠️ Please describe a theme."); return
            
        with st.spinner("🎨 Mixing colors..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Generate 5 hex color codes that perfectly match this theme: '{theme}'. Return ONLY the hex codes separated by commas."}],
                max_tokens=100,
                system_role="You are a professional color theorist and designer."
            )
            
        if result:
            st.markdown("### 🎨 Your Palette:")
            colors = [c.strip() for c in result.split(',') if '#' in c]
            cols = st.columns(min(len(colors), 5))
            for i, col in enumerate(cols):
                if i < len(colors):
                    hex_code = colors[i].replace('#', '').strip()[:6]
                    if len(hex_code) == 6:
                        col.markdown(f"<div style='background-color: #{hex_code}; height: 80px; border-radius: 8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>#{hex_code.upper()}</div>", unsafe_allow_html=True)

# ==========================================
# 22. EMAIL OPTIMIZER (PREMIUM)
# ==========================================
def render_email_optimizer():
    st.markdown("<h2 style='color: #FFD700; text-align:center;'>📧 Subject Line A/B Tester</h2>", unsafe_allow_html=True)
    st.caption("Maximize email open rates with psychology-backed subject lines.")
    
    if st.button("← Back", key="back_eo", type="secondary"): 
        st.session_state.selected_tool = "💬 Normal Chat"; st.rerun()
    st.divider()
    
    body = st.text_area("Paste Email Body:", height=200, placeholder="Hi team, I wanted to update you on the project status...", key="eo_body")
    
    if st.button("✨ Optimize Subjects", use_container_width=True, type="primary", key="eo_btn"):
        if not body.strip():
            st.warning("⚠️ Please paste your email body."); return
            
        with st.spinner("🧠 Analyzing email psychology..."):
            result = safe_ai_call(
                [{"role": "user", "content": f"Based on this email body, generate 5 high-converting subject lines. For each, explain WHY it works psychologically.\n\nEmail:\n{body}"}],
                max_tokens=800,
                system_role="You are an expert email marketing strategist."
            )
            
        if result:
            st.markdown("### 📧 Optimized Subject Lines:")
            st.markdown(result)

# ==========================================
# MAIN ROUTER
# ==========================================
def render_selected_tool(tool_name):
    """Maps tool names to their render functions safely"""
    tools_map = {
        "📺 YouTube Summarizer": render_youtube_summarizer,
        "📄 PDF Chat": render_pdf_chat,
        "✍️ Quick Writer": render_quick_writer,
        "💻 Code Helper": render_code_helper,
        "📰 Daily Briefing": render_daily_briefing,
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
        "📧 Email Optimizer": render_email_optimizer
    }
    
    if tool_name in tools_map:
        tools_map[tool_name]()
    else:
        st.error(f"❌ Tool '{tool_name}' not found in registry.")
        
    return "feature_rendered"