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
    

    # def _run_architect_phase(self):
    #     logger.info("🏗️  المرحلة 1: تصميم الهيكل...")
    #     structure = self.architect.analyze_project(self.project_state["description"], self.project_state["language"])
    #     self.project_state["structure"] = structure

    def _run_coding_phase(self):
        logger.info("💻 المرحلة 2: البرمجة والتدقيق مع التصحيح الذاتي...")
        
        project_dir = os.path.join(os.getcwd(), "projects", self.project_state["name"])
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)
            logger.info(f"📂 تم إنشاء مستودع المشروع في: {project_dir}")

        # جلب القواعد الخارجية
        external_rules = ""
        if os.path.exists("gui_rules.md"):
            try:
                with open("gui_rules.md", "r", encoding="utf-8") as f:
                    external_rules = f"\n\n### EXTERNAL STANDARDS (gui_rules.md) ###\n{f.read()}"
            except Exception as e:
                logger.warning(f"⚠️ تعذر قراءة ملف gui_rules.md: {e}")

        max_retries = self.project_state.get("max_attempts", 3)
        should_execute = self.project_state.get("auto_run", True)

        for file_name, task in self.project_state["structure"].items():
            success = False
            attempts = 0
            history = []

            while attempts < max_retries and not success:
                try:
                    attempts += 1
                    logger.info(f"📝 محاولة برمجة {file_name} رقم ({attempts})...")
                    
                    current_task = " ".join(task) if isinstance(task, list) else task
                    
                    # 1. القواعد التقنية (الموجودة سابقاً)
                    # ابحث عن technical_rules في orchestrator.py واستبدلها بـ:
                    technical_rules = (
                        "\n### GOLDEN ARCHITECTURE RULES ###\n"
                        "1. REAL-TIME LOGIC: Use `root.after()` for any task that needs periodic updating (e.g., clocks, counters).\n"
                        "2. NO BLOAT: If the user didn't ask for a button, don't write a button. Keep the UI surgical and clean.\n"
                        "3. WINDOW STABILITY: Use `root.title()`, `root.geometry()`, and `root.mainloop()` correctly.\n"
                        "4. NO TERMINAL: All outputs must appear on the GUI Label, never use input().\n"
                    )
                    # 🌟 2. إضافة تعليمات الجودة الاحترافية (الجديدة) 🌟
                    quality_standards = (
                        "\n### PROFESSIONAL STANDARDS ###\n"
                        "- ROBUSTNESS: Use try-except blocks for all file/network operations.\n"
                        "- CLEAN CODE: Add meaningful comments for complex logic.\n"
                        "- PORTABILITY: Use 'os.path.join' for paths, NEVER hardcode 'C:\\' paths.\n"
                        "- LOGGING: Include print() statements to log major app events to console.\n"
                        "- REQUIREMENTS: If you use external libraries, use their standard names.\n"
                    )
                    
                    # دمج كل شيء في مهمة واحدة معززة
                    # استبدل enhanced_task بهذا الهيكل الجديد:
                    instruction_header = "🚨 CRITICAL ARCHITECTURE RULE: YOU MUST USE root.after() FOR RECURSIVE UPDATES. STATIC TIME IS A FAILURE. 🚨"

                    enhanced_task = f"{instruction_header}\n\nTask: {current_task}\n{technical_rules}\n{quality_standards}"
                    short_history = history[-2:] if len(history) > 2 else history

                    # استدعاء المبرمج بالمهمة المعززة
                    code = self.coder.write_code(
                        file_name, 
                        self.project_state["description"], 
                        enhanced_task, 
                        history=short_history
                    )

                    # ... (بقية الكود الخاص بالمراجعة والفحص والتشغيل كما هو)

                    # 2. المراجعة المنطقية
                    logger.info("⏳ انتظار بسيط لتهدئة الـ API قبل المراجعة...")
                    time.sleep(5) 
                    
                    review_result = self.reviewer.review_code(code, enhanced_task, history=short_history)
                    
                    if review_result.strip().upper().startswith("FAIL"):                            
                        feedback = review_result
                        history.append(f"Attempt {attempts} - Review Fail: {feedback}")
                        logger.warning(f"⚠️ المراجع رفض المنطق في {file_name}. المحاولة القادمة ستكون أذكى.")
                        continue 

                    # 3. الفحص النحوي (Syntax Test)
                    is_valid, error_msg = self.tester.validate_code(code)
                    if not is_valid:
                        feedback = error_msg
                        history.append(f"Attempt {attempts} - Syntax Error: {error_msg}")
                        logger.warning(f"❌ خطأ سنتاكس في {file_name}، جاري إعادة المحاولة...")
                        continue

                    # 4. الحفظ المؤقت للفحص التشغيلي
                    file_path = os.path.join(project_dir, file_name)
                    self._save_file(file_path, code)
                    logger.info(f"✅ الكود سليم نحوياً لـ {file_name}")

                    # 5. اختبار التشغيل الفعلي (Execution)
                    if file_name.endswith(".py") and should_execute:
                        run_ok, run_output = self.executor.execute_code(file_path)
                        
                        failure_keywords = ["error", "failed", "exception", "traceback", "nameerror", "attributeerror"]
                        has_runtime_error = any(word in run_output.lower() for word in failure_keywords)

                        if run_ok and not has_runtime_error:
                            logger.info(f"🎉 نجاح التشغيل والاختبار النهائي لـ {file_name}!")
                            success = True
                        else:
                            feedback = run_output
                            history.append(f"Attempt {attempts} - Runtime Error: {run_output}")
                            logger.warning(f"⚠️ فشل التشغيل لـ {file_name}، جاري محاولة الإصلاح...")
                            continue
                    else:
                        logger.info(f"✅ تم حفظ {file_name} بنجاح.")
                        success = True

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        logger.warning(f"🕒 تم بلوغ حد الطلبات (Quota). سأنتظر 60 ثانية...")
                        time.sleep(60) 
                        attempts -= 1 
                        continue
                    else:
                        logger.error(f"🚨 خطأ نظام غير متوقع: {str(e)}")
                        raise e

            # 6. معالجة الفشل النهائي (لا تدخل هنا إلا إذا فشلت كل المحاولات)
            if not success:
                # تعريف المتغيرات هنا حصراً لتجنب UnboundLocalError
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                report_path = os.path.join(project_dir, f"CRASH_REPORT_{file_name}.md")
                
                crash_content = f"""# ⚠️ تقرير عطل في الملف: {file_name}
                ## 📅 معلومات التوقيت
                - **التاريخ والوقت:** {now}

                ## 🔍 حالة النظام عند الفشل
                - **عدد المحاولات:** {attempts}
                - **المهمة المطلوبة:** {current_task[:200]}...

                ## ❌ آخر تغذية راجعة (Feedback)
                ```text
                {feedback}
                تم إنشاء هذا التقرير تلقائياً بواسطة AI Engine v0.4.2"""

                self._save_file(report_path, crash_content)
                logger.error(f"📁 تم إنشاء تقرير العطل في {report_path}")
        
        # --- [إضافة احترافية: توليد ملف تشغيل ذكي start_app.bat] ---
        bat_content = """@echo off
        title Launching Smart Project...
        echo 🚀 Checking environment...

        if not exist venv (
            echo 📦 Creating virtual environment...
            python -m venv venv
        )

        echo 🔗 Activating environment...
        call venv\\Scripts\\activate

        if exist requirements.txt (
            echo 📥 Installing/Updating dependencies...
            pip install -r requirements.txt
        )

        echo ⚡ Starting Application...
        python main.py
        pause
        """
        bat_path = os.path.join(project_dir, "start_app.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        logger.info(f"💾 تم إنشاء ملف التشغيل السريع: {bat_path}")
        # -------------------------------------------------------
        
        # --- [إضافة احترافية: توليد ملف requirements.txt تلقائياً] ---
        # نقوم بمسح كافة ملفات البايثون التي تم إنشاؤها لجمع المكتبات المستخدمة
        all_imports = set()
        for root_dir, _, files in os.walk(project_dir):
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(os.path.join(root_dir, file), "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith("import ") or line.startswith("from "):
                                    # استخراج اسم المكتبة الأساسي (مثلاً من from pandas.api نأخذ pandas)
                                    parts = line.split()
                                    if len(parts) > 1:
                                        mod = parts[1].split('.')[0]
                                        all_imports.add(mod)
                    except Exception as e:
                        logger.warning(f"⚠️ تعذر قراءة الملف {file} لاستخراج التبعيات: {e}")
        
        # تصفية المكتبات القياسية (الموجودة مسبقاً في بايثون)
        standard_libs = [
            "os", "sys", "time", "datetime", "math", "tkinter", "json", 
            "shutil", "sqlite3", "logging", "subprocess", "re", "random"
        ]
        external_libs = [lib for lib in all_imports if lib and lib not in standard_libs]
        
        # إذا وجدنا مكتبات خارجية، نكتبها في ملف requirements.txt
        if external_libs:
            req_path = os.path.join(project_dir, "requirements.txt")
            with open(req_path, "w", encoding="utf-8") as f:
                f.write("\n".join(external_libs))
            logger.info(f"📦 تم تحديث requirements.txt بالمكتبات: {external_libs}")
        
        # نخرج من حلقة الملفات ونعيد True بنجاح تام
        return True


    def _save_file(self, path, content):
        # التأكد من أن المسار كامل (Absolute Path) لتجنب الحفظ في المكان الخطأ
        directory = os.path.dirname(path)
        
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📂 إنشاء مسار فرعي: {directory}")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)