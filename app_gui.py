# app_gui.py - النسخة المصححة
import streamlit as st
import sys
import os
import requests
import json
import shutil
import re
from datetime import datetime

# إضافة مسار src
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

# استيراد المحرك المحلي
from agentforge.core.orchestrator import AgentForgeOrchestrator

# ========== إعدادات الصفحة ==========
st.set_page_config(
    page_title="AgentForge AI",
    page_icon="🚀",
    layout="wide"
)

# ========== دالة توليد المشروع عبر السحاب ==========
def generate_via_cloud(project_name, description, template):
    """توليد مشروع باستخدام Gemini API مباشرة"""
    
    # الحصول على المفتاح من Secrets
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not API_KEY:
        st.error("❌ مفتاح Gemini API غير متوفر. يرجى إضافته في Settings → Secrets")
        return None
    
    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key={API_KEY}"
    
    with st.spinner("☁️ جاري التوليد على السحاب... (30-60 ثانية)"):
        try:
            # ✅ prompt مبسط بدون مشاكل في التنسيق
            prompt = f"""
            Generate a complete Python Streamlit application.
            
            Project Name: {project_name}
            Description: {description}
            
            Create a simple calculator app with basic operations (add, subtract, multiply, divide).
            
            Return ONLY valid JSON with this structure:
            {{
                "files": {{
                    "main.py": "import streamlit as st\\n\\nst.title('Calculator')\\n\\nnum1 = st.number_input('Enter first number', value=0.0)\\nnum2 = st.number_input('Enter second number', value=0.0)\\noperation = st.selectbox('Select operation', ['Add', 'Subtract', 'Multiply', 'Divide'])\\n\\nif st.button('Calculate'):\\n    if operation == 'Add':\\n        result = num1 + num2\\n    elif operation == 'Subtract':\\n        result = num1 - num2\\n    elif operation == 'Multiply':\\n        result = num1 * num2\\n    elif operation == 'Divide':\\n        if num2 != 0:\\n            result = num1 / num2\\n        else:\\n            result = 'Error: Division by zero'\\n    st.success(f'Result: {{result}}')",
                    "config.py": "# Configuration file\\nAPP_NAME = 'Calculator App'\\nVERSION = '1.0'",
                    "helpers.py": "# Helper functions\\ndef validate_numbers(a, b):\\n    try:\\n        return float(a), float(b)\\n    except ValueError:\\n        return None, None",
                    "start_app.bat": "@echo off\\nstreamlit run main.py\\npause"
                }}
            }}
            """
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(GEMINI_URL, json=payload, timeout=90)
            result = response.json()
            
            if "candidates" in result:
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    files_data = json.loads(json_match.group())
                    files = files_data.get("files", {})
                    
                    # إنشاء مجلد المشروع
                    project_path = os.path.join("projects", project_name)
                    os.makedirs(project_path, exist_ok=True)
                    
                    # حفظ الملفات
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
            
            st.error("❌ فشل في تحليل الرد من Gemini")
            return None
            
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في تحليل JSON: {e}")
            return None
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال: {e}")
            return None

# ========== دالة توليد المشروع محلياً ==========
def generate_via_local(project_name, description, template, auto_run, max_attempts):
    """توليد مشروع باستخدام المحرك المحلي"""
    
    with st.spinner("💻 جاري التوليد محلياً... (30-60 ثانية)"):
        try:
            af = AgentForgeOrchestrator()
            os.makedirs("projects", exist_ok=True)
            os.makedirs(os.path.join("projects", project_name), exist_ok=True)
            
            state = af.start_cycle(
                project_name=project_name,
                description=description,
                lang="python",
                auto_run=auto_run,
                max_attempts=max_attempts,
                template=template
            )
            
            if state.get("status") == "completed":
                # إنشاء ZIP
                shutil.make_archive(f"projects/{project_name}", 'zip', f"projects/{project_name}")
                return {
                    "success": True,
                    "project_id": project_name,
                    "files_generated": state.get("files", []),
                    "message": f"Project '{project_name}' generated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": state.get("reason", "Unknown error")
                }
                
        except Exception as e:
            st.error(f"❌ فشل التوليد المحلي: {e}")
            return {"success": False, "message": str(e)}

# ========== الواجهة الرئيسية ==========
st.title("🚀 AgentForge AI Engine")
st.subheader("محرك بناء البرمجيات الذكي - الإصدار 2.0")

# القائمة الجانبية
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1698/1698535.png", width=80)
    st.title("AgentForge 🤖")
    
    st.markdown("---")
    st.markdown("## ⚙️ طريقة التشغيل")
    
    execution_mode = st.radio(
        "اختر الطريقة المناسبة لك:",
        options=["☁️ **السحابي (Cloud API)**", "💻 **محلي (Local Engine)**"],
        help="""
        - ☁️ السحابي: يعمل فوراً، لا تحتاج تثبيت، مناسب للتجربة
        - 💻 المحلي: يشغل المحرك على جهازك، مناسب للمطورين
        """
    )
    
    st.markdown("---")
    
    # إعدادات حسب الوضع
    auto_run = True
    max_attempts = 3
    
    if "محلي" in execution_mode:
        auto_run = st.checkbox("تشغيل الكود تلقائياً", value=True)
        max_attempts = st.slider("محاولات التصحيح", 1, 5, 3)
    
    if "سحابي" in execution_mode:
        st.info("☁️ **وضع السحاب مفعل**")
        st.caption("✅ يستخدم Gemini API")
        st.caption("⚡ سريع - يعمل فوراً")

# إدخال بيانات المشروع
col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input("🏷️ **اسم المشروع**", placeholder="مثلاً: My_App")
with col2:
    st.caption("استخدم أسماء إنجليزية بدون مسافات")

project_desc = st.text_area(
    "📝 **وصف المشروع**",
    placeholder="مثال: Simple calculator app with basic operations",
    height=100
)

# زر التوليد
if st.button("🚀 **إطلاق عملية التصميم**", type="primary", use_container_width=True):
    
    if not project_name or not project_desc:
        st.warning("⚠️ رجاءً أدخل اسم المشروع ووصفه!")
    else:
        clean_name = project_name.replace(" ", "_")
        result = None
        
        if "سحابي" in execution_mode:
            result = generate_via_cloud(clean_name, project_desc, "auto")
        else:
            result = generate_via_local(clean_name, project_desc, "auto", auto_run, max_attempts)
        
        # عرض النتيجة
        if result and result.get("success"):
            st.success(f"🎉 {result.get('message')}")
            
            # زر التحميل
            zip_path = f"projects/{clean_name}.zip"
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label=f"📥 تحميل {clean_name}.zip",
                        data=fp,
                        file_name=f"{clean_name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            
            # عرض الملفات المنتجة
            with st.expander("📂 الملفات المنتجة"):
                for file in result.get("files_generated", []):
                    st.code(f"✅ {file}")
        else:
            st.error(f"❌ فشل التوليد: {result.get('message') if result else 'خطأ غير معروف'}")

st.markdown("---")
st.caption("صُنع بواسطة AgentForge - الإصدار 2.0")