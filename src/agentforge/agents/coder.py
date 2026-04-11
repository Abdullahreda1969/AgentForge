import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class CoderAgent:
    def __init__(self):
        # سحب المفتاح من البيئة الآمنة
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it" 
        # الرابط المباشر للموديل لضمان عدم حدوث خطأ 404
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"

        self.system_prompt = """
        You are a Senior Python Developer. You MUST follow these architectural rules:

        1. FRAMEWORK CONTEXT:
           - IF STREAMLIT: Never use infinite loops (`while True`).
           - IMPORTANT: To clear or modify a widget's value (like st.text_input), you MUST use a callback function (`on_change` or `on_click`). 
           - NEVER manually set a session_state key tied to a widget key in the main execution flow.

        2. FEATURE RESTRAINT: Stick strictly to the user request. Do NOT add extra UI elements.

        3. PRODUCTION STANDARDS:
           - Use `st.session_state` for data persistence.
           - Use `os.path.join` for all file paths.
           - For .bat files: Output ONLY raw commands without markdown or emojis.

        4. ERROR HANDLING: Always include basic try-except blocks for file operations.
        
        If a [STRATEGIC TEMPLATE] is provided, prioritize its coding patterns over any other logic.
        """

    def write_code(self, file_name, project_desc, task_details, history=None):
        """
        history: قائمة تحتوي على محاولات الفشل السابقة وردود فعل المراجع.
        """
        # تجهيز سياق الذاكرة (Memory Context)
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
            "Important: Return the COMPLETE improved code without any markdown formatting if it's a .bat file."
        )
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.3, # درجة حرارة منخفضة لضمان كود منطقي وثابت
                "maxOutputTokens": 8192 # مساحة واسعة لكتابة ملفات برمجية كاملة
            }
        }

        try:
            # استخدام requests للاتصال المباشر والمستقر
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            res_json = response.json()
            
            if "candidates" in res_json:
                code = res_json['candidates'][0]['content']['parts'][0]['text']
                # تنظيف الكود من علامات Markdown (```python)
                return code.replace('```python', '').replace('```', '').strip()
            else:
                error_msg = res_json.get("error", {}).get("message", "Unknown API Error")
                raise Exception(f"API Error: {error_msg}")
                
        except Exception as e:
            print(f"⚠️ Coder Agent Error: {e}")
            raise e