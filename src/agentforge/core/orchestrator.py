import logging
import sys
import os
import time
from agentforge.agents.architect import ArchitectAgent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.tester import TesterAgent
from agentforge.agents.executor import ExecutorAgent # الوكيل الجديد

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentForge")

class AgentForgeOrchestrator:
    def __init__(self):
        self.architect = ArchitectAgent()
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.executor = ExecutorAgent() # تفعيل الوكيل المنفذ
        self.project_state = {
            "name": "",
            "language": "",
            "description": "",
            "structure": {},
            "status": "initialized"
        }

    def start_cycle(self, project_name, description, lang="python"):
        self.project_state.update({"name": project_name, "description": description, "language": lang})
        logger.info(f"🚀 انطلاق المهمة: {project_name}")
        
        # 1. التصميم
        self._run_architect_phase()
        time.sleep(2) # استراحة للـ API
        
        # 2. البرمجة والتدقيق والتشغيل
        self._run_coding_phase()
        
        self.project_state["status"] = "completed"
        logger.info(f"✨ تم بناء وتشغيل {project_name} بنجاح!")
        return self.project_state

    def _run_architect_phase(self):
        logger.info("🏗️  المرحلة 1: تصميم الهيكل...")
        structure = self.architect.analyze_project(self.project_state["description"], self.project_state["language"])
        self.project_state["structure"] = structure

    def _run_coding_phase(self):
        logger.info("💻 المرحلة 2: البرمجة والتدقيق مع التصحيح الذاتي...")
        project_dir = self.project_state["name"]
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        for file_name, task in self.project_state["structure"].items():
            success = False
            attempts = 0
            feedback = ""
            
            while attempts < 3 and not success:
                attempts += 1
                logger.info(f"📝 جاري كتابة {file_name} (محاولة {attempts})...")
                
                current_task = " ".join(task) if isinstance(task, list) else task
                if feedback:
                    current_task += f"\n\n[CRITICAL FEEDBACK]: {feedback}"

                code = self.coder.write_code(file_name, self.project_state["description"], current_task)
                is_valid, error_msg = self.tester.validate_code(code)
                
                if is_valid:
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)
                    
                    if file_name.endswith(".py"):
                        run_ok, run_output = self.executor.execute_code(file_path)
                        
                        failure_keywords = ["error", "failed", "could not", "none", "exception", "timed out"]
                        is_logic_error = any(word in run_output.lower() for word in failure_keywords)

                        if run_ok and not is_logic_error:
                            logger.info(f"✅ نجاح كامل! المخرج: {run_output.strip()}")
                            success = True
                        else:
                            feedback = f"Runtime Issue: {run_output}"
                            logger.warning(f"⚠️ فشل في التشغيل، إعادة المحاولة...")
                    else:
                        success = True
                else:
                    feedback = f"Syntax Error: {error_msg}"
                    logger.warning(f"❌ خطأ في القواعد، إعادة المحاولة...")

            # --- نظام تقرير الأعطال الجديد ---
            # --- نظام تقرير الأعطال المصحح ---
            if not success:
                report_path = os.path.join(project_dir, "CRASH_REPORT.md")
                # استخدمنا علامات تنصيص مفردة لتجنب أي تداخل
                report_content = f'''# ⚠️ تقرير عطل فني: {file_name}
## حالة النظام: فشل بعد {attempts} محاولات

## آخر مخرج من النظام:
{feedback}

## التحليل المقترح:
1. تأكد من توفر اتصال بالإنترنت.
2. تأكد من توافق المكتبات.
3. إذا كان الخطأ Timed Out، فقد يحتاج الكود لتبسيط العمليات.
'''
                self._save_file(report_path, report_content)
                logger.error(f"📁 تم إنشاء تقرير العطل في: {report_path}")

    def _save_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)