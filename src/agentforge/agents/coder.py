from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class CoderAgent:
    def __init__(self):
        # إضافة إعدادات الـ API لضمان التوافق مع v1beta
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "models/gemma-3-1b-it" 
        # تحديث الـ System Prompt ليكون أكثر إصراراً على الحلول الحقيقية
        self.system_prompt = """
        You are an Expert Python Developer. Write clean, robust, and PEP 8 compliant code.

        CODING STANDARDS:

        GUI SAFETY: Never use input(). Use tkinter.Entry for user input.

        EVENT HANDLING: Every button must be linked to a functional callback. NO 'print(ready)' placeholders.

        ERROR HANDLING: Wrap all File I/O and Network calls in try...except blocks.

        PATH SAFETY: Use os.path.join() for cross-platform compatibility. NO hardcoded Windows paths.

        LOGGING: Use print() statements only for console logging to help debugging.
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