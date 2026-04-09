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
        self.model_id = "models/gemini-flash-latest"
        # 1. تحديث الـ System Prompt ليكون أكثر صرامة واحترافية
        self.system_prompt = """
        You are a Senior Software Architect. Your goal is to design a clean, modular directory structure for Python projects.

        STRICT DESIGN RULES:

        MODULARITY: Separate GUI logic from data processing.

        DOCUMENTATION: Always include a README.md with setup instructions.

        DEPENDENCIES: Always plan for a requirements.txt file.

        NAMING: Use snake_case for filenames and PascalCase for Classes.

        ENTRY POINT: Ensure there is a clear main.py to launch the application.
        
        Output MUST be a raw JSON object ONLY. No preamble, no markdown code blocks, no explanation. Just the JSON.
        """

    def design_project(self, name, description):
        """يستلم الوصف ويعيد هيكل الملفات كقاموس (Dictionary)"""
        logger.info(f"🧠 المصمم الاحترافي يخطط لمشروع: {name}...")
        
        full_prompt = f"{self.system_prompt}\n\nProject Name: {name}\nDescription: {description}"
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config={
                    'response_mime_type': 'application/json',
                }
            )
            # للحصول على النص المستخرج
            result_text = response.text
            
            # تحويل النص إلى قاموس
            structure = self._parse_json_response(response.text)
            
            # 2. ضمان وجود الملفات الاحترافية (Safety Check)
            # إذا نسي الذكاء الاصطناعي أياً منها، نقوم بإضافتها يدوياً هنا
            if "requirements.txt" not in structure:
                structure["requirements.txt"] = "List of all external libraries used in the project."
            if "README.md" not in structure:
                structure["README.md"] = f"Technical documentation and setup guide for {name}."
            if "main.py" not in structure:
                structure["main.py"] = "The main execution script to start the application."
                
            return structure

        except Exception as e:
            logger.error(f"❌ خطأ في تواصل المصمم: {e}")
            # بدلاً من إرجاع ملفات وهمية، نرجع None أو نرفع الخطأ
            return None

    def _parse_json_response(self, text):
        """دالة مساعدة لتنظيف النص وتحويله إلى JSON"""
        try:
            # تنظيف الـ Markdown
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"❌ فشل تحويل الرد إلى JSON: {e}")
            return {"main.py": "Basic entry point"}