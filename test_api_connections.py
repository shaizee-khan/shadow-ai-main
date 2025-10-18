# test_chatgpt_api.py
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Get your OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")

print("🔍 Testing ChatGPT (OpenAI) API connection...\n")

if not openai_key:
    print("❌ OPENAI_API_KEY missing in .env file")
    exit()

# ChatGPT (OpenAI) endpoint
url = "https://api.openai.com/v1/chat/completions"

# Request headers
headers = {
    "Authorization": f"Bearer {openai_key}",
    "Content-Type": "application/json"
}

# Simple test message
payload = {
    "model": "gpt-3.5-turbo",  # You can also use "gpt-4" or "gpt-4o" if your key supports it
    "messages": [
        {"role": "user", "content": "Hello ChatGPT! Please confirm you're online."}
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        print("✅ ChatGPT API responded successfully!")
        print("\nResponse:\n", text)
    elif response.status_code == 401:
        print("❌ Unauthorized – Invalid or missing API key.")
    elif response.status_code == 429:
        print("⚠️ Rate limit reached – Too many requests.")
    else:
        print(f"⚠️ Unexpected response (Status: {response.status_code})")
        print("Response:", response.text[:200])

except Exception as e:
    print("❌ Error connecting to ChatGPT API:", e)
