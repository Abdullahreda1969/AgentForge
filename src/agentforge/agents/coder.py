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
        You are an expert Python Engineer. 
        CRITICAL RULES:
        1. Use REAL, public, and reliable APIs or libraries (like yfinance, requests, or BeautifulSoup).
        2. DO NOT use fake URLs like 'mock-api.com'.
        3. If you need a financial data, use a known free library.
        4. Return ONLY the code.
        """

    def write_code(self, file_name, project_desc, task_details):
        full_prompt = (
            f"{self.system_prompt}\n"
            f"File to write: {file_name}\n"
            f"Project Context: {project_desc}\n"
            f"Task Details: {task_details}\n"
            "Important: If there is feedback about errors, fix them. If an API fails, try an alternative way or use a robust mock."
        )
        
        try:
            # استخدام config لضمان عدم حدوث تعارض مع الموديلات التجريبية
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt
            )
            return response.text.replace('```python', '').replace('```', '').strip()
        except Exception as e:
            # طباعة الخطأ كاملاً لنعرف إذا كان هناك Rate Limit
            print(f"⚠️ Error: {e}")
            return f"# Error in generating {file_name}"