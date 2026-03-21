# 🚀 AgentForge v0.6.0

An autonomous AI-powered software engineer that designs, codes, tests, and self-corrects applications.

## 🧠 Current Capabilities

- **Architecting:** Automatically generates folder structures based on project descriptions.
- **Multi-Agent Coding:** Uses **Gemma 3** to write clean, modular Python code.
- **Syntax Validation:** Built-in `TesterAgent` ensures code is syntactically correct before saving.
- **Runtime Execution:** `ExecutorAgent` runs the generated code in a sub-process to verify logic.
- **Self-Healing Loop:** The system detects runtime errors and logical failures, providing feedback to the AI for up to 3 retry attempts.

## 🛠️ Tech Stack

- **Engine:** Python 3.14+
- **AI Brain:** Google GenAI (Gemma-3-1b-it)
- **Orchestration:** Custom Multi-Agent Orchestrator

## 📈 Recent Achievement

Successfully generated **GoldTracker**, a project that went through 3 iterations of self-correction to fix `NameError` and logic failures automatically.

# 🚀 AgentForge v1.0.0

**AgentForge** هو محرك بناء برمجيات ذكي يعتمد على نموذج "الوكلاء المتعددين" (Multi-Agent System). يقوم المحرك بتحويل الأوصاف النصية البسيطة إلى مشاريع برمجية كاملة، مع نظام تدقيق ومراجعة ذاتي.

## 🛠️ كيف يعمل النظام؟ (Architecture)

يعتمد الإصدار 1.0.0 على أربعة وكلاء متخصصين يعملون في تناغم:

1.  **Architect Agent:** يقوم بتحليل الطلب وتصميم الهيكل المجلدات والملفات.
2.  **Coder Agent:** مبرمج خبير يقوم بكتابة الكود الفعلي بناءً على التصميم.
3.  **Reviewer Agent (New):** مراقب جودة يقوم بفحص المنطق البرمجي وربط الأزرار والوظائف قبل الاعتماد.

4.  **Executor & Tester Agent:** يقوم بتشغيل الكود في بيئة معزولة واختبار سلامته النحوية والوظيفية.


## ✨ المميزات الجديدة في الإصدار 1.0.0

- **التحقق المنطقي:** لن يتم قبول الكود الذي يحتوي على دوال فارغة أو أزرار غير مفعلة.
- **نظام التصحيح الذاتي (Self-Healing):** في حال فشل الكود، يقوم المحرك بإعادة المحاولة بناءً على تغذية راجعة دقيقة.
- **تقارير الأعطال الزمنية (Timestamped Crash Reports):** تقارير Markdown مفصلة توضح سبب ووقت فشل أي عملية تتبعاً لأفضل ممارسات الـ Logging.
- **دعم مكتبات AI الحديثة:** تكامل كامل مع Google Gemini API 2.0.

## 🚀 البدء في الاستخدام

 شغل التطبيق
powershell
streamlit run app_gui.py
