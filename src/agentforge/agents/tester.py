import ast

class TesterAgent:
    def validate_code(self, code):
        try:
            ast.parse(code)
            return True, "Code is valid."
        except SyntaxError as e:
            return False, f"Syntax Error: {e.msg} at line {e.lineno}"