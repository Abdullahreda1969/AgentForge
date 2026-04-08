import logging
import sys
import os
import time
import datetime

# استيرادات الوكلاء بناءً على هيكلية مشروعك
from agentforge.agents.architect import ArchitectAgent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.tester import TesterAgent
from agentforge.agents.executor import ExecutorAgent
from agentforge.agents.reviewer import Reviewer

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentForge")

class AgentForgeOrchestrator:
    def __init__(self):
        # تهيئة الوكلاء بنفس المسميات القديمة
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
            "status": "initialized"
        }

    def start_cycle(self, project_name, description, lang="python", auto_run=True, max_attempts=3):
        """يبدأ دورة حياة المشروع مع الحفاظ على التوافق مع app_gui.py"""
        self.project_state = {
            "name": project_name,
            "description": description,
            "lang": lang,
            "auto_run": auto_run,
            "max_attempts": max_attempts,
            "status": "starting",
            "structure": {}
        }
        
        logger.info(f"🚀 انطلاق المهمة: {project_name}")
        
        # المرحلة 1: التصميم
        self._run_design_phase()
        
        # المرحلة 2: البرمجة (المحسنة)
        success = self._run_coding_phase()
        
        self.project_state["status"] = "completed" if success else "failed"
        return self.project_state
    
    def _run_design_phase(self):
        """مرحلة هندسة هيكل المشروع"""
        logger.info(f"🏗️ المرحلة 1: تصميم الهيكل لمشروع {self.project_state['name']}...")
        structure = self.architect.design_project(
            self.project_state["name"], 
            self.project_state["description"]
        )
        self.project_state["structure"] = structure
        logger.info(f"✅ تم تحديد {len(structure)} ملفات للبناء.")

    def _run_coding_phase(self):
        logger.info("💻 المرحلة 2: البرمجة مع الحماية من استهلاك الـ Quota...")
        
        project_dir = os.path.join(os.getcwd(), "projects", self.project_state["name"])
        os.makedirs(project_dir, exist_ok=True)

        # دمج القواعد الذهبية لضمان "الذكاء الحركي" في الساعة
        instruction_header = "🚨 CRITICAL ARCHITECTURE RULE: YOU MUST USE root.after() FOR RECURSIVE UPDATES. STATIC TIME IS A FAILURE. 🚨"
        
        technical_rules = (
            "\n### GOLDEN ARCHITECTURE RULES ###\n"
            "1. REAL-TIME LOGIC: Use `root.after()` for periodic updating.\n"
            "2. WINDOW STABILITY: Use `root.title()` and `root.mainloop()` correctly.\n"
            "3. NO TERMINAL: All outputs must appear on the GUI Label.\n"
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
                    logger.info(f"📝 محاولة برمجة {file_name} رقم ({attempts})...")
                    
                    current_task = " ".join(task) if isinstance(task, list) else task
                    enhanced_task = f"{instruction_header}\n\nTask: {current_task}\n{technical_rules}"
                    
                    # نرسل آخر محاولة فقط لتوفير الـ Tokens ومنع الـ 429
                    short_history = history[-1:] if history else []

                    # 1. البرمجة (Coder)
                    code = self.coder.write_code(
                        file_name, 
                        self.project_state["description"], 
                        enhanced_task, 
                        history=short_history
                    )

                    # 2. المراجعة (Reviewer)
                    logger.info("⏳ مراجعة الكود...")
                    review_result = self.reviewer.review_code(code, enhanced_task, history=short_history)
                    
                    if review_result.strip().upper().startswith("FAIL"):
                        logger.warning(f"⚠️ المراجع رفض الكود. المحاولة القادمة ستكون أذكى.")
                        history.append(f"Attempt {attempts} - Review Fail: {review_result}")
                        continue

                    # 3. الفحص النحوي (Tester)
                    is_valid, error_msg = self.tester.validate_code(code)
                    if not is_valid:
                        logger.warning(f"❌ خطأ سنتاكس في {file_name}.")
                        history.append(f"Attempt {attempts} - Syntax Error: {error_msg}")
                        continue

                    # حفظ الملف
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)

                    # 4. اختبار التشغيل (Executor)
                    if file_name.endswith(".py") and should_execute:
                        run_ok, run_output = self.executor.execute_code(file_path)
                        if run_ok:
                            logger.info(f"🎉 نجاح التشغيل لـ {file_name}!")
                            success = True
                        else:
                            logger.warning(f"⚠️ فشل التشغيل، جاري محاولة الإصلاح...")
                            history.append(f"Attempt {attempts} - Runtime Error: {run_output}")
                            continue
                    else:
                        success = True

                    api_failure_count = 0 # تصفير عداد الأخطاء عند النجاح

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        api_failure_count += 1
                        wait_time = 60 * api_failure_count
                        logger.warning(f"🕒 Quota Limit! انتظار {wait_time} ثانية... (محاولة {api_failure_count}/3)")
                        if api_failure_count >= 3:
                            logger.error("🛑 توقف اضطراري لحماية الـ API.")
                            return False
                        time.sleep(wait_time)
                        attempts -= 1
                    else:
                        logger.error(f"🚨 خطأ غير متوقع: {e}")
                        return False

        return True

    def _save_file(self, path, content):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)