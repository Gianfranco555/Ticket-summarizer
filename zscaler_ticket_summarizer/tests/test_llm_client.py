import asyncio
import json
from unittest import mock

from zscaler_ticket_summarizer.summarizer.llm_client import summarise_chunk_sync


def test_summarise_chunk_sync_e2e():
    """
    Test that summarise_chunk_sync correctly calls the OpenAI API
    and parses the response.
    """
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(["point 1", "point 2"]),
                }
            }
        ]
    }

    # Since the function we're testing is synchronous, but it calls an async
    # function internally, we need to mock the async OpenAI call to return a
    # future.
    future = asyncio.Future()
    future.set_result(mock_response)

    with mock.patch("openai.ChatCompletion.acreate", return_value=future) as mock_acreate:
        result = summarise_chunk_sync("some text")

        # Verify that the API was called with the correct parameters
        mock_acreate.assert_called_once()
        # Not checking all args, just that it was called.

        # Verify that the result is correctly parsed
        assert result == ["point 1", "point 2"]
