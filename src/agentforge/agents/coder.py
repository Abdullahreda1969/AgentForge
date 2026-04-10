from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class CoderAgent:
    def __init__(self):
        # إضافة إعدادات الـ API لضمان التوافق مع v1beta
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemma-3-27b-it" 
       # داخل ملف coder.py
        self.system_prompt = """
        You are a Senior Python Developer. You follow strict architectural patterns based on the framework used.

        STRICT OPERATIONAL RULES:
        1. FRAMEWORK CONTEXT:
           - If using STREAMLIT: Never use infinite loops (`while True`). Use `st.session_state` for data persistence. 
           - To reset widgets in Streamlit, ALWAYS use a callback function (`on_click` or `on_change`). NEVER manually set a widget's key value in the main execution flow to avoid `StreamlitAPIException`.
           - If using TKINTER: Use `root.after(ms, func)` for updates. Never use `time.sleep()`.

        2. FEATURE RESTRAINT: Stick strictly to the user's request. Do NOT add clocks, timers, or extra features unless explicitly asked.

        3. PATH NEUTRALITY: Always use `os.path.join` for file operations.

        4. BATCH FILES (.bat):
           - Output ONLY the raw commands.
           - NO markdown, NO emojis, NO explanations.
           - Ensure the path to the script is correct (usually `python main.py`).

        5. PRODUCTION STANDARDS: Code must be clean, commented, and handle basic errors using try-except blocks.
        """

    def write_code(self, file_name, project_desc, task_details, history=None):
        """
        history: قائمة تحتوي على محاولات الفشل السابقة وردود فعل المراجع.
        """
        # تجهيز سياق الذاكرة
        history_context = ""
        if history and len(history) > 0:
            history_context = "\n\n⚠️ MEMORY: Previous attempts for this file failed. Learn from these logs:\n"
            for idx, entry in enumerate(history, 1):
                history_context += f"Attempt {idx}: {entry}\n"
            history_context += "\nFix the issues mentioned above and do not repeat the same mistakes."

        full_prompt = (
            f"{self.system_prompt}\n"
            f"File to write: {file_name}\n"
            f"Project Context: {project_desc}\n"
            f"Task Details: {task_details}\n"
            f"{history_context}\n"
            "Important: Return the COMPLETE improved code."
        )
        
        # داخل ملف coder.py
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt
            )
            return response.text.replace('```python', '').replace('```', '').strip()
        except Exception as e:
            print(f"⚠️ API Error: {e}")
            raise e # 🛑 نرفع الخطأ للأوركسترا بدل إرجاع نص وهمي