import os

def setup_agent_assets():
    # 1. إنشاء ملف قواعد الواجهات الرسومية
    gui_rules_content = """# AgentForge GUI Standards (v1.0)
## Mandatory Rules for Coder & Reviewer agents:

1. **Imports:** Always use `import tkinter as tk`, `from tkinter import ttk`, and `import requests`.
2. **Lifecycle:** Start with `root = tk.Tk()` and end with `root.mainloop()`.
3. **Visibility:** Use `root.lift()` to force the window to the front.
4. **Error Handling:** Wrap all API calls in `try...except` and display errors in a UI Label.
5. **No Blocking:** NEVER use `input()` or long `time.sleep()` in the main thread.
6. **Geometry:** Every widget MUST be packed or gridded immediately after creation.
"""

    # 2. إنشاء قالب محول العملات كمرجع (Template)
    currency_template_content = """# Template: Currency Converter GUI
# Use this structure for stability:
import tkinter as tk
from tkinter import ttk
import requests

def main():
    root = tk.Tk()
    root.title("Currency Converter v0.4.2")
    root.geometry("400x500")
    
    # UI Elements here...
    
    root.lift()
    root.mainloop()

if __name__ == "__main__":
    main()
"""

    # حفظ الملفات
    with open("gui_rules.md", "w", encoding="utf-8") as f:
        f.write(gui_rules_content)
    
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    with open("templates/currency_template.py", "w", encoding="utf-8") as f:
        f.write(currency_template_content)

    print("✅ تم إنشاء ملف المعايير gui_rules.md")
    print("✅ تم إنشاء مجلد القوالب templates/currency_template.py")

if __name__ == "__main__":
    setup_agent_assets()