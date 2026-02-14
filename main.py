from agentforge.core.orchestrator import AgentForgeOrchestrator

def main():
    af = AgentForgeOrchestrator()
    # طلب مشروع يحتاج مكتبة غير مثبتة (python-weather)
    state = af.start_cycle(
        project_name="BitcoinPriceChecker", 
        description="Create a python script that uses the requests library to get the current price of Bitcoin from Coingecko API and prints it.",
        lang="python"
    )
    print(f"\n✅ الحالة النهائية: {state['status']}")

if __name__ == "__main__":
    main()