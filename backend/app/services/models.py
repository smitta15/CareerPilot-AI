from dotenv import load_dotenv
import os

from app.settings import settings

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

LLM_AVAILABLE = False
planner_llm = None
agent_llm = None
report_llm = None

if settings.ENABLE_LLM and GROQ_API_KEY:
    try:
        from langchain_groq import ChatGroq

        planner_llm = ChatGroq(
            model=os.getenv("GROQ_PLANNER_MODEL", GROQ_MODEL),
            api_key=GROQ_API_KEY,
            temperature=0.0,
            max_retries=2,
        )

        agent_llm = ChatGroq(
            model=os.getenv("GROQ_AGENT_MODEL", GROQ_MODEL),
            api_key=GROQ_API_KEY,
            temperature=0.3,
            max_retries=2,
        )

        report_llm = ChatGroq(
            model=os.getenv("GROQ_REPORT_MODEL", GROQ_MODEL),
            api_key=GROQ_API_KEY,
            temperature=0.0,
            max_retries=2,
        )
        LLM_AVAILABLE = True
    except Exception:
        LLM_AVAILABLE = False
