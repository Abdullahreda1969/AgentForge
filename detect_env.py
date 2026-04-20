# detect_env.py
import os
import sys

def detect_environment():
    """
    يكتشف بيئة التشغيل الحالية:
    - 'cloud': إذا كان يعمل على Streamlit Cloud أو لديه مفاتيح Gemini
    - 'local': إذا كان يعمل محلياً مع Ollama
    """
    
    # 1. فحص إذا كنا على Streamlit Cloud
    if os.environ.get("STREAMLIT_CLOUD") == "true":
        return "cloud"
    
    # 2. فحص وجود مفتاح Gemini API
    if os.getenv("GEMINI_API_KEY"):
        return "cloud"
    
    # 3. فحص وجود Ollama محلياً
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            return "local"
    except:
        pass
    
    # 4. فحص وجود ملفات Ollama
    if os.path.exists("venv") or os.path.exists("ollama"):
        return "local"
    
    # 5. افتراضياً نعتبر Cloud
    return "cloud"

def get_engine_type():
    """ترجع نوع المحرك المناسب للبيئة الحالية"""
    env = detect_environment()
    return {
        "environment": env,
        "model": "ollama" if env == "local" else "gemini",
        "offline": env == "local"
    }