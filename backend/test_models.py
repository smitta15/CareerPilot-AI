import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
model = ChatGroq(
    model=model_name,
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0,
)

response = model.invoke("List available Groq models or describe your model configuration.")
print(response.content)