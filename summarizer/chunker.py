"""Ticket chunking and token counting utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import tiktoken

from .config import settings

if TYPE_CHECKING:
    from .loader import Ticket


__all__ = ["chunk_tickets", "token_len"]


def token_len(text: str, model: str | None = None) -> int:
    """Return the number of tokens in a string of text.

    Parameters
    ----------
    text
        The text to be tokenized.
    model
        The name of the model to use for tokenization. If ``None``,
        the model from the application settings will be used.

    Returns
    -------
    int
        The number of tokens in the text.
    """
    model = model or settings.model
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def chunk_tickets(
    tickets: list[Ticket], chunk_token_limit: int, max_records: int
) -> list[str]:
    """Chunk a list of tickets by token count and number of records.

    This function iterates through a list of tickets and groups them into
    chunks. A chunk is finalized and added to the output list if either of
    the following conditions is met:

    - The number of tickets in the current chunk has reached ``max_records``.
    - Adding the next ticket would cause the chunk's total tokens to
      exceed ``chunk_token_limit``.

    Each finalized chunk is a single string, with each ticket formatted as
    ``"[<TICKET_NUMBER>] <description>"`` and multiple tickets within the
    same chunk separated by ``"---"``.

    Any remaining tickets that do not form a full chunk are processed and
    returned as the final chunk.

    Parameters
    ----------
    tickets
        A list of :class:`Ticket` objects to be chunked.
    chunk_token_limit
        The maximum number of tokens allowed in a single chunk.
    max_records
        The maximum number of tickets allowed in a single chunk.

    Returns
    -------
    list[str]
        A list of strings, where each string is a chunk of formatted tickets.
    """
    chunks: list[str] = []
    current_chunk_tickets: list[str] = []
    current_chunk_tokens = 0

    def format_ticket(ticket: Ticket) -> str:
        return f"[{ticket.number}] {ticket.description}"

    for ticket in tickets:
        formatted_ticket = format_ticket(ticket)
        ticket_tokens = token_len(formatted_ticket)

        # Check if the current chunk is full
        if (
            current_chunk_tickets
            and (
                len(current_chunk_tickets) >= max_records
                or current_chunk_tokens + token_len("---") + ticket_tokens > chunk_token_limit
            )
        ):
            chunks.append("---".join(current_chunk_tickets))
            current_chunk_tickets = []
            current_chunk_tokens = 0

        # Add ticket to the current chunk
        current_chunk_tickets.append(formatted_ticket)
        if len(current_chunk_tickets) > 1:
            current_chunk_tokens += token_len("---")
        current_chunk_tokens += ticket_tokens

    # Add the last remaining chunk
    if current_chunk_tickets:
        chunks.append("---".join(current_chunk_tickets))

    return chunks
