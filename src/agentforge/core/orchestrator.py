import logging
import sys
import os
import time
import datetime

from streamlit import feedback, feedback, text
from agentforge.agents.architect import ArchitectAgent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.tester import TesterAgent
from agentforge.agents.executor import ExecutorAgent # الوكيل الجديد
from agentforge.agents.reviewer import Reviewer

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentForge")

class AgentForgeOrchestrator:
    def __init__(self):
        self.architect = ArchitectAgent()
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.executor = ExecutorAgent() # تفعيل الوكيل المنفذ
        self.reviewer = Reviewer() # تفعيل الوكيل المُراجع
        self.project_state = {
            "name": "",
            "language": "",
            "description": "",
            "structure": {},
            "status": "initialized"
        }

    def start_cycle(self, project_name, description, lang="python", auto_run=True, max_attempts=3):
        """يبدأ دورة حياة المشروع مع إعدادات مخصصة من الواجهة"""
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
        
        # المرحلة 2: البرمجة
        self._run_coding_phase()
        
        self.project_state["status"] = "completed"
        return self.project_state
    
    def _run_design_phase(self):
        """مرحلة هندسة هيكل المشروع"""
        logger.info(f"🏗️ المرحلة 1: تصميم الهيكل لمشروع {self.project_state['name']}...")
        
        # استدعاء المصمم (Architect) لتحديد الملفات المطلوبة
        structure = self.architect.design_project(
            self.project_state["name"], 
            self.project_state["description"]
        )
        
        # حفظ الهيكل في حالة المشروع
        self.project_state["structure"] = structure
        logger.info(f"✅ تم تحديد {len(structure)} ملفات للبناء.")
    

    def _run_architect_phase(self):
        logger.info("🏗️  المرحلة 1: تصميم الهيكل...")
        structure = self.architect.analyze_project(self.project_state["description"], self.project_state["language"])
        self.project_state["structure"] = structure

    def _run_coding_phase(self):
        logger.info("💻 المرحلة 2: البرمجة والتدقيق مع التصحيح الذاتي...")
        project_dir = self.project_state["name"]
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        max_retries = self.project_state.get("max_attempts", 3)
        should_execute = self.project_state.get("auto_run", True)

        for file_name, task in self.project_state["structure"].items():
            success = False
            attempts = 0
            feedback = ""
            
            while attempts < max_retries and not success:
                attempts += 1
                logger.info(f"📝 جاري كتابة {file_name} (محاولة {attempts})...")
                
                current_task = " ".join(task) if isinstance(task, list) else task
                if feedback:
                    current_task += f"\n\n[CRITICAL FEEDBACK]: {feedback}"

                # 1. المبرمج يكتب الكود
                code = self.coder.write_code(file_name, self.project_state["description"], current_task)

                # --- 🔍 بداية مرحلة المراجعة (Review Phase) الجديدة ---
                logger.info(f"🧐 مراجعة الكود لـ {file_name} بواسطة الوكيل المراجع...")
                review_result = self.reviewer.review_code(code, current_task)
                
                if "FAIL" in review_result.upper():
                    feedback = f"Reviewer Rejection: {review_result}"
                    logger.warning(f"⚠️ المراجع رفض الكود في {file_name}. السبب: {review_result[:100]}...")
                    continue # العودة لبداية الحلقة لإعادة الكتابة بناءً على نقد المراجع
                
                logger.info(f"✅ المراجع أعطى الضوء الأخضر لـ {file_name}.")
                # --- 🔍 نهاية مرحلة المراجعة ---

                # 2. فحص القواعد النحوية (Syntax)
                is_valid, error_msg = self.tester.validate_code(code)
                
                if is_valid:
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)
                    
                    if file_name.endswith(".py") and should_execute:
                        logger.info(f"🔍 جاري اختبار تشغيل {file_name}...")
                        run_ok, run_output = self.executor.execute_code(file_path)
                        
                        # تحليل النتائج
                        failure_keywords = ["error", "failed", "exception", "timed out"]
                        is_logic_error = any(word in run_output.lower() for word in failure_keywords)

                        if run_ok and not is_logic_error:
                            logger.info(f"✅ نجاح التشغيل والاختبار!")
                            success = True
                        else:
                            feedback = f"Runtime Issue: {run_output}"
                            logger.warning(f"⚠️ فشل في الاختبار الفعلي، إعادة المحاولة...")
                    else:
                        logger.info(f"✅ تم حفظ {file_name} بنجاح.")
                        success = True
                else:
                    feedback = f"Syntax Error: {error_msg}"
                    logger.warning(f"❌ خطأ في القواعد، إعادة المحاولة...")

            if not success:
                report_path = os.path.join(project_dir, "CRASH_REPORT.md")
                
                # الحصول على الوقت والتاريخ الحالي بتنسيق مقروء
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                crash_content = f"""# ⚠️ تقرير عطل في الملف: {file_name}
                
    ## 📅 معلومات التوقيت
    - **التاريخ والوقت:** {now}

    ## 🔍 حالة النظام عند الفشل
    - **عدد المحاولات:** {attempts}
    - **المهمة المطلوبة:** {current_task[:200]}...

    ## ❌ آخر تغذية راجعة (Feedback)
    ```text
    {feedback}
    تم إنشاء هذا التقرير تلقائياً بواسطة AgentForge v1.0.0
    """
    self._save_file(report_path, crash_content)
    
    logger.error(f"📁 تم إنشاء تقرير العطل المفصل في {file_name}.")



    def _save_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)