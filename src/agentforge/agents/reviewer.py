from google import genai
import os
import logging

logger = logging.getLogger("AgentForge.Reviewer")

class Reviewer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # نلتزم بنفس الموديل المستخدم في بقية الوكلاء لتوحيد الأداء
        self.model_id = "gemini-1.5-flash-8b"

    def review_code(self, code, task, history=None): 
        """Reviews the code based on task requirements and strict quality standards."""
        
        # ملاحظة: استخدمنا {{}} لتمثيل الأقواس داخل f-string لتجنب خطأ بايثون
        prompt = f"""
        You are a Lead QA Engineer. Your goal is to strictly review the following Python code.
        
        ---
        TARGET TASK: {task}
        PREVIOUS FAILURES (To avoid): {history if history else 'None'}
        ---
        CODE TO REVIEW:
        {code}
        ---

        🛑 REJECTION CRITERIA (FAIL if any of these are met):
        1. BUTTON LOGIC: FAIL if any button is not connected to a meaningful function or uses 'print("ready")'.
        2. DATA INTEGRITY: FAIL if JSON/Data loading is not robust. Check for 'TypeError'.
        3. PLACEHOLDERS: FAIL if there are empty 'pass' statements or 'TODO' comments.
        4. GUI STANDARDS: FAIL if results are only printed to console.
        5. IMPORTS: FAIL if any library is used but not imported.
        6. SECURITY: FAIL if there are hardcoded local paths like 'C:\\Users\\...'.
        7. README: FAIL if there is no English README.md with setup instructions.
        8. LANGUAGE: FAIL if comments or documentation are not in English.
        9. JSON VALIDITY: FAIL if any .json file created is empty or contains invalid syntax. Every JSON must start with [] or {{}}.
        10. ANIMATION/UPDATE: FAIL if a time-based app is 'static'. It MUST have a refreshing mechanism (.after() or threading).
        11. CLEAN REQUIREMENTS: FAIL if requirements.txt contains standard libraries like 'tkinter' or 'os'.
        12. SCOPE: FAIL if 'root.mainloop()' is missing or if the UI is non-responsive.
        ⚠️ RESPONSE FORMAT:
        - Start with 'PASS' ONLY if the code is 100% production-ready.
        - Start with 'FAIL' followed by a detailed technical report in English for the Coder to fix.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"❌ Error in Reviewer Communication: {e}")
            return "FAIL: Communication error with Gemma model. Please retry."