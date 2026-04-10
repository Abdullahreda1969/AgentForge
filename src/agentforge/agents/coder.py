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
        You are a Senior Python Developer. You MUST follow these architectural rules:

        1. FRAMEWORK CONTEXT:
           - IF STREAMLIT: Never use infinite loops (`while True`).
           - IMPORTANT: To clear or modify a widget's value (like st.text_input), you MUST use a callback function (`on_change` or `on_click`). 
           - NEVER manually set a session_state key tied to a widget key (e.g., st.session_state.new_task = "") in the main execution flow; this causes `StreamlitAPIException`.

        2. FEATURE RESTRAINT: Stick strictly to the user request. Do NOT add clocks or extra UI elements unless explicitly asked.

        3. PRODUCTION STANDARDS:
           - Use `st.session_state` for data persistence in web apps.
           - Use `os.path.join` for all file paths.
           - For .bat files: Output ONLY raw commands without markdown or emojis.

        4. ERROR HANDLING: Always include basic try-except blocks for file operations or API calls.
        
        "If a [STRATEGIC TEMPLATE] is provided in the user prompt, you MUST prioritize its coding patterns and rules over any other logic. Use it as the foundation for your code."
        
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