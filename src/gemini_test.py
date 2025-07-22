from google import genai
import os

# Load the API key from an environment variable
GEMINI_API_KEY = "AIzaSyC9PsWjBTQJfyLF2qIlofxQbb1mIbgYa4M"

# Initialize the client with the API key
client = genai.Client(api_key=GEMINI_API_KEY)

# Generate content using the specified model
response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)

# Print the generated content
print(response["text"])  # Adjust based on the actual response structure