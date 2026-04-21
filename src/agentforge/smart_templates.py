# src/agentforge/smart_templates.py
# القوالب الذكية الموحدة - تضمن عمل جميع التطبيقات المنتجة

class SmartTemplates:
    """قوالب ذكية موحدة لجميع أنواع المشاريع"""
    
    @staticmethod
    def get_config_template():
        """قالب config.py - يحتوي على جميع المتغيرات الأساسية"""
        
        return '''# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

# App settings
APP_NAME = os.getenv("APP_NAME", "My Application")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# متغيرات عامة (لمنع أخطاء الاستيراد)
PRIORITIES = {
    "High": 3,
    "Medium": 2,
    "Low": 1
}

# متغيرات خاصة بأنواع المشاريع المختلفة
TASK_PRIORITIES = PRIORITIES
CONTACT_PRIORITIES = PRIORITIES
PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Food", "Other"]
STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]
'''
    
    @staticmethod
    def get_database_template():
        """قالب database.py - نماذج SQLAlchemy"""
        
        return '''# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
'''
    
    @staticmethod
    def get_helpers_template(project_type, item_name):
        """قالب helpers.py - دوال CRUD بأسماء مناسبة"""
        
        items_name = f"{item_name}s"
        
        return f'''# helpers.py
from sqlalchemy.orm import Session
from database import SessionLocal, Item
from typing import List, Optional

def get_{items_name}() -> List[Item]:
    """جلب جميع {items_name}"""
    with SessionLocal() as db:
        return db.query(Item).all()

def get_{item_name}_by_id({item_name}_id: int) -> Optional[Item]:
    """جلب {item_name} محدد بالمعرف"""
    with SessionLocal() as db:
        return db.query(Item).filter(Item.id == {item_name}_id).first()

def add_{item_name}(name: str, description: str = "") -> Item:
    """إضافة {item_name} جديد"""
    with SessionLocal() as db:
        item = Item(name=name, description=description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

def update_{item_name}({item_name}_id: int, **kwargs) -> bool:
    """تحديث {item_name}"""
    with SessionLocal() as db:
        item = db.query(Item).filter(Item.id == {item_name}_id).first()
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.commit()
            return True
        return False

def delete_{item_name}({item_name}_id: int) -> bool:
    """حذف {item_name}"""
    with SessionLocal() as db:
        item = db.query(Item).filter(Item.id == {item_name}_id).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
'''
    
    @staticmethod
    def get_main_template(project_type, item_name):
        """قالب main.py - واجهة Streamlit موحدة"""
        
        items_name = f"{item_name}s"
        
        # عنوان حسب نوع المشروع
        titles = {
            "task": "📝 Task Manager",
            "contact": "📞 Contact Book",
            "product": "📦 Inventory Management",
            "expense": "💰 Expense Tracker"
        }
        title = titles.get(project_type, f"📱 {item_name.title()} Manager")
        
        return f'''# main.py
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# استيراد آمن - لا يفترض وجود متغيرات معينة
try:
    from config import *
except ImportError:
    # قيم افتراضية إذا فشل الاستيراد
    pass

try:
    from helpers import get_{items_name}, add_{item_name}, delete_{item_name}
except ImportError as e:
    st.error(f"خطأ في استيراد الدوال المساعدة: {{e}}")
    st.stop()

st.set_page_config(page_title="{title}", layout="wide")
st.title(f"{title}")

# Sidebar for adding items
with st.sidebar:
    st.header(f"Add New {item_name.title()}")
    with st.form("add_form"):
        name = st.text_input(f"{item_name.title()} Name")
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button(f"➕ Add")
        
        if submitted and name:
            try:
                add_{item_name}(name=name, description=description)
                st.success(f"Added: {{name}}")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding: {{e}}")

# Main area
st.header(f"{items_name.title()} List")

try:
    items = get_{items_name}()
except Exception as e:
    st.error(f"Error loading items: {{e}}")
    items = []

if not items:
    st.info(f"No {items_name} yet. Add one from the sidebar!")
else:
    for item in items:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{{item.name}}**")
            if hasattr(item, 'description') and item.description:
                st.caption(item.description)
        with col2:
            st.write(f"ID: {{item.id}}")
        with col3:
            if st.button("🗑️ Delete", key=f"del_{{item.id}}"):
                try:
                    delete_{item_name}(item.id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting: {{e}}")

st.markdown("---")
st.caption("Powered by AgentForge")
'''
    
    @staticmethod
    def get_start_app_template():
        """قالب start_app.bat"""
        return '''@echo off
streamlit run main.py
pause
'''
    
    @staticmethod
    def detect_project_type(description):
        """تحديد نوع المشروع من الوصف"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['task', 'todo', 'مهمة', 'مهام', 'to do']):
            return "task"
        if any(word in desc_lower for word in ['contact', 'phone', 'جهة', 'اتصال', 'عنوان']):
            return "contact"
        if any(word in desc_lower for word in ['product', 'inventory', 'منتج', 'مخزون']):
            return "product"
        if any(word in desc_lower for word in ['expense', 'money', 'مصروف', 'مالية']):
            return "expense"
        if any(word in desc_lower for word in ['calculator', 'حاسبة']):
            return "calculator"
        
        return "general"
    
    @staticmethod
    def detect_item_name(description, project_type):
        """استخراج اسم العنصر من الوصف"""
        names = {
            "task": "task",
            "contact": "contact",
            "product": "product",
            "expense": "expense",
            "calculator": "calculation"
        }
        return names.get(project_type, "item")