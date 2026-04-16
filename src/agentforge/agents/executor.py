import subprocess
import sys
import logging
import time
import os
import re

logger = logging.getLogger("AgentForge.Executor")

class ExecutorAgent:
    def __init__(self):
        # قائمة بالمكتبات التي فشل تثبيتها لمنع تكرار المحاولة
        self.failed_installs = set()

    def execute_code(self, file_path):
        """يشغل الكود مع فلتر ذكي للمكتبات المحلية"""
        try:
            # 1. تشغيل العملية
            process = subprocess.Popen(
                [sys.executable, file_path],
                stdout=None, 
                stderr=subprocess.PIPE, 
                text=True
            )

            # انتظر قليلاً للتحقق من استقرار التشغيل
            time.sleep(3)
            poll = process.poll()
            
            if poll is None:
                logger.info(f"🚀 تم إطلاق العملية بنجاح لـ {file_path}")
                return True, "Success"

            # 2. إذا انتهت العملية فوراً، نحلل الخطأ
            _, stderr = process.communicate()
            
            if "ModuleNotFoundError" in (stderr or ""):
                missing_module = self._extract_module_name(stderr)
                
                if missing_module:
                    # --- القاعدة الذهبية الجديدة: هل المكتبة محلية؟ ---
                    project_dir = os.path.dirname(file_path)
                    local_file = os.path.join(project_dir, f"{missing_module}.py")
                    
                    if os.path.exists(local_file):
                        logger.warning(f"⚠️ {missing_module} هو ملف محلي وليس مكتبة خارجية. انتظر اكتمال المبرمج.")
                        return False, f"Local module {missing_module} is missing or not yet written."

                    # --- إذا كانت مكتبة خارجية فعلاً ---
                    if missing_module not in self.failed_installs:
                        logger.info(f"🛠️ اكتشاف مكتبة مفقودة: {missing_module}. جاري التثبيت...")
                        if self._install_module(missing_module):
                            return self.execute_code(file_path) # إعادة المحاولة
                        else:
                            self.failed_installs.add(missing_module)

            if process.returncode == 0:
                return True, "Process finished successfully"
            else:
                return False, stderr or "Unknown Error"
                
        except Exception as e:
            return False, str(e)
        
    def _extract_module_name(self, error_msg):
        try:
            match = re.search(r"No module named '([^']+)'", error_msg)
            return match.group(1) if match else None
        except:
            return None

    def _install_module(self, module_name):
        """تنفيذ أمر التثبيت مع الحماية من الأسماء الخاطئة"""
        # حماية من تثبيت ملفات المشروع كأنها مكتبات (مثل calc_logic)
        forbidden_to_install = ["config", "helpers", "logic", "utils", "main", "app"]
        if any(f in module_name.lower() for f in forbidden_to_install):
            return False

        try:
            print(f"📦 Pip Installing {module_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            return True
        except Exception as e:
            print(f"❌ Failed to install {module_name}: {e}")
            return False