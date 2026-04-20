# api_service.py - النسخة الموحدة النهائية
# يدعم: Ollama محلي + Gemini سحابي

import os
import sys
import json
import secrets
import shutil
import time
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agentforge.core.orchestrator import AgentForgeOrchestrator

# ========== نماذج البيانات ==========
class GenerateRequest(BaseModel):
    description: str = Field(..., description="وصف المشروع", min_length=10, max_length=2000)
    project_name: Optional[str] = Field(None, description="اسم المشروع")
    project_type: str = Field("auto", description="نوع المشروع: task, contact, product, expense, auto")
    template: str = Field("auto", description="نوع القالب")

class GenerateResponse(BaseModel):
    success: bool
    project_id: str
    download_url: Optional[str] = None
    message: str
    files_generated: List[str] = Field(default_factory=list)
    mode: str = Field("unknown", description="local أو cloud")
    generated_at: datetime = Field(default_factory=datetime.now)

class APIKeyRequest(BaseModel):
    email: str
    plan: str = "free"
    company: Optional[str] = None

class APIKeyResponse(BaseModel):
    api_key: str
    plan: str
    monthly_limit: int
    created_at: datetime
    expires_at: Optional[datetime] = None

# ========== إعداد التطبيق ==========
app = FastAPI(
    title="AgentForge API",
    description="توليد تطبيقات كاملة من وصف نصي باستخدام الذكاء الاصطناعي",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# إضافة CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== مخزن بسيط للمفاتيح (للتجربة) ==========
# في الإنتاج، استخدم قاعدة بيانات حقيقية
API_KEYS = {}

# ========== دوال مساعدة ==========
def detect_mode():
    """كشف وضع التشغيل الحالي"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            return "local"
    except:
        pass
    
    if os.getenv("GEMINI_API_KEY"):
        return "cloud"
    
    return "local"

def create_zip(project_name):
    """إنشاء ملف ZIP للمشروع"""
    source_dir = os.path.join("projects", project_name)
    zip_path = os.path.join("projects", f"{project_name}.zip")
    
    if os.path.exists(source_dir):
        shutil.make_archive(f"projects/{project_name}", 'zip', source_dir)
        return zip_path
    return None

# ========== نقاط النهاية (Endpoints) ==========

@app.get("/")
async def root():
    return {
        "service": "AgentForge API",
        "version": "2.0.0",
        "description": "Generate full applications from text descriptions using AI",
        "mode": detect_mode(),
        "endpoints": {
            "POST /v1/generate": "Generate a new project",
            "POST /v1/api-key": "Request an API key",
            "GET /v1/stats": "Get usage statistics",
            "GET /download/{filename}": "Download generated project",
            "GET /health": "Health check"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": detect_mode(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/v1/api-key", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyRequest):
    """إنشاء مفتاح API جديد"""
    api_key = secrets.token_urlsafe(32)
    
    limits = {"free": 100, "pro": 5000, "business": 50000}
    
    API_KEYS[api_key] = {
        "email": request.email,
        "plan": request.plan,
        "monthly_limit": limits.get(request.plan, 100),
        "used": 0,
        "created_at": datetime.now()
    }
    
    return APIKeyResponse(
        api_key=api_key,
        plan=request.plan,
        monthly_limit=limits.get(request.plan, 100),
        created_at=datetime.now(),
        expires_at=None
    )

@app.post("/v1/generate", response_model=GenerateResponse)
async def generate_project(
    request: GenerateRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    توليد مشروع جديد من الوصف النصي
    
    - description: وصف المشروع بالعربية أو الإنجليزية
    - project_name: اسم المشروع (اختياري)
    - project_type: نوع المشروع (task, contact, product, expense, auto)
    """
    start_time = time.time()
    
    # التحقق من المفتاح (إذا كان مطلوباً)
    if x_api_key and x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if x_api_key:
        key_info = API_KEYS[x_api_key]
        if key_info["used"] >= key_info["monthly_limit"]:
            raise HTTPException(status_code=429, detail="Monthly limit exceeded")
        key_info["used"] += 1
    
    # تحديد اسم المشروع
    project_name = request.project_name or f"API_Project_{uuid.uuid4().hex[:8]}"
    project_name = project_name.replace(" ", "_")
    
    # كشف الوضع
    current_mode = detect_mode()
    
    try:
        # استخدام orchestrator الموحد
        # use_local=None → كشف تلقائي
        forge = AgentForgeOrchestrator(use_local=None)
        
        result = forge.start_cycle(
            project_name=project_name,
            description=request.description,
            template=request.template
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        if result["status"] == "completed":
            zip_file = create_zip(project_name)
            files = []
            project_path = os.path.join("projects", project_name)
            if os.path.exists(project_path):
                files = os.listdir(project_path)
            
            return GenerateResponse(
                success=True,
                project_id=project_name,
                download_url=f"/download/{project_name}.zip" if zip_file else None,
                message=f"Project '{project_name}' generated successfully",
                files_generated=files,
                mode=current_mode,
                generated_at=datetime.now()
            )
        else:
            return GenerateResponse(
                success=False,
                project_id=project_name,
                message=f"Generation failed: {result.get('reason', 'Unknown error')}",
                mode=current_mode
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_project(filename: str):
    """تحميل مشروع مولد"""
    file_path = os.path.join("projects", filename)
    if not os.path.exists(file_path):
        # جرب بدون مجلد projects
        file_path = filename
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/zip",
        filename=filename
    )

@app.get("/v1/stats")
async def get_stats(x_api_key: str = Header(...)):
    """الحصول على إحصائيات الاستخدام"""
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_info = API_KEYS[x_api_key]
    return {
        "email": key_info["email"],
        "plan": key_info["plan"],
        "used": key_info["used"],
        "monthly_limit": key_info["monthly_limit"],
        "remaining": key_info["monthly_limit"] - key_info["used"],
        "mode": detect_mode()
    }

# ========== التشغيل ==========
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              AgentForge API Service v2.0                     ║
    ║                    Unified Version                           ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📍 Local:   http://localhost:8000                          ║
    ║  📍 Docs:    http://localhost:8000/docs                     ║
    ║  📍 Mode:    {}  
    ╠══════════════════════════════════════════════════════════════╣
    ║  🚀 Ready to generate projects!                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """.format(detect_mode()))
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)