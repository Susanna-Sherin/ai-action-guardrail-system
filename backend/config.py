import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENAI_MODEL = os.getenv("OPENAI_MODEL")

GEMINI_MODEL = os.getenv("GEMINI_MODEL")

DB_PATH = os.getenv("DB_PATH")

POLICY_FILE = os.getenv("POLICY_FILE")

APP_ENV = os.getenv("APP_ENV")

LOG_LEVEL = os.getenv("LOG_LEVEL")