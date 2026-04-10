import streamlit as st
import sys
import os

# 1. تحديد مسار المجلد الذي يحتوي على الكود (src)
# بما أننا في الجذر، فالمجلد هو 'src'
base_path = os.path.join(os.getcwd(), "src")

# 2. إضافة المسار لبيئة بايثون لكي يرى ما بداخل src
if base_path not in sys.path:
    sys.path.append(base_path)

# 3. الآن الاستيراد سيعمل لأن بايثون سيبدأ البحث من داخل src
try:
    from agentforge.core.orchestrator import AgentForgeOrchestrator
    print("✅ Success: Orchestrator loaded from src/agentforge/core")
except ModuleNotFoundError as e:
    print(f"❌ Error: Could not find AgentForge. Searched in: {sys.path}")
    raise e
import shutil
import gspread # إضافة مكتبة الربط
from google.oauth2.service_account import Credentials # إضافة مكتبة التصاريح
from datetime import datetime # لإضافة الوقت والتاريخ

# كود تجريبي سريع تحت الـ Imports
try:
    creds_info = st.secrets["gcp_service_account"]
    st.sidebar.success("✅ تم العثور على صلاحيات Google Sheets")
except Exception:
    st.sidebar.error("❌ صلاحيات Google Sheets مفقودة في Secrets")

# --- إعداد المسارات لضمان رؤية المجلدات في السحابة ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from agentforge.core.orchestrator import AgentForgeOrchestrator

# 1️⃣ دالة تسجيل البيانات في Google Sheets (الإضافة الجديدة)
def log_to_sheets(project_name, status, file_count, duration):
    try:
        # قراءة البيانات من Secrets السحابية بدلاً من ملف JSON محلي
        creds_info = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        
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
        # إذا فشل السحابي (مثلاً أثناء التجربة المحلية)، جرب الملف المحلي
        try:
             creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
             # ... تكملة الكود للمحلي ...
        except:
             st.error(f"⚠️ فشل التسجيل: {e}")
        return False

def create_zip(project_name):
    """إنشاء ملف ZIP ونقله داخل مجلد projects لضمان التنظيم"""
    source_dir = os.path.join("projects", project_name)
    zip_filename = project_name # الاسم المؤقت للملف
    target_zip_path = os.path.join("projects", f"{zip_filename}.zip") # المسار النهائي
    
    if os.path.exists(source_dir):
        # 1. تنفيذ الضغط في المجلد الرئيسي مؤقتاً
        shutil.make_archive(zip_filename, 'zip', source_dir)
        
        # 2. التأكد من حذف النسخة القديمة في مجلد projects (إن وجدت) لتجنب الخطأ
        if os.path.exists(target_zip_path):
            os.remove(target_zip_path)
        
        # 3. نقل ملف الـ ZIP الناتج ليكون داخل مجلد projects
        shutil.move(f"{zip_filename}.zip", target_zip_path)
        
        # نرجع المسار الكامل للملف لكي يعرف زر التحميل أين يجده
        return target_zip_path
    return None

# إعدادات الصفحة
st.set_page_config(page_title="AgentForge AI", page_icon="🚀", layout="centered")

# القائمة الجانبية
st.sidebar.header("⚙️ إعدادات المحرك")
auto_run = st.sidebar.checkbox("تشغيل الكود تلقائياً (Auto-Run)", value=True)
auto_install = st.sidebar.checkbox("تثبيت المكتبات المفقودة", value=True)
max_attempts = st.sidebar.slider("أقصى عدد لمحاولات التصحيح", 1, 5, 3)

# --- الإضافة الجديدة: قائمة القوالب الاستراتيجية ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 محاكاة القوالب (Templates)")
template_options = {
    "Auto-Detect ✨": "auto",
    "Streamlit Web App 🌐": "streamlit_web",
    "Tkinter Desktop 🖥️": "tkinter_desktop",
    "Automation Script ⚙️": "automation_script",
    "Pure Python Logic 🐍": "pure_python"
}
selected_template_label = st.sidebar.selectbox("اختر قالب المحاكاة:", list(template_options.keys()))
selected_template_value = template_options[selected_template_label]
# ---------------------------------------------

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

if st.button("إطلاق عملية التصميم (Forge)"):
    if project_name and project_desc:
        clean_name = project_name.replace(" ", "_")
        
        with st.status("🛠️ جاري العمل على مشروعك...", expanded=True) as status:
            af = AgentForgeOrchestrator()
            st.write(f"🏗️ بدأ المحرك في بناء {clean_name}...")
            
            # تأكد أن هذا السطر موجود قبل تشغيل af.start_cycle
            if not os.path.exists("projects"):
                os.makedirs("projects")

            # تأكد أن clean_name يُستخدم لإنشاء مجلد فرعي داخل projects
            project_path = os.path.join("projects", clean_name)
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            
            state = af.start_cycle(
                project_name=clean_name,
                description=project_desc,
                lang="python",
                auto_run=auto_run,
                max_attempts=max_attempts,
                template=selected_template_value  # مررنا القالب هنا
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
                            file_name=os.path.basename(zip_file), # يأخذ الاسم فقط للتحميل (Pharmacy_System.zip)
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