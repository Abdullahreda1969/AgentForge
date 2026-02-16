import ast

class CodeTester:
    def validate_code(self, code):
        """التحقق من صحة قواعد اللغة (Syntax)"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)