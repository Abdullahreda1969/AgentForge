import logging
import sys
import os
import time
import datetime

# استيرادات الوكلاء بناءً على هيكلية مشروعك (تأكد من وجود هذه الملفات في مساراتها)
from agentforge.agents.architect import ArchitectAgent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.tester import TesterAgent
from agentforge.agents.executor import ExecutorAgent
from agentforge.agents.reviewer import Reviewer

# إعدادات الطباعة والسجل
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentForge")

class AgentForgeOrchestrator:
    def __init__(self):
        # تهيئة الوكلاء
        self.architect = ArchitectAgent()
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.executor = ExecutorAgent()
        self.reviewer = Reviewer()
        self.project_state = {
            "name": "",
            "language": "python",
            "description": "",
            "structure": {},
            "status": "initialized",
            "duration": 0
        }

    def start_cycle(self, project_name, description, lang="python", auto_run=True, max_attempts=3):
        """الدالة الأساسية التي تبدأ منها عملية الصهر"""
        start_time = time.time()
        self.project_state.update({
            "name": project_name,
            "description": description,
            "lang": lang,
            "auto_run": auto_run,
            "max_attempts": max_attempts,
            "status": "starting"
        })
        
        logger.info(f"🚀 بدء صهر المشروع: {project_name}")
        
        # 1. مرحلة التصميم
        try:
            structure = self.architect.design_project(project_name, description)
            self.project_state["structure"] = structure
            logger.info(f"✅ تم تصميم الهيكل: {len(structure)} ملفات.")
        except Exception as e:
            logger.error(f"❌ فشل المصمم: {e}")
            return {"status": "failed", "error": "Architect failed"}

        # 2. مرحلة البرمجة والتدقيق
        success = self._run_coding_phase()
        
        self.project_state["duration"] = int(time.time() - start_time)
        self.project_state["status"] = "completed" if success else "failed"
        
        return self.project_state

    def _run_coding_phase(self):
        project_dir = os.path.join(os.getcwd(), "projects", self.project_state["name"])
        os.makedirs(project_dir, exist_ok=True)

        # 🚨 القاعدة الذهبية (السر الذي يجعل الساعة تعمل)
        instruction_header = (
            "CRITICAL RULE: For REAL-TIME updates (like clocks), YOU MUST USE 'root.after(1000, function_name)'.\n"
            "STRICT PROHIBITION: NEVER use absolute paths like 'C:\\Users\\...'. Use relative paths only.\n"
            "STRICT PROHIBITION: DO NOT use infinite while-loops for UI updates."
        )

        max_retries = self.project_state.get("max_attempts", 3)
        should_execute = self.project_state.get("auto_run", True)
        api_failure_count = 0

        for file_name, task in self.project_state["structure"].items():
            success = False
            attempts = 0
            history = []

            while attempts < max_retries and not success:
                try:
                    attempts += 1
                    logger.info(f"📝 برمجة {file_name} - محاولة {attempts}/{max_retries}")
                    
                    # تحضير المهمة مع التعليمات الصارمة
                    current_task = " ".join(task) if isinstance(task, list) else task
                    full_prompt = f"{instruction_header}\n\nTask: {current_task}"
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        api_failure_count += 1
                        wait_time = 120 * api_failure_count # زدنا الانتظار لدقيقتين
                        logger.warning(f"🕒 السيرفر مزدحم! سأنتظر {wait_time} ثانية قبل المحاولة مجدداً...")
                        time.sleep(wait_time)
                        attempts -= 1 # لا تحسبها محاولة فاشلة، أعدها
                    # تقليل الـ history لمنع خطأ 429
                    short_history = history[-1:] if history else []

                    # استدعاء المبرمج
                    code = self.coder.write_code(
                        file_name, 
                        self.project_state["description"], 
                        full_prompt, 
                        history=short_history
                    )

                    # المراجعة المنطقية
                    review_result = self.reviewer.review_code(code, full_prompt, history=short_history)
                    if "FAIL" in review_result.upper():
                        logger.warning(f"⚠️ المراجع رفض الكود في محاولة {attempts}")
                        history.append({"feedback": review_result})
                        continue

                    # الفحص النحوي
                    is_valid, error_msg = self.tester.validate_code(code)
                    if not is_valid:
                        logger.warning(f"❌ خطأ نحو في {file_name}")
                        history.append({"feedback": error_msg})
                        continue

                    # حفظ الملف
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)

                    # اختبار التشغيل الفعلي
                    if file_name.endswith(".py") and should_execute:
                        run_ok, run_output = self.executor.execute_code(file_path)
                        if run_ok:
                            success = True
                            logger.info(f"🎉 تم صهر {file_name} بنجاح!")
                        else:
                            history.append({"feedback": f"Runtime Error: {run_output}"})
                            continue
                    else:
                        success = True

                    api_failure_count = 0 # تصفير عند النجاح

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        api_failure_count += 1
                        wait_time = 60 * api_failure_count
                        logger.warning(f"🕒 ضغط API! سأنتظر {wait_time} ثانية...")
                        if api_failure_count >= 3: return False
                        time.sleep(wait_time)
                        attempts -= 1
                    else:
                        logger.error(f"🚨 خطأ: {e}")
                        return False

        # --- توليد ملف التشغيل start_app.bat (بدون مسافات بادئة للأوامر) ---
        self._generate_bat_file(project_dir)
        
        return True

    def _generate_bat_file(self, project_dir):
        """توليد ملف بات نظيف بدون مسافات بادئة للأوامر لتجنب خطأ الويندوز"""
        bat_content = (
            "@echo off\n"
            "title AgentForge Launcher\n"
            "echo 🚀 Launching Project...\n"
            "python main.py\n"
            "if %errorlevel% neq 0 (\n"
            "    echo ❌ Application Crashed!\n"
            ")\n"
            "pause"
        )
        bat_path = os.path.join(project_dir, "start_app.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

    def _save_file(self, path, content):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)