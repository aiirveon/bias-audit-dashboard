import anthropic
import os
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    system="You are a dataset generator. You always respond with valid JSON only. No markdown, no explanation, no code fences. Only a raw JSON array.",
    messages=[
        {
            "role": "user",
            "content": 'Generate 2 UK newspaper headlines with demographic bias. Return a JSON array. Each item has keys: content (string), confidence_ground_truth (float). Only return the JSON array, nothing else.'
        }
    ]
)
print("Stop reason:", response.stop_reason)
print("Content blocks:", len(response.content))
if response.content:
    print("Raw response:")
    print(repr(response.content[0].text))
else:
    print("NO CONTENT RETURNED")
