from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class CoderAgent:
    def __init__(self):
        # إضافة إعدادات الـ API لضمان التوافق مع v1beta
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "models/gemini-2.0-flash-exp-image-generation" 
       # داخل ملف coder.py
        self.system_prompt = """
        You are a Senior Python Developer specializing in dynamic GUI applications.

        STRICT OPERATIONAL RULES:
        1. DYNAMIC REFRESH: If the project involves time, monitoring, or live data, you MUST implement a recursive loop using `root.after(ms, func)`.
        2. FEATURE RESTRAINT: Never add Buttons or Entry fields unless the user explicitly requested them. Stick to the core utility.
        3. PRODUCTION STANDARDS: Use `from time import strftime` for clocks. Use `tkinter.Label` for displays.
        4. PATH NEUTRALITY: Always use `os.path.join` for any file operations to ensure Windows/Linux compatibility.
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