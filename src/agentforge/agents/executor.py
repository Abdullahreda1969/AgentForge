import subprocess
import sys
import logging
import time # سنحتاجه للتحقق السريع

logger = logging.getLogger("AgentForge.Executor")

class ExecutorAgent:
    def execute_code(self, file_path):
        """يشغل الكود مع ضمان ظهور النوافذ وتجنب اختناق الأنابيب"""
        try:
            # تشغيل العملية بدون PIPE للمخرجات لضمان عدم التجمد
            # نترك stderr فقط للقبض على أخطاء التشغيل الفورية
            process = subprocess.Popen(
                [sys.executable, file_path],
                stdout=None, # السماح بالظهور المباشر
                stderr=subprocess.PIPE, 
                text=True
            )

            # انتظر 3 ثوانٍ فقط للتحقق من الاستقرار
            time.sleep(3)
            
            poll = process.poll()
            
            if poll is None:
                # العملية تعمل، نتركها تعمل في الخلفية ونعتبرها نجاحاً
                logger.info(f"🚀 تم إطلاق الواجهة الرسومية بنجاح لـ {file_path}")
                return True, "GUI Started Successfully"

            # إذا انتهت العملية فوراً، نقرأ الخطأ من stderr
            _, stderr = process.communicate()

            # معالجة نقص المكتبات
            if process.returncode != 0 and "ModuleNotFoundError" in (stderr or ""):
                missing_module = self._extract_module_name(stderr)
                if missing_module:
                    logger.info(f"🛠️ اكتشاف مكتبة مفقودة: {missing_module}. جاري التثبيت...")
                    if self._install_module(missing_module):
                        return self.execute_code(file_path)

            if process.returncode == 0:
                return True, "Process finished successfully"
            else:
                return False, stderr or "Unknown Error"
                
        except Exception as e:
            return False, str(e)
        
    def _extract_module_name(self, error_msg):
        """يستخرج اسم المكتبة من رسالة الخطأ"""
        # مثال: No module named 'yfinance'
        try:
            import re
            match = re.search(r"No module named '([^']+)'", error_msg)
            return match.group(1) if match else None
        except:
            return None

    def _install_module(self, module_name):
        """تنفيذ أمر التثبيت مع إظهار المخرجات"""
        try:
            print(f"📦 Installing {module_name}...")
            # استخدام check_call يضمن أننا ننتظر انتهاء التثبيت
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            return True
        except Exception as e:
            print(f"❌ Failed to install {module_name}: {e}")
            return False