# app_gui.py - النسخة المطورة مع دعم الثنائية

import streamlit as st
import sys
import os
import requests
import json
import shutil
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import secrets

# ========== إعداد المسارات ==========
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# استيراد المحرك المحلي (سيستخدم لاحقاً)
from agentforge.core.orchestrator import AgentForgeOrchestrator

# ========== إعدادات الصفحة ==========
st.set_page_config(
    page_title="AgentForge AI", 
    page_icon="🚀", 
    layout="wide",  # تغيير إلى wide لاستيعاب الأعمدة
    initial_sidebar_state="expanded"
)

# ========== القائمة الجانبية (مع خيارات التشغيل) ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1698/1698535.png", width=80)
    st.title("AgentForge 🤖")
    
    st.markdown("---")
    st.markdown("## ⚙️ طريقة التشغيل")
    
    # ❗ هذا هو الخيار الجديد - قلب الثنائية
    execution_mode = st.radio(
        "اختر الطريقة المناسبة لك:",
        options=["☁️ **السحابي (Cloud API)**", "💻 **محلي (Local Engine)**"],
        help="""
        - ☁️ السحابي: يعمل فوراً، لا تحتاج تثبيت، مناسب للتجربة والاستخدام السريع
        - 💻 المحلي: يشغل المحرك على جهازك، مناسب للمطورين والشركات
        """
    )
    
    st.markdown("---")
    st.subheader("⚙️ إعدادات المحرك")
    
    # إعدادات تظهر فقط عند اختيار "محلي"
    if "محلي" in execution_mode:
        auto_run = st.checkbox("تشغيل الكود تلقائياً (Auto-Run)", value=True)
        max_attempts = st.slider("أقصى عدد لمحاولات التصحيح", 1, 5, 3)
    
    # إعدادات تظهر فقط عند اختيار "سحابي"
    if "سحابي" in execution_mode:
        st.info("🔑 سيتم استخدام مفتاح API الخاص بك تلقائياً")
        st.caption("لديك 100 طلب مجاني شهرياً")
    
    st.markdown("---")
    st.subheader("🎯 محاكاة القوالب (Templates)")
    template_options = {
        "Auto-Detect ✨": "auto",
        "Streamlit Web App 🌐": "streamlit_web",
        "Tkinter Desktop 🖥️": "tkinter_desktop",
        "Automation Script ⚙️": "automation_script",
        "Pure Python Logic 🐍": "pure_python"
    }
    selected_template_label = st.selectbox("اختر قالب المحاكاة:", list(template_options.keys()))
    selected_template_value = template_options[selected_template_label]
    
    st.markdown("---")
    st.info(f"إصدار المحرك: v1.0.0")
    
    # عرض حالة الاتصال بـ Google Sheets
    try:
        if "gcp_service_account" in st.secrets:
            st.success("✅ متصل بالسحاب (Secrets)")
        elif os.path.exists("credentials.json"):
            st.success("✅ متصل محلياً (credentials.json)")
        else:
            st.warning("⚠️ Google Sheets غير متصل")
    except Exception:
        pass

# ========== دالة تسجيل البيانات في Google Sheets (موجودة بالفعل) ==========
def log_to_sheets(project_name, status, file_count, duration):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_info = None

        try:
            creds_info = dict(st.secrets["gcp_service_account"])
        except Exception:
            if os.path.exists("credentials.json"):
                import json
                with open("credentials.json", "r") as f:
                    creds_info = json.load(f)
        
        if not creds_info:
            return False

        if 'private_key' in creds_info:
            creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')
            
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        
        new_row = [
            project_name, 
            status, 
            file_count, 
            f"{duration}s", 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Cloud" if "سحابي" in execution_mode else "Local"
        ]
        sheet.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"⚠️ فشل المزامنة مع Google Sheets: {e}")
        return False

# ========== دالة إنشاء ZIP (موجودة بالفعل) ==========
def create_zip(project_name):
    source_dir = os.path.join("projects", project_name)
    zip_filename = project_name
    target_zip_path = os.path.join("projects", f"{zip_filename}.zip")
    
    if os.path.exists(source_dir):
        shutil.make_archive(zip_filename, 'zip', source_dir)
        if os.path.exists(target_zip_path):
            os.remove(target_zip_path)
        shutil.move(f"{zip_filename}.zip", target_zip_path)
        return target_zip_path
    return None

# ========== دالة توليد المشروع عبر السحاب (API) ==========
def generate_via_cloud(project_name, description, template):
    """توليد مشروع باستخدام API السحابي"""
    
    # عنوان API - سننشره لاحقاً
    API_URL = os.getenv("AGENTFORGE_API_URL", "https://agentforge-api.onrender.com")
    API_KEY = os.getenv("AGENTFORGE_API_KEY", st.secrets.get("API_KEY", ""))
    
    if not API_KEY:
        st.error("❌ مفتاح API غير متوفر. يرجى التواصل مع الدعم.")
        return None
    
    with st.spinner("☁️ جاري التوليد على السحاب... (30-90 ثانية)"):
        try:
            response = requests.post(
                f"{API_URL}/v1/generate",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": API_KEY
                },
                json={
                    "description": description,
                    "project_name": project_name,
                    "project_type": "auto",
                    "template": template
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                st.error(f"❌ فشل التوليد: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("❌ انتهى وقت الانتظار. الخادم قد يكون مشغولاً، حاول مرة أخرى.")
            return None
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال: {e}")
            return None

# ========== دالة توليد المشروع عبر المحرك المحلي ==========
def generate_via_local(project_name, description, template, auto_run, max_attempts):
    """توليد مشروع باستخدام المحرك المحلي"""
    
    with st.spinner("💻 جاري التوليد محلياً... (قد يستغرق 30-60 ثانية)"):
        try:
            af = AgentForgeOrchestrator()
            
            # إنشاء المجلد إذا لم يكن موجوداً
            if not os.path.exists("projects"):
                os.makedirs("projects")
            
            project_path = os.path.join("projects", project_name)
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            
            state = af.start_cycle(
                project_name=project_name,
                description=description,
                lang="python",
                auto_run=auto_run,
                max_attempts=max_attempts,
                template=template
            )
            
            return state
            
        except Exception as e:
            st.error(f"❌ فشل التوليد المحلي: {e}")
            return {"status": "failed", "reason": str(e)}

# ========== واجهة المستخدم الرئيسية ==========
st.title("🚀 AgentForge AI Engine")
st.subheader("محرك بناء البرمجيات الذكي - الإصدار 1.0")

# عرض بطاقة توضيحية حسب طريقة التشغيل المختارة
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    **حوّل أفكارك إلى تطبيقات كاملة بضغطة زر!**  
    اكتب وصفاً بسيطاً لمشروعك، وسيتولى الذكاء الاصطناعي بناءه بالكامل.
    """)
with col2:
    if "سحابي" in execution_mode:
        st.success("☁️ **وضع السحاب**\nيعمل فوراً، بدون تثبيت")
    else:
        st.info("💻 **وضع محلي**\nيشغل المحرك على جهازك")

st.markdown("---")

# ========== إدخال بيانات المشروع ==========
col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input("🏷️ **اسم المشروع**", placeholder="مثلاً: Pharmacy_System")
with col2:
    st.caption("استخدم أسماء إنجليزية بدون مسافات")

project_desc = st.text_area(
    "📝 **وصف المشروع**", 
    placeholder="مثال: تطبيق إدارة مهام بسيط مع Streamlit. يحتوي على: إضافة مهمة، عرض المهام، حذف مهمة...",
    height=150
)

# ========== زر التشغيل حسب الطريقة المختارة ==========
if st.button("🚀 **إطلاق عملية التصميم (Forge)**", type="primary", use_container_width=True):
    
    if not project_name or not project_desc:
        st.warning("⚠️ رجاءً أدخل اسم المشروع ووصفه!")
    else:
        clean_name = project_name.replace(" ", "_")
        
        # التشغيل حسب اختيار المستخدم
        if "سحابي" in execution_mode:
            # ========== وضع السحاب ==========
            result = generate_via_cloud(clean_name, project_desc, selected_template_value)
            
            if result and result.get("success"):
                st.success(f"🎉 تم بناء المشروع: {clean_name}")
                
                # تسجيل النجاح في Google Sheets
                log_to_sheets(clean_name, "Completed ✅", len(result.get("files_generated", [])), 0)
                
                # عرض رابط التحميل
                st.info(f"📥 المشروع جاهز للتحميل: [اضغط هنا]({result.get('download_url')})")
                
                # عرض الملفات المنتجة
                if result.get("files_generated"):
                    st.subheader("📂 الملفات المنتجة:")
                    for file in result["files_generated"]:
                        st.code(f"✅ {file}")
                        
            else:
                st.error("❌ فشل التوليد عبر السحاب. جرب الوضع المحلي بدلاً من ذلك.")
                log_to_sheets(clean_name, "Failed ❌", 0, 0)
        
        else:
            # ========== وضع محلي ==========
            state = generate_via_local(clean_name, project_desc, selected_template_value, auto_run, max_attempts)
            
            if state.get("status") == "completed":
                st.success(f"🎉 تم بناء المشروع: {clean_name}")
                
                # تسجيل النجاح
                file_count = len(state.get("files", []))
                duration = state.get("duration", 0)
                log_to_sheets(clean_name, "Completed ✅", file_count, duration)
                
                # إنشاء ZIP للتحميل
                zip_file = create_zip(clean_name)
                if zip_file and os.path.exists(zip_file):
                    with open(zip_file, "rb") as fp:
                        st.download_button(
                            label=f"📥 تحميل {clean_name}.zip",
                            data=fp,
                            file_name=os.path.basename(zip_file),
                            mime="application/zip"
                        )
                
                # معاينة الملفات
                st.info("📂 معاينة الملفات المنتجة:")
                project_full_path = os.path.join("projects", clean_name)
                if os.path.exists(project_full_path):
                    files = [f for f in os.listdir(project_full_path) if os.path.isfile(os.path.join(project_full_path, f))]
                    if files:
                        tabs = st.tabs(files)
                        for i, file in enumerate(files):
                            with tabs[i]:
                                with open(os.path.join(project_full_path, file), "r", encoding="utf-8") as f:
                                    st.code(f.read(), language="python" if file.endswith(".py") else "text")
            else:
                st.error("❌ فشلت المهمة. راجع التفاصيل في الـ Logs.")
                log_to_sheets(clean_name, "Failed ❌", 0, 0)

# ========== تذييل الصفحة ==========
st.markdown("---")
st.caption("صُنع بكل حب بواسطة AgentForge - 2026")