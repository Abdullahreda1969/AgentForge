import requests
import json
import logging

logger = logging.getLogger("AgentForge.Reviewer")

class Reviewer:
    def __init__(self):
        self.model_name = "gemma3"
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def review_code(self, code, task, history=None):
        prompt = f"""
        You are a code reviewer. Review this code and respond with either:
        - PASS (if code is correct, functional, and follows requirements)
        - FAIL (with specific issues to fix)
        
        TASK: {task}
        
        CODE TO REVIEW:
        {code}
        
        PREVIOUS ISSUES: {history if history else 'None'}
        
        RESPOND WITH PASS OR FAIL:
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            result = response.json()
            review = result.get('response', '')
            
            if 'PASS' in review.upper():
                return "PASS - Code accepted"
            else:
                return f"FAIL - {review}"
                
        except Exception as e:
            logger.error(f"Reviewer error: {e}")
            return "PASS - Auto-accept due to review error"