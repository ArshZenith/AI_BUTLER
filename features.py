import streamlit as st
import os
import requests
import urllib.parse
import base64
import string
import secrets
from datetime import datetime
from io import BytesIO
from pathlib import Path

# Import tools safely
try:
    from gmail_tools import GmailSummarizer
except ImportError:
    GmailSummarizer = None

try:
    from github_tools import GitHubTools
except ImportError:
    GitHubTools = None

try:
    from groq import Groq
    from config import Config
except ImportError:
    Groq = None
    Config = None

def get_ai_client():
    """Get Groq AI client"""
    if Groq and Config and Config.GROQ_API_KEY:
        return Groq(api_key=Config.GROQ_API_KEY)
    return None

def safe_ai_call(messages, max_tokens=800, system_role="You are a helpful expert.", model=None):
    """Safe wrapper for AI calls with fallback model"""
    client = get_ai_client()
    if not client: 
        st.error("❌ AI Client not available")
        return None
    
    if model is None:
        model = Config.SMART_MODEL if hasattr(Config, 'SMART_MODEL') else "llama-3.3-70b-versatile"
        
    final_msgs = [{"role": "system", "content": system_role}] + messages
    try:
        response = client.chat.completions.create(
            model=model, 
            messages=final_msgs, 
            temperature=0.7, 
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ AI Error: {str(e)[:100]}")
        return None

def render_selected_tool(tool_name):
    """
    Render selected feature/tool interface
    Returns: "feature_rendered" if successfully rendered
    """
    
    # ========================================
    # 📧 GMAIL SUMMARIZER
    # ========================================
    if tool_name == "📧 Gmail Summarizer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📧 Gmail Summarizer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Auto-summarize your recent emails using AI</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if GmailSummarizer is None:
            st.error("❌ Gmail tools not available. Please install required dependencies.")
            return "feature_rendered"
        
        # Check authentication
        if 'gmail_authenticated' not in st.session_state:
            st.session_state.gmail_authenticated = False
        
        if not st.session_state.gmail_authenticated:
            st.warning("⚠️ Gmail not connected yet!")
            st.info("""
            **📋 Setup Instructions:**
            
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project (e.g., "Jarvis Butler")
            3. Enable Gmail API
            4. Create OAuth 2.0 credentials (Desktop app)
            5. Download `credentials.json` and place it in this folder
            6. Click 'Connect Gmail' button below
            """)
            
            if st.button("🔐 Connect Gmail", type="primary", use_container_width=True):
                try:
                    gmail = GmailSummarizer()
                    success, msg = gmail.authenticate()
                    if success:
                        st.session_state.gmail_authenticated = True
                        st.success("✅ Gmail connected successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.success("✅ Gmail Connected")
            
            # Settings
            col1, col2 = st.columns(2)
            with col1:
                hours = st.number_input(
                    "Fetch emails from last (hours):", 
                    min_value=1, 
                    max_value=168, 
                    value=24, 
                    key="gmail_hours"
                )
            with col2:
                max_emails = st.number_input(
                    "Max emails to fetch:", 
                    min_value=1, 
                    max_value=50, 
                    value=10, 
                    key="gmail_max"
                )
            
            if st.button("📥 Fetch & Summarize Emails", type="primary", use_container_width=True):
                with st.spinner("📧 Fetching your emails..."):
                    try:
                        gmail = GmailSummarizer()
                        summary = gmail.get_email_summary(
                            max_results=max_emails, 
                            hours_back=hours
                        )
                        
                        st.markdown("---")
                        st.markdown(summary)
                        
                        # Download options
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Save as TXT", use_container_width=True):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                st.download_button(
                                    "⬇️ Download",
                                    summary,
                                    file_name=f"gmail_summary_{timestamp}.txt",
                                    use_container_width=True
                                )
                        with col2:
                            if st.button("📋 Copy to Clipboard", use_container_width=True):
                                st.code(summary, language="")
                                
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if st.button("🔌 Disconnect Gmail"):
                st.session_state.gmail_authenticated = False
                if os.path.exists('token.json'):
                    os.remove('token.json')
                st.rerun()
    
    # ========================================
    # 💻 GITHUB ASSISTANT
    # ========================================
    elif tool_name == "💻 GitHub Assistant":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>💻 GitHub Assistant</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Analyze repos, track commits, and summarize issues</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if GitHubTools is None:
            st.error("❌ GitHub tools not available. Please install required dependencies.")
            return "feature_rendered"
        
        repo_input = st.text_input(
            "Enter Repository URL or Name:",
            placeholder="e.g., facebook/react or https://github.com/facebook/react",
            key="gh_repo"
        )
        
        if st.button("🔍 Analyze Repository", type="primary", use_container_width=True):
            if not repo_input:
                st.warning("Please enter a repository name or URL!")
            else:
                with st.spinner("📡 Fetching data from GitHub..."):
                    try:
                        gh = GitHubTools()
                        owner, repo = gh.parse_repo_url(repo_input)
                        
                        if not owner or not repo:
                            st.error("Invalid repository format! Use 'owner/repo'.")
                            st.stop()
                        
                        repo_data = gh.get_repo_info(owner, repo)
                        
                        if "error" in repo_data:
                            st.error(f"Error: {repo_data['error']}")
                            st.stop()
                        
                        commits = gh.get_recent_commits(owner, repo)
                        issues = gh.get_open_issues(owner, repo)
                        
                        with st.spinner("🤖 AI is analyzing the repository..."):
                            summary = gh.ai_summarize_repo(repo_data, commits, issues)
                        
                        st.markdown("---")
                        st.markdown(summary)
                        
                        # Quick Links
                        st.markdown(f"**🔗 Quick Links:** [View Repo]({repo_data['html_url']}) | [Issues]({repo_data['html_url']}/issues) | [Pull Requests]({repo_data['html_url']}/pulls)")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # ========================================
    # 👤 GITHUB PROFILE ANALYZER
    # ========================================
    elif tool_name == "👤 GitHub Profile Analyzer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>👤 GitHub Profile Analyzer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Get an AI-powered audit of your GitHub account</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.info("""
        **🔑 Get your GitHub Token:**
        1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
        2. Click **"Generate new token (classic)"**
        3. Select scopes: `repo`, `read:user`
        4. Copy the token and paste below
        """)
        
        gh_token = st.text_input(
            "Enter your GitHub Token:",
            type="password",
            placeholder="ghp_xxxxxxxxxxxx",
            key="gh_token_input"
        )
        
        if st.button("🔍 Analyze My Account", type="primary", use_container_width=True):
            if not gh_token:
                st.warning("Please enter your GitHub token!")
            else:
                with st.spinner("📡 Fetching your GitHub data..."):
                    try:
                        headers = {
                            "Accept": "application/vnd.github.v3+json",
                            "Authorization": f"token {gh_token}"
                        }
                        
                        # Fetch profile
                        profile_response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                        if profile_response.status_code != 200:
                            st.error("Invalid token or GitHub API error!")
                            st.stop()
                        
                        profile = profile_response.json()
                        
                        # Fetch repos
                        repos_response = requests.get(
                            "https://api.github.com/user/repos?sort=stars&direction=desc&per_page=10",
                            headers=headers,
                            timeout=10
                        )
                        repos = repos_response.json() if repos_response.status_code == 200 else []
                        
                        # Calculate total stars
                        total_stars = sum([r.get('stargazers_count', 0) for r in repos])
                        
                        # Format repos for AI
                        repo_details = "\n".join([
                            f"- {r['name']}: ⭐ {r['stargazers_count']} stars | 💻 {r.get('language', 'N/A')} | 🍴 {r['forks_count']} forks" 
                            for r in repos[:5]
                        ])
                        
                        # AI Analysis
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        prompt = f"""
                        Analyze this GitHub developer profile and give a structured audit:
                        
                        👤 Username: {profile.get('login')}
                        📛 Name: {profile.get('name', 'N/A')}
                        📝 Bio: {profile.get('bio', 'No bio')}
                        🌟 Public Repos: {profile.get('public_repos')} | Followers: {profile.get('followers')} | Following: {profile.get('following')}
                        ⭐ Total Stars: {total_stars}
                        
                        🏆 Top Repos:
                        {repo_details}
                        
                        Give: Developer Persona, Strengths, Top Projects, Growth Tips
                        """
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.6,
                            max_tokens=800
                        )
                        
                        summary = response.choices[0].message.content
                        
                        # Display
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if profile.get('avatar_url'):
                                st.image(profile.get('avatar_url'), width=100)
                        with col2:
                            st.subheader(f"{profile.get('name', profile.get('login', 'Developer'))}")
                            st.caption(f"@{profile.get('login', 'unknown')}")
                            if profile.get('bio'):
                                st.markdown(f"*{profile.get('bio')}*")
                        
                        st.markdown("---")
                        
                        # Quick Stats
                        st.markdown("### 📊 Quick Stats")
                        cols = st.columns(4)
                        cols[0].metric("Public Repos", profile.get('public_repos', 0))
                        cols[1].metric("Followers", profile.get('followers', 0))
                        cols[2].metric("Following", profile.get('following', 0))
                        cols[3].metric("Total Stars", total_stars)
                        
                        st.markdown("---")
                        st.markdown(summary)
                        
                        st.markdown(f"**🔗 [View Full Profile](https://github.com/{profile.get('login', '')})**")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📺 YOUTUBE SUMMARIZER
    # ========================================
    elif tool_name == "📺 YouTube Summarizer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📺 YouTube Summarizer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Get AI-powered summaries of YouTube videos</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        video_url = st.text_input(
            "YouTube Video URL:", 
            placeholder="https://www.youtube.com/watch?v=...",
            key="yt_url"
        )
        
        if st.button("🎬 Summarize Video", type="primary", use_container_width=True):
            if not video_url:
                st.warning("Please enter a YouTube URL!")
            else:
                try:
                    from youtube_transcript_api import YouTubeTranscriptApi
                    
                    # Extract video ID
                    if "watch?v=" in video_url:
                        video_id = video_url.split("watch?v=")[1].split("&")[0]
                    elif "youtu.be/" in video_url:
                        video_id = video_url.split("youtu.be/")[1].split("?")[0]
                    else:
                        st.error("Invalid YouTube URL!")
                        st.stop()
                    
                    with st.spinner("📥 Fetching transcript..."):
                        try:
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            full_text = " ".join([entry['text'] for entry in transcript])
                        except:
                            st.error("Sorry, this video doesn't have captions available.")
                            st.stop()
                    
                    with st.spinner("🤖 AI is summarizing..."):
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[
                                {
                                    "role": "system",
                                    "content": """Summarize this YouTube video transcript in a clear, structured format:
                                    
                                    Format:
                                    📹 **Video Summary**
                                    
                                    **Main Topic:** [What's the video about?]
                                    
                                    **Key Points:**
                                    • [Point 1]
                                    • [Point 2]
                                    • [Point 3]
                                    
                                    **Takeaways:**
                                    • [Important takeaway 1]
                                    • [Important takeaway 2]
                                    
                                    **Conclusion:** [Brief conclusion]
                                    
                                    Keep it concise but informative."""
                                },
                                {
                                    "role": "user",
                                    "content": f"Summarize this video:\n{full_text[:15000]}"
                                }
                            ],
                            temperature=0.5,
                            max_tokens=1500
                        )
                        
                        summary = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown(summary)
                    
                    # Download option
                    if st.button("💾 Download Summary"):
                        st.download_button(
                            "⬇️ Download",
                            summary,
                            file_name=f"youtube_summary_{video_id}.txt",
                            use_container_width=True
                        )
                        
                except ImportError:
                    st.error("Please install: pip install youtube-transcript-api")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📄 PDF CHAT
    # ========================================
    elif tool_name == "📄 PDF Chat":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📄 PDF Chat</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Upload a PDF and ask questions about it</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Upload PDF", 
            type=['pdf'],
            key="pdf_upload"
        )
        
        if uploaded_file:
            try:
                import PyPDF2
                
                # Read PDF
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                
                st.success(f"✅ PDF loaded! ({len(pdf_text)} characters)")
                
                # Question input
                question = st.text_area(
                    "Ask about the PDF:",
                    placeholder="What is this document about?",
                    key="pdf_question"
                )
                
                if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                    if not question:
                        st.warning("Please ask a question!")
                    else:
                        with st.spinner("🤖 Analyzing PDF..."):
                            client = get_ai_client()
                            if not client:
                                st.error("AI client not available")
                                st.stop()
                            
                            response = client.chat.completions.create(
                                model=Config.SMART_MODEL,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are a PDF analyzer. Answer questions based on the provided document content. Be accurate and cite specific information."
                                    },
                                    {
                                        "role": "user",
                                        "content": f"Document:\n{pdf_text[:15000]}\n\nQuestion: {question}"
                                    }
                                ],
                                temperature=0.3,
                                max_tokens=1000
                            )
                            
                            answer = response.choices[0].message.content
                        
                        st.markdown("---")
                        st.markdown(answer)
                        
            except ImportError:
                st.error("Please install: pip install pypdf")
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
    
    # ========================================
    # ✍️ QUICK WRITER
    # ========================================
    elif tool_name == "✍️ Quick Writer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>✍️ Quick Writer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>AI-powered content writing assistant</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        topic = st.text_area(
            "Topic/Subject:",
            placeholder="Write an email about project deadline...",
            key="writer_topic",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            tone = st.selectbox(
                "Tone:",
                ["Professional", "Friendly", "Formal", "Witty", "Casual", "Persuasive"],
                key="writer_tone"
            )
        with col2:
            length = st.selectbox(
                "Length:",
                ["Short (100 words)", "Medium (300 words)", "Long (500 words)"],
                key="writer_length"
            )
        
        if st.button("✍️ Write", type="primary", use_container_width=True):
            if not topic:
                st.warning("Please enter a topic!")
            else:
                with st.spinner("✍️ Crafting content..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    word_limits = {
                        "Short (100 words)": 100,
                        "Medium (300 words)": 300,
                        "Long (500 words)": 500
                    }
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are a professional writer. Write content in {tone.lower()} tone. Keep it around {word_limits[length]} words."
                            },
                            {
                                "role": "user",
                                "content": f"Write about: {topic}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    content = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(content)
                
                # Copy button
                if st.button("📋 Copy to Clipboard"):
                    st.code(content, language="")
    
    # ========================================
    # 💻 CODE HELPER
    # ========================================
    elif tool_name == "💻 Code Helper":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>💻 Code Helper</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Debug, optimize, and explain your code</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        code = st.text_area(
            "Paste your code:",
            placeholder="# Paste your code here...",
            key="code_input",
            height=200
        )
        
        task = st.selectbox(
            "What do you want?",
            ["Debug 🔍", "Optimize ⚡", "Explain 📖", "Refactor 🔄", "Add Comments 💬"],
            key="code_task"
        )
        
        if st.button("🔧 Analyze Code", type="primary", use_container_width=True):
            if not code:
                st.warning("Please paste some code!")
            else:
                with st.spinner("🤖 Analyzing..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    prompts = {
                        "Debug 🔍": "Find and fix bugs in this code",
                        "Optimize ⚡": "Optimize this code for better performance",
                        "Explain 📖": "Explain what this code does step by step",
                        "Refactor 🔄": "Refactor this code to follow best practices",
                        "Add Comments 💬": "Add detailed comments to this code"
                    }
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert programmer. Provide clear, actionable advice."
                            },
                            {
                                "role": "user",
                                "content": f"{prompts[task]}:\n\n{code}"
                            }
                        ],
                        temperature=0.3,
                        max_tokens=1500
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 📰 DAILY BRIEFING
    # ========================================
    elif tool_name == "📰 Daily Briefing":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📰 Daily Briefing</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Get your daily news and updates</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.button("📰 Get Daily Briefing", type="primary", use_container_width=True):
            with st.spinner("📰 Fetching news..."):
                try:
                    # Tech News
                    tech_news_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
                    ids = requests.get(tech_news_url, timeout=5).json()[:5]
                    
                    tech_news = []
                    for story_id in ids:
                        item = requests.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                            timeout=5
                        ).json()
                        tech_news.append(f"- {item['title']}")
                    
                    # Weather
                    try:
                        from tools import ButlerTools
                        tools = ButlerTools()
                        weather = tools.get_weather("Delhi")
                    except:
                        weather = "Weather data not available"
                    
                    # Time
                    try:
                        from tools import ButlerTools
                        tools = ButlerTools()
                        time_date = tools.get_time_date()
                    except:
                        time_date = datetime.now().strftime("%A, %d %B %Y")
                    
                    # Display
                    st.markdown("---")
                    st.markdown(f"### 📅 {datetime.now().strftime('%A, %B %d, %Y')}")
                    st.markdown("")
                    st.markdown(f"**{time_date.split('Time:')[0].replace('Current Date:', '').strip()}**")
                    st.markdown("")
                    st.markdown(weather)
                    st.markdown("")
                    st.markdown("### 🔥 Top Tech News")
                    st.markdown("\n".join(tech_news))
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 🔍 WEB SEARCH
    # ========================================
    elif tool_name == "🔍 Web Search":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🔍 Web Search</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Search the web and get AI summaries</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        query = st.text_input("Search Query:", key="ws_query")
        
        if st.button("🔍 Search", type="primary", use_container_width=True):
            if not query:
                st.warning("Please enter a search query!")
            else:
                try:
                    from duckduckgo_search import DDGS
                    
                    with st.spinner("🔍 Searching..."):
                        results = DDGS().text(query, max_results=5)
                        text = "\n".join([f"{r['title']}: {r['body']}" for r in results])
                    
                    with st.spinner("🤖 Summarizing..."):
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Summarize these search results for '{query}':\n{text}"
                                }
                            ],
                            temperature=0.5,
                            max_tokens=800
                        )
                        
                        summary = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown(summary)
                    
                except ImportError:
                    st.error("Please install: pip install duckduckgo-search")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📄 ARTICLE SUMMARIZER
    # ========================================
    elif tool_name == "📄 Article Summarizer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📄 Article Summarizer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Summarize web articles instantly</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        url = st.text_input("Article URL:", key="as_url")
        
        if st.button("📄 Summarize", type="primary", use_container_width=True):
            if not url:
                st.warning("Please enter a URL!")
            else:
                try:
                    from bs4 import BeautifulSoup
                    
                    with st.spinner("📥 Fetching article..."):
                        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        text = " ".join([p.get_text() for p in soup.find_all('p')])
                    
                    with st.spinner("🤖 Summarizing..."):
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Summarize this article:\n{text[:5000]}"
                                }
                            ],
                            temperature=0.5,
                            max_tokens=800
                        )
                        
                        summary = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown(summary)
                    
                except ImportError:
                    st.error("Please install: pip install beautifulsoup4")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 🃏 FLASHCARD GENERATOR
    # ========================================
    elif tool_name == "🃏 Flashcard Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🃏 Flashcard Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Create flashcards from your notes</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        text = st.text_area("Your Notes:", height=150, key="fg_text")
        
        if st.button("🃏 Generate Flashcards", type="primary", use_container_width=True):
            if not text:
                st.warning("Please enter some notes!")
            else:
                with st.spinner("🤖 Creating flashcards..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Create 5 flashcards (Q/A format) from:\n{text[:3000]}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 📝 QUIZ GENERATOR
    # ========================================
    elif tool_name == "📝 Quiz Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📝 Quiz Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Generate MCQs from any content</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        text = st.text_area("Source Content:", height=150, key="qg_text")
        
        if st.button("📝 Generate Quiz", type="primary", use_container_width=True):
            if not text:
                st.warning("Please enter content!")
            else:
                with st.spinner("🤖 Creating quiz..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Create 5 MCQs from:\n{text[:3000]}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 🌐 TRANSLATOR
    # ========================================
    elif tool_name == "🌐 Translator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🌐 Translator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Translate text between languages</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        text = st.text_area("Text to Translate:", key="tr_text")
        
        col1, col2 = st.columns(2)
        with col1:
            src = st.selectbox("From:", ["English", "Hindi", "Spanish"], key="tr_src")
        with col2:
            tgt = st.selectbox("To:", ["Hindi", "English", "Spanish"], key="tr_tgt")
        
        if st.button("🌐 Translate", type="primary", use_container_width=True):
            if not text:
                st.warning("Please enter text!")
            else:
                with st.spinner("🤖 Translating..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Translate from {src} to {tgt}:\n{text}"
                            }
                        ],
                        temperature=0.3,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 📊 TEXT ANALYZER
    # ========================================
    elif tool_name == "📊 Text Analyzer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📊 Text Analyzer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Analyze sentiment and tone</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        text = st.text_area("Text to Analyze:", key="ta_text")
        
        if st.button("📊 Analyze", type="primary", use_container_width=True):
            if not text:
                st.warning("Please enter text!")
            else:
                words = len(text.split())
                st.metric("Words", words)
                
                with st.spinner("🤖 Analyzing..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Analyze sentiment and tone of:\n{text[:2000]}"
                            }
                        ],
                        temperature=0.5,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 💡 IDEA GENERATOR
    # ========================================
    elif tool_name == "💡 Idea Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>💡 Idea Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Brainstorm ideas on any topic</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        topic = st.text_input("Topic:", key="ig_topic")
        
        if st.button("💡 Generate Ideas", type="primary", use_container_width=True):
            if not topic:
                st.warning("Please enter a topic!")
            else:
                with st.spinner("🤖 Brainstorming..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Give 10 ideas for: {topic}"
                            }
                        ],
                        temperature=0.8,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 🐙 GITHUB ANALYZER (BASIC)
    # ========================================
    elif tool_name == "🐙 GitHub Analyzer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🐙 GitHub Analyzer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Analyze any GitHub profile</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("GitHub Username:", key="gh_user")
        
        if st.button("🐙 Analyze", type="primary", use_container_width=True):
            if not username:
                st.warning("Please enter a username!")
            else:
                try:
                    data = requests.get(f"https://api.github.com/users/{username}", timeout=10).json()
                    
                    if "message" in data:
                        st.error(f"User not found!")
                    else:
                        st.image(data.get('avatar_url'), width=100)
                        st.markdown(f"**{data.get('name')}** - {data.get('bio')}")
                        st.metric("Repos", data.get('public_repos'))
                        st.metric("Followers", data.get('followers'))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📄 RESUME ANALYZER
    # ========================================
    elif tool_name == "📄 Resume Analyzer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📄 Resume Scanner</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Score your resume against job description</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        file = st.file_uploader("Upload Resume (PDF):", type=["pdf"], key="ra_pdf")
        jd = st.text_area("Job Description:", key="ra_jd")
        
        if st.button("📄 Scan Resume", type="primary", use_container_width=True):
            if not file or not jd:
                st.warning("Upload resume and enter job description!")
            else:
                try:
                    import PyPDF2
                    
                    text = "".join([p.extract_text() for p in PyPDF2.PdfReader(file).pages])
                    
                    with st.spinner("🤖 Scanning..."):
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Score this resume (1-100) for this JD:\nJD: {jd}\nResume: {text[:5000]}"
                                }
                            ],
                            temperature=0.5,
                            max_tokens=800
                        )
                        
                        result = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown(result)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📋 MEETING NOTES
    # ========================================
    elif tool_name == "📋 Meeting Notes":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📋 Meeting Notes</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Structure your meeting notes</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        notes = st.text_area("Raw Notes:", height=150, key="mn_notes")
        
        if st.button("📋 Structure Notes", type="primary", use_container_width=True):
            if not notes:
                st.warning("Please enter notes!")
            else:
                with st.spinner("🤖 Processing..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Structure these notes into Action Items and Decisions:\n{notes}"
                            }
                        ],
                        temperature=0.5,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 🔐 PASSWORD GENERATOR
    # ========================================
    elif tool_name == "🔐 Password Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🔐 Password Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Generate secure passwords</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        length = st.slider("Password Length:", 8, 32, 16, key="pg_len")
        
        if st.button("🔐 Generate Password", type="primary", use_container_width=True):
            chars = string.ascii_letters + string.digits + string.punctuation
            pwd = "".join(secrets.choice(chars) for _ in range(length))
            
            st.code(pwd)
    
    # ========================================
    # 📱 QR CODE GENERATOR
    # ========================================
    elif tool_name == "📱 QR Code Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📱 QR Code Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Generate QR codes from text/URL</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        data = st.text_input("URL or Text:", key="qr_data")
        
        if st.button("📱 Generate QR", type="primary", use_container_width=True):
            if not data:
                st.warning("Please enter data!")
            else:
                try:
                    import qrcode
                    
                    img = qrcode.make(data)
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    
                    st.image(buf.getvalue())
                    
                except ImportError:
                    st.error("Please install: pip install qrcode")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 🍳 RECIPE GENERATOR
    # ========================================
    elif tool_name == "🍳 Recipe Generator":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🍳 Recipe Generator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Find recipes from your ingredients</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        ingredients = st.text_area("Your Ingredients:", key="rg_ing")
        
        if st.button("🍳 Find Recipes", type="primary", use_container_width=True):
            if not ingredients:
                st.warning("Please enter ingredients!")
            else:
                with st.spinner("🍳 Cooking..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Give 3 recipes using: {ingredients}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 📊 CSV DATA ANALYZER
    # ========================================
    elif tool_name == "📊 CSV Data Analyzer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📊 CSV Data Analyzer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Analyze CSV files with AI</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        file = st.file_uploader("Upload CSV:", type=["csv"], key="csv_file")
        question = st.text_input("Your Question:", key="csv_q")
        
        if st.button("📊 Analyze", type="primary", use_container_width=True):
            if not file or not question:
                st.warning("Upload CSV and ask a question!")
            else:
                try:
                    import pandas as pd
                    
                    df = pd.read_csv(file)
                    st.dataframe(df.head())
                    
                    with st.spinner("🤖 Analyzing..."):
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                        
                        response = client.chat.completions.create(
                            model=Config.SMART_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Data:\n{df.head().to_string()}\n\nQ: {question}"
                                }
                            ],
                            temperature=0.5,
                            max_tokens=800
                        )
                        
                        result = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown(result)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # ✍️ TEXT TO HANDWRITING
    # ========================================
    elif tool_name == "✍️ Text to Handwriting":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>✍️ Text to Handwriting</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Convert text to handwriting image</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        text = st.text_area("Your Text:", key="hw_text")
        
        if st.button("✍️ Convert", type="primary", use_container_width=True):
            if not text:
                st.warning("Please enter text!")
            else:
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    
                    img = Image.new('RGB', (800, 400), color='white')
                    draw = ImageDraw.Draw(img)
                    draw.text((10, 10), text[:200], fill='black')
                    
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    
                    st.image(buf.getvalue())
                    
                except ImportError:
                    st.error("Please install: pip install Pillow")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ========================================
    # 🎨 COLOR PALETTE
    # ========================================
    elif tool_name == "🎨 Color Palette":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🎨 Color Palette</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Generate color palettes from themes</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        theme = st.text_input("Theme:", key="cp_theme")
        
        if st.button("🎨 Generate Palette", type="primary", use_container_width=True):
            if not theme:
                st.warning("Please enter a theme!")
            else:
                with st.spinner("🎨 Mixing colors..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Give 5 hex colors for '{theme}'. Format: #XXXXXX, #XXXXXX..."
                            }
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(f"**Colors:** {result}")
    
    # ========================================
    # 📧 EMAIL OPTIMIZER
    # ========================================
    elif tool_name == "📧 Email Optimizer":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📧 Email Optimizer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Optimize your email subject lines</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        body = st.text_area("Email Body:", height=150, key="eo_body")
        
        if st.button("📧 Optimize", type="primary", use_container_width=True):
            if not body:
                st.warning("Please enter email body!")
            else:
                with st.spinner("🤖 Optimizing..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Give 3 better subject lines for:\n{body}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=400
                    )
                    
                    result = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown(result)
    
    # ========================================
    # 🎨 AI IMAGE STUDIO
    # ========================================
    elif tool_name == "🎨 AI Image Studio":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🎨 AI Image Studio</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Generate stunning images with AI</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        prompt = st.text_input(
            "Describe your image:",
            placeholder="e.g., futuristic cyberpunk city at sunset",
            key="image_prompt"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            width = st.slider("Width:", 512, 1024, 1024, key="img_width")
        with col2:
            height = st.slider("Height:", 512, 1024, 1024, key="img_height")
        
        if st.button("🎨 Generate Image", type="primary", use_container_width=True):
            if not prompt:
                st.warning("Please describe the image!")
            else:
                with st.spinner("🎨 Creating masterpiece..."):
                    try:
                        encoded_prompt = urllib.parse.quote(prompt)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
                        
                        response = requests.get(image_url, timeout=15)
                        
                        if response.status_code == 200:
                            st.image(response.content, use_container_width=True)
                            st.caption(f"Prompt: {prompt}")
                            
                            # Download button
                            if st.button("💾 Download Image"):
                                st.download_button(
                                    "⬇️ Download",
                                    response.content,
                                    file_name=f"ai_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                        else:
                            st.error("Failed to generate image. Try again!")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # ========================================
    # 📸 MAGIC VISION
    # ========================================
    elif tool_name == "📸 Magic Vision":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>📸 Magic Vision</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Analyze images with AI (Powered by Pollinations.ai)</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Upload Image:", type=["png", "jpg", "jpeg"], key="mv_upload")
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded", use_container_width=True)
            
            task = st.selectbox("Task:", ["Describe", "Extract Text (OCR)", "Answer Question"], key="mv_task")
            question = ""
            if task == "Answer Question":
                question = st.text_input("Your Question:", key="mv_q")
                
            if st.button("📸 Analyze", type="primary", use_container_width=True):
                try:
                    # Prepare prompt based on task
                    if task == "Describe":
                        prompt_text = "Describe this image in detail."
                    elif task == "Extract Text (OCR)":
                        prompt_text = "Extract all text from this image exactly as it appears."
                    elif task == "Answer Question":
                        prompt_text = f"Answer this question about the image: {question}"
                    
                    with st.spinner("📸 Analyzing image..."):
                        # Convert image to base64 for API
                        img_bytes = uploaded_file.getvalue()
                        b64_img = base64.b64encode(img_bytes).decode('utf-8')
                        
                        # Use Llama 3.2 Vision via Groq
                        client = get_ai_client()
                        if not client:
                            st.error("AI client not available")
                            st.stop()
                            
                        response = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
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
                    
                except Exception as e:
                    st.error(f"Error: {str(e)[:150]}")
    
    # ========================================
    # 🗣️ AI DEBATE PARTNER
    # ========================================
    elif tool_name == "🗣️ AI Debate Partner":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🗣️ AI Debate Partner</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Challenge your ideas with AI-powered debate</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        topic = st.text_input(
            "Your Position/Topic:",
            placeholder="e.g., Remote work is better than office work",
            key="debate_topic"
        )
        
        stance = st.radio(
            "Your stance:",
            ["For", "Against"],
            key="debate_stance"
        )
        
        if st.button("⚔️ Start Debate", type="primary", use_container_width=True):
            if not topic:
                st.warning("Please enter a topic!")
            else:
                with st.spinner("🤖 Preparing counterarguments..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    position = "supporting" if stance == "For" else "opposing"
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a skilled debater. Present strong, logical counterarguments.
                                Use:
                                - Logical reasoning
                                - Evidence and examples
                                - Respectful but firm tone
                                
                                Challenge ideas, not the person."""
                            },
                            {
                                "role": "user",
                                "content": f"I am {position} this statement: {topic}. Challenge my position with strong counterarguments."
                            }
                        ],
                        temperature=0.6,
                        max_tokens=1000
                    )
                    
                    counterargument = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown("### ⚔️ Counterargument:")
                st.markdown(counterargument)
                
                # Continue debate
                if st.button("🔄 Respond"):
                    st.session_state.debate_history = counterargument
    
    # ========================================
    # 🌙 DREAM INTERPRETER
    # ========================================
    elif tool_name == "🌙 Dream Interpreter":
        st.markdown("<h2 style='color:#FFD700; text-align:center;'>🌙 Dream Interpreter</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; text-align:center;'>Discover the meaning behind your dreams</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        dream = st.text_area(
            "Describe your dream:",
            placeholder="I was flying over a neon city but my wings were made of glass...",
            key="dream_input",
            height=150
        )
        
        if st.button("🔮 Interpret Dream", type="primary", use_container_width=True):
            if not dream:
                st.warning("Please describe your dream!")
            else:
                with st.spinner("🌙 Consulting the Oracle..."):
                    client = get_ai_client()
                    if not client:
                        st.error("AI client not available")
                        st.stop()
                    
                    response = client.chat.completions.create(
                        model=Config.SMART_MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a dream interpreter with knowledge of psychology and symbolism.
                                Interpret dreams in a thoughtful, insightful way.
                                Consider:
                                - Symbolic meanings
                                - Psychological perspectives
                                - Emotional themes
                                
                                Be encouraging and positive."""
                            },
                            {
                                "role": "user",
                                "content": f"Interpret this dream: {dream}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    interpretation = response.choices[0].message.content
                
                st.markdown("---")
                st.markdown("### 🔮 The Oracle Says:")
                st.markdown(interpretation)
    
    # ========================================
    # DEFAULT CASE
    # ========================================
    else:
        st.info(f"🚧 {tool_name} is under construction!")
    
    return "feature_rendered"