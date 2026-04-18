import os
import requests
import json
import logging
from dotenv import load_dotenv

# إعداد السجل
logger = logging.getLogger("AgentForge.Coder")
load_dotenv()

class CoderAgent:
    def __init__(self, memory=None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_id = "gemma-3-1b-it" 
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        self.memory = memory

        self.system_prompt = """
        You are an Expert Python Developer. 
        Your response must be a valid JSON object containing a 'code' field.
        STRICT RULES:
        1. No markdown tags (```python) inside the JSON code field.
        2. Start the code directly with imports.
        3. Use 'with SessionLocal() as db:' for all database operations in helpers.py.
        """

    def write_code(self, file_name, project_desc, task_details, history=None):
        # جلب القوالب من الذاكرة
        template_instruction = ""
        if self.memory and hasattr(self.memory, 'knowledge'):
            templates = self.memory.knowledge.get("Mandatory_Templates", {})
            if file_name in templates:
                template_instruction = f"\n⚠️ USE THIS EXACT TEMPLATE:\n{templates[file_name]}\n"

        history_context = f"\n⚠️ FIX THESE ERRORS: {json.dumps(history)}" if history else ""

        full_prompt = (
            f"{self.system_prompt}\n"
            f"FILE: {file_name}\n"
            f"{template_instruction}\n"
            f"GOAL: {project_desc}\n"
            f"TASK: {task_details}\n"
            f"{history_context}\n"
            "RETURN ONLY JSON: {\"file_name\": \"...\", \"code\": \"...\"}"
        )
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            # طباعة للتصحيح (يمكنك إزالتها بعد أن تعمل)
            print(f"DEBUG: Response status: {response.status_code}")
            
            res_json = response.json()
            
            # طباعة جزء من الرد للتصحيح (اختياري)
            if 'error' in res_json:
                logger.error(f"API Error: {res_json['error']}")
                # محاولة بديلة: استخدام نموذج مختلف أو إعادة المحاولة
                return self._generate_fallback_code(file_name, project_desc, task_details)
            
            # ========== الجزء المهم: التعامل مع تنسيقات الرد المختلفة ==========
            raw_text = self._extract_text_from_response(res_json)
            
            if not raw_text:
                logger.error("No text extracted from API response")
                return self._generate_fallback_code(file_name, project_desc, task_details)
            
            return self._process_response(raw_text)
            
        except Exception as e:
            logger.error(f"🚨 Coder Failure: {e}")
            # محاولة بديلة
            return self._generate_fallback_code(file_name, project_desc, task_details)

    def _extract_text_from_response(self, res_json):
        """استخراج النص من تنسيقات مختلفة للـ API"""
        
        # تنسيق Gemini القياسي
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            candidate = res_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
        
        # تنسيق بديل (بعض الإصدارات)
        if 'choices' in res_json and len(res_json['choices']) > 0:
            if 'message' in res_json['choices'][0]:
                return res_json['choices'][0]['message'].get('content', '')
            if 'text' in res_json['choices'][0]:
                return res_json['choices'][0]['text']
        
        # تنسيق بسيط
        if 'response' in res_json:
            return res_json['response']
        
        # إذا وجدنا نصاً مباشراً
        if 'text' in res_json:
            return res_json['text']
        
        # طباعة المفاتيح المتاحة للتصحيح
        logger.warning(f"Unknown response format. Keys: {list(res_json.keys())}")
        return None

    def _generate_fallback_code(self, file_name, project_desc, task_details):
        """توليد كود بديل عندما يفشل الـ API"""
        logger.warning(f"⚠️ Using fallback code generation for {file_name}")
        
        if file_name == "helpers.py":
            return '''
    # helpers.py - نسخة بديلة معتمدة
    import os
    from dotenv import load_dotenv
    from sqlalchemy.orm import Session
    from .database import SessionLocal, Task
    from typing import List, Optional

    load_dotenv()

    def create_task(title: str, description: str = "") -> Task:
        """إنشاء مهمة جديدة"""
        with SessionLocal() as db:
            task = Task(title=title, description=description)
            db.add(task)
            db.commit()
            db.refresh(task)
            return task

    def get_all_tasks() -> List[Task]:
        """جلب جميع المهام"""
        with SessionLocal() as db:
            return db.query(Task).all()

    def get_task_by_id(task_id: int) -> Optional[Task]:
        """جلب مهمة محددة"""
        with SessionLocal() as db:
            return db.query(Task).filter(Task.id == task_id).first()

    def update_task(task_id: int, title: str = None, description: str = None) -> bool:
        """تحديث مهمة"""
        with SessionLocal() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                if title:
                    task.title = title
                if description:
                    task.description = description
                db.commit()
                return True
            return False

    def delete_task(task_id: int) -> bool:
        """حذف مهمة"""
        with SessionLocal() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                db.delete(task)
                db.commit()
                return True
            return False
    '''
        
        elif file_name == "config.py":
            return '''
    # config.py
    import os
    from dotenv import load_dotenv

    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///inventory.db")
    APP_NAME = "Inventory Management System"
    DEBUG = True
    '''
        
        elif file_name == "database.py":
            return '''
    # database.py
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    import os
    from datetime import datetime

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///inventory.db")

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class Task(Base):
        __tablename__ = "tasks"
        
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String, nullable=False)
        description = Column(String, default="")
        created_at = Column(DateTime, default=datetime.utcnow)

    Base.metadata.create_all(bind=engine)
    '''
        
        return "# Fallback code generated"

    def _process_response(self, text):
        """دالة تنظيف الكود لضمان عدم وجود Syntax Error"""
        try:
            # 1. محاولة استخراج الكود من JSON إذا أرسله الموديل داخل هيكل JSON
            if '"code":' in text:
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1
                try:
                    data = json.loads(text[start_idx:end_idx])
                    text = data.get("code", text)
                except:
                    pass

            # 2. تنظيف الأسطر الأولى من أي شوائب (مثل ```python أو كلمة python)
            lines = text.split('\n')
            final_code_lines = []
            found_start = False

            for line in lines:
                # نبدأ الحفظ فقط عندما نجد أول سطر برمجي حقيقي
                stripped = line.strip().lower()
                if not found_start:
                    if stripped.startswith('import') or stripped.startswith('from') or stripped.startswith('#'):
                        found_start = True
                        final_code_lines.append(line)
                    continue # تجاهل أي سطر قبل البداية
                
                # تجاهل علامات الإغلاق الخاصة بالماركدوان
                if stripped == '```':
                    continue
                
                final_code_lines.append(line)

            return '\n'.join(final_code_lines).strip()
        except Exception as e:
            return text.strip()