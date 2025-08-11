"""Data loading utilities for ticket summarization."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from .config import settings


@dataclass(slots=True)
class Ticket:
    """Representation of a support ticket."""

    number: str
    description: str
    work_notes: str
    comments: str
    opened_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
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
    df = pd.read_csv(path, delimiter=delimiter, dtype=str)

    # Strip whitespace from all string fields to ensure consistency
    for col in df.columns:
        df[col] = df[col].str.strip()

    required_columns = {"number", "description"}
    if not required_columns.issubset(df.columns):
        missing = sorted(required_columns - set(df.columns))
        raise ValueError(f"Input CSV file is missing required columns: {', '.join(missing)}")

    # Dynamically discover the columns from the dataclass fields
    known_columns = {f.name for f in fields(Ticket) if f.name != "extra"}
    date_columns = {"opened_at", "resolved_at", "closed_at"}

    # Convert date columns to datetime objects, coercing errors to NaT
    for col in date_columns:
        if col in df.columns:
            # Convert to datetime, coercing errors. This creates NaT for invalid dates.
            s = pd.to_datetime(df[col], errors="coerce")
            # Explicitly convert NaT to None. This is more robust than relying on to_pydatetime().
            # The series must be of object dtype to hold None.
            df[col] = s.astype(object).where(s.notna(), None)

    # Fill any remaining NaN/NA values with empty strings for non-date columns
    non_date_cols = [c for c in df.columns if c not in date_columns]
    df[non_date_cols] = df[non_date_cols].fillna('')

    tickets: list[Ticket] = []
    for row in df.to_dict(orient="records"):
        if not row.get("number") or not row.get("description"):
            raise ValueError("Missing 'number' or 'description' in row")

        # Prepare data for dataclass instantiation
        init_data = {
            col: row.get(col) if col in df.columns else (None if col in date_columns else "")
            for col in known_columns
        }

        # All other columns go into "extra"
        init_data["extra"] = {k: v for k, v in row.items() if k not in known_columns}

        tickets.append(Ticket(**init_data))

    return tickets
