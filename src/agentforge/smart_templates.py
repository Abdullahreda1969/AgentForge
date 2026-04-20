# src/agentforge/smart_templates.py

class SmartTemplates:
    """قوالب ذكية تتكيف مع نوع المشروع"""
    
    @staticmethod
    def get_database_template(project_type):
        """قالب database.py - ثابت 100%"""
        return '''
# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
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
    def get_config_template():
        """قالب config.py - ثابت"""
        return '''
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
APP_NAME = os.getenv("APP_NAME", "My Application")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
'''

    @staticmethod
    def get_helpers_template(project_type, item_name):
        """قالب helpers.py - ذكي (هيكل ثابت، أسماء متغيرة)"""
        
        templates_map = {
            "task": {
                "items": "tasks",
                "item": "task",
                "fields": "name: str, description: str = ''",  # ✅ changed from 'title' to 'name'
                "assign": "name=name, description=description"  # ✅保持一致
            },
            "contact": {
                "items": "contacts",
                "item": "contact",
                "fields": "name: str, phone: str = '', email: str = ''",
                "assign": "name=name, phone=phone, email=email"
            },
            "product": {
                "items": "products",
                "item": "product",
                "fields": "name: str, price: float = 0.0, quantity: int = 0",
                "assign": "name=name, price=price, quantity=quantity"
            },
            "expense": {
                "items": "expenses",
                "item": "expense",
                "fields": "description: str, amount: float, category: str = ''",
                "assign": "description=description, amount=amount, category=category"
            }
        }
        
        template = templates_map.get(project_type, {
            "items": f"{item_name}s",
            "item": item_name,
            "fields": "name: str, description: str = ''",
            "assign": "name=name, description=description"
        })
        
        return f'''
# helpers.py
from sqlalchemy.orm import Session
from database import SessionLocal, Item
from typing import List, Optional

def get_{template["items"]}() -> List[Item]:
    """جلب جميع {template["items"]}"""
    with SessionLocal() as db:
        return db.query(Item).all()

def get_{template["item"]}_by_id({template["item"]}_id: int) -> Optional[Item]:
    """جلب {template["item"]} محدد بالمعرف"""
    with SessionLocal() as db:
        return db.query(Item).filter(Item.id == {template["item"]}_id).first()

def add_{template["item"]}({template["fields"]}) -> Item:
    """إضافة {template["item"]} جديد"""
    with SessionLocal() as db:
        item = Item({template["assign"]})
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

def update_{template["item"]}({template["item"]}_id: int, **kwargs) -> bool:
    """تحديث {template["item"]}"""
    with SessionLocal() as db:
        item = db.query(Item).filter(Item.id == {template["item"]}_id).first()
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.commit()
            return True
        return False

def delete_{template["item"]}({template["item"]}_id: int) -> bool:
    """حذف {template["item"]}"""
    with SessionLocal() as db:
        item = db.query(Item).filter(Item.id == {template["item"]}_id).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
'''

    @staticmethod
    def get_main_template(project_type, item_name):
        """قالب main.py - مرن (تصميم حر)"""
        
        templates_map = {
            "task": "📝 Task Manager",
            "contact": "📞 Contact Book",
            "product": "📦 Inventory Management",
            "expense": "💰 Expense Tracker"
        }
        
        title = templates_map.get(project_type, f"📱 {item_name.title()} Manager")
        items_name = f"{item_name}s"
        
        return f'''
# main.py
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from helpers import get_{items_name}, add_{item_name}, delete_{item_name}

st.set_page_config(page_title="{title}", layout="wide")
st.title(f"{title}")

# Initialize session state
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# Sidebar for adding items
with st.sidebar:
    st.header(f"Add New {item_name.title()}")
    with st.form("add_form"):
        name = st.text_input(f"{item_name.title()} Name")
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button(f"➕ Add {item_name.title()}")
        
        if submitted and name:
            add_{item_name}(name=name, description=description)
            st.success(f"Added: {{name}}")
            st.session_state.refresh = True
            st.rerun()

# Main area - display items
st.header(f"{items_name.title()} List")

# Refresh data if needed
if st.session_state.refresh:
    st.session_state.refresh = False

# Get and display items
items = get_{items_name}()

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
                if delete_{item_name}(item.id):
                    st.success(f"Deleted: {{item.name}}")
                    st.rerun()

# Footer
st.markdown("---")
st.caption(f"Powered by AgentForge - {{len(items)}} {items_name} total")
'''