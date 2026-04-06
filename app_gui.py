import streamlit as st
import os
import sys
import shutil

# --- إضافة هذا الجزء للتأكد من رؤية المجلدات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)
# -------------------------------------------

from agentforge.core.orchestrator import AgentForgeOrchestrator

def create_zip(project_name):
    """ضغط مجلد المشروع بالكامل لضمان الهيكلية الصحيحة"""
    # المسار الفعلي للمشروع داخل مجلد projects
    project_path = os.path.join("projects", project_name)
    
    # التأكد من وجود المجلد قبل الضغط
    if os.path.exists(project_path):
        shutil.make_archive(project_name, 'zip', project_path)
    else:
        # إذا كان المشروع في المجلد الرئيسي مباشرة (fallback)
        shutil.make_archive(project_name, 'zip', project_name)
        
    return f"{project_name}.zip"
# إضافة مسار src لضمان عمل الاستيراد بشكل صحيح
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# إعدادات الصفحة (تظهر بشكل رائع على الموبايل)
st.set_page_config(
    page_title="AgentForge AI",
    page_icon="🚀",
    layout="centered"
)

# --- القائمة الجانبية للإعدادات ---
st.sidebar.header("⚙️ إعدادات المحرك")

# خيار التشغيل التلقائي
auto_run = st.sidebar.checkbox("تشغيل الكود تلقائياً (Auto-Run)", value=True, 
                               help="إذا تم تفعيله، سيحاول المحرك تشغيل الكود للتأكد من خلوه من الأخطاء المنطقية.")

# خيار تثبيت المكتبات
auto_install = st.sidebar.checkbox("تثبيت المكتبات المفقودة", value=True,
                                   help="تفعيل ميزة pip install التلقائية في حال وجود مكتبات ناقصة.")

# عدد محاولات التصحيح
max_attempts = st.sidebar.slider("أقصى عدد لمحاولات التصحيح", 1, 5, 3)

st.sidebar.markdown("---")
st.sidebar.info(f"إصدار المحرك: v0.9.6 Stable")

# التصميم الجمالي (CSS بسيط لتحسين المظهر)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AgentForge AI Engine")
st.subheader("محرك بناء البرمجيات الذكي - v0.9.0")

# صندوق المدخلات
project_name = st.text_input("اسم المشروع", placeholder="مثلاً: CryptoTracker")
project_desc = st.text_area("ماذا تريد أن تبني؟", placeholder="اكتب وصفاً تفصيلياً هنا...")

if st.button("إطلاق عملية الصهر (Forge)"):
    if project_name and project_desc:
        with st.status("🛠️ جاري العمل على مشروعك...", expanded=True) as status:
            af = AgentForgeOrchestrator()
            
            st.write(f"🏗️ بدأ المحرك في بناء {project_name}...")
            
            # استدعاء واحد فقط بجميع الإعدادات
            state = af.start_cycle(
                project_name=project_name,
                description=project_desc,
                lang="python",
                auto_run=auto_run,
                max_attempts=max_attempts
            )
            
            if state.get("status") == "completed":
                status.update(label="✅ تم الانجاز!", state="complete", expanded=False)
                st.success(f"🎉 تم بناء المشروع: {project_name}")
                
                # إنشاء وتحميل الـ ZIP
                zip_file = create_zip(project_name)
                with open(zip_file, "rb") as fp:
                    st.download_button(
                        label="📥 تحميل المشروع كاملاً (ZIP)",
                        data=fp,
                        file_name=zip_file,
                        mime="application/zip"
                    )
                
                # تبويبات المعاينة
                st.info("📂 معاينة الملفات:")
                # التأكد من وجود المجلد قبل قراءة الملفات
                if os.path.exists(project_name):
                    files = [f for f in os.listdir(project_name) if os.path.isfile(os.path.join(project_name, f))]
                    if files:
                        tabs = st.tabs(files)
                        for i, file in enumerate(files):
                            with tabs[i]:
                                with open(os.path.join(project_name, file), "r", encoding="utf-8") as f:
                                    st.code(f.read(), language="python" if file.endswith(".py") else "text")
            else:
                status.update(label="❌ فشلت المهمة", state="error")
                st.error("المراجع رفض الكود أو حدث خطأ تقني.")
# تذييل الصفحة
st.markdown("---")
st.caption("صُنع بكل حب بواسطة AgentForge & Gemini - 2026")