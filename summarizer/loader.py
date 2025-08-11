"""Data loading utilities for ticket summarization."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from .config import settings


@dataclass(slots=True)
class Ticket:
    """Representation of a support ticket."""

    number: str
    description: str
    work_notes: str
    comments: str
    opened_at: str
    resolved_at: str
    closed_at: str
    assignment_group: str
    original_assignment_group: str
    extra: dict[str, Any] = field(default_factory=dict)


__all__ = ["Ticket", "load_tickets"]


def load_tickets(path: Path, delimiter: str = ",") -> list[Ticket]:
    """Load a list of :class:`Ticket` objects from a CSV file.

    Parameters
    ----------
    path:
        Path to the CSV file containing ticket data.
    delimiter:
        The delimiter character for the input CSV file.

    Returns
    -------
    list[Ticket]
        A list of tickets parsed from the CSV file.
    """
    if len(delimiter) != 1:
        raise ValueError("Delimiter must be a single character.")
    df = pd.read_csv(path, delimiter=delimiter, dtype=str).fillna("")
    required_columns = {"number", "description"}
    if not required_columns.issubset(df.columns):
        missing = sorted(required_columns - set(df.columns))
        raise ValueError(f"Input CSV file is missing required columns: {', '.join(missing)}")

    known_columns = {
        "number",
        "description",
        "work_notes",
        "comments",
        "opened_at",
        "resolved_at",
        "closed_at",
        "assignment_group",
        "original_assignment_group",
    }

    tickets: list[Ticket] = []
    for row in df.to_dict(orient="records"):
        ticket_data = {
            "number": row.get("number"),
            "description": row.get("description"),
            "work_notes": row.get("work_notes", ""),
            "comments": row.get("comments", ""),
            "opened_at": row.get("opened_at", ""),
            "resolved_at": row.get("resolved_at", ""),
            "closed_at": row.get("closed_at", ""),
            "assignment_group": row.get("assignment_group", ""),
            "original_assignment_group": row.get("original_assignment_group", ""),
        }
        if ticket_data["number"] is None or ticket_data["description"] is None:
            raise ValueError("Missing 'number' or 'description' in row")

        extra = {k: v for k, v in row.items() if k not in known_columns}
        ticket_data["extra"] = extra

        tickets.append(Ticket(**ticket_data))
    return tickets
