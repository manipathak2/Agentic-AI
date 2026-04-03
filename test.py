from google.genai import Client
import os

# new SDK usage
client = Client(api_key=os.getenv("GROQ_API_KEY"))
chat = client.chats.create(model="gemini-2.5-flash")
response = chat.send_message("Say hello")

# extract text (simple version)
if hasattr(response, 'output') and response.output:
    print('Reply:', response.output[0].content[0].text)
else:
    print('Raw response:', response)