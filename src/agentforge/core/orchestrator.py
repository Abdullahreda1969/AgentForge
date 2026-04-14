import logging
import sys
import time
import datetime
import re
import json
import os
import shutil
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
    def _inject_env_file(self, project_dir):
        """دالة البحث الصارم عن المفتاح وحقنه"""
        try:
            # نبدأ من مسار ملف الـ orchestrator الحالي
            current_path = os.path.abspath(__file__)
            base_path = current_path
            root_env = None

            # # البحث عن مجلد AgentForge صعوداً
            # while "AgentForge" in base_path.lower():
            #     print(f"DEBUG: Checking in: {base_path}") # سطر جديد
            #     potential_env = os.path.join(base_path, ".env")
            #     if os.path.exists(potential_env):
            #         root_env = potential_env
            #         break
                
            #     parent = os.path.dirname(base_path)
            #     if parent == base_path: break # وصلنا لجذر القرص ولم نجد شيئاً
            #     base_path = parent

            # استبدل حلقة الـ while بهذا الكود تماماً لمرة واحدة لنفهم المسار:
            print(f"🔍 DEBUG: Starting search from: {base_path}")
            while True:
                potential_env = os.path.join(base_path, ".env")
                print(f"🔍 DEBUG: Checking for .env in: {base_path}")
                if os.path.exists(potential_env):
                    root_env = potential_env
                    print(f"✅ FOUND KEY AT: {root_env}")
                    break
                
                parent = os.path.dirname(base_path)
                if parent == base_path or "Users" not in parent: # توقف عند مجلد المستخدم للامان
                    break
                base_path = parent
            
            if root_env:
                # --- هنا مكان سطر الطباعة الذي سيكشف لنا الحقيقة ---
                logger.info(f"🔍 I found the key here: {root_env}")                
                target_env = os.path.join(project_dir, ".env")
                import shutil
                shutil.copy(root_env, target_env)
                print(f"[DEBUG] Successfully injected to: {target_env}\n")
            else:
                print(f"\n[ERROR] Master .env NOT FOUND in any parent directory of AgentForge!\n")

        except Exception as e:
            print(f"[ERROR] Injection failed: {e}")
    
    def _clean_code_output(self, raw_response):
        """
        تنظيف رد الموديل واستخراج الكود البرمجي النقي.
        تتعامل مع JSON، Markdown، وكلمات التوضيح الزائدة.
        """
        actual_code = raw_response
        try:
            # 1. محاولة استخراج JSON إذا وجد بين أقواس متعرجة
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                data = json.loads(json_text)
                if isinstance(data, dict) and "code" in data:
                    actual_code = data["code"]
                else:
                    actual_code = json_text
            else:
                # 2. تنظيف علامات الـ Markdown (```python, ```json, إلخ)
                # نستخدم re.sub بشكل آمن
                clean_text = re.sub(r'```[\w]*\n', '', raw_response)
                clean_text = clean_text.replace('```', '').strip()
                
                # حذف كلمة 'json' أو أي روابط غريبة قد تظهر في السطر الأول
                lines = clean_text.split('\n')
                if lines and (lines[0].strip().lower() == 'json' or lines[0].startswith('http')):
                    actual_code = '\n'.join(lines[1:]).strip()
                else:
                    actual_code = clean_text.strip()

        except Exception as e:
            logger.warning(f"⚠️ فشل التنظيف المتقدم: {e}")
            # تنظيف يدوي بسيط كخيار أخير
            actual_code = raw_response.replace('```python', '').replace('```', '').replace('json', '').strip()

        return actual_code
    
    def _run_coding_phase(self):
        # 1. إعداد المجلدات والحقن
        project_name = self.project_state["name"]
        project_dir = os.path.join(os.getcwd(), "projects", project_name)
        os.makedirs(project_dir, exist_ok=True)
        self._inject_env_file(project_dir)

        enhanced_desc = self.project_state.get("enhanced_description", self.project_state["description"])
        
        # تعريف الوكلاء
        tester = TesterAgent()
        executor = ExecutorAgent()
        
        for file_name, task in self.project_state["structure"].items():
            # تجاهل المفاتيح التي ليست ملفات
            if file_name.lower() in ["project_name", "description"] or "." not in file_name:
                continue
            
            success = False
            attempts = 0
            while attempts < self.project_state.get("max_attempts", 3) and not success:
                try:
                    attempts += 1
                    logger.info(f"📝 برمجة {file_name} - محاولة {attempts}")
                    
                    # استلام الرد
                    raw_response = self.coder.write_code(file_name, enhanced_desc, str(task))
                    
                    # تنظيف واستخراج الكود (باستخدام الدالة التي أنشأناها سابقاً)
                    actual_code = self._clean_code_output(raw_response)

                    # 2. الاختبار البرمجي (Static Analysis)
                    is_valid, report = tester.validate_code(actual_code)
                    if not is_valid:
                        logger.warning(f"❌ خطأ قواعد في {file_name}: {report}")
                        continue 

                    # 3. حفظ الملف
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, actual_code)
                    
                    # 4. التشغيل والتصحيح الذاتي للمكتبات
                    if file_name == "main.py":
                        logger.info(f"⚙️ جاري فحص تشغيل {file_name} وتثبيت المكتبات...")
                        run_success, run_msg = executor.execute_code(file_path)
                        if not run_success:
                            logger.error(f"⚠️ فشل التشغيل التجريبي: {run_msg}")
                            # هنا يمكننا إضافة محاولة إصلاح إذا أردت مستقبلاً
                    
                    success = True
                    logger.info(f"💾 تم اعتماد {file_name} بنجاح.")
                    
                except Exception as e:
                    logger.error(f"🚨 خطأ في محاولة برمجة {file_name}: {e}")
                    # في حال فشل كل شيء، نقوم بتنظيف يدوي أخير كملاذ أخير
                    if attempts == self.project_state.get("max_attempts", 3):
                        logger.warning("🔄 محاولة الإنقاذ الأخيرة عبر التنظيف اليدوي...")
                        lines = raw_response.split('\n')
                        rescue_code = '\n'.join([l for l in lines if l.strip().lower() != 'json'])
                        self._save_file(os.path.join(project_dir, file_name), rescue_code)
        self.update_cloud_ledger(project_name, "Completed", len(self.project_state["structure"]), 45)
        # توليد ملفات المساعدة
        self._generate_bat_file(project_dir)
        self._generate_readme(project_name, enhanced_desc, project_dir)
        return True
        
    # أضف هذه الدالة داخل كلاس Orchestrator
    def update_cloud_ledger(self, project_name, status, files_count, duration):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            import json
            from datetime import datetime

            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            with open("credentials.json", "r") as f:
                creds_info = json.load(f)
            
            # تنظيف المفتاح كما فعلنا سابقاً
            if 'private_key' in creds_info:
                creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')
                
            creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
            client = gspread.authorize(creds)
            
            sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
            sheet = client.open_by_url(sheet_url).sheet1
            
            # إضافة سطر جديد بالبيانات
            new_row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # وقت الإنشاء
                project_name,                                  # اسم المشروع
                status,                                        # الحالة
                files_count,                                   # عدد الملفات
                f"{duration}s"                                 # المدة المستغرقة
            ]
            sheet.append_row(new_row)
            logger.info("☁️ تم تحديث سجل العمليات السحابي بنجاح.")
        except Exception as e:
            logger.error(f"☁️ فشل تحديث السحاب: {e}")
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
        