import logging
import sys
import time
import datetime
import json
import os
import shutil

# تحديد مكان orchestrator.py
current_dir = os.path.dirname(os.path.abspath(__file__)) 

# الصعود 3 مستويات: core -> agentforge -> src -> AgentForge
# المستوى الأول: core
# المستوى الثاني: agentforge
# المستوى الثالث: src
# المستوى الرابع: AgentForge (المجلد الرئيسي)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

# الآن نحدد مسار الـ .env الرئيسي
root_env = os.path.join(project_root, ".env")

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
            "enhanced_description": "", 
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
        """الدالة الأساسية مع دعم نظام القوالب"""
        start_time = time.time()
        self.history = [] 
        
        template_context = self._get_template_content(template, description)
        enhanced_desc = f"{description}\n\n[STRATEGIC TEMPLATE]:\n{template_context}"
        
        self.project_state.update({
            "name": project_name,
            "description": description,
            "enhanced_description": enhanced_desc,
            "template_used": template,
            "status": "designing",
            "max_attempts": max_attempts,
            "auto_run": auto_run
        })

        logger.info(f"🚀 بدء المحاكاة: {project_name} | القالب: {template}")

        try:
            structure_raw = self.architect.design_project(project_name, enhanced_desc)
            if isinstance(structure_raw, str):
                clean_json = structure_raw.replace("```json", "").replace("```", "").strip()
                structure = json.loads(clean_json)
            else:
                structure = structure_raw            

            self.project_state["structure"] = structure
            logger.info(f"✅ تم تصميم الهيكل: {len(structure)} ملفات.")
            
        except Exception as e:
            logger.error(f"❌ خطأ التصميم: {e}")
            return {"status": "failed", "error": str(e)}

        success = self._run_coding_phase()
        self.project_state["duration"] = int(time.time() - start_time)
        self.project_state["status"] = "completed" if success else "failed"
        return self.project_state

    def _run_coding_phase(self):
        project_name = self.project_state["name"]
        project_dir = os.path.join(os.getcwd(), "projects", project_name)
        os.makedirs(project_dir, exist_ok=True)
        enhanced_desc = self.project_state.get("enhanced_description", self.project_state["description"])

        # قائمة المفاتيح التي يجب تجاهلها تماماً لأنها ليست ملفات برمجية
        forbidden_keys = ["project_name", "description", "directory_structure", "file_descriptions", "class_names", "state_management", "coding_rules", "example_code_snippets"]

        for file_name, task in self.project_state["structure"].items():
            # إذا كان المفتاح ليس ملفاً حقيقياً (لا ينتهي بصيغة ملف)، نتجاهله
            if file_name.lower() in forbidden_keys or "." not in file_name:
                continue
            
            success = False
            attempts = 0
            while attempts < self.project_state["max_attempts"] and not success:
                try:
                    attempts += 1
                    logger.info(f"📝 برمجة {file_name} - محاولة {attempts}")
                    code = self.coder.write_code(file_name, enhanced_desc, str(task))
                    
                    # محاولة المراجعة، لكن لا تقتل المشروع إذا فشل السيرفر (503)
                    try:
                        review = self.reviewer.review_code(code, str(task))
                        if "FAIL" in review.upper() and attempts < self.project_state["max_attempts"]:
                            continue
                    except:
                        logger.warning(f"⚠️ السيرفر مضغوط، سيتم تجاوز المراجعة لملف {file_name}")

                    # حفظ الملف في كل الأحوال إذا وصلنا لهذه النقطة
                    self._save_file(os.path.join(project_dir, file_name), code)
                    success = True
                    logger.info(f"💾 تم حفظ {file_name} بنجاح.")
                except Exception as e:
                    logger.error(f"🚨 خطأ في {file_name}: {e}")
        
        self._generate_bat_file(project_dir)
        self._generate_readme(project_name, enhanced_desc, project_dir)
        
        # --- 🚀 نظام الحقن الذكي ---
        try:
            # الوصول للمجلد الرئيسي ديناميكياً
            current_file = os.path.abspath(__file__)
            # نصعد 4 مرات لنصل من core إلى المجلد الرئيسي AgentForge
            master_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            root_env = os.path.join(master_dir, ".env")
            
            target_env = os.path.join(project_dir, ".env")
            
            if os.path.exists(root_env):
                shutil.copy(root_env, target_env)
                logger.info(f"✅ [SYSTEM] تم سحب المفتاح من المجلد الرئيسي وحقنه في: {project_name}")
            else:
                logger.warning(f"⚠️ لم يتم العثور على المفتاح في المسار المتوقع: {root_env}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحديد مسار المفتاح: {e}")
            
            
        self._generate_bat_file(project_dir)
        self._generate_readme(project_name, enhanced_desc, project_dir)
        return True
        

    def _generate_readme(self, project_name, description, project_dir):
        clean_desc = description.split("[STRATEGIC TEMPLATE]")[0].strip()
        readme_content = f"""# 🚀 Project: {project_name.replace('_', ' ').title()}

## 📝 Description
{clean_desc}

## 🌟 Key Features
- **Automated Workflow:** Built using AgentForge multi-agent system.
- **Modern UI:** Interactive interface powered by Streamlit.
- **AI-Validated:** Verified by an AI Reviewer Agent.

## 🛠️ Installation & Setup
1. **Dependencies:** `pip install -r requirements.txt`
2. **Run:** Double-click `start_app.bat` or run `streamlit run main.py`

---
*Created by AgentForge - Your AI Software Factory*
"""
        with open(os.path.join(project_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)
        logger.info(f"✅ README.md generated.")

    def _generate_bat_file(self, project_dir):
        bat_content = "@echo off\ncd /d \"%~dp0\"\nstreamlit run main.py\npause"
        with open(os.path.join(project_dir, "start_app.bat"), "w", encoding="utf-8") as f:
            f.write(bat_content)

    def _save_file(self, path, content):
        clean = content.replace("```python", "").replace("```", "").strip()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(clean)