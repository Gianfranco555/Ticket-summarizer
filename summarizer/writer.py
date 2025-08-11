"""Writes data to different file formats."""

from pathlib import Path
from typing import List, Dict

import pandas as pd

__all__ = ["write_csv", "write_markdown"]


def write_csv(rows: List[Dict], path: Path) -> None:
    """Writes a list of dictionaries to a CSV file.

    Args:
        rows: A list of dictionaries, where each dictionary represents a row.
        path: The path to the output CSV file.
    """
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def write_markdown(rows: List[Dict], path: Path) -> None:
    """Renders a simple pipe table with incident and summary columns.

    Args:
        rows: A list of dictionaries, where each dictionary must have 'incident' and 'summary' keys.
        path: The path to the output Markdown file.
    """
    with open(path, "w") as f:
        f.write("| incident | summary |\n")
        f.write("|---|---|\n")
        for row in rows:
            f.write(f"| {row['incident']} | {row['summary']} |\n")
