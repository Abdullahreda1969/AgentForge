from agentforge.core.orchestrator import AgentForgeOrchestrator

def main():
    af = AgentForgeOrchestrator()
    # لنطلب منه بناء أداة بسيطة لحساب العملات أو جلب سعر الذهب مثلاً
    state = af.start_cycle(
        project_name="GoldTracker", 
        description="A script that gets real-time gold price using a mock API and saves it to a file",
        lang="python"
    )
    print(f"\n✅ الحالة النهائية: {state['status']}")

if __name__ == "__main__":
    main()