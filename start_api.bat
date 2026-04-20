@echo off
title AgentForge API Server
echo Starting AgentForge API Server...
echo.

:: تفعيل البيئة الافتراضية
call venv\Scripts\activate.bat

:: تثبيت المتطلبات
pip install -r requirements_api.txt

:: تشغيل الخدمة
python api_service.py

pause