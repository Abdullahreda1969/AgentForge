import os
import requests
import json
import logging
import re
from dotenv import load_dotenv

logger = logging.getLogger("AgentForge.Reviewer")
load_dotenv()

class Reviewer:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"

    def review_code(self, code, task, history=None): 
        """مراجعة الكود بناءً على معايير الجودة الصارمة والدستور المحلي."""
        
        rejection_criteria = """
        🛑 CRITICAL REJECTION CRITERIA:
        1. MODULARITY: FAIL if business logic is inside main.py instead of helpers.py.
        2. ENVIRONMENT: FAIL if 'load_dotenv()' or 'import os' is missing in .py files.
        3. STREAMLIT TYPES: FAIL if st.number_input initial value is not a float (e.g., must be 0.0).
        4. IMPORTS: FAIL if the code calls a function from 'helpers.py' without importing it.
        5. PLACEHOLDERS: FAIL if any 'YOUR_API_KEY' or 'pass' statements exist.
        6. MODEL: FAIL if any model ID other than 'gemma-3-27b-it' is mentioned.
        7. SECRETS: FAIL if st.secrets is used without a try-except block.
        8. UI/UX: FAIL if no loading spinner (st.spinner) is used for long operations.
        9. STATIC CONTENT: FAIL if the file is a .bat or .css but contains Python syntax.
        10. CROSS-FILE INTEGRATION: > You are provided with the code of previously approved files in the 'PREVIOUS FAILURES/CONTEXT' section. You MUST verify that the current code calls functions from those files correctly. If helpers.py is provided and it defines calculate(a, b), reject the current code if it calls calculate(data_list). Consistency is your top priority.
        11. MINOR ERRORS: If the error is minor and the programmer can fix it on the next attempt, be very specific in stating the error.
        """

        full_prompt = (
            f"You are a Senior Lead QA Engineer. Review this code strictly:\n"
            f"TASK: {task}\n"
            f"PREVIOUS ERRORS: {history if history else 'None'}\n"
            f"---\n"
            f"CODE TO REVIEW:\n{code}\n"
            f"---\n"
            f"{rejection_criteria}\n"
            f"\nRESPONSE PROTOCOL:\n"
            f"- If perfect: Start with 'PASS'.\n"
            f"- If flawed: Start with 'FAIL' followed by a bulleted technical report."
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
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=30)
            res_json = response.json()
            
            if "candidates" in res_json:
                raw_review = res_json['candidates'][0]['content']['parts'][0]['text']
                return self._clean_review_text(raw_review)
            else:
                return "FAIL: API error during review."
        except Exception as e:
            logger.error(f"❌ Reviewer Error: {e}")
            return f"FAIL: Connection failure during review: {str(e)}"

    def _clean_review_text(self, text):
        """تطهير نص المراجعة لضمان بدءه بـ PASS أو FAIL مباشرة"""
        text = text.strip()
        # إزالة أي علامات ماركداون قد تسبق الكلمة المفتاحية
        text = re.sub(r'^[`\s]*', '', text)
        return text