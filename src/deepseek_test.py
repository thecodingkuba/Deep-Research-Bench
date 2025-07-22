from openai import OpenAI
import os
import httpx
import json

DEEPSEEK_API_KEY="msk-68a74a8195300e232b449a651964efdf65ccc31f2a2e16e8f7994ae781337e01"

client = OpenAI(
    base_url="https://aimpapi.midea.com/t-aigc/aimp-deepseek-v3-0324/v1",
    api_key=DEEPSEEK_API_KEY,
)
response = client.chat.completions.create(
    model="/model/Deepseek-V3",
    messages=[
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ],
    stream=False,
)

# Access the choices attribute
print(response.choices[0].message.content)




