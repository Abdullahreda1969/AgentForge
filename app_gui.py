import streamlit as st
import os
import sys
import shutil

# --- إعداد المسارات لضمان رؤية المجلدات في السحابة ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from agentforge.core.orchestrator import AgentForgeOrchestrator

def create_zip(project_name):
    """إنشاء ملف ZIP احترافي باسم المشروع داخل مجلد projects"""
    # المسار الفعلي للمجلد الذي أنشأه الوكلاء
    source_path = os.path.join("projects", project_name)
    # اسم ملف الـ ZIP النهائي
    zip_name = project_name
    
    if os.path.exists(source_path):
        # ضغط المجلد (سيتم إنشاء ملف باسم project_name.zip في المجلد الرئيسي للتحميل)
        shutil.make_archive(zip_name, 'zip', source_path)
        return f"{zip_name}.zip"
    return None

# إعدادات الصفحة
st.set_page_config(
    page_title="AgentForge AI",
    page_icon="🚀",
    layout="centered"
)

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
        # تنظيف اسم المشروع من المسافات لضمان سلامة الروابط والملفات
        clean_name = project_name.replace(" ", "_")
        
        with st.status("🛠️ جاري العمل على مشروعك...", expanded=True) as status:
            af = AgentForgeOrchestrator()
            st.write(f"🏗️ بدأ المحرك في بناء {clean_name}...")
            
            # استدعاء واحد شامل للمحرك
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
                
                # إنشاء الـ ZIP باسم المشروع
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
                status.update(label="❌ فشلت المهمة", state="error")
                st.error("المراجع رفض الكود. راجع التفاصيل في Logs.")
    else:
        st.warning("رجاءً أدخل اسم المشروع ووصفه!")

st.markdown("---")
st.caption("صُنع بكل حب بواسطة AgentForge & Gemini - 2026")