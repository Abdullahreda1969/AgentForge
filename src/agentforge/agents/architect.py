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
        # إعداد العميل (Client)
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "models/gemma-3-1b-it"
        self.system_prompt = """
        You are an expert Software Architect. 
        Analyze the project and respond ONLY with a valid JSON object.
        Keys: file paths. Values: brief tasks for that file.
        Example: {"main.py": "Entry point that starts the app"}
        """

    def design_project(self, name, description):
        """يستلم الوصف ويعيد هيكل الملفات كقاموس (Dictionary)"""
        logger.info(f"🧠 المصمم يفكر في هيكل مشروع: {name}...")
        
        full_prompt = f"{self.system_prompt}\n\nProject Name: {name}\nDescription: {description}"
        
        try:
            # استخدام مكتبة genai الجديدة بشكل صحيح
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt
            )
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"❌ خطأ في تواصل المصمم: {e}")
            return {"main.py": "Primary script"}

    def _parse_json_response(self, text):
        """دالة مساعدة لتنظيف النص وتحويله إلى JSON"""
        try:
            # تنظيف الـ Markdown
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"❌ فشل تحويل الرد إلى JSON: {e}")
            return {"main.py": "Basic entry point"}