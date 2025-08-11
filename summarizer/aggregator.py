"""Aggregates chunks of data into a single list."""

from typing import List, Dict

__all__ = ["merge_results"]


def merge_results(chunks: List[List[Dict]]) -> List[Dict]:
    """Flattens and sorts a list of lists of dictionaries by 'incident'.

    Args:
        chunks: A list of lists of dictionaries, where each inner list is a chunk of data.

    Returns:
        A single list of dictionaries, sorted by the 'incident' key.
    """
    flattened = [item for sublist in chunks for item in sublist]
    return sorted(flattened, key=lambda x: x["incident"])
