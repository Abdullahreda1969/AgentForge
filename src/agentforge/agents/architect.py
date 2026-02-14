from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class ArchitectAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "models/gemma-3-1b-it"
        self.system_prompt = """
        You are an expert Software Architect. 
        Analyze the project and respond ONLY with a valid JSON object.
        Keys: file paths. Values: brief tasks for that file.
        Example: {"main.py": "Entry point that starts the app"}
        """

    def analyze_project(self, description, lang):
        prompt = f"Project: {description}\nLanguage: {lang}"
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"{self.system_prompt}\n{prompt}"
        )
        
        # تنظيف وتحويل النص إلى JSON
        try:
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except:
            return {"main.py": "Main script logic"}