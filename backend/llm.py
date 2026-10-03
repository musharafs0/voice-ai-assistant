import os

from dotenv import load_dotenv
from google import genai    
load_dotenv(override=True)

    
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)



def get_ai_response(message: str, history: list) -> str:

    conversation = ""

    for chat in history:
        conversation += f"User: {chat['message']}\n"
        conversation += f"Assistant: {chat['response']}\n"

    conversation += f"User: {message}\n"
    conversation += "Assistant:"

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation
    )

    return response.text