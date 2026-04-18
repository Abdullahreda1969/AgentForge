# 📜 AgentForge v2.0 Code of Practice

## 🛠️ Streamlit Blackout Requirements

- **Keys and State:** Do not initialize any numeric key with full text `""`. Use "0.0".

- **Callbacks:** Any modification to `session_state` must be performed by a callback function called via `on_click`.

- **Imports:** Each file is an independent island; retrieve `streamlit as st` in each file that uses it.

- **Streamlit Imports:** ALWAYS place import streamlit as st at the absolute top of the file, before any logic or try-except blocks.
- **Streamlit Inputs:** NEVER use integers for st.number_input value. ALWAYS use floats like 0.0 or 1.0.
                        Button Callbacks: When using on_click with arguments, ALWAYS use a lambda: on_click=lambda: func(arg).
                        Function Consistency: You MUST check the function names in helpers.py before calling them in main.py. Use view_tasks if it was defined as view_tasks.

## 📂 File Structure Requirements

- **Names:** Do not use the name `utils.py` under any circumstances; the accepted name is `helpers.py`.

- **Secrets:** Do not use placeholder values ​​such as `YOUR_API_KEY`. Leave them blank or drag them from the environment.

- "- Separation of responsibilities: config.py is for variables only. database.py is for SQLAlchemy engines and models. Never confuse them."

## 🛡️ Pen Rules (Verification)

- The required files (CSS) and the runtime (BAT) are static files, not living objects, for checking Python execution.

## 🗄️ Database Operations Rules (CRUD)

- **For Small/Medium Projects (Inventory, Task Manager, etc.):**
  - CRUD operations (Create, Read, Update, Delete) MUST be placed in `helpers.py`
  - This is the ACCEPTED and RECOMMENDED pattern for projects of this size
  - Database session management belongs in `database.py`, business logic belongs in `helpers.py`

- **Acceptable helpers.py Structure:**
  ```python
  # helpers.py - Contains ALL database interaction functions
  def create_task(...): ...
  def get_all_tasks(...): ...
  def update_task(...): ...
  def delete_task(...): ...
  This is NOT a violation of separation of concerns - it's appropriate modularity for the project scale.

Rejection Criteria: Only reject helpers.py if it contains UI code (Streamlit) or hardcoded credentials.

text

## 🔧 تعديل إضافي - في `system_prompt` الخاص بـ Reviewer

إذا كان لديك وصول إلى `reviewer.py`، تأكد من أن `system_prompt` الخاص به يحتوي على:

```python
system_prompt = """
أنت مراجع كود ذكي. مهمتك هي قبول أو رفض الكود بناءً على القواعد.

**استثناءات مهمة للمشاريع البسيطة:**
- في مشروع بحجم Inventory أو Task Manager، ملف helpers.py هو المكان الصحيح لجميع دوال CRUD.
- هذا ليس انتهاكاً لمبدأ فصل المسؤوليات في هذا السياق.
- لا ترفض الكود إلا إذا:
  1. يحتوي على أخطاء نحوية
  2. يستخدم placeholders حقيقية (YOUR_API_KEY)
  3. يحتوي على كود Streamlit في helpers.py
  4. يقوم بتعريف database engine في غير مكانه

إذا كان الكود يعمل ويتبع البنية المطلوبة، اعتمده بكلمة PASS.
"""
⚡ حل سريع (دون تعديل الملفات)
إذا كنت لا تريد تعديل gui_rules.md الآن، أضف هذا السطر إلى بداية orchestrator.py في دالة start_cycle:

python
# بعد سطر gui_rules = self._load_gui_rules()
# أضف هذا التعديل لتوضيح القاعدة للمراجع:
if "helpers.py" in str(structure):
    gui_rules += """

🔴 **توضيح هام للمراجع:**
في هذا المشروع البسيط، ملف helpers.py هو المكان المخصص لجميع دوال CRUD الخاصة بقاعدة البيانات.
هذا التصميم معتمد ولا يعتبر انتهاكاً لمبدأ فصل المسؤوليات.
قم بقبول helpers.py إذا كان يحتوي على دوال create/read/update/delete فقط.
"""


