import os
import time
import logging
from typing import List, Dict

# إعداد السجل لمراقبة ما يحدث في السحاب
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentForge")

class Orchestrator:
    def __init__(self, architect, coder, reviewer, tester):
        self.architect = architect
        self.coder = coder
        self.reviewer = reviewer
        self.tester = tester
        self.project_state = {"description": "", "files": {}, "history": []}

    def start_forging(self, description: str):
        self.project_state["description"] = description
        logger.info(f"🚀 بدء عملية الصهر للمشروع: {description}")

        # 1. مرحلة التصميم (Architect)
        plan = self.architect.design_project(description)
        if not plan:
            logger.error("❌ فشل المصمم في وضع خطة.")
            return False

        # 2. مرحلة التنفيذ والمراجعة (Coding & Review)
        for file_name, task in plan.items():
            success = self._run_coding_loop(file_name, task)
            if not success:
                logger.error(f"❌ فشل النظام في إنتاج ملف: {file_name}")
                return False
        
        return True

    def _run_coding_loop(self, file_name: str, current_task: str, max_retries: int = 3):
        attempts = 0
        api_failure_count = 0
        history = []

        # القواعد الذهبية التي سنحقنها في كل طلب
        instruction_header = (
            "🚨 CRITICAL: Use root.after() for updates. NO static loops. NO extra buttons. 🚨\n"
            "STRICT RULE: Write ONLY clean, functional Python code.\n"
        )

        while attempts < max_retries:
            attempts += 1
            logger.info(f"📝 محاولة {file_name} رقم ({attempts})...")

            try:
                # استدعاء المبرمج
                code = self.coder.write_code(
                    file_name, 
                    self.project_state["description"], 
                    f"{instruction_header}\nTask: {current_task}", 
                    history=history[-1:] # نرسل آخر محاولة فقط لتقليل التوكينز
                )

                # استدعاء المراجع
                review_result = self.reviewer.review_code(file_name, code)

                if review_result.get("status") == "APPROVED":
                    # فحص السنتاكس (Tester)
                    if self.tester.test_code(code):
                        self._save_file(file_name, code)
                        logger.info(f"✅ تم قبول ملف {file_name} بنجاح.")
                        return True
                    else:
                        feedback = "Syntax Error detected by Tester."
                else:
                    feedback = review_result.get("feedback", "Code rejected by Reviewer.")

                logger.warning(f"⚠️ مراجعة سلبية: {feedback}")
                history.append({"code": code, "feedback": feedback})
                
                # تصفير عداد أخطاء الـ API عند نجاح الاتصال
                api_failure_count = 0 

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    api_failure_count += 1
                    wait_time = 60 * api_failure_count
                    logger.warning(f"🕒 حصة API ممتلئة. محاولة {api_failure_count}/3. انتظار {wait_time} ثانية...")
                    
                    if api_failure_count >= 3:
                        logger.error("🛑 توقف اضطراري لتجنب حظر المفتاح.")
                        return False
                    
                    time.sleep(wait_time)
                    attempts -= 1 # لا تحسب هذه كمحاولة برمجة فاشلة
                else:
                    logger.error(f"💥 خطأ غير متوقع: {error_msg}")
                    return False

        return False

    def _save_file(self, file_name: str, content: str):
        # التأكد من وجود مجلد المشاريع
        project_dir = os.path.join("projects", "current_project")
        os.makedirs(project_dir, exist_ok=True)
        
        file_path = os.path.join(project_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)