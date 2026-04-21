def generate_via_cloud(project_name, description, template):
    """توليد مشروع باستخدام قالب جاهز (بدون AI)"""
    
    # إنشاء مجلد المشروع
    project_path = os.path.join("projects", project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # كود آلة حاسبة بسيط وجاهز
    calculator_code = '''import streamlit as st

st.set_page_config(page_title="Calculator", page_icon="🧮")
st.title("🧮 Simple Calculator")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("Enter first number", value=0.0, step=0.1)

with col2:
    num2 = st.number_input("Enter second number", value=0.0, step=0.1)

operation = st.selectbox(
    "Select operation",
    ["➕ Add", "➖ Subtract", "✖️ Multiply", "➗ Divide"]
)

if st.button("Calculate", type="primary"):
    if operation == "➕ Add":
        result = num1 + num2
        symbol = "+"
    elif operation == "➖ Subtract":
        result = num1 - num2
        symbol = "-"
    elif operation == "✖️ Multiply":
        result = num1 * num2
        symbol = "×"
    else:  # Divide
        if num2 != 0:
            result = num1 / num2
            symbol = "÷"
        else:
            result = "Error: Division by zero"
            symbol = "÷"
    
    if isinstance(result, (int, float)):
        st.success(f"✅ {num1} {symbol} {num2} = {result}")
    else:
        st.error(result)

st.markdown("---")
st.caption("Powered by AgentForge")
'''
    
    # حفظ الملفات
    files = {
        "main.py": calculator_code,
        "config.py": "# Configuration\nAPP_NAME = 'Calculator'\nVERSION = '1.0'",
        "helpers.py": "# Helper functions\ndef add(a, b): return a + b\ndef subtract(a, b): return a - b\ndef multiply(a, b): return a * b\ndef divide(a, b): return a / b if b != 0 else None",
        "start_app.bat": "@echo off\nstreamlit run main.py\npause"
    }
    
    for filename, code in files.items():
        with open(os.path.join(project_path, filename), "w", encoding="utf-8") as f:
            f.write(code)
    
    # إنشاء ZIP
    shutil.make_archive(f"projects/{project_name}", 'zip', project_path)
    
    return {
        "success": True,
        "project_id": project_name,
        "files_generated": list(files.keys()),
        "message": f"Project '{project_name}' generated successfully"
    }