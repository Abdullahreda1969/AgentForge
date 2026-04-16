import os
import requests
import json
import logging
from dotenv import load_dotenv

# إعداد السجل
logger = logging.getLogger("AgentForge.Coder")
load_dotenv()

class CoderAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it" 
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"

        self.system_prompt = """
        You are an Expert Python Developer specializing in Modular Clean Code.
        Your response must be a valid JSON object unless the file type is non-python (.bat, .css).
        Never use Placeholders, and never add comments explaining where the code should be placed; write the code in full.
        STRICT CODING PROTOCOL:
        1. SELF-CONTAINED IMPORTS: Every Python file must import all necessary libraries (os, streamlit, etc.) even if they are imported elsewhere.
        2. ENV & SECRETS: 
           - Use 'from dotenv import load_dotenv' and 'load_dotenv()' at the start.
           - Access keys via 'os.getenv("KEY_NAME")'. 
           - For Streamlit Cloud, fallback to 'st.secrets.get("KEY_NAME")'.
        3. MODULAR CALLS: When calling functions from 'helpers.py', ensure they match the names provided by the Architect.
        4. STREAMLIT TYPES: In 'st.number_input', 'value' and 'min_value' MUST be floats (e.g., 0.0) to prevent TypeErrors. 
        5. NON-PYTHON FILES: For .bat or .css, provide only the raw content without any python comments or syntax.

        OUTPUT STRUCTURE (JSON):
        {
          "file_name": "filename.extension",
          "code": "full_source_code_here"
        }
        5. FUNCTION SYNCHRONIZATION:
        Before calling any function from helpers.py or any other file you wrote, you MUST check the function signature (arguments). If helpers.py defines func(data_list), do NOT call it as func(a, b). Always match the data structure (e.g., if inventory is a list of dictionaries, iterate or pass the whole list as defined).
        """

    def write_code(self, file_name, project_desc, task_details, history=None):
        # تجهيز سياق الذاكرة (Memory Context) للأخطاء السابقة
        history_context = ""
        if history:
            history_context = f"\n\n⚠️ PREVIOUS ERRORS TO FIX:\n{json.dumps(history)}"

        full_prompt = (
            f"{self.system_prompt}\n"
            f"FILE TO WRITE: {file_name}\n"
            f"PROJECT GOAL: {project_desc}\n"
            f"TASK FOR THIS FILE: {task_details}\n"
            f"{history_context}\n"
            "Final Instruction: Deliver the code inside the JSON 'code' field. Ensure strings are properly escaped."
        )
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # حرارة منخفضة لضمان استقرار المنطق
                "maxOutputTokens": 8192 
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=30)
            res_json = response.json()
            
            if "candidates" in res_json:
                raw_response = res_json['candidates'][0]['content']['parts'][0]['text']
                return self._process_response(raw_response)
            else:
                error = res_json.get("error", {}).get("message", "Unknown API Error")
                logger.error(f"API Error: {error}")
                raise Exception(f"API Limit/Error: {error}")
                
        except Exception as e:
            logger.error(f"🚨 Coder Failure: {e}")
            raise e

    def _process_response(self, text):
        """دالة ذكية لاستخراج الكود سواء كان JSON أو نص خام"""
        try:
            # محاولة استخراج JSON أولاً
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                data = json.loads(text[start:end])
                return data.get("code", text)
            
            # إذا لم يكن JSON، تنظيف الماركدوان والعودة للنص الخام
            clean_code = text.replace('```python', '').replace('```json', '').replace('```', '').strip()
            return clean_code
        except:
            return text.strip()