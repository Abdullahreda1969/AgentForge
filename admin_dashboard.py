import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import shutil

from st_gsheets_connection import GSheetsConnection


st.set_page_config(page_title="AgentForge Admin", layout="wide", page_icon="🛡️")

st.title("🛡️ لوحة تحكم مدير AgentForge")
st.markdown("---")

def get_admin_data():
    # إنشاء اتصال بجدول بيانات جوجل (يتم ضبط الرابط في Secrets)
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="10m") # تحديث البيانات كل 10 دقائق
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
# --- استبدل قسم "3. قسم تحميل المشاريع" بهذا الكود المطور ---

st.subheader("📦 مركز تسليم المشاريع (Download Center)")

# 1. فحص مجلد projects الفعلي في السيرفر (سواء سحابي أو محلي)
projects_dir = "projects"
if not os.path.exists(projects_dir):
    os.makedirs(projects_dir)

# جلب أسماء المجلدات الموجودة فعلياً وتجاهل الملفات المخفية
actual_projects = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) and not d.startswith('.')]

if actual_projects:
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        # عرض المشاريع الموجودة فعلياً في المجلد
        selected_project = st.selectbox("اختر المشروع المتاح حالياً في السيرفر:", actual_projects)
    
    with col_btn:
        st.write("") # موازنة
        st.write("") 
        
        # 2. إنشاء ملف ZIP للمشروع المختار "أونلاين" للتحميل المباشر
        import shutil
        zip_path = f"{selected_project}.zip"
        source_dir = os.path.join(projects_dir, selected_project)
        
        if os.path.exists(source_dir):
            shutil.make_archive(selected_project, 'zip', source_dir)
            
            with open(zip_path, "rb") as rb:
                st.download_button(
                    label=f"🚀 تحميل {selected_project}",
                    data=rb,
                    file_name=f"{selected_project}.zip",
                    mime="application/zip"
                )
else:
    st.info("لا توجد مشاريع منشأة في المجلد حالياً. قم بإنشاء مشروع من واجهة Forge أولاً.")

# إضافة زر تحديث يدوي قوي
if st.sidebar.button("🔄 تحديث القائمة فوراً"):
    st.rerun()

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