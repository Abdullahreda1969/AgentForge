import logging
import sys
import os
import time
import datetime
import json

# استيرادات الوكلاء
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
        self.history = []
        self.project_state = {
            "name": "",
            "language": "python",
            "description": "",
            "enhanced_description": "", # أضفنا هذا الحقل لتخزين الوصف المطور
            "structure": {},
            "status": "initialized",
            "duration": 0
        }

    def _get_template_content(self, template_type, description):
        """تبحث عن ملف القالب وتقرأ محتواه"""
        template_folder = "templates"
        if template_type == "auto":
            desc_low = description.lower()
            if "web" in desc_low or "streamlit" in desc_low:
                template_file = "streamlit_web.txt"
            elif "gui" in desc_low or "tkinter" in desc_low:
                template_file = "tkinter_desktop.txt"
            else:
                return "No specific template, use general best practices."
        else:
            template_file = f"{template_type}.txt"

        file_path = os.path.join(template_folder, template_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Template file not found, proceeding with default logic."
    
    def start_cycle(self, project_name, description, lang="python", auto_run=True, max_attempts=3, template="auto"):
        """الدالة الأساسية مع دعم نظام القوالب (Simulation)"""
        start_time = time.time()
        self.history = [] 
        
        # 1. جلب محتوى القالب وتجهيز الوصف المطور
        template_context = self._get_template_content(template, description)
        enhanced_desc = f"{description}\n\n[STRATEGIC TEMPLATE]:\n{template_context}"
        
        self.project_state.update({
            "name": project_name,
            "description": description,
            "enhanced_description": enhanced_desc, # تخزين الوصف هنا ليعبر بين الدوال
            "template_used": template,
            "status": "designing",
            "max_attempts": max_attempts,
            "auto_run": auto_run
        })

        logger.info(f"🚀 بدء المحاكاة: {project_name} | القالب: {template}")

        # 1. مرحلة التصميم
        try:
            # نمرر enhanced_desc للمصمم
            structure_raw = self.architect.design_project(project_name, enhanced_desc)

            if isinstance(structure_raw, str):
                clean_json = structure_raw.replace("```json", "").replace("```", "").strip()
                try:
                    structure = json.loads(clean_json)
                except:
                    logger.error("❌ فشل تنظيف الـ JSON اليدوي")
                    return {"status": "failed", "error": "JSON parse error"}
            else:
                structure = structure_raw            

            if not structure or not isinstance(structure, dict):
                logger.error("❌ فشل المصمم في تقديم هيكل صالح للمشروع.")
                return {"status": "failed", "error": "Architect returned empty structure"}

            self.project_state["structure"] = structure
            logger.info(f"✅ تم تصميم الهيكل: {len(structure)} ملفات.")
            
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع أثناء التصميم: {e}")
            return {"status": "failed", "error": str(e)}

        # 2. مرحلة البرمجة والتدقيق
        success = self._run_coding_phase()
        
        self.project_state["duration"] = int(time.time() - start_time)
        self.project_state["status"] = "completed" if success else "failed"
        
        return self.project_state

    def _run_coding_phase(self):
        project_name = self.project_state["name"]
        project_dir = os.path.join(os.getcwd(), "projects", project_name)
        os.makedirs(project_dir, exist_ok=True)

        # سحب الوصف المطور من حالة المشروع (هذا هو الإصلاح الجذري)
        enhanced_desc = self.project_state.get("enhanced_description", self.project_state["description"])

        instruction_header = (
            "--- WEB DESIGN RULES ---\n"
            "1. FRAMEWORK: Use 'Streamlit' for the UI.\n"
            "2. NO GUI LIBRARIES: Strictly PROHIBITED to use tkinter or PyQt.\n"
            "3. REAL-TIME: Use 'st.empty()' for dynamic updates.\n"
            "4. PATHS: Use relative paths only."
        )
        
        max_retries = self.project_state.get("max_attempts", 3)
        should_execute = self.project_state.get("auto_run", True)
        
        forbidden_keys = ["project_name", "description", "directory_structure"]
        
        for file_name, task in self.project_state["structure"].items():
            if file_name.lower() in forbidden_keys:
                continue

            success = False
            attempts = 0
            history = []

            while attempts < max_retries and not success:
                try:
                    attempts += 1
                    short_history = history[-1:] if history else []
                    logger.info(f"📝 برمجة {file_name} - محاولة {attempts}/{max_retries}")

                    task_description = " ".join(task) if isinstance(task, list) else task
                    
                    if file_name.endswith(".bat"):
                        current_task = f"STRICT RULE: Output ONLY raw commands for {task_description}."
                    else:
                        current_task = task_description

                    full_prompt = f"{instruction_header}\n\nTask: {current_task}"
                    
                    # نستخدم الآن enhanced_desc المعرف في بداية الدالة
                    code = self.coder.write_code(
                        file_name, 
                        enhanced_desc, 
                        full_prompt, 
                        history=short_history
                    )

                    review_result = self.reviewer.review_code(code, full_prompt, history=short_history)
                    if "FAIL" in review_result.upper():
                        logger.warning(f"⚠️ المراجع رفض الكود في محاولة {attempts}")
                        history.append({"feedback": review_result})
                        continue

                    is_valid, error_msg = self.tester.validate_code(code)
                    if not is_valid:
                        history.append({"feedback": error_msg})
                        continue

                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)

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

                except Exception as e:
                    logger.error(f"🚨 خطأ: {e}")
                    return False

        self._generate_bat_file(project_dir)
        return True

    def _generate_bat_file(self, project_dir):
        bat_content = "@echo off\ntitle AgentForge Web Launcher\nstreamlit run main.py\npause"
        bat_path = os.path.join(project_dir, "start_app.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

    def _save_file(self, path, content):
        clean_content = content.replace("```python", "").replace("```", "").strip()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(clean_content)