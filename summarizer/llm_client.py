import asyncio
import json
import backoff
import openai
from openai import RateLimitError, APIError

from . import config

# Set OpenAI API key
openai.api_key = config.openai_api_key

SYSTEM_PROMPT = """
You are a helpful assistant that summarises ZScaler support tickets.
The user will provide a chunk of a ticket, and you will respond with a list of key points.
Respond with a JSON list of strings.
"""

@backoff.on_exception(backoff.expo, (RateLimitError, APIError), max_tries=5)
async def summarise_chunk(chunk_text: str) -> list[dict]:
    """
    Summarises a chunk of text using the OpenAI ChatCompletion API.
    """
    response = await openai.ChatCompletion.acreate(
        model=config.model,
        max_tokens=config.max_tokens // 8,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk_text},
        ],
    )
    assistant_message = response["choices"][0]["message"]["content"]
    return json.loads(assistant_message)

def summarise_chunk_sync(text: str) -> list[dict]:
    """
    Synchronous wrapper for summarise_chunk.
    """
    return asyncio.run(summarise_chunk(text))
