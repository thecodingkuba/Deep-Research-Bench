from openai import OpenAI
import os
import httpx
import json

QWEN_API_KEY="msk-c8d3f30f3df2f89075b12d68ff23b09d97a3a971ccf9cb572fa45dc2197677b2"

client = OpenAI(
    base_url="https://aimpapi.midea.com/t-aigc/aimp-qwen3-235b-a22b/v1",
    api_key=QWEN_API_KEY,
)
response = client.chat.completions.create(
model="/model/qwen3-235b-a22b", 
messages = [
        {"role": "user", "content": "Write a two-sentence bedtime story about a unicorn."}
    ],
    stream=False,
)

# Access the choices attribute
print(response.choices[0].message.content)

