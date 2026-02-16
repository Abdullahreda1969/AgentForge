from google import genai
import os

class Reviewer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.0-flash" # أو gemma-3-1b-it حسب تفضيلك

    def review_code(self, code, original_task):
        prompt = f"""
        أنت الآن 'مراقب جودة برمجية' (Senior Code Reviewer). 
        المهمة الأصلية كانت: {original_task}
        الكود الذي كتبه المبرمج هو:
        ---
        {code}
        ---
        قم بتحليل الكود وابحث عن:
        1. هل جميع الأزرار مرتبطة بدوال (Missing commands)?
        2. هل الدوال تحتوي على منطق حقيقي أم مجرد 'pass'?
        3. هل هناك مكتبات مستخدمة لم يتم استيرادها (Import errors)?
        4. هل يلتزم الكود بأفضل الممارسات؟

        إذا كان الكود ممتازاً، ابدأ ردك بكلمة 'PASS'.
        إذا كان هناك أخطاء، ابدأ بكلمة 'FAIL' ثم اذكر الأخطاء بدقة ليتمكن المبرمج من إصلاحها.
        """
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text