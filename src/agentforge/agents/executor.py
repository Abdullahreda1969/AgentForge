import subprocess
import sys
import logging

logger = logging.getLogger("AgentForge.Executor")

class ExecutorAgent:
    def execute_code(self, file_path):
        """يشغل الكود ويصلح نقص المكتبات تلقائياً"""
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # إذا كان الخطأ هو نقص في مكتبة
            if result.returncode != 0 and "ModuleNotFoundError" in result.stderr:
                missing_module = self._extract_module_name(result.stderr)
                if missing_module:
                    logger.info(f"🛠️ اكتشاف مكتبة مفقودة: {missing_module}. جاري التثبيت...")
                    if self._install_module(missing_module):
                        # إعادة التشغيل بعد التثبيت
                        return self.execute_code(file_path)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
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