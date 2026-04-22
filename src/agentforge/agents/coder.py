# coder.py - النسخة النهائية الكاملة
import os
import requests
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger("AgentForge.Coder")
load_dotenv()


class CoderAgent:
    def __init__(self, memory=None, use_local=None, templates=None):
        """
        memory: ذاكرة النظام
        use_local: True = Ollama, False = Gemini, None = كشف تلقائي
        templates: SmartTemplates للقوالب الذكية
        """
        self.memory = memory
        self.templates = templates
        
        # كشف البيئة إذا لم يحدد المستخدم
        if use_local is None:
            use_local = self._detect_local_environment()
        
        self.use_local = use_local

        if use_local:
            # ========== وضع Ollama المحلي ==========
            self.model_name = os.getenv("OLLAMA_MODEL", "gemma3")
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
            logger.info(f"💻 CoderAgent: Using LOCAL Ollama (model: {self.model_name})")
        else:
            # ========== وضع Gemini السحابي ==========
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model_id = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
            logger.info(f"☁️ CoderAgent: Using CLOUD Gemini (model: {self.model_id})")
        
        # النظام prompt الموحد
        self.system_prompt = """
        You are an Expert Python Developer. 
        Your response must be a valid JSON object containing a 'code' field.
        STRICT RULES:
        1. No markdown tags (```python) inside the JSON code field.
        2. Start the code directly with imports.
        3. Use 'with SessionLocal() as db:' for all database operations in helpers.py.
        """
        
        # التحقق من القوالب
        if self.templates:
            logger.info("✅ Smart templates loaded into CoderAgent")
        else:
            logger.warning("⚠️ No templates provided to CoderAgent - will use AI generation only")

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

    def write_code(self, file_name, project_desc, task_details, history=None):
        """الواجهة الرئيسية - توليد الكود"""
        
        # ========== استخدام القوالب للملفات الأساسية ==========
        if self.templates:
            # config.py
            if file_name == "config.py":
                logger.info(f"📄 Using template for {file_name}")
                return self.templates.get_config_template()
            
            # database.py
            if file_name == "database.py":
                logger.info(f"📄 Using template for {file_name}")
                return self.templates.get_database_template()
            
            # start_app.bat
            if file_name == "start_app.bat":
                logger.info(f"📄 Using template for {file_name}")
                return self.templates.get_start_app_template()
            
            # helpers.py و main.py
            if file_name in ["helpers.py", "main.py"]:
                project_type = self.templates.detect_project_type(project_desc)
                item_name = self.templates.detect_item_name(project_desc, project_type)
                logger.info(f"📄 Using template for {file_name} (type: {project_type}, item: {item_name})")
                
                if file_name == "helpers.py":
                    return self.templates.get_helpers_template(project_type, item_name)
                if file_name == "main.py":
                    return self.templates.get_main_template(project_type, item_name)
        
        # ========== إذا لم يكن هناك قالب، استخدم AI ==========
        if self.use_local:
            return self._generate_with_ollama(file_name, project_desc, task_details, history)
        else:
            return self._generate_with_gemini(file_name, project_desc, task_details, history)

    # ==================== وضع Ollama المحلي ====================

    def _generate_with_ollama(self, file_name, project_desc, task_details, history=None):
        """توليد الكود باستخدام Ollama المحلي"""
        
        prompt = self._build_prompt(file_name, project_desc, task_details, history)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=180)
            result = response.json()
            raw_text = result.get('response', '')
            
            if not raw_text:
                logger.error("Empty response from Ollama")
                return self._get_fallback_code(file_name)
            
            return self._clean_code(raw_text)
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ollama not running! Please run 'ollama serve'")
            return self._get_fallback_code(file_name)
        except requests.exceptions.Timeout:
            logger.error("❌ Ollama timeout - model may be loading or too slow")
            return self._get_fallback_code(file_name)
        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return self._get_fallback_code(file_name)

    # ==================== وضع Gemini السحابي ====================
    def set_templates(self, templates):
        """تعيين القوالب الذكية"""
        self.templates = templates
        if self.templates:
            logger.info("✅ Smart templates loaded into CoderAgent")
    def _generate_with_gemini(self, file_name, project_desc, task_details, history=None):
        """توليد الكود باستخدام Gemini API"""
        
        prompt = self._build_prompt(file_name, project_desc, task_details, history)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096,
                "topP": 0.9
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            res_json = response.json()
            
            if "candidates" in res_json:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                return self._clean_code(raw_text)
            elif "error" in res_json:
                logger.error(f"Gemini API error: {res_json['error']}")
                return self._get_fallback_code(file_name)
            else:
                logger.error(f"Unknown Gemini response: {res_json}")
                return self._get_fallback_code(file_name)
                
        except requests.exceptions.Timeout:
            logger.error("❌ Gemini API timeout")
            return self._get_fallback_code(file_name)
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return self._get_fallback_code(file_name)

    # ==================== دوال مساعدة مشتركة ====================

    def _build_prompt(self, file_name, project_desc, task_details, history=None):
        """بناء الـ prompt الموحد لكلا المحركين"""
        
        history_context = f"\n⚠️ FIX THESE ERRORS: {json.dumps(history)}" if history else ""

        return f"""{self.system_prompt}

FILE: {file_name}
GOAL: {project_desc}
TASK: {task_details}
{history_context}

Return ONLY valid JSON: {{"file_name": "{file_name}", "code": "...code here..."}}
"""

    def _clean_code(self, text):
        """تنظيف الكود من علامات Markdown والـ JSON"""
        try:
            if '"code":' in text:
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    data = json.loads(text[start_idx:end_idx])
                    text = data.get("code", text)
            
            text = text.replace('```python', '').replace('```', '').strip()
            
            lines = text.split('\n')
            while lines and not lines[0].strip():
                lines.pop(0)
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.warning(f"Code cleaning warning: {e}")
            return text.strip()

    def _get_fallback_code(self, file_name):
        """كود احتياطي في حالة فشل جميع المحاولات"""
        
        fallbacks = {
            "config.py": '''# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
APP_NAME = "My Application"
''',
            "database.py": '''# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)
''',
            "helpers.py": '''# helpers.py
from database import SessionLocal, Item

def get_items():
    with SessionLocal() as db:
        return db.query(Item).all()

def add_item(name):
    with SessionLocal() as db:
        item = Item(name=name)
        db.add(item)
        db.commit()
        return item

def delete_item(item_id):
    with SessionLocal() as db:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
''',
            "main.py": '''# main.py
import streamlit as st
from helpers import get_items, add_item, delete_item

st.title("My Application")

with st.sidebar:
    with st.form("add_form"):
        name = st.text_input("Name")
        if st.form_submit_button("Add"):
            add_item(name)
            st.rerun()

items = get_items()
for item in items:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{item.name}**")
    with col2:
        if st.button("Delete", key=item.id):
            delete_item(item.id)
            st.rerun()
''',
            "start_app.bat": '''@echo off
streamlit run main.py
pause
'''
        }
        
        return fallbacks.get(file_name, f"# Fallback code for {file_name}\nprint('Hello World')")