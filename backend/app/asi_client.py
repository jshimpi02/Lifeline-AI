import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

ASI_ONE_URL = "https://api.asi1.ai/v1/chat/completions"
MODEL = "asi1"
TIMEOUT = 90
SESSION_MAP = {}


def get_session_id(conversation_id: str) -> str:
    if conversation_id not in SESSION_MAP:
        SESSION_MAP[conversation_id] = str(uuid.uuid4())
    return SESSION_MAP[conversation_id]


def asi_one_chat_completion(
    messages,
    tools=None,
    conversation_id="lifeline_ai",
    temperature=0.2,
    max_tokens=1200,
):
    api_key = os.getenv("ASI_ONE_API_KEY")

    if not api_key:
        raise ValueError("ASI_ONE_API_KEY is missing")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "x-session-id": get_session_id(conversation_id),
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if tools:
        payload["tools"] = tools

    response = requests.post(
        ASI_ONE_URL,
        headers=headers,
        json=payload,
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def asi_one_chat(prompt: str, conversation_id: str = "lifeline_ai") -> str:
    response = asi_one_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        conversation_id=conversation_id,
    )

    return response["choices"][0]["message"]["content"]


def asi_one_json(prompt: str, conversation_id: str = "lifeline_ai"):
    text = asi_one_chat(prompt, conversation_id=conversation_id).strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        return {
            "recommendation": text,
            "reason": "ASI:One returned plain text instead of JSON.",
            "next_steps": [
                "Review incident details",
                "Dispatch appropriate response resources",
                "Continue monitoring new reports",
            ],
        }