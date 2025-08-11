"""Ticket chunking and token counting utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import tiktoken

from .config import settings

if TYPE_CHECKING:
    from .loader import Ticket


__all__ = ["chunk_tickets", "token_len"]


def token_len(text: str, model: str | None = None) -> int:
    """Return the number of tokens in a string of text."""
    model = model or settings.model
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def chunk_tickets(
    tickets: list[Ticket], max_tokens: int, overlap: int
) -> list[str]:
    """Chunk a list of tickets by token count with overlap.

    Args:
        tickets: A list of Ticket objects.
        max_tokens: The maximum number of tokens per chunk.
        overlap: The number of tokens to overlap between chunks.

    Returns:
        A list of strings, where each string is a chunk of formatted tickets.
    """
    chunks: list[str] = []
    all_formatted_tickets = [
        f"[{ticket.number}] {ticket.description}" for ticket in tickets
    ]

    current_pos = 0
    while current_pos < len(all_formatted_tickets):
        chunk_tickets_list = []
        current_chunk_tokens = 0

        # Find end of chunk
        end_pos = current_pos
        while end_pos < len(all_formatted_tickets):
            ticket_to_add = all_formatted_tickets[end_pos]
            ticket_tokens = token_len(ticket_to_add)

            separator_tokens = token_len("---") if chunk_tickets_list else 0

            if current_chunk_tokens + ticket_tokens + separator_tokens > max_tokens:
                break

            chunk_tickets_list.append(ticket_to_add)
            current_chunk_tokens += ticket_tokens + separator_tokens
            end_pos += 1

        if not chunk_tickets_list:
            # This can happen if a single ticket is larger than max_tokens.
            # In this case, we just add the single ticket as a chunk.
            chunks.append(all_formatted_tickets[current_pos])
            current_pos += 1
            continue

        chunks.append("---".join(chunk_tickets_list))

        # If we are at the end, break
        if end_pos >= len(all_formatted_tickets):
            break

        # Move current_pos back by overlap
        overlap_tokens_count = 0
        new_start_pos = end_pos - 1

        while new_start_pos > current_pos:
            ticket_to_overlap = all_formatted_tickets[new_start_pos]
            overlap_tokens_count += token_len(ticket_to_overlap)
            if chunk_tickets_list and new_start_pos > 0:
                overlap_tokens_count += token_len("---")

            if overlap_tokens_count > overlap:
                break

            new_start_pos -= 1

        current_pos = new_start_pos + 1
        if current_pos >= end_pos: # Ensure we make progress
        current_pos = end_pos

    return chunks
