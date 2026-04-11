import os
import requests
import json
import logging
from dotenv import load_dotenv

# إعداد الـ Logger الخاص بـ AgentForge
logger = logging.getLogger("AgentForge.Reviewer")

load_dotenv()

class Reviewer:
    def __init__(self):
        # سحب المفتاح من البيئة الآمنة
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it"
        # الرابط المباشر المستقر
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"

    def review_code(self, code, task, history=None): 
        """مراجعة الكود بناءً على متطلبات المهمة ومعايير الجودة الصارمة."""
        
        prompt = f"""
        You are a Lead QA Engineer. Your goal is to strictly review the following Python code.
        
        "When reviewing, ensure the code follows the [STRATEGIC TEMPLATE] patterns if one was provided. Specifically, for Streamlit, reject any code that resets widget-linked keys outside of a callback function."
        
        ---
        TARGET TASK: {task}
        PREVIOUS FAILURES (To avoid): {history if history else 'None'}
        ---
        CODE TO REVIEW:
        {code}
        ---

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
        12. SCOPE: FAIL if the UI is non-responsive.

        ⚠️ RESPONSE FORMAT:
        - Start with 'PASS' ONLY if the code is 100% production-ready.
        - Start with 'FAIL' followed by a detailed technical report in English for the Coder to fix.
        """
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1, # أقل درجة حرارة ممكنة لضمان أقصى درجات "الصرامة" في النقد
                "maxOutputTokens": 2048
            }
        }

        try:
            # استخدام الاتصال المباشر لضمان الاستمرارية
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            res_json = response.json()
            
            if "candidates" in res_json:
                return res_json['candidates'][0]['content']['parts'][0]['text']
            else:
                error_msg = res_json.get("error", {}).get("message", "API Error")
                return f"FAIL: Communication error with Gemma model ({error_msg}). Please retry."
        except Exception as e:
            logger.error(f"❌ Error in Reviewer Communication: {e}")
            return "FAIL: Connection failure during review process."