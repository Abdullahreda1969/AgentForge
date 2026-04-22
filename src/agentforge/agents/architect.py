# architect.py - النسخة الموحدة النهائية
# يدعم: Ollama محلي (Offline) + Gemini API (Cloud)

import os
import json
import requests
import logging
from dotenv import load_dotenv
from src.agentforge.smart_templates import SmartTemplates


logger = logging.getLogger(__name__)
load_dotenv()


class ArchitectAgent:
    def __init__(self, use_local=None):
        """
        use_local = True  → استخدام Ollama (محلي)
        use_local = False → استخدام Gemini API (سحاب)
        use_local = None  → كشف تلقائي
        """

        # كشف البيئة تلقائياً إذا لم يحدد المستخدم
        if use_local is None:
            use_local = self._detect_local_environment()

        self.use_local = use_local

        if use_local:
            # ========== وضع Ollama المحلي ==========
            self.model_name = os.getenv("OLLAMA_MODEL", "gemma3")
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
            logger.info(f"💻 ArchitectAgent: Using LOCAL Ollama (model: {self.model_name})")
        else:
            # ========== وضع Gemini السحابي ==========
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model_id = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
            logger.info(f"☁️ ArchitectAgent: Using CLOUD Gemini (model: {self.model_id})")

        # النظام prompt الموحد
        self.system_prompt = """
        You are a Senior Software Architect. Your goal is to design a clean, modular directory structure for Python projects.
        RESPONSE FORMAT: Return ONLY a valid JSON object. No markdown, no conversational text.

        STRICT ARCHITECTURAL RULES:
        1. Every project must have:
           - 'config.py': Environment variables and configuration
           - 'database.py': SQLAlchemy models and database engine (if data persistence needed)
           - 'helpers.py': CRUD operations and business logic
           - 'main.py': Streamlit UI calling functions from helpers.py

        2. NO MOCK SECRETS: Do not create placeholder files with "YOUR_KEY"

        3. FILE NAMING: Never use 'utils.py' or 'test.py'

        REQUIRED OUTPUT STRUCTURE:
        {
          "config.py": "Load environment variables and app config",
          "database.py": "SQLAlchemy models and database connection",
          "helpers.py": "CRUD operations and business logic",
          "main.py": "Streamlit UI application",
          "start_app.bat": "streamlit run main.py"
        }
        """
        self.templates = SmartTemplates()  # ✅ أضف هذا السطر

    def _detect_local_environment(self):
        """كشف تلقائي إذا كان Ollama متاحاً محلياً"""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            if response.status_code == 200:
                logger.info("✅ Detected local Ollama, using LOCAL mode")
                return True
        except:
            pass

        if os.getenv("GEMINI_API_KEY"):
            logger.info("☁️ No local Ollama detected, using CLOUD Gemini mode")
            return False

        logger.warning("⚠️ Could not detect environment, defaulting to LOCAL mode")
        return True

    def design_project(self, name, description):
        """الواجهة الرئيسية - تصميم هيكل المشروع"""
        logger.info(f"🧠 Architect designing project: {name}...")

        # ✅ كشف نوع المشروع باستخدام القوالب
        project_type = self.templates.detect_project_type(description)
        item_name = self.templates.detect_item_name(description, project_type)
        
        if self.use_local:
            return self._design_with_ollama(name, description)
        else:
            return self._design_with_gemini(name, description)

    # ==================== وضع Ollama المحلي ====================

    def _design_with_ollama(self, name, description):
        """تصميم الهيكل باستخدام Ollama المحلي"""

        user_context = f"Project Name: {name}\nGoal: {description}\nTask: Design the structure. Return ONLY valid JSON."
        full_prompt = f"{self.system_prompt}\n\n{user_context}"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 2048
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=180)
            result = response.json()
            raw_text = result.get('response', '')

            if not raw_text:
                return self._get_fallback_structure()

            structure = self._parse_json_response(raw_text)
            return self._validate_structure(structure)

        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return self._get_fallback_structure()

    # ==================== وضع Gemini السحابي ====================

    def _design_with_gemini(self, name, description):
        """تصميم الهيكل باستخدام Gemini API"""

        user_context = f"Project Name: {name}\nGoal: {description}\nTask: Design the structure. Return ONLY valid JSON."
        full_prompt = f"{self.system_prompt}\n\n{user_context}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            res_json = response.json()

            if "candidates" in res_json:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                structure = self._parse_json_response(raw_text)
                return self._validate_structure(structure)
            else:
                logger.error(f"Gemini API error: {res_json.get('error', {}).get('message', 'Unknown')}")
                return self._get_fallback_structure()

        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return self._get_fallback_structure()

    # ==================== دوال مساعدة مشتركة ====================

    def _parse_json_response(self, text):
        """تطهير الرد واستخراج JSON سليم"""
        try:
            text = text.replace('```json', '').replace('```', '').strip()
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                clean_text = text[start_idx:end_idx]
                return json.loads(clean_text)
            return json.loads(text)
        except Exception as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            return self._get_fallback_structure()

    def _validate_structure(self, structure):
        """تأكد من وجود الملفات الأساسية"""
        required_files = ["config.py", "database.py", "helpers.py", "main.py"]
        for file in required_files:
            if file not in structure:
                structure[file] = f"{file.replace('.py', '')} file"

        if "start_app.bat" not in structure:
            structure["start_app.bat"] = "streamlit run main.py"

        return structure

    def _get_fallback_structure(self):
        """هيكل احتياطي في حالة فشل جميع المحاولات"""
        return {
            "config.py": "Load environment variables and configuration",
            "database.py": "SQLAlchemy models and database engine",
            "helpers.py": "CRUD operations and business logic",
            "main.py": "Streamlit UI application",
            "start_app.bat": "streamlit run main.py"
        }