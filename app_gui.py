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
# في بداية الملف، بعد import streamlit
try:
    if "GEMINI_API_KEY" in st.secrets:
        st.sidebar.success("✅ Gemini API key found")
    else:
        st.sidebar.error("❌ Gemini API key NOT found in secrets")
        st.sidebar.info("Available keys: " + ", ".join(st.secrets.keys()))
except:
    st.sidebar.error("❌ No secrets found")
# ========== دالة توليد المشروع عبر السحاب ==========
def generate_via_cloud(project_name, description, template):
    """توليد مشروع باستخدام Gemini API مباشرة"""
    
    # الحصول على المفتاح
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not API_KEY:
        st.error("❌ مفتاح Gemini API غير متوفر")
        return None
    
    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key={API_KEY}"
    
    with st.spinner("☁️ جاري التوليد..."):
        try:
            # ✅ بناء prompt بسيط وواضح
            prompt = f"""Create a complete Streamlit application.

User request: {description}
Project name: {project_name}

Requirements:
1. Generate 4 files: main.py, config.py, helpers.py, start_app.bat
2. main.py must contain the full Streamlit UI
3. helpers.py must contain business logic
4. config.py for configuration
5. start_app.bat to run the app

Return ONLY valid JSON. Example format:
{{"files": {{"main.py": "code", "config.py": "code", "helpers.py": "code", "start_app.bat": "code"}}}}"""
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 4096
                }
            }
            
            response = requests.post(GEMINI_URL, json=payload, timeout=90)
            result = response.json()
            
            # طباعة للتصحيح (ستظهر في logs)
            print(f"Gemini Response: {result}")
            
            if "candidates" in result and len(result["candidates"]) > 0:
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # استخراج JSON
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    files = data.get("files", {})
                    
                    # إنشاء المشروع
                    project_path = os.path.join("projects", project_name)
                    os.makedirs(project_path, exist_ok=True)
                    
                    for filename, code in files.items():
                        with open(os.path.join(project_path, filename), "w", encoding="utf-8") as f:
                            f.write(code)
                    
                    # إضافة start_app.bat إذا لم يكن موجوداً
                    bat_path = os.path.join(project_path, "start_app.bat")
                    if not os.path.exists(bat_path):
                        with open(bat_path, "w") as f:
                            f.write("@echo off\nstreamlit run main.py\npause")
                    
                    shutil.make_archive(f"projects/{project_name}", 'zip', project_path)
                    
                    return {
                        "success": True,
                        "project_id": project_name,
                        "files_generated": list(files.keys()),
                        "message": f"✅ {project_name} created successfully"
                    }
            
            # إذا فشل Gemini، استخدم القالب العام
            return generate_fallback_project(project_name, description)
            
        except Exception as e:
            st.warning(f"⚠️ Gemini error: {e}")
            return generate_fallback_project(project_name, description)

def generate_fallback_project(project_name, description):
    """قالب عام عندما يفشل Gemini"""
    
    project_path = os.path.join("projects", project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # كود عام يعمل لأي مشروع
    generic_code = f'''import streamlit as st

st.set_page_config(page_title="{project_name}", page_icon="🚀")
st.title("{project_name}")

st.markdown(f"### Based on: {description}")

# Simple template
st.info("This is a generic template. For custom apps, try again or use local mode.")

user_input = st.text_input("Enter something:")
if st.button("Process"):
    st.success(f"You entered: {{user_input}}")

st.markdown("---")
st.caption("Powered by AgentForge")
'''
    
    with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
        f.write(generic_code)
    
    # config.py
    with open(os.path.join(project_path, "config.py"), "w") as f:
        f.write("# Configuration\nAPP_NAME = '" + project_name + "'\nVERSION = '1.0'")
    
    # helpers.py
    with open(os.path.join(project_path, "helpers.py"), "w") as f:
        f.write("# Helper functions\ndef process(data):\n    return data")
    
    # start_app.bat
    with open(os.path.join(project_path, "start_app.bat"), "w") as f:
        f.write("@echo off\nstreamlit run main.py\npause")
    
    shutil.make_archive(f"projects/{project_name}", 'zip', project_path)
    
    return {
        "success": True,
        "project_id": project_name,
        "files_generated": ["main.py", "config.py", "helpers.py", "start_app.bat"],
        "message": f"✅ {project_name} created (generic template)"
    }

# ========== دالة توليد المشروع محلياً ==========
def generate_via_local(project_name, description, template, auto_run, max_attempts):
    """توليد مشروع باستخدام المحرك المحلي"""
    
    with st.spinner("💻 جاري التوليد محلياً..."):
        try:
            af = AgentForgeOrchestrator()
            os.makedirs("projects", exist_ok=True)
            os.makedirs(os.path.join("projects", project_name), exist_ok=True)
            
            # ✅ إزالة المعامل 'lang' و 'auto_run' و 'max_attempts'
            # استخدم فقط المعاملات التي يقبلها start_cycle
            state = af.start_cycle(
                project_name=project_name,
                description=description,
                template=template
                # ❌ لا تمرر lang, auto_run, max_attempts
            )
            
            if state.get("status") == "completed":
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