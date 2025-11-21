import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "sk-b78cada5a61c42188e095daf0ce76c5f"
client = OpenAI()

resp = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world"
)
print(resp)
