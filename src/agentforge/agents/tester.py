import ast
import os

class TesterAgent:
    def validate_code(self, code, file_name="unknown.py"):
        """
        فحص ذكي للكود بناءً على نوع الملف لمنع الانهيارات العشوائية.
        """
        if not code or len(code.strip()) == 0:
            return False, "Error: File content is empty."

        # 1. فحص ملفات بايثون
        if file_name.endswith(".py"):
            try:
                # الفحص النحوي العميق
                ast.parse(code)
                
                # فحص إضافي: التأكد من عدم وجود علامات Markdown متبقية (مثل ```python)
                if "```" in code:
                    return False, "Syntax Error: Markdown tags found inside the code."
                
                return True, "Python code is syntactically valid."
            except SyntaxError as e:
                return False, f"Python Syntax Error: {e.msg} at line {e.lineno}"
            except Exception as e:
                return False, f"Unexpected validation error: {str(e)}"

        # 2. فحص ملفات الـ Batch (.bat)
        elif file_name.endswith(".bat"):
            # التأكد من عدم وجود أوامر بايثون داخل ملف BAT
            if "import " in code or "def " in code:
                return False, "Format Error: Python syntax detected in a .bat file."
            return True, "Batch file format looks good."

        # 3. فحص ملفات التنسيق (.css) أو الإعدادات (.env / .toml)
        elif file_name.endswith((".css", ".env", ".toml", ".md")):
            # فحص بسيط للتأكد من وجود محتوى نصي
            if "{" in code or "=" in code or "#" in code:
                return True, "Static file content validated."
            return False, "Static file seems to have invalid or empty content."

        # 4. أي ملف آخر
        return True, "File type not strictly validated, proceeding."