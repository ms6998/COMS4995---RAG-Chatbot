import requests
import subprocess
import logging

# Set up logging so you can see errors in your VS Code terminal
logging.basicConfig(level=logging.INFO)

class ChatbotService:
    def __init__(self):
        self.url = "https://pathwise-1056631112792.us-east1.run.app/ask"

    def _get_token(self):
        """Fetches the identity token from gcloud."""
        try:
            return subprocess.check_output("gcloud auth print-identity-token", shell=True).decode("utf-8").strip()
        except Exception as e:
            logging.error(f"Failed to get gcloud token: {e}")
            return None

    def ask_question(self, question, program="MS Computer Science", year=2026):
        token = self._get_token()
        if not token:
            return {"error": "Authentication failed. Run 'gcloud auth login'"}

        payload = {
            "question": question,
            "user_profile": {
                "program": program,
                "catalog_year": year
            }
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers)
            response.raise_for_status() # Raises error for 4xx or 5xx codes
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Request failed: {e}")
            return {"error": str(e)}