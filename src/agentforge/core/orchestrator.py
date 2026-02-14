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
            logger.info(f"📁 تم إنشاء مجلد المشروع: {project_dir}")
        
        for file_name, task in self.project_state["structure"].items():
            success = False
            attempts = 0
            feedback = "" # التغذية الراجعة التي سنرسلها للمبرمج
            
            while attempts < 3 and not success:
                attempts += 1
                logger.info(f"📝 جاري كتابة {file_name} (محاولة {attempts})...")
                
                # إرسال التغذية الراجعة للمبرمج إذا وجدت
                # 1. تأكد أن task عبارة عن نص (String) حتى لو جاء من المعماري كقائمة
                current_task = " ".join(task) if isinstance(task, list) else task

                # 2. أضف التغذية الراجعة فقط إذا كانت موجودة
                if feedback:
                    current_task += f"\n\n[CRITICAL FEEDBACK]: {feedback}"

                # 3. أرسل النص الصافي والمنظم للمبرمج
                code = self.coder.write_code(
                    file_name, 
                    self.project_state["description"], 
                    current_task
                )
                
                is_valid, error_msg = self.tester.validate_code(code)
                
                if is_valid:
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)
                    
                    if file_name.endswith(".py"):
                        run_ok, run_output = self.executor.execute_code(file_path)
                        
                        # تحليل ذكي للمخرج: هل المخرج يوحي بالفشل؟
                        failure_keywords = ["error", "failed", "could not", "none", "exception"]
                        is_logic_error = any(word in run_output.lower() for word in failure_keywords)

                        if run_ok and not is_logic_error:
                            logger.info(f"✅ نجاح كامل! المخرج: {run_output.strip()}")
                            success = True
                        else:
                            feedback = f"Runtime Output: {run_output}. Please fix the logic to ensure it works correctly."
                            logger.warning(f"⚠️ فشل منطقي أو برمي، إعادة المحاولة... المخرج: {run_output.strip()}")
                    else:
                        success = True
                else:
                    feedback = f"Syntax Error: {error_msg}"
                    logger.warning(f"❌ خطأ في القواعد، إعادة المحاولة...")
                    
    def _save_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)