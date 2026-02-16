import subprocess
import os

class CodeExecutor:
    def execute_code(self, file_path):
        """تشغيل ملف بايثون وإعادة النتيجة"""
        try:
            # تشغيل الملف مع وضع حد زمني (Timeout) لمنع التعليق
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=10 
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "Error: Execution timed out (Possible GUI window or infinite loop)"
        except Exception as e:
            return False, str(e)