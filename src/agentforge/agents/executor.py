import subprocess
import sys

class ExecutorAgent:
    def execute_code(self, file_path):
        """يقوم بتشغيل ملف بايثون ويعيد النتيجة أو الخطأ"""
        try:
            # تشغيل الملف والتقاط المخرجات والأخطاء
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=15 # حماية من الحلقات اللانهائية
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Error: Execution timed out (Possible infinite loop)."
        except Exception as e:
            return False, f"Error: {str(e)}"