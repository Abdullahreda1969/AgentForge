from google import genai
import os

class Reviewer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "models/gemma-3-1b-it" # أو gemma-3-1b-it حسب تفضيلك

    
        # تأكد من إضافة history=None في تعريف الدالة
    def review_code(self, code, task, history=None): 
        """يراجع الكود بناءً على المهمة وتاريخ المحاولات السابقة"""
        
        prompt = f"""
        أنت مراجع كود خبير. 
        المهمة: {task}

        قواعد صارمة للمراجعة:
        1. إذا كان المشروع واجهة رسومية (GUI/Tkinter)، يمنع منعاً باتاً استخدام `input()` أو `print()` لجلب البيانات أو عرض النتائج.
        2. يجب استخدام `Entry.get()` لجلب البيانات و `label.config()` أو `messagebox` لعرض النتائج.
        3. إذا وجدت `input()` في كود GUI، رد بـ "FAIL: يمنع استخدام input في تطبيقات الواجهات".
        4. إذا كان الكود سليماً ومنطقياً، رد بـ "PASS".
        """
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text