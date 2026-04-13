import os
import json
import requests
import logging
from dotenv import load_dotenv

# --- إعداد الـ Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ArchitectAgent:
    def __init__(self):
        # سحب المفتاح من البيئة الآمنة
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it"
        # الرابط المباشر للموديل
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        
        self.system_prompt = """
        You are a Senior Software Architect. Your goal is to design a clean, modular directory structure for Python projects.

        STRICT DESIGN RULES:
        1. WEB FRAMEWORK: Use Streamlit for the UI. It is the best for our cloud environment.
        2. STATE MANAGEMENT: For interactive apps, instruct the coder to use 'st.session_state' to store data. Avoid local file databases (like .db or .txt) unless explicitly asked.
        3. MODULARITY: Separate logic from data processing.
        4. NAMING: Use snake_case for filenames and PascalCase for Classes.
        5. ENTRY POINT: Ensure there is a clear main.py to launch the application.
        6. HYBRID ENVIRONMENT AWARENESS:
        - Always plan for a 'config.py' or 'utils.py' to manage API keys.
        - Design the logic to support both Local (dotenv) and Cloud (streamlit secrets) environments.
        - Ensure the structure includes a '.streamlit/secrets.toml' placeholder for local testing.
        # - Do not include .env in the project structure. The system will inject it automatically. However, you MUST ensure that config.py or the main file expects the API key from environment variables.
        "If a [STRATEGIC TEMPLATE] is provided, prioritize its architectural patterns."
        """

    def design_project(self, name, description):
        logger.info(f"🧠 المصمم الاحترافي يخطط لمشروع: {name}...")
        
        user_context = f"Project: {name}\nGoal: {description}\nContext: Create a functional Python GUI application."
        full_prompt = f"{self.system_prompt}\n\n{user_context}"
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # درجة حرارة منخفضة لضمان الحصول على JSON سليم
                "maxOutputTokens": 1024
            }
        }
        
        headers = {'Content-Type': 'application/json'}

        try:
            # استدعاء الموديل عبر requests بدلاً من مكتبة genai القديمة
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            res_json = response.json()
            
            if "candidates" in res_json:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                structure = self._parse_json_response(raw_text)
                
                # ضمان وجود الملفات الأساسية
                if "main.py" not in structure:
                    structure["main.py"] = "Create the main GUI entry point using Streamlit."
                if "start_app.bat" not in structure:
                    structure["start_app.bat"] = "streamlit run main.py"
                    
                return structure
            else:
                raise Exception(res_json.get("error", {}).get("message", "فشل في الحصول على رد"))

        except Exception as e:
            logger.error(f"❌ خطأ في تواصل المصمم: {e}")
            return {"main.py": "import streamlit as st\nst.title('Failed to generate project structure')"}

    def _parse_json_response(self, text):
        """دالة قوية لاستخراج الـ JSON وتطهيره من أي نص زائد"""
        try:
            # تنظيف علامات الماركدوان إن وجدت
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except:
            try:
                import re
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except Exception as e:
                logger.error(f"❌ فشل تحويل الرد إلى JSON: {e}")
                return {"main.py": "Coding task failed"}