import sys
import os
import uuid
import sqlite3
import json
import time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import shutil
from fastapi.responses import FileResponse
from fastapi import FastAPI, BackgroundTasks, HTTPException, Security, Header
from fastapi.security.api_key import APIKeyHeader
from agentforge.core.orchestrator import AgentForgeOrchestrator
# 1. إضافة المسار أولاً (مهم جداً)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# 2. إعداد الحماية
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
VALID_API_KEYS = ["agentforge_admin_2026", "dev_user_77"]

# 3. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('agentforge_tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            job_id TEXT PRIMARY KEY,
            project TEXT,
            status TEXT,
            result TEXT,
            file_count INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="AgentForge SaaS API v1.2")

# --- وظائف مساعدة لقاعدة البيانات ---

def save_task_to_db(job_id, project_name):
    conn = sqlite3.connect('agentforge_tasks.db')
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO tasks (job_id, project, status, created_at) VALUES (?, ?, ?, ?)",
        (job_id, project_name, "In Progress 🚀", now)
    )
    conn.commit()
    conn.close()

def update_task_status(job_id, status, result=""):
    conn = sqlite3.connect('agentforge_tasks.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ?, result = ? WHERE job_id = ?", (status, result, job_id))
    conn.commit()
    conn.close()

def update_task_stats(job_id, file_count, duration):
    conn = sqlite3.connect('agentforge_tasks.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET file_count = ?, duration_seconds = ? WHERE job_id = ?", (file_count, duration, job_id))
    conn.commit()
    conn.close()

def get_task_from_db(job_id):
    conn = sqlite3.connect('agentforge_tasks.db')
    cursor = conn.cursor()
    # تصحيح الاسم هنا من project_name إلى project
    cursor.execute("SELECT project, status, result, created_at FROM tasks WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# --- التحقق من المفتاح ---
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API Key")

# --- نقاط الاتصال ---

@app.post("/create-task/")
async def create_task(
    project_name: str, 
    task_description: str, 
    background_tasks: BackgroundTasks,
    api_key: str = Security(get_api_key)
):
    job_id = str(uuid.uuid4())
    save_task_to_db(job_id, project_name)
    background_tasks.add_task(run_engine, job_id, project_name, task_description)
    return {"job_id": job_id, "message": "Task started 🚀"}

@app.get("/status/{job_id}")
async def check_status(job_id: str):
    task = get_task_from_db(job_id)
    if not task:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return {
        "job_id": job_id,
        "project": task[0],
        "status": task[1],
        "result": task[2],
        "created_at": task[3]
    }
@app.get("/")
async def root():
    return {"message": "AgentForge API is online!", "docs": "/docs"}
    
def log_to_sheets(project_name, status, file_count, duration):
    try:
        # تحديد المسار المطلق للملف لضمان العثور عليه في البيئة المحلية
        current_dir = os.path.dirname(os.path.abspath(__file__))
        creds_path = os.path.join(current_dir, "credentials.json")

        if not os.path.exists(creds_path):
            print(f"❌ خطأ: ملف المفاتيح غير موجود في {creds_path}")
            return False

        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # تحميل البيانات ومعالجة المفتاح السري
        with open(creds_path, "r") as f:
            creds_info = json.load(f)
            # الحل السحري لمشكلة الـ Private Key في ويندوز
            creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')

        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # رابط الجدول الخاص بك (تأكد أنه متاح للحساب البرمجي - Service Account)
        sheet_url = "https://docs.google.com/spreadsheets/d/1gWF-LQ4MQqgUJx2GVbno_2BplQBGQBuU8goQBTT1Bl4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        
        row = [
            project_name, 
            status, 
            file_count, 
            f"{duration}s", 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
        print(f"🚀 تم بنجاح إرسال البيانات لجداول جوجل: {project_name}")
        return True
    except Exception as e:
        print(f"⚠️ فشل الاتصال بغوغل: {e}")
        return False
def run_engine(job_id: str, project_name: str, task_description: str):
    start_time = time.time()
    update_task_status(job_id, "In Progress 🏗️", "Engine is working...")
    
    try:
        af = AgentForgeOrchestrator()
        af.start_cycle(project_name=project_name, description=task_description)
        
        duration = round(time.time() - start_time, 2)
        project_path = os.path.abspath(os.path.join(os.getcwd(), "projects", project_name))
        
        actual_file_count = 0
        if os.path.exists(project_path):
            files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))]
            actual_file_count = len(files)

        # --- الاستدعاء الآن سيعمل بنجاح ---
        log_to_sheets(project_name, "Completed ✅", actual_file_count, duration)
        
        update_task_status(job_id, "Completed ✅", f"Project {project_name} built successfully.")
        update_task_stats(job_id, actual_file_count, duration)
        
    except Exception as e:
        log_to_sheets(project_name, "Failed ❌", 0, 0) # سجل الفشل أيضاً
        update_task_status(job_id, "Failed ❌", str(e))

@app.get("/download/{project_name}")
async def download_project(project_name: str):
    project_path = os.path.abspath(os.path.join(os.getcwd(), "projects", project_name))
    zip_path = os.path.abspath(os.path.join(os.getcwd(), "projects", f"{project_name}.zip"))

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="المشروع غير موجود!")

    # إنشاء ملف ZIP للمجلد
    shutil.make_archive(os.path.join(os.getcwd(), "projects", project_name), 'zip', project_path)

    return FileResponse(
        path=zip_path, 
        filename=f"{project_name}.zip", 
        media_type='application/zip'
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    