import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AgentForge Admin", layout="wide", page_icon="🛡️")

st.title("🛡️ لوحة تحكم مدير AgentForge")
st.markdown("---")

def get_admin_data():
    conn = sqlite3.connect('agentforge_tasks.db')
    # جلب البيانات والتأكد من ترتيبها
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY created_at DESC", conn)
    conn.close()
    return df

data = get_admin_data()

# 📊 1. قسم الإحصائيات السريعة
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("إجمالي المشاريع", len(data))
with col2:
    # فلترة المشاريع الناجحة فقط
    success_count = len(data[data['status'].str.contains('Completed', na=False)])
    st.metric("مشاريع ناجحة ✅", success_count)
with col3:
    avg_time = round(data['duration_seconds'].mean(), 1) if not data.empty else 0
    st.metric("متوسط وقت البناء", f"{avg_time} ثانية")
with col4:
    total_files = data['file_count'].sum()
    st.metric("إجمالي الملفات المنشأة", total_files)

st.markdown("---")

# 📈 2. الرسوم البيانية (اختياري: عرضها فقط إذا كانت هناك بيانات)
if not data.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 وتيرة العمل")
        fig = px.line(data, x='created_at', y='file_count', title="عدد الملفات لكل مشروع")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("📂 حالة المشاريع")
        fig_pie = px.pie(data, names='status', title="توزيع حالات المهام")
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# 📦 3. قسم تحميل المشاريع (الجديد والمثير!)
st.subheader("📦 مركز تسليم المشاريع (Download Center)")
if not data.empty:
    # نختار فقط المشاريع الناجحة للتحميل
    completed_projects = data[data['status'].str.contains('Completed', na=False)]['project'].unique()
    
    if len(completed_projects) > 0:
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_project = st.selectbox("اختر المشروع الذي ترغب في تحميله كملف ZIP:", completed_projects)
        with col_btn:
            st.write("") # للموازنة البصرية
            st.write("") 
            # رابط التحميل يوجه مباشرة إلى الـ API الذي أنشأناه في الخطوة السابقة
            download_url = f"http://127.0.0.1:8000/download/{selected_project}"
            st.link_button(f"🚀 تحميل {selected_project}", download_url)
    else:
        st.info("لا توجد مشاريع مكتملة للتحميل بعد.")
else:
    st.warning("قاعدة البيانات فارغة حالياً.")

st.markdown("---")

# 📋 4. سجل المهام التفصيلي
st.subheader("📋 سجل المهام التفصيلي")
st.dataframe(data, use_container_width=True)

# ⚙️ 5. أدوات المدير
with st.expander("🛠️ أدوات الصيانة"):
    if st.button("تحديث البيانات 🔄"):
        st.rerun()
    
    if st.button("🚨 حذف السجلات القديمة (Reset DB)"):
        st.warning("هذا الإجراء سيحذف تاريخ العمليات من قاعدة البيانات فقط، ولن يحذف ملفات المشاريع.")
        # هنا يمكنك إضافة كود حذف السجلات إذا أردت فعلياً تفعيله