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
    extra: dict[str, Any] = field(default_factory=dict)


__all__ = ["Ticket", "load_tickets"]


def load_tickets(path: Path) -> list[Ticket]:
    """Load a list of :class:`Ticket` objects from a CSV file.

    Parameters
    ----------
    path:
        Path to the CSV file containing ticket data.

    Returns
    -------
    list[Ticket]
        A list of tickets parsed from the CSV file.
    """

    df = pd.read_csv(path, delimiter=settings.csv_delimiter, dtype=str)
    tickets: list[Ticket] = []
    for row in df.to_dict(orient="records"):
        number = row.pop("number")
        description = row.pop("description")
        tickets.append(Ticket(number=number, description=description, extra=row))
    return tickets
