from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

resp = client.responses.create(
    model="gpt-4o-mini",
    input="Hello, this is a test."
)

print(resp.output_text)
