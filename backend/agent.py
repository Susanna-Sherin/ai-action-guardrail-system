import json
import logging

from google import genai

from backend.config import GEMINI_API_KEY, GEMINI_MODEL

# ---------------------------------------------------
# Configure Gemini Client
# ---------------------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------

SYSTEM_PROMPT = """
You are an enterprise AI agent.

Your ONLY responsibility is to convert the user's request into a structured tool call.

You NEVER execute actions.

Return ONLY valid JSON.

Available tools:

1. db_delete
2. send_email
3. read_file

Rules:

If the user wants to delete database records:

{
  "tool":"db_delete",
  "params":{
      "record_count":<number>
  }
}

If the user wants to send an email:

{
  "tool":"send_email",
  "params":{
      "recipient_domain":"example.com"
  }
}

If the user wants to read a file:

{
  "tool":"read_file",
  "params":{
      "path":"..."
  }
}

Return ONLY JSON.

Never explain.

Never use markdown.

Never output anything except JSON.
"""
# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------


def clean_json_response(text: str) -> str:
    """
    Removes markdown code fences if the model returns them.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def parse_response(response_text: str) -> dict:
    """
    Convert Gemini response into a Python dictionary.
    """

    cleaned = clean_json_response(response_text)

    try:
        return json.loads(cleaned)

    except Exception as e:
        logger.error("Invalid JSON returned by Gemini")
        logger.exception(e)
        raise ValueError("Gemini returned invalid JSON.")


# ---------------------------------------------------
# Main Function
# ---------------------------------------------------


def generate_tool_call(user_prompt: str) -> dict:
    """
    Converts a natural language request into
    a structured tool call using Gemini.
    """

    prompt = f"""
{SYSTEM_PROMPT}

User Request:

{user_prompt}
"""

    try:
        print("Model:", GEMINI_MODEL)

        response = client.models.generate_content(
            model=GEMINI_MODEL or "gemini-flash-latest",
            contents=prompt,
        )

        tool_call = parse_response(response.text)

        logger.info("Tool call generated successfully.")

        return tool_call

    except Exception as e:

        logger.exception("Gemini request failed. Using local fallback agent.")

        return generate_local_tool_call(user_prompt)

def generate_local_tool_call(user_prompt: str) -> dict:
    """
    Fallback rule-based agent.
    Used when LLM is unavailable.
    """

    prompt = user_prompt.lower()

    # Database delete
    if "delete" in prompt:

        numbers = [
            int(word)
            for word in prompt.split()
            if word.isdigit()
        ]

        count = numbers[0] if numbers else 1

        return {
            "tool": "db_delete",
            "params": {
                "record_count": count
            }
        }


    # Email
    if "email" in prompt or "mail" in prompt:

        domain = "external.com"

        if "gmail" in prompt:
            domain = "gmail.com"

        elif "company" in prompt:
            domain = "company.com"


        return {
            "tool": "send_email",
            "params": {
                "recipient_domain": domain
            }
        }


    # File read
    if "read" in prompt or "file" in prompt:

        path = "confidential/file.txt"

        return {
            "tool": "read_file",
            "params": {
                "path": path
            }
        }


    return {
        "tool": "read_file",
        "params": {
            "path": "normal/file.txt"
        }
    }


# ---------------------------------------------------
# Local Test
# ---------------------------------------------------

if __name__ == "__main__":

    result = generate_tool_call(
        "Delete 500 customer records."
    )

    print(json.dumps(result, indent=4))