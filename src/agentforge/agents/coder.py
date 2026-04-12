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

        # تحديث الـ system_prompt في coder.py
        self.system_prompt = """
        You are a Senior Python Developer. You MUST follow these architectural rules:

        1. FRAMEWORK CONTEXT (STREAMLIT):
        - NEVER use 'lambda' inside widget callbacks (on_change, on_click). Define a dedicated function.
        - Example: Use 'on_change=update_data' instead of 'on_change=lambda x: update_data(x)'.
        - NEVER set session_state keys tied to widgets manually in the main flow.

        2. API & SECURITY STANDARDS (STRICT):
        - MODEL RESTRICTION: You are EXCLUSIVELY allowed to use the 'gemma-3-27b-it' model.
        - FORBIDDEN: Do not use 'gemini-pro', 'gemini-1.5-flash', or any other model names.
        - EXACT ENDPOINT: The API URL must always be exactly:
            f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key={api_key}"
        - HYBRID KEY LOGIC: Always implement safe key retrieval:
          api_key = os.getenv("GEMINI_API_KEY")
          try:
              if not api_key and "GEMINI_API_KEY" in st.secrets:
                  api_key = st.secrets["GEMINI_API_KEY"]
          except:
              pass
        -CRITICAL RULE: Never call st.secrets or st.secrets.get() directly in the global scope or without a try-except block. Streamlit WILL CRASH if the secrets file is missing. Always prioritize os.getenv and use a fallback mechanism.
        
        3. PRODUCTION STANDARDS:
        - Use 'st.spinner' for long API calls to improve UX.
        - Use 'try-except' blocks for all 'requests.post' calls.
        
        CRITICAL: Never access st.secrets directly because it raises an exception if the file is missing. Always wrap it in a try-except block or prioritize os.getenv first to ensure local compatibility.
        
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