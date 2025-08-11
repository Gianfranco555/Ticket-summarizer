from pathlib import Path
from summarizer.loader import load_tickets

def test_sample_load():
    sample = Path("sample_data/tiny_demo.csv")
    rows = load_tickets(sample)
    assert len(rows) == 3
