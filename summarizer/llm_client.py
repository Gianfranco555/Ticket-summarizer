import asyncio
import json
import backoff
from openai import OpenAI, RateLimitError, APIError

from . import config

client = OpenAI(api_key=config.settings.openai_api_key)

SYSTEM_PROMPT = """
You are a helpful assistant that summarises support tickets.
The user will provide a chunk of a ticket, and you will respond with a JSON object.
The JSON object should have a single key, "key_points", which is a list of strings.
"""

@backoff.on_exception(backoff.expo, (RateLimitError, APIError), max_tries=5)
async def summarise_chunk(chunk_text: str) -> list[str]:
    """
    Summarises a chunk of text using the OpenAI ChatCompletion API.
    Returns a list of key points.
    """
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=config.settings.model,
        max_tokens=config.settings.max_tokens // 8,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk_text},
        ],
        response_format={"type": "json_object"},
    )
    assistant_message = response.choices[0].message.content
    if assistant_message:
        try:
            data = json.loads(assistant_message)
            return data.get("key_points", [])
        except json.JSONDecodeError:
            return []
    return []

def summarise_chunk_sync(text: str) -> list[str]:
    """
    Synchronous wrapper for summarise_chunk.
    """
    return asyncio.run(summarise_chunk(text))
