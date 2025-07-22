from openai import OpenAI
import os
import httpx

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")
client = OpenAI(
    base_url="https://aimpapi.midea.com/t-aigc/aimp-deepseek-v3-0324/v1",
    api_key=deepseek_api_key,
)
response = client.chat.completions.create(
    model="deepseek-v3-0324",
    messages=[
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ]

)

# Print the model's response
print(response.choices[0].message.content)




