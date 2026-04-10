from google import genai
import os
import json
import logging # استيراد المكتبة
from dotenv import load_dotenv

# --- تعريف الـ logger لكي لا يظهر الخطأ ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# ---------------------------------------

load_dotenv()

class ArchitectAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemma-3-27b-it"
        
         # التعديل المطلوب في ArchitectAgent
        self.system_prompt = """
        You are a Senior Software Architect. Your goal is to design a clean, modular directory structure for Python projects.

        STRICT DESIGN RULES:
        
        1. WEB FRAMEWORK: Use Streamlit for the UI. It is the best for our cloud environment.
        
        2. STATE MANAGEMENT: For interactive apps, instruct the coder to use 'st.session_state' to store data. Avoid local file databases (like .db or .txt) unless explicitly asked.

        3. MODULARITY: Separate logic from data processing.

        4. NAMING: Use snake_case for filenames and PascalCase for Classes.

        5. ENTRY POINT: Ensure there is a clear main.py to launch the application.
        
        Output MUST be a raw JSON object ONLY. No preamble, no markdown code blocks.
        """
    def design_project(self, name, description):
        logger.info(f"🧠 المصمم الاحترافي يخطط لمشروع: {name}...")
        
        # إضافة تعليمات مخصصة لكل طلب لتقليل الملفات
        user_context = f"Project: {name}\nGoal: {description}\nContext: Create a functional Python GUI application."
        full_prompt = f"{self.system_prompt}\n\n{user_context}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
            )
            
            structure = self._parse_json_response(response.text)
            
            # ضمان وجود الملفات الأساسية بتعليمات برمجية وليست وصفية
            if "main.py" not in structure:
                structure["main.py"] = "Create the main GUI entry point using tkinter."
            if "start_app.bat" not in structure:
                structure["start_app.bat"] = "python main.py"
                
            return structure

        except Exception as e:
            logger.error(f"❌ خطأ في تواصل المصمم: {e}")
            return {"main.py": "import tkinter as tk\nroot = tk.Tk()\nroot.mainloop()"}

    def _parse_json_response(self, text):
        """دالة قوية لاستخراج الـ JSON حتى لو وجد نص غريب حوله"""
        try:
            # محاولة التنظيف العادية
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except:
            try:
                # محاولة البحث عن أول { وآخر } في حال وجود ثرثرة من الموديل
                import re
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except Exception as e:
                logger.error(f"❌ فشل تحويل الرد إلى JSON: {e}")
                return {"main.py": "Coding task failed"}