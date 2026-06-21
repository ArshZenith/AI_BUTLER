import os
import base64
import re
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from groq import Groq
from config import Config

class GmailSummarizer:
    def __init__(self, token_file='token.json', credentials_file='credentials.json'):
        """
        Initialize GmailSummarizer with configurable file paths
        
        Args:
            token_file: Path to token.json (default: 'token.json')
            credentials_file: Path to credentials.json (default: 'credentials.json')
        """
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.token_file = token_file
        self.credentials_file = credentials_file
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            # Check if token exists
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    # Refresh expired credentials
                    self.creds.refresh(Request())
                else:
                    # Check if credentials.json exists
                    if not os.path.exists(self.credentials_file):
                        return False, f"{self.credentials_file} not found! Please download from Google Cloud Console."
                    
                    # Start OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True, "Authentication successful!"
            
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"
    
    def fetch_recent_emails(self, max_results=10, hours_back=24):
        """Fetch recent emails from Gmail"""
        if not self.service:
            success, msg = self.authenticate()
            if not success:
                return []
        
        try:
            # Calculate time range
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            query = f"after:{int(time_threshold.timestamp())}"
            
            # Fetch emails
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg_data in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_data['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                # Extract body
                body = self._extract_body(msg['payload'])
                
                emails.append({
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body[:1000]  # Limit body length
                })
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _extract_body(self, payload):
        """Extract email body from payload with enhanced HTML cleaning"""
        if 'parts' in payload:
            # Multi-part email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Enhanced HTML cleaning
                        # Remove style tags
                        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        # Remove script tags
                        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        # Remove all HTML tags
                        html = re.sub(r'<[^>]+>', ' ', html)
                        # Clean up whitespace
                        html = re.sub(r'\s+', ' ', html)
                        return html.strip()
        elif payload.get('mimeType') == 'text/plain':
            # Single-part plain text email
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload.get('mimeType') == 'text/html':
            # Single-part HTML email
            data = payload.get('body', {}).get('data', '')
            if data:
                html = base64.urlsafe_b64decode(data).decode('utf-8')
                html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
                html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                html = re.sub(r'<[^>]+>', ' ', html)
                html = re.sub(r'\s+', ' ', html)
                return html.strip()
        
        return "No content available"
    
    def summarize_emails(self, emails):
        """Summarize emails using AI"""
        if not emails:
            return "No recent emails found in the specified time range."
        
        # Format emails for AI
        email_text = ""
        for i, email in enumerate(emails, 1):
            email_text += f"\n--- Email {i} ---\n"
            email_text += f"From: {email['sender']}\n"
            email_text += f"Subject: {email['subject']}\n"
            email_text += f"Date: {email['date']}\n"
            email_text += f"Content: {email['body'][:500]}\n"
        
        try:
            response = self.client.chat.completions.create(
                model=Config.SMART_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an elite email summarizer. Summarize the emails in a clear, concise format.
                        
Format:
📧 **Email Summary**

For each email:
- **From:** [sender]
- **Subject:** [subject]
- **Key Points:** [2-3 bullet points]
- **Action Required:** [Yes/No - if any action needed]

End with:
📊 **Overall Stats:**
- Total emails: X
- Urgent: X
- Can wait: X

Be professional and highlight important information."""
                    },
                    {
                        "role": "user",
                        "content": f"Summarize these recent emails:\n{email_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error summarizing emails: {str(e)}"
    
    def get_email_summary(self, max_results=10, hours_back=24):
        """Main function to fetch and summarize emails"""
        emails = self.fetch_recent_emails(max_results, hours_back)
        return self.summarize_emails(emails)