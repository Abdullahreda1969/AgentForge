import json
import os

class MemoryAgent:
    def __init__(self, memory_file="knowledge_base.json"):
        self.memory_file = memory_file
        self.knowledge = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "preferences": ["Use SQLAlchemy for databases", "Use Streamlit for GUI"],
            "avoid": ["Placeholders like YOUR_API_KEY", "Business logic in main.py"],
            "technical_rules": ["Always include __init__.py in packages"]
        }

    def update_memory(self, session_history):
        """
        تحليل سجل الأخطاء والنجاحات لإضافة قواعد جديدة (يمكن تطويرها مستقبلاً بالذكاء الاصطناعي)
        """
        # حالياً سنعتمد على القواعد الثابتة وتحديثها يدوياً أو برمجياً
        pass

    def get_context_for_coder(self):
        """جلب السياق البرمجي بناءً على الهيكلية الإنجليزية الجديدة"""
        context = "\n--- SYSTEM KNOWLEDGE & RULES ---\n"
        
        # جلب القواعد التقنية (Technical Standards)
        if "Technical_Standards" in self.knowledge:
            standards = self.knowledge["Technical_Standards"]
            for category, rules in standards.items():
                context += f"- {category}: " + ", ".join(rules) + "\n"
        
        # جلب مسؤوليات الملفات (Project Structure)
        if "Project_Structure_Responsibility" in self.knowledge:
            context += "- Structure Rules: "
            for file, desc in self.knowledge["Project_Structure_Responsibility"].items():
                context += f"[{file}: {desc}] "
            context += "\n"

        # جلب معايير الرفض (Critical Rejection Criteria)
        if "Critical_Rejection_Criteria" in self.knowledge:
            context += "- CRITICAL REJECTIONS: " + " | ".join(self.knowledge["Critical_Rejection_Criteria"]) + "\n"

        return context