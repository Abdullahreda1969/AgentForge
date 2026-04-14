import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="AgentForge Admin Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- دالة جلب البيانات من Google Sheets ---
# --- دالة جلب البيانات من Google Sheets المطورة ---
def get_admin_data():
    try:
        # 1. إعداد الصلاحيات
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 2. تحميل المفاتيح ومعالجة الـ Private Key برمجياً
        # هذا يضمن حل مشكلة الـ JWT Signature تماماً
        import json
        with open("credentials.json", "r") as f:
            credentials_info = json.load(f)
        
        # تنظيف عميق للمفتاح الخاص
        if 'private_key' in credentials_info:
            pk = credentials_info['private_key']
            # إزالة أي علامات تنصيص زائدة أو مسافات في البداية والنهاية
            pk = pk.strip()
            # التأكد من أن الروابط السطرية صحيحة
            if "\\n" in pk:
                pk = pk.replace("\\n", "\n")
            credentials_info['private_key'] = pk
            
        creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 3. فتح الملف باستخدام الرابط المباشر
        sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        
        # 4. جلب البيانات وتحويلها لـ DataFrame
        records = sheet.get_all_records()
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        
        # تنظيف البيانات لضمان عمل الرسوم البيانية
        if not df.empty:
            # تحويل عدد الملفات لرقم
            if 'files_count' in df.columns:
                df['files_count'] = pd.to_numeric(df['files_count'], errors='coerce').fillna(0)
            
            # تنظيف عمود الوقت
            if 'duration_seconds' in df.columns:
                df['duration_seconds'] = df['duration_seconds'].astype(str).str.replace('s', '', regex=False)
                df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce').fillna(0)
            
            # ترتيب البيانات حسب الأحدث
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values(by='created_at', ascending=False)
        
        return df
    except Exception as e:
        # عرض الخطأ بشكل مفصل للمدير فقط في التيرمينال
        print(f"DEBUG: Detailed Error -> {e}")
        st.error(f"❌ خطأ في الاتصال بالسحاب: {e}")
        return pd.DataFrame()

# عنوان اللوحة
st.title("🛡️ لوحة تحكم مدير AgentForge")
st.markdown(f"**آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# جلب البيانات الحية
data = get_admin_data()

if not data.empty:
    # 📊 1. قسم الإحصائيات السريعة (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي المشاريع", len(data))
    with col2:
        success_count = len(data[data['status'].str.contains('Completed', na=False)])
        st.metric("مشاريع ناجحة ✅", success_count)
    with col3:
        avg_time = round(data['duration_seconds'].mean(), 1)
        st.metric("متوسط وقت البناء", f"{avg_time} ثانية")
    with col4:
        total_files = int(data['files_count'].sum())
        st.metric("إجمالي الملفات المنشأة", total_files)

    st.markdown("---")

    # 📈 2. الرسوم البيانية التفاعلية
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 وتيرة الإنتاج الرقمي")
        fig = px.area(data, x='created_at', y='files_count', title="عدد الملفات لكل مشروع عبر الزمن", line_shape="spline")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("📂 تحليل حالة المهام")
        fig_pie = px.pie(data, names='status', title="توزيع حالات النجاح والفشل", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # 📦 3. مركز تحميل المشاريع (من المجلد الفعلي)
    st.subheader("📦 مركز تسليم المشاريع (Cloud Storage)")
    projects_dir = "projects"
    
    # فحص المشاريع الموجودة فعلياً في السيرفر
    if os.path.exists(projects_dir):
        actual_projects = [d for d in os.listdir(projects_dir) 
                          if os.path.isdir(os.path.join(projects_dir, d)) and not d.startswith('.')]
        
        if actual_projects:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                selected_project = st.selectbox("اختر مشروعاً لتحميله كملف ZIP:", actual_projects)
            with col_btn:
                import shutil
                st.write("") # موازنة
                st.write("")
                if st.button(f"📦 تجهيز {selected_project}"):
                    zip_path = shutil.make_archive(selected_project, 'zip', os.path.join(projects_dir, selected_project))
                    with open(f"{selected_project}.zip", "rb") as f:
                        st.download_button(label="⬇️ اضغط للتحميل الآن", data=f, file_name=f"{selected_project}.zip")
        else:
            st.info("لا توجد مجلدات مشاريع فعلياً على هذا السيرفر حالياً.")
    else:
        st.warning("مجلد Projects غير موجود. قم بإنشاء مشروع أولاً.")

    st.markdown("---")

    # 📋 4. سجل العمليات الشامل
    st.subheader("📋 سجل العمليات السحابي (Cloud Ledger)")
    st.dataframe(data, use_container_width=True)

else:
    st.warning("⚠️ لا توجد بيانات مسجلة في Google Sheets حالياً. ابدأ بصهّر مشروعك الأول!")

# ⚙️ 5. أدوات المدير الجانبية
st.sidebar.title("🛠️ أدوات الصيانة")
if st.sidebar.button("🔄 تحديث يدوي للبيانات"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("إصدار اللوحة: v1.0 (Cloud Sync)")