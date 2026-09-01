import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Listing accessible Gemini models...")
try:
    for m in client.models.list():
        print(f"Model: {m.name}, display_name: {getattr(m, 'display_name', '')}")
except Exception as e:
    print(f"Failed to list models: {e}")
