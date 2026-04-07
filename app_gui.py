import streamlit as st
import os
import sys
import shutil
import gspread # إضافة مكتبة الربط
from google.oauth2.service_account import Credentials # إضافة مكتبة التصاريح
from datetime import datetime # لإضافة الوقت والتاريخ

# --- إعداد المسارات لضمان رؤية المجلدات في السحابة ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from agentforge.core.orchestrator import AgentForgeOrchestrator

# 1️⃣ دالة تسجيل البيانات في Google Sheets (الإضافة الجديدة)
def log_to_sheets(project_name, status, file_count, duration):
    try:
        # إعداد الصلاحيات (تأكد من وجود ملف credentials.json في المجلد الرئيسي)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # رابط الملف الخاص بك
        sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        
        # تجهيز السطر (الاسم، الحالة، عدد الملفات، الوقت، التاريخ)
        new_row = [
            project_name, 
            status, 
            file_count, 
            f"{duration}s", 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"⚠️ فشل التسجيل في Google Sheets: {e}")
        return False

def create_zip(project_name):
    """إنشاء ملف ZIP احترافي باسم المشروع داخل مجلد projects"""
    source_path = os.path.join("projects", project_name)
    zip_name = project_name
    if os.path.exists(source_path):
        shutil.make_archive(zip_name, 'zip', source_path)
        return f"{zip_name}.zip"
    return None

# إعدادات الصفحة
st.set_page_config(page_title="AgentForge AI", page_icon="🚀", layout="centered")

# القائمة الجانبية
st.sidebar.header("⚙️ إعدادات المحرك")
auto_run = st.sidebar.checkbox("تشغيل الكود تلقائياً (Auto-Run)", value=True)
auto_install = st.sidebar.checkbox("تثبيت المكتبات المفقودة", value=True)
max_attempts = st.sidebar.slider("أقصى عدد لمحاولات التصحيح", 1, 5, 3)
st.sidebar.markdown("---")
st.sidebar.info(f"إصدار المحرك: v0.9.6 Stable")

# التنسيق الجمالي
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AgentForge AI Engine")
st.subheader("محرك بناء البرمجيات الذكي - v0.9.0")

project_name = st.text_input("اسم المشروع", placeholder="مثلاً: Pharmacy_System")
project_desc = st.text_area("ماذا تريد أن تبني؟", placeholder="اكتب وصفاً تفصيلياً...")

if st.button("إطلاق عملية الصهر (Forge)"):
    if project_name and project_desc:
        clean_name = project_name.replace(" ", "_")
        
        with st.status("🛠️ جاري العمل على مشروعك...", expanded=True) as status:
            af = AgentForgeOrchestrator()
            st.write(f"🏗️ بدأ المحرك في بناء {clean_name}...")
            
            state = af.start_cycle(
                project_name=clean_name,
                description=project_desc,
                lang="python",
                auto_run=auto_run,
                max_attempts=max_attempts
            )
            
            if state.get("status") == "completed":
                status.update(label="✅ تم الانجاز!", state="complete", expanded=False)
                st.success(f"🎉 تم بناء المشروع: {clean_name}")

                # 2️⃣ استدعاء دالة التسجيل في Google Sheets فور النجاح (الإضافة الجديدة)
                file_count = len(state.get("files", []))
                duration = state.get("duration", 0)
                log_to_sheets(clean_name, "Completed ✅", file_count, duration)
                
                zip_file = create_zip(clean_name)
                if zip_file and os.path.exists(zip_file):
                    with open(zip_file, "rb") as fp:
                        st.download_button(
                            label=f"📥 تحميل {clean_name}.zip",
                            data=fp,
                            file_name=zip_file,
                            mime="application/zip"
                        )
                
                # معاينة الملفات
                st.info("📂 معاينة الملفات المصهورة:")
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
                # تسجيل الفشل أيضاً (اختياري)
                log_to_sheets(clean_name, "Failed ❌", 0, 0)
                status.update(label="❌ فشلت المهمة", state="error")
                st.error("المراجع رفض الكود. راجع التفاصيل في Logs.")
    else:
        st.warning("رجاءً أدخل اسم المشروع ووصفه!")

st.markdown("---")
st.caption("صُنع بكل حب بواسطة AgentForge & Gemini - 2026")