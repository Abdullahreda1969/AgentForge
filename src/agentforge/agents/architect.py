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
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-27b-it"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        
        self.system_prompt = """
        You are a Senior Software Architect. Your goal is to design a clean, modular directory structure for Python projects.
        RESPONSE FORMAT: Return ONLY a valid JSON object. No markdown, no conversational text.
        Whenever the project requires data persistence, you MUST include a database.py file. This file should define SQLAlchemy models. The project structure should now follow this pattern: database.py (Models/Engine), helpers.py (CRUD Operations), and main.py (UI).
        STRICT ARCHITECTURAL RULES:
        1. MODULARITY: You MUST separate business logic from the UI. Every project must have:
           - 'config.py': To handle environment variables and keys.
           - 'helpers.py': To contain all functions, calculations, and API calls.
           - 'main.py': ONLY for the Streamlit UI and calling functions from helpers.py.
        
        2. NO MOCK SECRETS: Do NOT create '.streamlit/secrets.toml' with "YOUR_KEY" placeholders. The system handles secrets via .env. If you must include it, keep it empty or note it in comments.

        3. FILE NAMING: Use unique, descriptive names (e.g., 'weather_logic.py' instead of 'logic.py'). NEVER use generic names like 'utils' or 'test'.

        4. DEPENDENCY ORDER: In the JSON description for each file, explicitly state which file it depends on. 
           Example: "main.py": "UI code. REQUIRES functions from helpers.py".

        5. STREAMLIT BEST PRACTICES:
           - Use 'st.session_state' for data persistence.
           - Plan for a 'style.css' if professional look is needed.

        6. EXECUTION SEQUENCE (Crucial): 
           Structure the project so that logic is defined before the UI. 
           Order: Configuration -> Logic Helpers -> Main UI.

        REQUIRED OUTPUT STRUCTURE:
        {
          "config.py": "description",
          "helpers.py": "description",
          "main.py": "description",
          "style.css": "description",
          "start_app.bat": "command"
        }
        """

    def design_project(self, name, description):
        logger.info(f"🧠 المصمم الاحترافي يخطط لمشروع: {name}...")
        
        # دمج القواعد المحلية إذا وجدت لضمان الالتزام
        user_context = f"Project Name: {name}\nGoal: {description}\nTask: Design the structure."
        full_prompt = f"{self.system_prompt}\n\n{user_context}"
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.1, # خفضنا الحرارة أكثر لزيادة الدقة في الـ JSON
                "maxOutputTokens": 2048
            }
        }
        
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            res_json = response.json()
            
            if "candidates" in res_json:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                structure = self._parse_json_response(raw_text)
                
                # تصحيح تلقائي للهيكل لضمان عدم الانهيار
                if "main.py" not in structure:
                    structure["main.py"] = "Main Streamlit entry point."
                
                # إزالة أي ملفات قد تسبب تعارضات برمجية غير مقصودة
                forbidden_files = ["utils.py", "test.py", "requests.py"]
                for f in forbidden_files:
                    if f in structure:
                        new_name = f"project_{f}"
                        structure[new_name] = structure.pop(f)

                return structure
            else:
                error_msg = res_json.get("error", {}).get("message", "API Spike or Connection Issue")
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"❌ خطأ في تواصل المصمم: {e}")
            # رد احتياطي (Fallback) في حالة فشل الـ API تماماً
            return {
                "config.py": "Load environment variables.",
                "helpers.py": "Main logic and functions.",
                "main.py": "Streamlit UI calling helpers.py.",
                "start_app.bat": "streamlit run main.py"
            }

    def _parse_json_response(self, text):
        """تطهير الرد واستخراج JSON سليم"""
        try:
            # محاولة البحث عن أول { وآخر } لقص أي نصوص زائدة
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                clean_text = text[start_idx:end_idx]
                return json.loads(clean_text)
            return json.loads(text)
        except Exception as e:
            logger.error(f"❌ فشل تطهير JSON: {e}")
            return {"main.py": "Error in architecture generation."}