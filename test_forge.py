from src.agentforge.core.orchestrator import AgentForgeOrchestrator
import os

# تأكد أنك وضعت مفتاحك في ملف .env
# أو قم بتعريفه هنا يدوياً للتجربة
# os.environ["GEMINI_API_KEY"] = "YOUR_KEY_HERE"

def run_test():
    # 1. تهيئة الأوركسترا (المنسق) الذي قمنا بتعديله
    forge = AgentForgeOrchestrator()

    # 2. تعريف مشروع جديد لاختبار "قوة المناعة"
    project_name = "Inventory_Final_Test"
    goal = """
            Create a Smart Task Manager with the following:
            1. Persistence: Use SQLAlchemy to save tasks (id, title, status, priority).
            2. Database: A dedicated 'database.py' for models and engine.
            3. Logic: All DB operations (CRUD) must be in 'helpers.py'.
            4. GUI: A Streamlit interface in 'main.py' to add, view, and delete tasks.
            5. Standards: No placeholders, use context managers for sessions, and include a professional CSS.
            """

    print(f"🚀 Starting AgentForge v0.5 Simulation...")
    
    # 3. إطلاق الدورة
    # سيقوم المنسق باستدعاء (Architect -> Coder -> Reviewer -> Tester -> Executor)
    final_result = forge.start_cycle(
        project_name=project_name,
        description=goal
    )

    print("\n" + "="*30)
    print(f"🏁 Final Status: {final_result['status']}")
    print("="*30)

if __name__ == "__main__":
    run_test()