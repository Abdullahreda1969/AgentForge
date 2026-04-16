from src.agentforge.core.orchestrator import AgentForgeOrchestrator
import os

# تأكد أنك وضعت مفتاحك في ملف .env
# أو قم بتعريفه هنا يدوياً للتجربة
# os.environ["GEMINI_API_KEY"] = "YOUR_KEY_HERE"

def run_test():
    # 1. تهيئة الأوركسترا (المنسق) الذي قمنا بتعديله
    forge = AgentForgeOrchestrator()

    # 2. تعريف مشروع جديد لاختبار "قوة المناعة"
    project_name = "Inventory_Pro_Test"
    goal = """
    Create a professional Inventory manager.
    - Requirements: main.py for UI, helpers.py for calculations.
    - Logic: Calculate total value (price * quantity).
    - UI: Use Streamlit with st.number_input(value=0.0).
    Fix the previous TypeError in Inventory_Pro_Test.
ERROR LOG: calculate_total_value() missing 1 required positional argument: 'quantity'.
ENSURE: 
1. helpers.py has calculate_total_value(inventory_list).
2. main.py calls it as helpers.calculate_total_value(st.session_state.inventory).
3. All math operations handle float values (0.0).
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