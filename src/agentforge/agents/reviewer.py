import os
import requests
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger("AgentForge.Reviewer")
load_dotenv()

class Reviewer:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"

    def review_code(self, code, task, history=None): 
        """Reviews the code based on task requirements and strict quality standards."""
        
        # استخدمنا نصاً عادياً للقواعد لضمان عدم تداخل الأقواس مع f-string
        rejection_criteria = """
        🛑 REJECTION CRITERIA (FAIL if any of these are met):
        1. BUTTON LOGIC: FAIL if any button is not connected to a meaningful function.
        2. DATA INTEGRITY: FAIL if JSON/Data loading is not robust.
        3. PLACEHOLDERS: FAIL if there are empty 'pass' statements or 'TODO' comments.
        4. GUI STANDARDS: FAIL if results are only printed to console.
        5. IMPORTS: FAIL if any library is used but not imported.
        6. SECURITY: FAIL if there are hardcoded local paths like 'C:\\Users\\...'.
        7. README: FAIL if there is no English README.md with setup instructions.
        8. LANGUAGE: FAIL if comments or documentation are not in English.
        9. JSON VALIDITY: FAIL if any .json file created is invalid.
        10. ANIMATION/UPDATE: FAIL if a time-based app is 'static'.
        11. CLEAN REQUIREMENTS: FAIL if requirements.txt contains standard libraries like 'os'.
        12. SCOPE: FAIL if the UI is non-responsive or root.mainloop() is missing.
        13. CALLBACK ERRORS: FAIL if 'lambda' is used in Streamlit widget parameters (on_change/on_click).
        14. PLACEHOLDERS: FAIL if the code contains 'YOUR_API_KEY', 'your-endpoint', or any placeholder strings.
        15. CLOUD READINESS: FAIL if the code doesn't check 'st.secrets' for API keys.
        16. UX: FAIL if an AI-dependent app doesn't use a spinner or loading indicator during API calls.
        """

        full_prompt = (
            f"You are a Lead QA Engineer. Strictly review this code:\n"
            f"TARGET TASK: {task}\n"
            f"PREVIOUS FAILURES: {history if history else 'None'}\n"
            f"---\n"
            f"CODE TO REVIEW:\n{code}\n"
            f"---\n"
            f"{rejection_criteria}\n"
            f"\n⚠️ RESPONSE FORMAT:\n"
            f"- Start with 'PASS' ONLY if the code is 100% production-ready.\n"
            f"- Start with 'FAIL' followed by a detailed technical report in English."
        )
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            res_json = response.json()
            
            if "candidates" in res_json:
                return res_json['candidates'][0]['content']['parts'][0]['text']
            else:
                error_msg = res_json.get("error", {}).get("message", "API Error")
                return f"FAIL: Communication error with Gemma model ({error_msg})."
        except Exception as e:
            logger.error(f"❌ Error in Reviewer Communication: {e}")
            return f"FAIL: Connection failure during review process: {str(e)}"