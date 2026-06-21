import requests
import os
from groq import Groq
from config import Config

class GitHubTools:
    def __init__(self, token=None):
        """
        Initialize GitHubTools with optional token
        If token is provided, use it. Otherwise, try .env file.
        """
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        # Priority: 1. Passed token, 2. .env token
        if token:
            self.headers["Authorization"] = f"token {token}"
        else:
            env_token = os.getenv("GITHUB_TOKEN")
            if env_token:
                self.headers["Authorization"] = f"token {env_token}"

    # ========================================
    # 🔧 HELPER METHODS
    # ========================================
    
    def parse_repo_url(self, url):
        """Extract owner and repo name from URL or 'owner/repo' format"""
        url = url.strip().replace("https://github.com/", "").replace("http://github.com/", "")
        url = url.rstrip("/")
        parts = url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return None, None

    # ========================================
    # 📂 REPOSITORY ANALYSIS (Public)
    # ========================================
    
    def get_repo_info(self, owner, repo):
        """Fetch basic info about a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return {"error": res.json().get("message", "Repo not found")}

    def get_recent_commits(self, owner, repo, count=5):
        """Fetch recent commits from a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={count}"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []

    def get_open_issues(self, owner, repo, count=5):
        """Fetch open issues (excluding pull requests)"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page={count}"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
            # Pull requests ko filter out karna hai
            return [issue for issue in res.json() if 'pull_request' not in issue]
        return []

    def ai_summarize_repo(self, repo_data, commits, issues):
        """Use Groq AI to summarize the GitHub repository data"""
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        commits_text = "\n".join([f"- {c['commit']['message']} (by {c['commit']['author']['name']})" for c in commits[:5]])
        issues_text = "\n".join([f"- {i['title']}" for i in issues[:5]])

        prompt = f"""
        Analyze this GitHub repository data and give a clean, structured summary for a developer:
        
        📂 Repo: {repo_data.get('full_name')}
        📝 Description: {repo_data.get('description', 'No description')}
        ⭐ Stars: {repo_data.get('stargazers_count')} |  Forks: {repo_data.get('forks_count')} | 💻 Language: {repo_data.get('language')}
        
         Recent Commits:
        {commits_text if commits_text else "No recent commits found."}
        
        🐛 Open Issues:
        {issues_text if issues_text else "No open issues. Clean repo!"}
        
        Format the output beautifully with emojis. Give a brief overview, highlight the recent activity, and summarize the top open issues. Keep it professional and concise.
        """
        
        response = client.chat.completions.create(
            model=Config.SMART_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content

    # ========================================
    # 👤 MY ACCOUNT ANALYSIS (Requires Token)
    # ========================================
    
    def get_my_profile(self):
        """Fetch authenticated user's profile"""
        url = "https://api.github.com/user"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return {"error": "Failed to fetch profile. Check your GITHUB_TOKEN in .env file or provide token."}

    def get_my_top_repos(self, count=5):
        """Fetch user's top repositories sorted by stars"""
        url = f"https://api.github.com/user/repos?sort=stars&direction=desc&per_page={count}&type=all"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []

    def get_my_languages(self):
        """Analyze languages used across all user repos"""
        repos = self.get_my_top_repos(100)
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        # Sort by frequency
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        return sorted_langs[:5]  # Top 5 languages

    def get_my_contributions(self):
        """Fetch recent contributions stats"""
        profile = self.get_my_profile()
        if "error" in profile:
            return {}
        
        return {
            "public_repos": profile.get("public_repos", 0),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "account_age": profile.get("created_at", ""),
            "total_stars": 0  # Will be calculated
        }

    def analyze_my_account(self):
        """Use Groq AI to analyze the user's entire GitHub profile"""
        profile = self.get_my_profile()
        if "error" in profile:
            return profile["error"], None, 0
        
        repos = self.get_my_top_repos(10)
        languages = self.get_my_languages()
        
        # Calculate total stars
        total_stars = sum([r.get('stargazers_count', 0) for r in repos])
        
        # Format repos for AI
        repo_details = "\n".join([
            f"- {r['name']}: ⭐ {r['stargazers_count']} stars | 💻 {r.get('language', 'N/A')} | 🍴 {r['forks_count']} forks | 📝 {r.get('description', 'No description')[:80]}" 
            for r in repos
        ])
        
        # Format languages
        lang_text = ", ".join([f"{lang} ({count} repos)" for lang, count in languages]) if languages else "No languages detected"

        client = Groq(api_key=Config.GROQ_API_KEY)
        
        prompt = f"""
        Analyze this GitHub developer profile and give a cool, structured "Developer Audit":
        
        👤 Username: {profile.get('login')}
        📛 Name: {profile.get('name', 'N/A')}
        📝 Bio: {profile.get('bio', 'No bio')}
        🏢 Company: {profile.get('company', 'N/A')}
        📍 Location: {profile.get('location', 'N/A')}
        🌟 Public Repos: {profile.get('public_repos')} |  Followers: {profile.get('followers')} |  Following: {profile.get('following')}
        ⭐ Total Stars Earned: {total_stars}
        💻 Top Languages: {lang_text}
        📅 Account Created: {profile.get('created_at', 'Unknown')}
        
        🏆 Top 10 Repositories:
        {repo_details if repo_details else "No public repositories found."}
        
        Format the output beautifully with emojis in this structure:
        
        1. **Developer Persona Title** (e.g., "The Open Source Enthusiast", "The Backend Wizard", "The Rising Star")
        2. **Profile Overview** - Brief summary of who they are
        3. **Strengths** - Highlight their best qualities based on repos and languages
        4. **Top Projects** - Mention their best 2-3 repos with why they're impressive
        5. **Coding Style** - What kind of developer they seem to be based on their stack
        6. **Growth Tips** - 2-3 actionable tips to improve their GitHub profile and get more stars
        
        Keep it encouraging, professional, and insightful. Make it feel like a premium developer audit.
        """
        
        response = client.chat.completions.create(
            model=Config.SMART_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1000
        )
        return response.choices[0].message.content, profile, total_stars